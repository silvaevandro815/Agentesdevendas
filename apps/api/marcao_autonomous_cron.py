"""
=============================================================================
MOTOR AUTÔNOMO DE FOLLOW-UP, COBRANÇAS E AUDITORIA STRAVA — MARCÃO PERSONAL
Executa o agendador interno (cron) de alta confiabilidade:
1. 12:30 (Seg-Sex) - Cobrança de foto de almoço / dieta
2. 18:00 (Seg, Qua, Sex) - Cobrança de treinos (academia/casa) e dados pendentes
3. 22:00 (Diário) - Auditoria Noturna Strava (conselhos/broncas) & Sono Anabólico GH
4. 19:00 (Domingos) - Envio semanal da Landing Page individual do aluno
=============================================================================
"""

import os
import json
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

try:
    from fichas_engine import (
        enviar_mensagem_whatsapp_fichas,
        enviar_presenca_fichas,
        buscar_ficha_existente,
        verificar_e_cobrar_alunos_com_dados_pendentes,
        get_supabase_headers
    )
except ImportError:
    from apps.api.fichas_engine import (
        enviar_mensagem_whatsapp_fichas,
        enviar_presenca_fichas,
        buscar_ficha_existente,
        verificar_e_cobrar_alunos_com_dados_pendentes,
        get_supabase_headers
    )

try:
    from strava_service import executar_auditoria_strava_noturna_22h
except ImportError:
    from apps.api.strava_service import executar_auditoria_strava_noturna_22h

class MarcaoAutonomousScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
        self.historico_disparos: List[Dict[str, Any]] = []
        self._inicializado = False

    def iniciar(self):
        """Inicia os agendamentos automáticos em segundo plano."""
        if self._inicializado:
            return
        
        # 1. Cobrança de Almoço / Dieta às 12:30 (Segunda a Sexta)
        self.scheduler.add_job(
            self.rotina_cobranca_almoco,
            CronTrigger(hour=12, minute=30, day_of_week="mon-fri", timezone="America/Sao_Paulo"),
            id="cron_cobranca_almoco",
            replace_existing=True
        )

        # 2. Cobrança de Treino & Dados Pendentes às 18:00 (Segunda, Quarta e Sexta)
        self.scheduler.add_job(
            self.rotina_cobranca_treino_e_pendencias,
            CronTrigger(hour=18, minute=0, day_of_week="mon,wed,fri", timezone="America/Sao_Paulo"),
            id="cron_cobranca_treino_pendencias",
            replace_existing=True
        )

        # 3. Auditoria Noturna Strava & Sono Anabólico GH às 22:00 (Todos os dias)
        self.scheduler.add_job(
            self.rotina_auditoria_strava_e_sono,
            CronTrigger(hour=22, minute=0, timezone="America/Sao_Paulo"),
            id="cron_strava_auditoria_noturna",
            replace_existing=True
        )

        # 4. Disparo Semanal da Landing Page do Aluno aos Domingos às 19:00
        self.scheduler.add_job(
            self.rotina_disparo_landing_pages_semanais,
            CronTrigger(hour=19, minute=0, day_of_week="sun", timezone="America/Sao_Paulo"),
            id="cron_landing_page_semanal",
            replace_existing=True
        )

        self.scheduler.start()
        self._inicializado = True
        print("[MARCAO AUTONOMOUS CRON] Agendador de Follow-ups do Marcão INICIADO com sucesso!")

    def _registrar_log(self, tipo: str, detalhes: Any):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo,
            "detalhes": detalhes
        }
        self.historico_disparos.append(log_entry)
        if len(self.historico_disparos) > 50:
            self.historico_disparos.pop(0)

    # -------------------------------------------------------------------------
    # 1. ROTINA DE COBRANÇA DE ALMOÇO / NUTRIÇÃO (12:30)
    # -------------------------------------------------------------------------
    async def rotina_cobranca_almoco(self, filtro_aluno: str = None) -> dict:
        """Pede foto do prato para os alunos avaliarem os macronutrientes."""
        headers = get_supabase_headers()
        enviados = []
        try:
            async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=id,nome,telefone,local_treino", headers=headers)
                alunos = r.json() if r.status_code == 200 else []

            for a in alunos:
                tel = a.get("telefone")
                nome = a.get("nome") or "Guerreiro(a)"
                if not tel:
                    continue
                if filtro_aluno and filtro_aluno not in str(tel) and filtro_aluno.lower() not in nome.lower():
                    continue

                # 2 balões curtos conforme regra de ouro
                baloes = [
                    f"Fala, {nome}! 🦁 Tudo na paz? Marcão passando pra ver seu almoço!",
                    "Manda a foto do seu prato aqui pra eu dar uma olhada se tem proteína e salada suficientes! 📸👊"
                ]

                for b in baloes:
                    await enviar_presenca_fichas(tel, "composing", 1400)
                    await asyncio.sleep(1.2)
                    await enviar_mensagem_whatsapp_fichas(tel, b)

                enviados.append({"aluno": nome, "telefone": tel, "status": "cobranca_refeicao_enviada"})

            self._registrar_log("cobranca_almoco", {"total": len(enviados), "enviados": enviados})
            return {"sucesso": True, "total": len(enviados), "detalhes": enviados}
        except Exception as e:
            print(f"[CRON COBRANCA ALMOCO] Erro: {e}")
            return {"sucesso": False, "erro": str(e)}

    # -------------------------------------------------------------------------
    # 2. ROTINA DE COBRANÇA DE TREINO & DADOS PENDENTES (18:00)
    # -------------------------------------------------------------------------
    async def rotina_cobranca_treino_e_pendencias(self, filtro_aluno: str = None) -> dict:
        """
        1. Se o aluno tiver dados incompletos (fotos, balança, altura): cobra as pendências.
        2. Se estiver completo: cobra o treino do dia (Academia vs Casa).
        """
        headers = get_supabase_headers()
        resultado = []

        try:
            # 1. Dispara cobrança de pendências para quem está incompleto
            pendencias = await verificar_e_cobrar_alunos_com_dados_pendentes(filtro_aluno=filtro_aluno)
            resultado.extend(pendencias)

            # 2. Para alunos completos, cobra o treino do dia
            async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=id,nome,telefone,local_treino,objetivo", headers=headers)
                alunos = r.json() if r.status_code == 200 else []

            alunos_com_pendencias = [p.get("telefone") for p in pendencias if p.get("telefone")]

            for a in alunos:
                tel = a.get("telefone")
                nome = a.get("nome") or "Guerreiro(a)"
                local = a.get("local_treino") or "academia"
                if not tel or tel in alunos_com_pendencias:
                    continue
                if filtro_aluno and filtro_aluno not in str(tel) and filtro_aluno.lower() not in nome.lower():
                    continue

                if local == "casa":
                    msg1 = f"Fala, {nome}! 🦁💪 Treinão funcional em casa de hoje já tá pago ou vai ser agora no início da noite?"
                    msg2 = "Não pula o treino por nada! São 40 minutinhos que vão acelerar seu resultado! Me avisa quando terminar! 🔥"
                else:
                    msg1 = f"Fala, {nome}! 🦁💪 Já foi pra academia mandar o treino pra conta ou vai agora à noite?"
                    msg2 = "Bora pra cima! Foco na execução e carga progressiva! Me conta como foi a sessão hoje! 👊🔥"

                await enviar_presenca_fichas(tel, "composing", 1500)
                await asyncio.sleep(1.2)
                await enviar_mensagem_whatsapp_fichas(tel, msg1)
                await asyncio.sleep(1.5)
                await enviar_mensagem_whatsapp_fichas(tel, msg2)

                resultado.append({"aluno": nome, "telefone": tel, "status": "treino_cobrado", "local": local})

            self._registrar_log("cobranca_treino_pendencias", {"total": len(resultado), "resultado": resultado})
            return {"sucesso": True, "total": len(resultado), "detalhes": resultado}
        except Exception as e:
            print(f"[CRON COBRANCA TREINO] Erro: {e}")
            return {"sucesso": False, "erro": str(e)}

    # -------------------------------------------------------------------------
    # 3. ROTINA DE AUDITORIA STRAVA & SONO ANABÓLICO GH (22:00)
    # -------------------------------------------------------------------------
    async def rotina_auditoria_strava_e_sono(self, filtro_aluno: str = None) -> dict:
        """
        Executa a auditoria noturna das 22h do Strava:
        - Analisa batimentos cardíacos, pace e calorias no Strava.
        - Parabeniza treinos fortes ("Treino de Monstro").
        - Dá bronca se o aluno faltou ao treino planejado.
        - Lembra a janela de sono anabólico GH (22h30 às 06h30).
        """
        try:
            res_strava = await executar_auditoria_strava_noturna_22h()
            self._registrar_log("auditoria_strava_sono", res_strava)
            return {"sucesso": True, "auditoria_strava": res_strava}
        except Exception as e:
            print(f"[CRON AUDITORIA STRAVA] Erro: {e}")
            return {"sucesso": False, "erro": str(e)}

    # -------------------------------------------------------------------------
    # 4. DISPARO SEMANAL DA LANDING PAGE DO ALUNO (DOMINGO 19:00)
    # -------------------------------------------------------------------------
    async def rotina_disparo_landing_pages_semanais(self, filtro_aluno: str = None) -> dict:
        """Envia para cada aluno o link de sua Landing Page personalizada atualizada."""
        headers = get_supabase_headers()
        enviados = []
        try:
            async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=id,nome,telefone", headers=headers)
                alunos = r.json() if r.status_code == 200 else []

            for a in alunos:
                tel = a.get("telefone")
                nome = a.get("nome") or "Guerreiro(a)"
                if not tel:
                    continue
                if filtro_aluno and filtro_aluno not in str(tel) and filtro_aluno.lower() not in nome.lower():
                    continue

                link_portal = f"https://marcaopersonal.com/aluno?id={tel}"

                try:
                    from apps.api.aluno_portal_engine import calcular_ranking_top5
                    ranking = await calcular_ranking_top5(tel)
                    top1_nome = ranking[0]["nome"] if ranking else "Evandro Silva Gallina"
                    pos_aluno = next((r["posicao"] for r in ranking if r.get("is_current_user")), None)
                    destaque_rank = f"Você tá em #{pos_aluno} no Ranking dos Leões!" if pos_aluno else f"O topo da semana tá com {top1_nome}! Bora buscar o Top 5!"
                except Exception:
                    destaque_rank = "Confira seu lugar no Ranking dos Leões da semana!"

                baloes = [
                    f"Fala, {nome}! 🦁 Passando pra te entregar sua plataforma oficial atualizada desta semana!",
                    f"Lá tá sua ficha de treinos, metas de água e proteína, e o ranking da semana: {destaque_rank} 🏆",
                    f"Acessa direto aqui: {link_portal}",
                    "Dica de ouro: fixa o link na tela inicial do celular (Compartilhar > Adicionar à Tela de Início no iPhone ou 3 pontinhos > Adicionar à tela inicial no Android) pra virar um app no seu menu! 📲👊"
                ]

                for b in baloes:
                    await enviar_presenca_fichas(tel, "composing", 1500)
                    await asyncio.sleep(1.2)
                    await enviar_mensagem_whatsapp_fichas(tel, b)

                enviados.append({"aluno": nome, "telefone": tel, "link": link_portal})

            self._registrar_log("landing_pages_semanais", {"total": len(enviados), "enviados": enviados})
            return {"sucesso": True, "total": len(enviados), "detalhes": enviados}
        except Exception as e:
            print(f"[CRON LANDING PAGE] Erro: {e}")
            return {"sucesso": False, "erro": str(e)}

    def status(self) -> dict:
        """Retorna o estado do agendador e próximos disparos."""
        jobs_info = []
        if self._inicializado and self.scheduler.running:
            for j in self.scheduler.get_jobs():
                jobs_info.append({
                    "id": j.id,
                    "proxima_execucao": j.next_run_time.isoformat() if j.next_run_time else None
                })
        return {
            "ativo": self._inicializado and self.scheduler.running,
            "jobs_agendados": jobs_info,
            "total_historico_logs": len(self.historico_disparos),
            "ultimos_logs": self.historico_disparos[-10:]
        }

# Instância Singleton
marcao_cron = MarcaoAutonomousScheduler()

if __name__ == "__main__":
    import asyncio
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    async def testar():
        print("Testando inicialização do Agendador do Marcão...")
        marcao_cron.iniciar()
        print("Status:", json.dumps(marcao_cron.status(), indent=2, ensure_ascii=False))
    asyncio.run(testar())
