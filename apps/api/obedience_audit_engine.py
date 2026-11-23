"""
=============================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
MOTOR PROFISSIONAL DE AUDITORIA DE OBEDIÊNCIA & RANKING SEMANAL REAL
=============================================================================
Substitui qualquer pontuação fictícia/estática por uma auditoria matemática
em tempo real (0 a 100 pontos = 0% a 100%) baseada em 5 pilares verificáveis
nos últimos 7 dias (horário de Brasília UTC-3):

1. TREINOS EXECUTADOS (Ficha do Portal + Relógio/Strava): até 35 pontos
   - Conexão Strava ativa: +3 pts
   - Treinos reais na semana (dias únicos >= 10 min no Strava ou salvos na Ficha): até 32 pts
2. FOTOS DE REFEIÇÕES & EVOLUÇÃO CORPORAL (WhatsApp/Portal): até 25 pontos
   - +5 pts por dia único com foto enviada na semana (máximo 25 pts = 5 dias)
3. FICHA COMPLETA, BIOMETRIA & PESAGEM SEMANAL: até 20 pontos
   - Peso + Altura cadastrados (+4), Dias de treino (+3), Local/Objetivo (+3)
   - Pesagem/Bioimpedância na semana (+6), Check-in ativo na semana (+4)
4. PRODUTOS & EQUIPAMENTOS DO PROTOCOLO (Balança/Shopee/Braip): até 15 pontos
   - Balança de Bioimpedância ativa (+8)
   - Produtos complementares adquiridos (Creatina, Colágeno, Whey, Acessórios): até +7
5. CONSTÂNCIA SEMANAL (Streak Real dos Últimos 7 Dias): até 5 pontos
   - 5+ dias ativos (+5), 3-4 dias (+3), 1-2 dias (+1), 0 dias (0)

Zero inflação artificial. Se o aluno não obedece, a nota cai de verdade.
=============================================================================
"""

import os
import time
import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""

FUSO_BR = timezone(timedelta(hours=-3))

# Cache em memória para evitar excesso de chamadas à API do Strava (TTL 10 min)
_STRAVA_CACHE: Dict[str, Tuple[float, List[dict]]] = {}
_STRAVA_CACHE_TTL = 600  # segundos


def _get_headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def _normalizar_tel(tel: Any) -> str:
    return "".join(filter(str.isdigit, str(tel or "")))


def _last8(tel: Any) -> str:
    t = _normalizar_tel(tel)
    return t[-8:] if len(t) >= 8 else t


def _extrair_data_iso(valor: Any) -> Optional[str]:
    """Extrai YYYY-MM-DD de uma string ISO ou data."""
    if not valor:
        return None
    s = str(valor).strip()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    return None


def _esta_na_janela_7d(data_str: Optional[str], limite_inicio: str, hoje_str: str) -> bool:
    if not data_str:
        return False
    d = _extrair_data_iso(data_str)
    if not d:
        return False
    return limite_inicio <= d <= hoje_str


def _buscar_atividades_strava_7d_cached(
    ficha: dict, inicio_7d_epoch: int
) -> Tuple[List[dict], Optional[dict]]:
    """
    Busca atividades reais do Strava dos últimos 7 dias com cache de 10 minutos.
    Retorna (lista_atividades_validas, tokens_atualizados_ou_None).
    """
    metas = ficha.get("metas_nutricionais") or {}
    if not isinstance(metas, dict):
        return [], None

    access_token = metas.get("strava_access_token")
    refresh_token = metas.get("strava_refresh_token")
    expires_at = metas.get("strava_token_expires_at") or 0
    athlete_id = str(metas.get("strava_athlete_id") or "")

    if not access_token and not refresh_token:
        return [], None

    cache_key = athlete_id or _last8(ficha.get("telefone"))
    now_ts = time.time()
    if cache_key in _STRAVA_CACHE:
        cached_ts, cached_ativs = _STRAVA_CACHE[cache_key]
        if now_ts - cached_ts < _STRAVA_CACHE_TTL:
            return cached_ativs, None

    try:
        try:
            from strava_service import renovar_token_strava, buscar_atividades_aluno_strava
        except ImportError:
            from apps.api.strava_service import renovar_token_strava, buscar_atividades_aluno_strava

        tokens_novos = None
        if (not access_token or now_ts > float(expires_at) - 60) and refresh_token:
            ren = renovar_token_strava(refresh_token)
            if ren.get("success") and ren.get("access_token"):
                access_token = ren["access_token"]
                tokens_novos = {
                    "strava_access_token": ren["access_token"],
                    "strava_refresh_token": ren.get("refresh_token") or refresh_token,
                    "strava_token_expires_at": ren.get("expires_at"),
                }

        if not access_token:
            return [], tokens_novos

        brutas = buscar_atividades_aluno_strava(access_token, start_epoch=inicio_7d_epoch) or []
        # Filtra atividades reais (mínimo 10 minutos = 600 segundos para impedir treinos falsos)
        validas = [
            a for a in brutas
            if isinstance(a, dict) and int(a.get("moving_time") or 0) >= 600
        ]
        _STRAVA_CACHE[cache_key] = (now_ts, validas)
        return validas, tokens_novos
    except Exception as e:
        print(f"[AUDIT_OBEDIENCIA] Erro ao consultar Strava de {ficha.get('nome')}: {e}")
        return [], None


def _classificar_obediencia(score: int, treinos_semana: int, fotos_semana: int) -> dict:
    """Retorna selo, status, cor e diagnóstico honesto baseado na nota real."""
    if score >= 90:
        return {
            "nivel": "ELITE",
            "badge": f"👑 Leão Alfa ({score}% Obediente)",
            "status_obediencia": f"{score}% • Disciplina de Elite",
            "cor": "#fbbf24",
            "sinalizador": "Obediência Total • Treino, Dieta & Evolução em Dia",
        }
    elif score >= 70:
        return {
            "nivel": "ALTA",
            "badge": f"🔥 Modo Leão ({score}% Obediente)",
            "status_obediencia": f"{score}% • Alta Obediência",
            "cor": "#10b981",
            "sinalizador": "No Ritmo Certo • Mantenha a Constância",
        }
    elif score >= 50:
        dica = "Faltam treinos na semana" if treinos_semana == 0 else "Capriche mais nas fotos e treinos"
        return {
            "nivel": "MEDIA",
            "badge": f"⚡ Em Evolução ({score}%)",
            "status_obediencia": f"{score}% • Obediência Parcial",
            "cor": "#06b6d4",
            "sinalizador": f"Em Evolução • {dica}",
        }
    elif score >= 30:
        if treinos_semana == 0:
            motivo = "Zero treinos registrados na semana"
        elif fotos_semana == 0:
            motivo = "Sem fotos de refeição/evolução na semana"
        else:
            motivo = "Frequência abaixo da meta semanal"
        return {
            "nivel": "ALERTA",
            "badge": f"⚠️ Alerta de Disciplina ({score}%)",
            "status_obediencia": f"{score}% • Atenção na Disciplina",
            "cor": "#f97316",
            "sinalizador": f"Alerta • {motivo}",
        }
    else:
        return {
            "nivel": "CRITICO",
            "badge": f"🚨 Fora do Foco ({score}%)",
            "status_obediencia": f"{score}% • Fora do Protocolo",
            "cor": "#ef4444",
            "sinalizador": "Fora do Foco • Sem treinos e metas atrasadas",
        }


def _gerar_proximos_passos(detalhes: dict) -> List[str]:
    """Gera recomendações objetivas para o aluno saber exatamente como subir no ranking."""
    passos = []
    if detalhes["treinos"]["pontos"] < 32:
        faltam = max(0, detalhes["treinos"]["meta_semanal"] - detalhes["treinos"]["dias_unicos_7d"])
        if faltam > 0:
            passos.append(f"Registrar {faltam} treino(s) na ficha ou no Strava (+{32 - min(32, detalhes['treinos']['pontos_execucao'])} pts)")
    if not detalhes["treinos"]["strava_conectado"]:
        passos.append("Conectar relógio/app Strava no painel (+3 pts)")
    if detalhes["fotos"]["pontos"] < 25:
        faltam_f = max(0, 5 - detalhes["fotos"]["dias_unicos_7d"])
        if faltam_f > 0:
            passos.append(f"Enviar fotos de refeições/evolução em mais {faltam_f} dia(s) (+{25 - detalhes['fotos']['pontos']} pts)")
    if detalhes["ficha_biometria"]["pontos"] < 20:
        if not detalhes["ficha_biometria"]["pesagem_7d"]:
            passos.append("Enviar pesagem/print da balança esta semana (+6 pts)")
        if not detalhes["ficha_biometria"]["dias_treino_definidos"]:
            passos.append("Definir seus dias fixos de treino com o Marcão (+3 pts)")
    if detalhes["produtos"]["pontos"] < 15:
        if not detalhes["produtos"]["tem_balanca"]:
            passos.append("Adquirir e ativar a Balança Inteligente Shopee (+8 pts)")
        elif detalhes["produtos"]["produtos_extras"] == 0:
            passos.append("Garantir suplemento ou acessório prescrito no Arsenal (+7 pts)")
    return passos[:3]


async def auditar_obediencia_semanal(
    aluno_atual_telefone: Optional[str] = None,
    incluir_strava: bool = True,
) -> dict:
    """
    Executa a Auditoria Profissional de Obediência Semanal para TODOS os alunos reais
    cadastrados em `fichas_alunos`, cruzando com:
    - `fichas_alunos` (treinos salvos, fotos, ficha completa, pesagem, check-ins, produtos)
    - `clientes_balanca` (compra e ativação da Balança Inteligente)
    - `avaliacoes_corporais` (pesagens e avaliações recentes)
    - `pedidos_braip` e `orders` (compras reais de suplementos/produtos)
    - Strava API v3 (treinos reais de relógio/app nos últimos 7 dias)

    Retorna o relatório completo da auditoria e o ranking ordenado pela pontuação real.
    """
    agora_br = datetime.now(FUSO_BR)
    hoje_str = agora_br.strftime("%Y-%m-%d")
    inicio_7d_dt = agora_br - timedelta(days=6)  # hoje + 6 dias anteriores = 7 dias corridos
    limite_inicio_str = inicio_7d_dt.strftime("%Y-%m-%d")
    inicio_7d_epoch = int(
        datetime(inicio_7d_dt.year, inicio_7d_dt.month, inicio_7d_dt.day, 0, 0, 0, tzinfo=FUSO_BR).timestamp()
    )

    headers = _get_headers()
    last8_atual = _last8(aluno_atual_telefone)

    async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
        r_fichas = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=*", headers=headers)
        fichas = r_fichas.json() if r_fichas.status_code == 200 else []

        r_balanca = await client.get(f"{SUPABASE_URL}/rest/v1/clientes_balanca?select=telefone,remote_jid,status_vip,data_compra", headers=headers)
        clientes_balanca = r_balanca.json() if r_balanca.status_code == 200 else []

        r_aval = await client.get(f"{SUPABASE_URL}/rest/v1/avaliacoes_corporais?select=telefone,remote_jid,created_at,peso_kg", headers=headers)
        avaliacoes = r_aval.json() if r_aval.status_code == 200 else []

        r_braip = await client.get(f"{SUPABASE_URL}/rest/v1/pedidos_braip?select=*", headers=headers)
        pedidos_braip = r_braip.json() if r_braip.status_code == 200 else []

        r_orders = await client.get(f"{SUPABASE_URL}/rest/v1/orders?select=*", headers=headers)
        orders = r_orders.json() if r_orders.status_code == 200 else []

        balanca_last8 = {_last8(c.get("telefone") or c.get("remote_jid")) for c in clientes_balanca if c.get("telefone") or c.get("remote_jid")}

        resultados_brutos = []

        for ficha in fichas:
            nome = (ficha.get("nome") or "Aluno VIP").strip()
            tel = str(ficha.get("telefone") or "")
            l8 = _last8(tel)
            if not l8:
                continue

            metas = ficha.get("metas_nutricionais") or {}
            if not isinstance(metas, dict):
                metas = {}

            treino_obj = ficha.get("treino_atual") or {}
            if not isinstance(treino_obj, dict):
                treino_obj = {}

            dias_treino_lista = ficha.get("dias_treino") or []
            if not isinstance(dias_treino_lista, list):
                dias_treino_lista = []

            meta_treinos_semana = max(3, min(6, len(dias_treino_lista))) if dias_treino_lista else 3

            # -----------------------------------------------------------------
            # PILAR 1: TREINOS EXECUTADOS (FICHA + RELÓGIO/STRAVA) — ATÉ 35 PTS
            # -----------------------------------------------------------------
            dias_treino_portal_7d = set()
            historico_treinos = treino_obj.get("historico_treinos") or []
            if isinstance(historico_treinos, list):
                for h in historico_treinos:
                    if isinstance(h, dict):
                        d_h = _extrair_data_iso(h.get("data") or h.get("salvo_em"))
                        if _esta_na_janela_7d(d_h, limite_inicio_str, hoje_str):
                            dias_treino_portal_7d.add(d_h)

            # Verifica também ultimo_treino_registrado se estiver na janela
            utr = treino_obj.get("ultimo_treino_registrado") or treino_obj.get("ultimo_treino")
            if isinstance(utr, dict):
                d_u = _extrair_data_iso(utr.get("data") or utr.get("salvo_em"))
                if _esta_na_janela_7d(d_u, limite_inicio_str, hoje_str):
                    dias_treino_portal_7d.add(d_u)

            strava_conectado = bool(metas.get("strava_athlete_id") or metas.get("strava_access_token") or metas.get("strava_refresh_token"))
            dias_strava_7d = set()
            atividades_strava_nomes = []
            if incluir_strava and strava_conectado:
                ativs_strava, tokens_novos = _buscar_atividades_strava_7d_cached(ficha, inicio_7d_epoch)
                for at in ativs_strava:
                    d_at = _extrair_data_iso(at.get("start_date_local") or at.get("start_date"))
                    if _esta_na_janela_7d(d_at, limite_inicio_str, hoje_str):
                        dias_strava_7d.add(d_at)
                        atividades_strava_nomes.append(f"{at.get('type', 'Treino')} ({round(int(at.get('moving_time', 0))/60)}min)")

                # Persiste token renovado no Supabase para manter integração saudável
                if tokens_novos and ficha.get("id"):
                    try:
                        metas_atualizadas = dict(metas)
                        metas_atualizadas.update(tokens_novos)
                        await client.patch(
                            f"{SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.{ficha['id']}",
                            headers=headers,
                            json={"metas_nutricionais": metas_atualizadas},
                        )
                    except Exception:
                        pass

            dias_treino_unicos_7d = dias_treino_portal_7d.union(dias_strava_7d)
            qtd_treinos_7d = len(dias_treino_unicos_7d)
            pts_strava_conexao = 3 if strava_conectado else 0
            pts_treino_execucao = round(min(1.0, qtd_treinos_7d / float(meta_treinos_semana)) * 32)
            pts_pilar_treinos = min(35, pts_strava_conexao + pts_treino_execucao)

            # -----------------------------------------------------------------
            # PILAR 2: FOTOS DE REFEIÇÕES & EVOLUÇÃO CORPORAL — ATÉ 25 PTS
            # -----------------------------------------------------------------
            dias_fotos_7d = set()
            fotos = ficha.get("fotos_criptografadas") or []
            total_fotos_7d = 0
            if isinstance(fotos, list):
                for f_item in fotos:
                    if isinstance(f_item, dict):
                        d_f = _extrair_data_iso(f_item.get("data") or f_item.get("created_at"))
                        if _esta_na_janela_7d(d_f, limite_inicio_str, hoje_str):
                            dias_fotos_7d.add(d_f)
                            total_fotos_7d += 1

            ultima_foto_corp = _extrair_data_iso(metas.get("ultima_foto_corporal_data"))
            if _esta_na_janela_7d(ultima_foto_corp, limite_inicio_str, hoje_str):
                dias_fotos_7d.add(ultima_foto_corp)

            dispensa_fotos = bool(ficha.get("dispensa_fotos") or metas.get("dispensa_fotos") or metas.get("recusou_fotos"))
            if dispensa_fotos and len(dias_fotos_7d) == 0:
                # Se tem dispensa formal de fotos corporais, pontua se houve pesagem na semana
                data_peso_tmp = _extrair_data_iso(metas.get("data_ultimo_peso") or metas.get("ultimo_peso_data"))
                pts_pilar_fotos = 15 if _esta_na_janela_7d(data_peso_tmp, limite_inicio_str, hoje_str) else 0
            else:
                pts_pilar_fotos = min(25, len(dias_fotos_7d) * 5)

            # -----------------------------------------------------------------
            # PILAR 3: FICHA COMPLETA, BIOMETRIA & PESAGEM SEMANAL — ATÉ 20 PTS
            # -----------------------------------------------------------------
            peso_val = ficha.get("peso_kg") or metas.get("peso")
            altura_val = ficha.get("altura_cm") or metas.get("altura_cm")
            tem_peso_altura = bool(peso_val and altura_val)
            tem_dias_treino = len(dias_treino_lista) > 0
            tem_local_objetivo = bool(ficha.get("local_treino") and (ficha.get("objetivo") or metas.get("objetivo")))

            pts_cadastro = (4 if tem_peso_altura else 0) + (3 if tem_dias_treino else 0) + (3 if tem_local_objetivo else 0)

            # Pesagem nos últimos 7 dias
            dias_pesagem_7d = set()
            for campo_peso in [metas.get("data_ultimo_peso"), metas.get("ultimo_peso_data")]:
                d_p = _extrair_data_iso(campo_peso)
                if _esta_na_janela_7d(d_p, limite_inicio_str, hoje_str):
                    dias_pesagem_7d.add(d_p)

            for av in avaliacoes:
                if _last8(av.get("telefone") or av.get("remote_jid")) == l8:
                    d_av = _extrair_data_iso(av.get("created_at"))
                    if _esta_na_janela_7d(d_av, limite_inicio_str, hoje_str):
                        dias_pesagem_7d.add(d_av)

            pesagem_7d = len(dias_pesagem_7d) > 0
            pts_pesagem = 6 if pesagem_7d else 0

            # Check-in ativo nos últimos 7 dias
            d_checkin = _extrair_data_iso(ficha.get("ultimo_checkin_data"))
            checkin_7d = _esta_na_janela_7d(d_checkin, limite_inicio_str, hoje_str)
            pts_checkin = 4 if checkin_7d else 0

            pts_pilar_ficha = min(20, pts_cadastro + pts_pesagem + pts_checkin)

            # -----------------------------------------------------------------
            # PILAR 4: PRODUTOS & EQUIPAMENTOS DO PROTOCOLO — ATÉ 15 PTS
            # -----------------------------------------------------------------
            tem_balanca = bool(metas.get("tem_balanca_bioimpedancia") or (l8 in balanca_last8))
            pts_balanca = 8 if tem_balanca else 0

            # Produtos extras comprados (Braip, Orders ou registrados em metas_nutricionais.produtos_comprados)
            produtos_extras = 0
            prods_meta = metas.get("produtos_comprados") or metas.get("compras") or []
            if isinstance(prods_meta, list):
                produtos_extras += len(prods_meta)

            for pb in pedidos_braip:
                pb_tel = _last8(pb.get("telefone") or pb.get("client_cel") or pb.get("customer_phone"))
                pb_status = str(pb.get("status") or pb.get("trans_status") or "").lower()
                if pb_tel == l8 and pb_status in ["pago", "aprovado", "completa", "paid", "approved", "2"]:
                    produtos_extras += 1

            for od in orders:
                od_tel = _last8(od.get("telefone") or od.get("phone") or od.get("customer_phone"))
                od_status = str(od.get("status") or "").lower()
                if od_tel == l8 and od_status in ["paid", "pago", "approved", "completed", "concluido"]:
                    produtos_extras += 1

            pts_extras = min(7, produtos_extras * 4)
            pts_pilar_produtos = min(15, pts_balanca + pts_extras)

            # -----------------------------------------------------------------
            # PILAR 5: CONSTÂNCIA SEMANAL (DIAS ÚNICOS ATIVOS NA SEMANA) — ATÉ 5 PTS
            # -----------------------------------------------------------------
            dias_ativos_7d = dias_treino_unicos_7d.union(dias_fotos_7d).union(dias_pesagem_7d)
            if checkin_7d and d_checkin:
                dias_ativos_7d.add(d_checkin)

            qtd_dias_ativos = len(dias_ativos_7d)
            if qtd_dias_ativos >= 5:
                pts_pilar_constancia = 5
            elif qtd_dias_ativos >= 3:
                pts_pilar_constancia = 3
            elif qtd_dias_ativos >= 1:
                pts_pilar_constancia = 1
            else:
                pts_pilar_constancia = 0

            # -----------------------------------------------------------------
            # SCORE FINAL REAL (0 A 100%)
            # -----------------------------------------------------------------
            score_total = min(
                100,
                pts_pilar_treinos
                + pts_pilar_fotos
                + pts_pilar_ficha
                + pts_pilar_produtos
                + pts_pilar_constancia,
            )

            classif = _classificar_obediencia(score_total, qtd_treinos_7d, len(dias_fotos_7d))

            auditoria_detalhada = {
                "treinos": {
                    "pontos": pts_pilar_treinos,
                    "max": 35,
                    "pontos_execucao": pts_treino_execucao,
                    "dias_unicos_7d": qtd_treinos_7d,
                    "meta_semanal": meta_treinos_semana,
                    "portal_dias": sorted(list(dias_treino_portal_7d)),
                    "strava_dias": sorted(list(dias_strava_7d)),
                    "strava_conectado": strava_conectado,
                    "strava_atividades": atividades_strava_nomes,
                },
                "fotos": {
                    "pontos": pts_pilar_fotos,
                    "max": 25,
                    "dias_unicos_7d": len(dias_fotos_7d),
                    "total_enviadas_7d": total_fotos_7d,
                    "dias": sorted(list(dias_fotos_7d)),
                },
                "ficha_biometria": {
                    "pontos": pts_pilar_ficha,
                    "max": 20,
                    "peso_altura_ok": tem_peso_altura,
                    "dias_treino_definidos": tem_dias_treino,
                    "pesagem_7d": pesagem_7d,
                    "checkin_7d": checkin_7d,
                },
                "produtos": {
                    "pontos": pts_pilar_produtos,
                    "max": 15,
                    "tem_balanca": tem_balanca,
                    "produtos_extras": produtos_extras,
                },
                "constancia": {
                    "pontos": pts_pilar_constancia,
                    "max": 5,
                    "dias_ativos_7d": qtd_dias_ativos,
                    "dias": sorted(list(dias_ativos_7d)),
                },
            }

            proximos_passos = _gerar_proximos_passos(auditoria_detalhada)

            objetivo_txt = str(ficha.get("objetivo") or metas.get("objetivo") or "Saúde & Performance")
            local_txt = "Academia" if str(ficha.get("local_treino") or "").lower() != "casa" else "Treino em Casa"

            resultados_brutos.append({
                "nome": nome,
                "telefone": tel,
                "meta": f"{objetivo_txt[:42]} ({local_txt})",
                "score": score_total,
                "streak_dias": qtd_dias_ativos,  # Streak REAL da semana (dias ativos nos últimos 7 dias)
                "treinos_semana": qtd_treinos_7d,
                "fotos_semana": len(dias_fotos_7d),
                "tem_balanca": tem_balanca,
                "strava_conectado": strava_conectado,
                "nivel_obediencia": classif["nivel"],
                "badge": classif["badge"],
                "status_obediencia": classif["status_obediencia"],
                "cor_status": classif["cor"],
                "sinalizador": classif["sinalizador"],
                "auditoria": auditoria_detalhada,
                "como_subir": proximos_passos,
                "is_current_user": bool(last8_atual and last8_atual == l8),
            })

    # Ordena do maior score real para o menor; desempate por treinos na semana e dias ativos
    resultados_brutos.sort(
        key=lambda x: (x["score"], x["treinos_semana"], x["streak_dias"], x["fotos_semana"]),
        reverse=True,
    )

    ranking_final = []
    for pos, r in enumerate(resultados_brutos, 1):
        medalha = "👑" if pos == 1 and r["score"] >= 70 else ("🥇" if pos == 1 else ("🥈" if pos == 2 else ("🥉" if pos == 3 else f"#{pos}")))
        ranking_final.append({
            "posicao": pos,
            "medalha": medalha,
            "nome": r["nome"],
            "telefone": r["telefone"],
            "meta": r["meta"],
            "score": r["score"],
            "metas_batidas_pct": f"{r['score']}%",
            "streak_dias": r["streak_dias"],
            "treinos_semana": r["treinos_semana"],
            "fotos_semana": r["fotos_semana"],
            "tem_balanca": r["tem_balanca"],
            "strava_conectado": r["strava_conectado"],
            "nivel_obediencia": r["nivel_obediencia"],
            "badge": r["badge"],
            "status_obediencia": r["status_obediencia"],
            "cor_status": r["cor_status"],
            "sinalizador": r["sinalizador"],
            "auditoria": r["auditoria"],
            "como_subir": r["como_subir"],
            "is_current_user": r["is_current_user"],
        })

    return {
        "sucesso": True,
        "janela_auditoria": {
            "inicio": limite_inicio_str,
            "fim": hoje_str,
            "dias_avaliados": 7,
            "auditado_em": agora_br.isoformat(),
        },
        "criterios_pontuacao": {
            "treinos_ficha_e_relogio": 35,
            "fotos_refeicoes_e_evolucao": 25,
            "ficha_biometria_e_pesagem": 20,
            "produtos_e_equipamentos": 15,
            "constancia_semanal": 5,
            "total_maximo": 100,
        },
        "total_alunos_auditados": len(ranking_final),
        "ranking": ranking_final,
    }


async def registrar_compra_produto_aluno(identificador: str, produto_nome: str, origem: str = "Shopee/Braip") -> dict:
    """
    Registra uma compra de produto confirmado na ficha do aluno (metas_nutricionais.produtos_comprados)
    para contabilizar automaticamente no Pilar 4 da Auditoria de Obediência Semanal.
    """
    l8 = _last8(identificador)
    if not l8:
        return {"sucesso": False, "erro": "Identificador inválido"}

    headers = _get_headers()
    agora_br = datetime.now(FUSO_BR)
    async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
        q = f"{SUPABASE_URL}/rest/v1/fichas_alunos?or=(telefone.ilike.*{l8}*,remote_jid.ilike.*{l8}*)&select=id,nome,metas_nutricionais"
        r = await client.get(q, headers=headers)
        if r.status_code != 200 or not r.json():
            return {"sucesso": False, "erro": "Aluno não encontrado"}

        row = r.json()[0]
        metas = row.get("metas_nutricionais") or {}
        if not isinstance(metas, dict):
            metas = {}

        compras = metas.get("produtos_comprados") or []
        if not isinstance(compras, list):
            compras = []

        novo_item = {
            "produto": produto_nome,
            "origem": origem,
            "data": agora_br.strftime("%Y-%m-%d"),
            "registrado_em": agora_br.isoformat(),
        }
        compras.append(novo_item)
        metas["produtos_comprados"] = compras
        if "balan" in produto_nome.lower():
            metas["tem_balanca_bioimpedancia"] = True

        patch_r = await client.patch(
            f"{SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.{row['id']}",
            headers=headers,
            json={"metas_nutricionais": metas},
        )
        if patch_r.status_code in [200, 204]:
            return {"sucesso": True, "aluno": row.get("nome"), "compra": novo_item, "total_produtos": len(compras)}
        return {"sucesso": False, "erro": f"Erro ao atualizar ficha: {patch_r.status_code}"}


if __name__ == "__main__":
    import asyncio
    import json
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    res = asyncio.run(auditar_obediencia_semanal())
    print(json.dumps(res, indent=2, ensure_ascii=False))
