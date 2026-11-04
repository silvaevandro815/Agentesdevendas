"""
=============================================================================
MOTOR AUTÔNOMO DE FOLLOW-UP, COBRANÇAS E AUDITORIA STRAVA — MARCÃO PERSONAL
Executa o agendador interno (cron) de alta confiabilidade:
1. 12:30 (Seg-Sex) - Cobrança de foto de almoço / dieta
2. 18:00 (Seg, Qua, Sex) - Cobrança de treinos (academia/casa) e dados pendentes
3. 22:00 (Diário) - Auditoria Noturna Strava (conselhos/broncas) & Sono Anabólico GH
4. 19:00 (Domingos) - Envio semanal da Landing Page individual do aluno

BLINDAGEM ANTI-DUPLICAÇÃO & HUMANIZAÇÃO (REGRA INVIOLÁVEL):
- Trava de Idempotência persistente (Memória + Disco JSON + Redis) para que
  NENHUM aluno receba mensagens repetidas no mesmo dia.
- Balões curtos e ágeis (30 a 70 caracteres cada) com pausas naturais de digitação (composing).
=============================================================================
"""

import os
import json
import time
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

# Arquivo de persistência local das travas de deduplicação
DEDUP_LOCK_FILE = os.path.join(_base_dir, "data", "cron_dedup_locks.json")
os.makedirs(os.path.dirname(DEDUP_LOCK_FILE), exist_ok=True)


def _carregar_locks_disco() -> dict:
    try:
        if os.path.exists(DEDUP_LOCK_FILE):
            with open(DEDUP_LOCK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _salvar_lock_disco(chave: str, ts: float):
    try:
        dados = _carregar_locks_disco()
        agora = time.time()
        # Expira locks com mais de 48 horas
        dados = {k: v for k, v in dados.items() if agora - v < 172800}
        dados[chave] = ts
        with open(DEDUP_LOCK_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)
    except Exception as e:
        print(f"[DEDUP LOCK] Erro salvando lock em disco: {e}")


class MarcaoAutonomousScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
        self.historico_disparos: List[Dict[str, Any]] = []
        self._inicializado = False
        self._locks_memoria: Dict[str, float] = {}

    def adquirir_trava_deduplicacao(self, tipo: str, telefone: str, ttl_segundos: int = 43200) -> bool:
        """
        Garante que NENHUM follow-up repetido seja disparado para o mesmo aluno no mesmo dia.
        Retorna True se o disparo for inédito e a trava for adquirida.
        Retorna False se o disparo já foi realizado hoje por qualquer processo (VPS ou Local).
        """
        tel_digitos = "".join(filter(str.isdigit, str(telefone)))
        hoje_str = datetime.now().strftime("%Y-%m-%d")
        chave = f"lock:{tipo}:{tel_digitos}:{hoje_str}"
        agora = time.time()

        # 1. Checa memória interna
        if chave in self._locks_memoria:
            if agora - self._locks_memoria[chave] < ttl_segundos:
                print(f"[DEDUPLICACAO MEMÓRIA] {tipo} para {tel_digitos} já enviado hoje. Ignorando duplicata!")
                return False

        # 2. Checa persistência em disco
        locks_disco = _carregar_locks_disco()
        if chave in locks_disco:
            if agora - locks_disco[chave] < ttl_segundos:
                self._locks_memoria[chave] = locks_disco[chave]
                print(f"[DEDUPLICACAO DISCO] {tipo} para {tel_digitos} já enviado hoje. Ignorando duplicata!")
                return False

        # 3. Adquire a trava de idempotência com sucesso
        self._locks_memoria[chave] = agora
        _salvar_lock_disco(chave, agora)
        return True

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
        """
        Pede foto do prato para os alunos avaliarem os macronutrientes.
        Regra Inviolável: 3 balões ultracurtos (30-70 caracteres cada),
        digitação humana (composing) e trava anti-duplicação absoluta.
        """
        headers = get_supabase_headers()
        enviados = []
        bloqueados_dedup = []

        try:
            async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=id,nome,telefone,local_treino", headers=headers)
                alunos = r.json() if r.status_code == 200 else []

            for a in alunos:
                tel = a.get("telefone")
                nome = a.get("nome") or "Guerreiro(a)"
                if not tel or any(b in str(tel) for b in ["85066687", "553285066687"]):
                    continue
                if filtro_aluno and filtro_aluno not in str(tel) and filtro_aluno.lower() not in nome.lower():
                    continue

                # Trava anti-duplicação: se já enviou hoje para este telefone, pula sem repetir
                if not self.adquirir_trava_deduplicacao("cobranca_almoco", tel):
                    bloqueados_dedup.append({"aluno": nome, "telefone": tel, "motivo": "ja_enviado_hoje"})
                    continue

                # Primeiro nome para máxima humanização e tom próximo de Personal Trainer
                primeiro_nome = nome.strip().split()[0] if nome else "Guerreiro"

                # 3 balões curtos e ágeis (30 a 65 caracteres cada)
                baloes = [
                    f"Fala, {primeiro_nome}! 🦁 Tudo na paz por aí?",
                    "Marcão passando na ronda do almoço! 👊🔥",
                    "Manda a foto do seu prato pra eu checar os macros e a proteína! 📸🥗"
                ]

                for b in baloes:
                    await enviar_presenca_fichas(tel, "composing", 1500)
                    await asyncio.sleep(1.4)
                    await enviar_mensagem_whatsapp_fichas(tel, b)
                    await asyncio.sleep(1.0)

                enviados.append({"aluno": nome, "telefone": tel, "status": "cobranca_refeicao_enviada"})

            self._registrar_log("cobranca_almoco", {
                "total_enviados": len(enviados),
                "total_bloqueados_dedup": len(bloqueados_dedup),
                "enviados": enviados,
                "bloqueados": bloqueados_dedup
            })
            return {"sucesso": True, "total": len(enviados), "detalhes": enviados, "bloqueados_dedup": bloqueados_dedup}
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
        Regra Inviolável: múltiplos balões curtos (35-70 caracteres) e trava anti-duplicação.
        """
        headers = get_supabase_headers()
        resultado = []
        bloqueados_dedup = []

        try:
            # 1. Dispara cobrança de pendências para quem está incompleto
            pendencias = await verificar_e_cobrar_alunos_com_dados_pendentes(filtro_aluno=filtro_aluno)
            resultado.extend(pendencias)

            # 2. Para alunos completos, cobra o treino SOMENTE NOS DIAS REAIS DE TREINO DE CADA UM
            from datetime import timezone, timedelta
            fuso_br = timezone(timedelta(hours=-3))
            agora_br = datetime.now(fuso_br)
            dias_map = {0: "segunda", 1: "terça", 2: "quarta", 3: "quinta", 4: "sexta", 5: "sábado", 6: "domingo"}
            dia_hoje_norm = dias_map[agora_br.weekday()].lower().replace("terça", "terca").replace("sábado", "sabado")

            async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=id,nome,telefone,local_treino,objetivo,dias_treino", headers=headers)
                alunos = r.json() if r.status_code == 200 else []

            alunos_com_pendencias = [p.get("telefone") for p in pendencias if p.get("telefone")]

            for a in alunos:
                tel = a.get("telefone")
                nome = a.get("nome") or "Guerreiro(a)"
                local = a.get("local_treino") or "academia"
                if not tel or tel in alunos_com_pendencias or any(b in str(tel) for b in ["85066687", "553285066687"]):
                    continue
                if filtro_aluno and filtro_aluno not in str(tel) and filtro_aluno.lower() not in nome.lower():
                    continue

                # REGRA INVIOLÁVEL DO DIRETOR EVANDRO: SOMENTE NOS DIAS REAIS DE TREINO!
                dias_aluno = [str(d).lower().replace("terça", "terca").replace("sábado", "sabado").strip() for d in (a.get("dias_treino") or [])]
                if not dias_aluno or dia_hoje_norm not in dias_aluno:
                    # Hoje NÃO é dia de treino deste aluno. O Marcão respeita o descanso!
                    continue

                # Trava anti-duplicação para cobrança de treino diária
                if not self.adquirir_trava_deduplicacao("cobranca_treino", tel):
                    bloqueados_dedup.append({"aluno": nome, "telefone": tel, "motivo": "ja_enviado_hoje"})
                    continue

                primeiro_nome = nome.strip().split()[0] if nome else "Guerreiro"

                if local == "casa":
                    baloes = [
                        f"Fala, {primeiro_nome}! 🦁💪 Treinão funcional em casa de hoje tá pago?",
                        "Não pula o treino por nada! São 40 minutinhos que aceleram o resultado! 🔥",
                        "Me avisa aqui quando terminar pra eu computar no ranking! 👊"
                    ]
                else:
                    baloes = [
                        f"Fala, {primeiro_nome}! 🦁💪 Já foi pra academia mandar o treino pra conta?",
                        "Foco na execução, carga progressiva e nada de enrolar! 🔥",
                        "Me conta aqui como foi a pegada do treino de hoje! 👊"
                    ]

                for b in baloes:
                    await enviar_presenca_fichas(tel, "composing", 1500)
                    await asyncio.sleep(1.4)
                    await enviar_mensagem_whatsapp_fichas(tel, b)
                    await asyncio.sleep(1.0)

                resultado.append({"aluno": nome, "telefone": tel, "status": "treino_cobrado", "local": local})

            self._registrar_log("cobranca_treino_pendencias", {
                "total_enviados": len(resultado),
                "total_bloqueados_dedup": len(bloqueados_dedup),
                "resultado": resultado,
                "bloqueados": bloqueados_dedup
            })
            return {"sucesso": True, "total": len(resultado), "detalhes": resultado, "bloqueados_dedup": bloqueados_dedup}
        except Exception as e:
            print(f"[CRON COBRANCA TREINO] Erro: {e}")
            return {"sucesso": False, "erro": str(e)}

    # -------------------------------------------------------------------------
    # 3. ROTINA DE AUDITORIA STRAVA & SONO ANABÓLICO GH (22:00)
    # -------------------------------------------------------------------------
    async def rotina_auditoria_strava_e_sono(self, filtro_aluno: str = None) -> dict:
        """
        Dispara a auditoria noturna de treinos conectados ao Strava.
        Se treinou: avalia frequência cardíaca e parabeniza.
        Se faltou no dia de treino: dá uma bronca técnica, puxa a orelha e prescreve sono anabólico.
        Se não tem Strava: envia o link direto de conexão OAuth para vincular relógio/app.
        """
        try:
            # Trava anti-duplicação global para a auditoria noturna
            if filtro_aluno:
                chave_filtro = f"strava_auditoria_{filtro_aluno}"
            else:
                chave_filtro = "strava_auditoria_global"

            if not self.adquirir_trava_deduplicacao(chave_filtro, "todos_alunos"):
                print("[DEDUPLICACAO] Auditoria noturna Strava já realizada hoje. Ignorando repetição!")
                return {"sucesso": True, "aviso": "Auditoria já realizada hoje", "bloqueado_dedup": True}

            resultado = await executar_auditoria_strava_noturna_22h(filtro_aluno=filtro_aluno)
            self._registrar_log("auditoria_strava_sono", resultado)
            return {"sucesso": True, "resultado": resultado}
        except Exception as e:
            print(f"[CRON AUDITORIA STRAVA] Erro: {e}")
            return {"sucesso": False, "erro": str(e)}

    # -------------------------------------------------------------------------
    # 4. ROTINA DE DISPARO DAS LANDING PAGES SEMANAIS AOS DOMINGOS (19:00)
    # -------------------------------------------------------------------------
    async def rotina_disparo_landing_pages_semanais(self, filtro_aluno: str = None) -> dict:
        """
        Envia a landing page exclusiva de cada aluno no domingo à noite:
        - Link dinâmico: https://marcaopersonal.com/aluno?id={tel}
        - Ficha de treinos e ranking da semana
        - Instruções de PWA (fixar como app na tela inicial do celular)
        """
        headers = get_supabase_headers()
        enviados = []
        bloqueados_dedup = []

        try:
            async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=id,nome,telefone", headers=headers)
                alunos = r.json() if r.status_code == 200 else []

            for a in alunos:
                tel = a.get("telefone")
                nome = a.get("nome") or "Guerreiro(a)"
                if not tel or any(b in str(tel) for b in ["85066687", "553285066687"]):
                    continue
                if filtro_aluno and filtro_aluno not in str(tel) and filtro_aluno.lower() not in nome.lower():
                    continue

                if not self.adquirir_trava_deduplicacao("landing_page_semanal", tel, ttl_segundos=86400):
                    bloqueados_dedup.append({"aluno": nome, "telefone": tel, "motivo": "ja_enviado_hoje"})
                    continue

                primeiro_nome = nome.strip().split()[0] if nome else "Guerreiro"
                link_portal = f"https://marcaopersonal.com/aluno?id={tel}"

                baloes = [
                    f"Fala, {primeiro_nome}! 🦁💪 Passando pra te entregar sua Landing Page atualizada da semana!",
                    f"Abre aqui e confere sua evolução e treinos: {link_portal} 👊🔥",
                    "Lá tá sua ficha completa, meta de água e proteína e o ranking Top 5 da semana!",
                    "Dica de ouro: clica em Compartilhar e Adicionar à Tela de Início pra virar um app no seu celular! 📲👊"
                ]

                for b in baloes:
                    await enviar_presenca_fichas(tel, "composing", 1500)
                    await asyncio.sleep(1.4)
                    await enviar_mensagem_whatsapp_fichas(tel, b)
                    await asyncio.sleep(1.0)

                enviados.append({"aluno": nome, "telefone": tel, "link": link_portal})

            self._registrar_log("landing_pages_semanais", {
                "total": len(enviados),
                "total_bloqueados_dedup": len(bloqueados_dedup),
                "enviados": enviados
            })
            return {"sucesso": True, "total": len(enviados), "detalhes": enviados, "bloqueados_dedup": bloqueados_dedup}
        except Exception as e:
            print(f"[CRON LANDING PAGES] Erro: {e}")
            return {"sucesso": False, "erro": str(e)}

    # -------------------------------------------------------------------------
    # PAINEL DE STATUS & TELEMETRIA DO AGENDADOR
    # -------------------------------------------------------------------------
    def status(self) -> dict:
        """Retorna o status atual dos jobs agendados e os últimos disparos executados."""
        jobs_info = []
        if self._inicializado and self.scheduler.running:
            for job in self.scheduler.get_jobs():
                jobs_info.append({
                    "id": job.id,
                    "proxima_execucao": job.next_run_time.isoformat() if job.next_run_time else None
                })

        return {
            "ativo": self._inicializado and self.scheduler.running,
            "jobs_agendados": jobs_info,
            "total_historico_logs": len(self.historico_disparos),
            "ultimos_logs": self.historico_disparos[-10:] if self.historico_disparos else []
        }


# Instância Singleton do Agendador Autônomo Marcão
marcao_cron = MarcaoAutonomousScheduler()


if __name__ == "__main__":
    async def testar():
        print("Testando inicialização do Agendador Marcão...")
        marcao_cron.iniciar()
        print(json.dumps(marcao_cron.status(), indent=2, ensure_ascii=False))

    asyncio.run(testar())
