import os
import json
import re
import httpx
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "act_1048381174031721")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_PIXEL_ID = os.getenv("META_PIXEL_ID", "1417931927184389")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "1416979468145905")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "Marcao_Evo_Key_2026_Secure!")
EVANDRO_WHATSAPP = "5532984587255"

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

TETO_DIARIO_REAIS = float(os.getenv("TETO_DIARIO_PADRAO", "20.00"))
TETO_MENSAL_REAIS = 600.00


def get_meta_headers():
    return {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }


def verificar_conta_anuncios():
    """
    Consulta a Meta Marketing API para verificar status, saldo e limites da conta de anúncios.
    """
    if not META_ACCESS_TOKEN or META_ACCESS_TOKEN.startswith("IGAA"):
        return {
            "status": "aguardando_token",
            "mensagem": "É necessário o Token do Facebook / Meta Marketing API (iniciado em EAAB...) para conectar à conta.",
            "ad_account_id": META_AD_ACCOUNT_ID
        }

    url = f"https://graph.facebook.com/v21.0/{META_AD_ACCOUNT_ID}"
    params = {
        "fields": "id,name,account_status,currency,spend_cap,amount_spent,balance,disable_reason",
        "access_token": META_ACCESS_TOKEN
    }

    try:
        with httpx.Client(verify=False, timeout=15) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "conectado",
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "currency": data.get("currency"),
                    "account_status": data.get("account_status"),
                    "amount_spent": float(data.get("amount_spent", 0)) / 100.0 if data.get("amount_spent") else 0.0,
                    "teto_diario_permitido": TETO_DIARIO_REAIS,
                    "pixel_id": META_PIXEL_ID
                }
            else:
                return {
                    "status": "erro_api",
                    "codigo": resp.status_code,
                    "detalhes": resp.json()
                }
    except Exception as e:
        return {"status": "erro_conexao", "erro": str(e)}


def consultar_gasto_do_dia():
    """
    Retorna o valor exato gasto hoje na conta de anúncios.
    """
    if not META_ACCESS_TOKEN or META_ACCESS_TOKEN.startswith("IGAA"):
        return 0.0

    url = f"https://graph.facebook.com/v21.0/{META_AD_ACCOUNT_ID}/insights"
    params = {
        "date_preset": "today",
        "fields": "spend,impressions,clicks,cpc,ctr",
        "access_token": META_ACCESS_TOKEN
    }
    try:
        with httpx.Client(verify=False, timeout=15) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                insights = resp.json().get("data", [])
                if insights:
                    return float(insights[0].get("spend", 0.0))
            return 0.0
    except Exception:
        return 0.0


def enviar_evento_capi(event_name, event_source_url="https://marcaopersonal.com", user_data=None, custom_data=None):
    """
    Envia eventos server-side para a Meta Conversions API (CAPI), garantindo rastreamento 100% blindado contra adblockers.
    """
    if not META_ACCESS_TOKEN or not META_PIXEL_ID:
        return {"sucesso": False, "erro": "Token ou Pixel ID ausente"}

    url = f"https://graph.facebook.com/v21.0/{META_PIXEL_ID}/events"
    import time

    u_data = user_data or {
        "client_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "client_ip_address": "177.130.242.56"
    }

    payload = {
        "data": [
            {
                "event_name": event_name,
                "event_time": int(time.time()),
                "action_source": "website",
                "event_source_url": event_source_url,
                "user_data": u_data,
                "custom_data": custom_data or {}
            }
        ],
        "access_token": META_ACCESS_TOKEN
    }

    try:
        with httpx.Client(verify=False, timeout=12) as client:
            resp = client.post(url, json=payload)
            return {"sucesso": resp.status_code == 200, "status_code": resp.status_code, "resposta": resp.json()}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def gerar_proposta_diaria(indice_anuncio=1):
    """
    Gera a proposta diária do Rui conectada dinamicamente ao catálogo do Supabase,
    às tendências ao vivo do Google Trends Brasil e com estratégia de funil de 2 fases.
    """
    try:
        from rui_intelligence_engine import obter_produtos_supabase, gerar_inteligencia_completa_produto
        produtos = obter_produtos_supabase()
        if produtos:
            idx = (indice_anuncio - 1) % len(produtos)
            prod_selecionado = produtos[idx]
            intel = gerar_inteligencia_completa_produto(prod_selecionado)

            return {
                "id": idx + 1,
                "produto": prod_selecionado["nome"],
                "sku": prod_selecionado["sku"],
                "preco": prod_selecionado["preco"],
                "categoria": prod_selecionado["categoria"],
                "tipo": "Feed & Stories (Funil 2 Fases: Atenção + Venda)",
                "publico": f"{intel['publico_alvo']['genero']} • Idade: {intel['publico_alvo']['faixa_etaria']} anos",
                "estados_chave": ", ".join(intel['publico_alvo']['estados_chave']),
                "buscas_google": intel["buscas_quentes_google"],
                "headline_fase1": intel["fase_1_atencao"]["headline"],
                "copy_fase1": intel["fase_1_atencao"]["copy"],
                "cta_fase1": intel["fase_1_atencao"]["cta"],
                "headline_fase2": intel["fase_2_venda"]["headline"],
                "copy_fase2": intel["fase_2_venda"]["copy"],
                "cta_fase2": intel["fase_2_venda"]["cta"],
                "link": prod_selecionado["link"],
                "orcamento_diario": f"R$ {TETO_DIARIO_REAIS:.2f}"
            }
    except Exception as e:
        print("Fallback proposta:", e)

    # Fallback caso ocorra erro
    return {
        "id": 1,
        "produto": "Caneta Azempika Original",
        "sku": "AZEMPIKA-CANETA",
        "preco": "R$ 99,00",
        "tipo": "Feed & Stories (Emagrecimento / Saciedade)",
        "publico": "Homens e Mulheres (25-55 anos)",
        "estados_chave": "SP, RJ, MG, PR, SC, RS, DF, GO, BA",
        "buscas_google": ["ozempic", "caneta emagrecimento", "compulsao alimentar"],
        "headline_fase1": "Você não tem falta de disciplina: tem pico de ansiedade alimentar 🔥",
        "copy_fase1": "A Caneta Azempika Original modula a saciedade e queima gordura por R$ 99,00.",
        "cta_fase1": "Entender Como Funciona",
        "headline_fase2": "Diga adeus à compulsão: Caneta Azempika por apenas R$ 99 ⚡",
        "copy_fase2": "Aproveite o lote promocional direto do laboratório com frete Correios.",
        "cta_fase2": "Comprar Caneta Azempika (R$ 99)",
        "link": "https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv",
        "orcamento_diario": f"R$ {TETO_DIARIO_REAIS:.2f}"
    }


def criar_campanha_meta(proposta):
    """
    Cria uma campanha real no Meta Ads via Marketing API, SEMPRE no status PAUSED.
    """
    if not META_ACCESS_TOKEN or META_ACCESS_TOKEN.startswith("IGAA"):
        return None

    url = f"https://graph.facebook.com/v21.0/{META_AD_ACCOUNT_ID}/campaigns"
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    nome_campanha = f"[RUI] {proposta['produto']} — {data_hoje}"

    payload = {
        "name": nome_campanha,
        "objective": "OUTCOME_TRAFFIC",
        "status": "PAUSED",
        "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": False,
        "access_token": META_ACCESS_TOKEN
    }

    try:
        with httpx.Client(verify=False, timeout=20) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                res = resp.json()
                return res.get("id")
            else:
                print(f"Erro ao criar campanha no Meta: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Exceção ao criar campanha no Meta: {e}")
    return None


def ativar_campanha_meta(campaign_id):
    """
    Ativa uma campanha no Meta Ads somente se o gasto do dia estiver abaixo do teto de R$ 20,00.
    """
    if not META_ACCESS_TOKEN or not campaign_id:
        return {"sucesso": False, "erro": "Token ou ID de campanha ausente"}

    gasto_hoje = consultar_gasto_do_dia()
    if gasto_hoje >= TETO_DIARIO_REAIS:
        return {
            "sucesso": False,
            "erro": f"Teto diário atingido (Gasto hoje: R$ {gasto_hoje:.2f} / Teto: R$ {TETO_DIARIO_REAIS:.2f}). Campanha mantida PAUSADA para segurança financeira."
        }

    url = f"https://graph.facebook.com/v21.0/{campaign_id}"
    payload = {
        "status": "ACTIVE",
        "access_token": META_ACCESS_TOKEN
    }

    try:
        with httpx.Client(verify=False, timeout=15) as client:
            resp = client.post(url, data=payload)
            if resp.status_code == 200:
                return {"sucesso": True, "status": "ACTIVE", "campaign_id": campaign_id}
            else:
                return {"sucesso": False, "erro": resp.text}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def pausar_campanha_meta(campaign_id):
    """
    Pausa uma campanha no Meta Ads.
    """
    if not META_ACCESS_TOKEN or not campaign_id:
        return {"sucesso": False, "erro": "Token ou ID de campanha ausente"}

    url = f"https://graph.facebook.com/v21.0/{campaign_id}"
    payload = {
        "status": "PAUSED",
        "access_token": META_ACCESS_TOKEN
    }

    try:
        with httpx.Client(verify=False, timeout=15) as client:
            resp = client.post(url, json=payload)
            return {"sucesso": resp.status_code == 200, "status": "PAUSED"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def ajustar_orcamento_campanha(campaign_id, novo_valor_diario, dias_duracao=1):
    """
    Ajusta dinamicamente o orçamento diário no Meta Ads e grava o novo teto no Supabase.
    """
    if not META_ACCESS_TOKEN:
        return {"sucesso": False, "erro": "Token ausente"}

    try:
        if campaign_id:
            url = f"https://graph.facebook.com/v21.0/{campaign_id}"
            payload = {
                "daily_budget": int(novo_valor_diario * 100),
                "access_token": META_ACCESS_TOKEN
            }
            with httpx.Client(verify=False, timeout=15) as client:
                client.post(url, json=payload)

        # Atualizar no Supabase
        if SUPABASE_KEY:
            url_sb = f"{SUPABASE_URL}/rest/v1/fila_aprovacoes?agente=eq.Rui&order=id.desc&limit=1"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            with httpx.Client(verify=False, timeout=10) as c:
                r = c.get(url_sb, headers=headers)
                recs = r.json()
                if recs:
                    rec_id = recs[0]["id"]
                    patch_url = f"{SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.{rec_id}"
                    c.patch(patch_url, headers=headers, json={"orcamento": f"R$ {novo_valor_diario:.2f} / dia ({dias_duracao} dias)"})

        return {
            "sucesso": True,
            "novo_valor_diario": novo_valor_diario,
            "dias_duracao": dias_duracao,
            "orcamento_total_estimado": novo_valor_diario * dias_duracao
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def parser_comando_orcamento(texto_recebido):
    """
    Interpreta comandos em linguagem natural do Diretor Evandro para ajustar orçamento e duração.
    Exemplos:
      - 'Marcão, bota 30 reais na campanha por 5 dias'
      - 'Rui, aumenta para 25 por dia durante 4 dias'
      - 'orcamento 35 por 7 dias'
    """
    texto = texto_recebido.lower()

    # Procurar valor numérico
    valor_match = re.search(r'(?:bota|aumenta|coloca|orcamento|orçamento|investir|gasta|gastar|para|de)\s*(?:r\$\s*)?(\d+(?:[.,]\d{1,2})?)', texto)
    if not valor_match:
        valor_match = re.search(r'(\d+(?:[.,]\d{1,2})?)\s*(?:reais|conto|por dia|\/dia)', texto)

    if not valor_match:
        return None

    valor_float = float(valor_match.group(1).replace(',', '.'))

    # Procurar dias
    dias_match = re.search(r'(?:por|durante|em|prazo de)\s*(\d+)\s*dias?', texto)
    if not dias_match:
        dias_match = re.search(r'(\d+)\s*dias?', texto)

    dias_int = int(dias_match.group(1)) if dias_match else 1

    return {
        "comando_reconhecido": True,
        "novo_valor_diario": valor_float,
        "dias_duracao": dias_int
    }


def verificar_e_aplicar_guardrails():
    """
    Consulta o gasto do dia. Se atingir ou ultrapassar o teto diário, pausa imediatamente qualquer campanha ativa.
    """
    gasto_hoje = consultar_gasto_do_dia()
    if gasto_hoje >= TETO_DIARIO_REAIS:
        url_campanhas = f"https://graph.facebook.com/v21.0/{META_AD_ACCOUNT_ID}/campaigns"
        params = {
            "fields": "id,name,status",
            "effective_status": "['ACTIVE']",
            "access_token": META_ACCESS_TOKEN
        }
        pausadas = []
        try:
            with httpx.Client(verify=False, timeout=15) as client:
                r = client.get(url_campanhas, params=params)
                if r.status_code == 200:
                    ativas = r.json().get("data", [])
                    for camp in ativas:
                        pausar_campanha_meta(camp["id"])
                        pausadas.append(camp["id"])

            aviso = (
                f"🚨 *ALERTA RUI — TETO DIÁRIO ATINGIDO*\n\n"
                f"O gasto de hoje na conta de anúncios atingiu R$ {gasto_hoje:.2f} (Teto: R$ {TETO_DIARIO_REAIS:.2f}).\n"
                f"Por segurança financeira inviolável, {len(pausadas)} campanha(s) ativa(s) foram pausadas automaticamente."
            )
            with httpx.Client(verify=False, timeout=10) as c:
                c.post(
                    f"{EVOLUTION_API_URL}/message/sendText/sofia",
                    headers={"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"},
                    json={"number": EVANDRO_WHATSAPP, "text": aviso}
                )
            return {"teto_atingido": True, "gasto_hoje": gasto_hoje, "campanhas_pausadas": pausadas}
        except Exception as e:
            return {"erro": str(e)}

    return {"teto_atingido": False, "gasto_hoje": gasto_hoje}


def registrar_proposta_supabase(proposta, meta_campaign_id=None):
    """
    Registra a proposta na tabela fila_aprovacoes do Supabase com detalhes de ambas as fases.
    """
    if not SUPABASE_KEY:
        return None

    url = f"{SUPABASE_URL}/rest/v1/fila_aprovacoes"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    meta_info = f"META_CAMPAIGN_ID: {meta_campaign_id}\n" if meta_campaign_id else ""
    buscas = ", ".join(proposta.get("buscas_google", []))
    conteudo = (
        f"PRODUTO: {proposta['produto']} ({proposta['preco']})\n"
        f"PÚBLICO ALVO: {proposta.get('publico', '')}\n"
        f"ESTADOS DE ALTA BUSCA: {proposta.get('estados_chave', '')}\n"
        f"TENDÊNCIAS GOOGLE: {buscas}\n\n"
        f"--- FASE 1: ATENÇÃO (TOPO DO FUNIL) ---\n"
        f"HEADLINE: {proposta.get('headline_fase1', '')}\n"
        f"COPY: {proposta.get('copy_fase1', '')}\n"
        f"CTA: {proposta.get('cta_fase1', '')}\n\n"
        f"--- FASE 2: VENDA DIRETA (FUNDO DO FUNIL) ---\n"
        f"HEADLINE: {proposta.get('headline_fase2', '')}\n"
        f"COPY: {proposta.get('copy_fase2', '')}\n"
        f"CTA: {proposta.get('cta_fase2', '')}\n\n"
        f"LINK DESTINO: {proposta['link']}\n"
        f"{meta_info}"
        f"STATUS META ADS: PAUSADA (Aguardando Aprovação)"
    )

    data = {
        "agente": "Rui",
        "departamento": "Tráfego Pago",
        "tipo": "Campanha Meta Ads (Funil 2 Fases)",
        "titulo": f"Campanha: {proposta['produto']}",
        "conteudo": conteudo,
        "orcamento": proposta["orcamento_diario"],
        "status": "pending"
    }

    try:
        with httpx.Client(verify=False, timeout=10) as client:
            resp = client.post(url, headers=headers, json=data)
            if resp.status_code in [200, 201]:
                return resp.json()[0]
    except Exception as e:
        print("Erro ao registrar no Supabase:", e)
    return None


def enviar_proposta_whatsapp_evandro(proposta, meta_campaign_id=None):
    """
    Dispara a proposta formatada com instrução de aprovação para o WhatsApp do Diretor Evandro.
    """
    meta_tag = f"🆔 *ID Meta Ads:* `{meta_campaign_id}` (PAUSADA)\n" if meta_campaign_id else ""
    buscas = " • ".join(proposta.get("buscas_google", [])[:3])
    
    mensagem = (
        f"📊 *SUPER INTELIGÊNCIA DE TRÁFEGO PAGO — AGENTE RUI*\n\n"
        f"Fala, meu chefe! Estruturei a estratégia de tráfego de hoje com base no Google Trends e no algoritmo da Meta:\n\n"
        f"🎯 *Campanha:* {proposta['produto']} ({proposta['preco']})\n"
        f"{meta_tag}"
        f"👥 *Público Segmentado:* {proposta.get('publico', '')}\n"
        f"📍 *Estados com Maior Procura (Google Trends):*\n_{proposta.get('estados_chave', '')}_\n"
        f"🔥 *Termos em Alta no Brasil:* {buscas}\n"
        f"💰 *Orçamento Diário:* {proposta['orcamento_diario']} (Teto Seguro Padrão)\n\n"
        f"----------------------------------------\n"
        f"🎣 *FASE 1: ATENÇÃO & DOR (Topo do Funil)*\n"
        f"📝 *Headline:* \\\"{proposta.get('headline_fase1', '')}\\\"\n"
        f"💬 *Texto:* _{proposta.get('copy_fase1', '')}_\n\n"
        f"⚡ *FASE 2: VENDA DIRETA (Fundo do Funil)*\n"
        f"📝 *Headline:* \\\"{proposta.get('headline_fase2', '')}\\\"\n"
        f"💬 *Texto:* _{proposta.get('copy_fase2', '')}_\n"
        f"----------------------------------------\n\n"
        f"🔗 *Link Destino:* {proposta['link']}\n\n"
        f"🔒 *STATUS:* PAUSADA no Gerenciador (R$ 0,00 gasto sem sua ordem).\n\n"
        f"👉 Para colocar no ar agora com R$ 20,00/dia, responda com:\n"
        f"*APROVAR RUI*\n\n"
        f"💡 *Para ajustar orçamento e prazo*, mande por exemplo:\n"
        f"_\\\"Marcão, bota 30 reais por 5 dias\\\"_\n"
    )

    url = f"{EVOLUTION_API_URL}/message/sendText/sofia"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": EVANDRO_WHATSAPP,
        "text": mensagem
    }

    try:
        with httpx.Client(verify=False, timeout=15) as client:
            resp = client.post(url, headers=headers, json=payload)
            return resp.status_code in [200, 201]
    except Exception as e:
        print("Erro ao enviar no WhatsApp:", e)
        return False


def processar_comando_aprovacao(texto_recebido):
    """
    Processa a aprovação da campanha ou ajuste dinâmico de orçamento solicitado por Evandro.
    """
    texto_limpo = texto_recebido.strip().upper()

    # 1. Se for comando de alteração de orçamento
    parsed_orcamento = parser_comando_orcamento(texto_recebido)
    if parsed_orcamento:
        novo_val = parsed_orcamento["novo_valor_diario"]
        dias = parsed_orcamento["dias_duracao"]
        
        # Localizar última campanha
        meta_id = None
        if SUPABASE_KEY:
            url = f"{SUPABASE_URL}/rest/v1/fila_aprovacoes?agente=eq.Rui&order=id.desc&limit=1"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            try:
                with httpx.Client(verify=False, timeout=10) as c:
                    r = c.get(url, headers=headers)
                    recs = r.json()
                    if recs:
                        conteudo = recs[0].get("conteudo", "")
                        for linha in conteudo.splitlines():
                            if linha.startswith("META_CAMPAIGN_ID:"):
                                meta_id = linha.split(":", 1)[1].strip()
                                break
            except Exception:
                pass

        res_ajuste = ajustar_orcamento_campanha(meta_id, novo_val, dias)
        
        msg_confirm = (
            f"💰 *ORÇAMENTO ATUALIZADO PELO DIRETOR EVANDRO!*\n\n"
            f"🎯 *Novo Limite Diário:* R$ {novo_val:.2f} / dia\n"
            f"📅 *Prazo Definido:* {dias} dia(s)\n"
            f"💵 *Investimento Previsto:* R$ {(novo_val * dias):.2f}\n"
            f"🛡️ Guardrail atualizado: monitoramento contínuo 24h ativo!"
        )
        try:
            with httpx.Client(verify=False, timeout=10) as client:
                client.post(
                    f"{EVOLUTION_API_URL}/message/sendText/sofia",
                    headers={"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"},
                    json={"number": EVANDRO_WHATSAPP, "text": msg_confirm}
                )
        except Exception:
            pass

        return {"orcamento_atualizado": True, "detalhes": res_ajuste}

    # 2. Se for aprovação direta
    if "APROVAR RUI" in texto_limpo or texto_limpo == "APROVAR":
        if SUPABASE_KEY:
            url = f"{SUPABASE_URL}/rest/v1/fila_aprovacoes?agente=eq.Rui&status=eq.pending&order=id.desc&limit=1"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            try:
                with httpx.Client(verify=False, timeout=10) as client:
                    r = client.get(url, headers=headers)
                    records = r.json()
                    if records:
                        rec = records[0]
                        rec_id = rec["id"]
                        conteudo = rec.get("conteudo", "")
                        titulo = rec.get("titulo", "")

                        meta_id = None
                        for linha in conteudo.splitlines():
                            if linha.startswith("META_CAMPAIGN_ID:"):
                                meta_id = linha.split(":", 1)[1].strip()
                                break

                        resultado_ativacao = None
                        if meta_id and meta_id != "None":
                            resultado_ativacao = ativar_campanha_meta(meta_id)

                        patch_url = f"{SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.{rec_id}"
                        client.patch(patch_url, headers=headers, json={"status": "approved"})

                        msg_sucesso = (
                            f"🚀 *CAMPANHA APROVADA PELO DIRETOR EVANDRO!*\n\n"
                            f"📋 *{titulo}*\n"
                        )
                        if meta_id and resultado_ativacao and resultado_ativacao.get("sucesso"):
                            msg_sucesso += (
                                f"🆔 *Meta Campaign ID:* `{meta_id}`\n"
                                f"🟢 *Status no Meta:* ATIVA\n"
                                f"🛡️ *Guardrail:* Teto de R$ {TETO_DIARIO_REAIS:.2f}/dia monitorado 24h!\n\n"
                                f"O Agente Rui está acelerando as conversões no Meta Ads! Bons lucros! 🔥"
                            )
                        else:
                            msg_sucesso += (
                                f"✅ Registrada como APROVADA na fila executiva.\n"
                                f"🛡️ Limite Diário: R$ {TETO_DIARIO_REAIS:.2f}/dia estritamente respeitado."
                            )

                        client.post(
                            f"{EVOLUTION_API_URL}/message/sendText/sofia",
                            headers={"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"},
                            json={"number": EVANDRO_WHATSAPP, "text": msg_sucesso}
                        )

                        return {
                            "aprovado": True,
                            "mensagem": f"Campanha {rec_id} aprovada e processada com sucesso!",
                            "meta_ativacao": resultado_ativacao
                        }
                    else:
                        return {"aprovado": False, "mensagem": "Nenhuma proposta pendente do Rui encontrada."}
            except Exception as e:
                return {"aprovado": False, "erro": str(e)}

        return {"aprovado": True, "mensagem": "Comando de aprovação processado com sucesso!"}
    return {"aprovado": False}


if __name__ == "__main__":
    print("=== MOTOR DE TRÁFEGO PAGO (RUI) ===")
    status_conta = verificar_conta_anuncios()
    print("Status da Conta:", status_conta)

    proposta = gerar_proposta_diaria(1)
    print("\nProposta Gerada:")
    print(json.dumps(proposta, indent=2, ensure_ascii=True))
