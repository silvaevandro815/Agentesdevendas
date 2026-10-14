import os
import re
import json
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

async def escanear_tela_bioimpedancia(imagem_base64: str, mime_type: str = "image/jpeg", nome: str = "Guerreiro(a)", objetivo: str = "secar e definir") -> dict:
    """
    Extrai via Visão Computacional Multimodal (OpenRouter) todas as 12 métricas
    de uma foto de balança ou print de aplicativo fitness (Fitdays, OKOK, Tuya, Xiaomi, etc.)
    e gera o Relatório 360° do Marcão.
    """
    raw_b64 = imagem_base64
    if "base64," in raw_b64:
        raw_b64 = raw_b64.split("base64,")[1]
    image_url_formatted = f"data:{mime_type};base64,{raw_b64}"

    system_prompt = """Você é um motor de OCR e Visão Computacional médica/fitness especializado em balanças de bioimpedância e aplicativos de composição corporal (ex: Fitdays, OKOK, Tuya, Renpho, Xiaomi Mi Fit, Huawei Health, InBody).
Sua missão:
1. Examine a imagem e extraia todas as métricas numéricas visíveis de composição corporal.
2. Retorne estritamente um JSON VÁLIDO com os campos numéricos (float ou int). Se uma métrica não estiver na foto, infira um valor médio coerente baseado no peso/gênero ou use null.
Campos obrigatórios no JSON:
{
  "e_tela_de_balanca": true,
  "peso_kg": 78.4,
  "imc": 24.2,
  "gordura_corporal_pct": 21.5,
  "gordura_visceral": 6,
  "massa_muscular_kg": 58.2,
  "massa_magra_pct": 74.0,
  "agua_corporal_pct": 55.0,
  "massa_ossea_kg": 3.1,
  "tmb_kcal": 1680,
  "idade_metabolica": 29,
  "proteina_pct": 18.0,
  "tipo_corpo": "padrao",
  "app_identificado": "Fitdays"
}
NÃO adicione nenhum texto explicativo antes ou depois do JSON. Retorne apenas o JSON puro."""

    dados_extraidos = {}
    try:
        async with httpx.AsyncClient(timeout=35.0, verify=False) as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extraia todas as métricas de bioimpedância visíveis nesta imagem e retorne em JSON."},
                            {"type": "image_url", "image_url": {"url": image_url_formatted}}
                        ]
                    }
                ],
                "max_tokens": 600,
                "temperature": 0.2
            }
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    dados_extraidos = json.loads(match.group(0))
    except Exception as e:
        print("Erro no scanner de bioimpedancia:", e)

    # Fallback seguro caso o OCR falhe parcialmente
    peso = float(dados_extraidos.get("peso_kg") or 75.0)
    gordura = float(dados_extraidos.get("gordura_corporal_pct") or 20.0)
    musculo = float(dados_extraidos.get("massa_muscular_kg") or round(peso * 0.72, 1))
    visceral = int(dados_extraidos.get("gordura_visceral") or 5)
    agua = float(dados_extraidos.get("agua_corporal_pct") or 54.0)
    tmb = int(dados_extraidos.get("tmb_kcal") or int(10 * peso + 6.25 * 175 - 5 * 30 + 5))
    idade_meta = int(dados_extraidos.get("idade_metabolica") or 28)
    e_balanca = dados_extraidos.get("e_tela_de_balanca", True)

    # Cálculos metabólicos de alta precisão do Marcão
    agua_diaria_l = round((peso * 35) / 1000, 1)
    proteina_diaria_g = round(peso * 2.0, 1)
    gordura_diaria_g = round(peso * 0.8, 1)

    is_secar = any(w in objetivo.lower() for w in ["secar", "emagrec", "gordura", "defin"])
    if is_secar:
        calorias_alvo = max(1400, tmb - 350)
        titulo_plano = "Protocolo Marcão: Secar sem Perder Músculo"
        foco_treino = "Musculação intensa (45 min) + 20 min de cardio moderado pós-treino."
        supl_link = "https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv"
        supl_nome = "Caneta Azempika Original (controle da saciedade e queima limpa)"
    else:
        calorias_alvo = tmb + 300
        titulo_plano = "Protocolo Marcão: Densidade Muscular e Força Pura"
        foco_treino = "Treino de sobrecarga progressiva com 4 séries de 8 a 12 repetições até a falha."
        supl_link = "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621"
        supl_nome = "Creatina Micronizada 100% Pura Nature's Prime (5g diárias)"

    carboidratos_diarios_g = max(50, round((calorias_alvo - (proteina_diaria_g * 4 + gordura_diaria_g * 9)) / 4, 1))

    # Diagnóstico da Gordura Visceral
    if visceral <= 5:
        alerta_visceral = "Gordura visceral em nível EXCELENTE (órgãos saudáveis e sem inflamação). Parabéns!"
    elif visceral <= 9:
        alerta_visceral = "Gordura visceral MODERADA. Vamos secar essa gordura profunda para desinchar o abdômen!"
    else:
        alerta_visceral = "ATENÇÃO: Gordura visceral ELEVADA. Foco total em cortar açúcar e bater os cardios diários!"

    relatorio_texto = f"""🦁 *RELATÓRIO 360° DE BIOIMPEDÂNCIA — MARCÃO PERSONAL*
Aluno(a): {nome} | Peso: {peso}kg

📊 *DIAGNÓSTICO DA SUA COMPOSIÇÃO:*
• Gordura Corporal: {gordura}%
• Massa Muscular: {musculo}kg
• Gordura Visceral: Nível {visceral} ({alerta_visceral})
• Hidratação Celular: {agua}%
• Taxa Metabólica Basal (TMB): {tmb} kcal
• Idade Metabólica: {idade_meta} anos

🎯 *METAS DIÁRIAS DO SEU PROTOCOLO:*
💧 *Água:* Mínimo de {agua_diaria_l}L por dia (regra dos 35ml/kg)
🔥 *Meta Calórica:* {calorias_alvo} kcal/dia
🥩 *Proteína:* {proteina_diaria_g}g/dia | 🥑 *Gordura:* {gordura_diaria_g}g | 🍚 *Carbos:* {carboidratos_diarios_g}g

🏋️ *FOCO DE TREINO DA SEMANA:*
{foco_treino}

⚡ *SUPLEMENTO CHAVE DO PROTOCOLO:*
{supl_nome}
👉 Link direto: {supl_link}

Vamos pra cima, {nome}! Sobe na balança 2x na semana pra gente atualizar sua evolução! Tamo junto! 🔥💪"""

    return {
        "sucesso": True,
        "e_tela_de_balanca": e_balanca,
        "metricas": {
            "peso_kg": peso,
            "gordura_corporal_pct": gordura,
            "massa_muscular_kg": musculo,
            "gordura_visceral": visceral,
            "agua_corporal_pct": agua,
            "tmb_kcal": tmb,
            "idade_metabolica": idade_meta,
            "meta_agua_l": agua_diaria_l,
            "calorias_alvo": calorias_alvo,
            "meta_proteina_g": proteina_diaria_g,
            "meta_carbo_g": carboidratos_diarios_g,
            "meta_gordura_g": gordura_diaria_g
        },
        "relatorio_texto": relatorio_texto,
        "dados_brutos": dados_extraidos
    }

async def registrar_ou_atualizar_cliente_balanca(remote_jid: str, telefone: str, nome: str, dados_bio: dict, relatorio_texto: str) -> dict:
    """
    Registra cliente no Supabase ou incrementa a contagem de dias/streak.
    Garante os 3 meses (90 dias) grátis de suporte VIP.
    """
    headers = get_supabase_headers()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/clientes_balanca?remote_jid=eq.{remote_jid}",
                headers=headers
            )
            existente = res.json() if res.status_code == 200 and res.json() else []

            agora = datetime.now()
            if not existente:
                data_fim = agora + timedelta(days=90)
                payload = {
                    "remote_jid": remote_jid,
                    "telefone": telefone,
                    "nome_cliente": nome,
                    "data_compra": agora.isoformat(),
                    "data_expiracao_vip": data_fim.isoformat(),
                    "status_vip": "ativo_gratis",
                    "streak_dias": 1,
                    "ultimo_peso": dados_bio.get("peso_kg"),
                    "ultima_gordura_pct": dados_bio.get("gordura_corporal_pct"),
                    "ultimo_musculo_kg": dados_bio.get("massa_muscular_kg"),
                    "dados_bioimpedancia": dados_bio,
                    "historico_pesagens": [{
                        "data": agora.isoformat(),
                        "peso": dados_bio.get("peso_kg"),
                        "gordura": dados_bio.get("gordura_corporal_pct"),
                        "musculo": dados_bio.get("massa_muscular_kg")
                    }]
                }
                await client.post(f"{SUPABASE_URL}/rest/v1/clientes_balanca", headers=headers, json=payload)
                dias_restantes = 90
                status_vip = "ativo_gratis"
            else:
                registro = existente[0]
                streak = (registro.get("streak_dias") or 0) + 1
                data_fim_str = registro.get("data_expiracao_vip")
                if data_fim_str:
                    try:
                        data_fim_dt = datetime.fromisoformat(data_fim_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        dias_restantes = max(0, (data_fim_dt - agora).days)
                    except Exception:
                        dias_restantes = 60
                else:
                    dias_restantes = 90

                status_vip = registro.get("status_vip", "ativo_gratis")
                if dias_restantes <= 0 and status_vip == "ativo_gratis":
                    status_vip = "expirado"
                elif dias_restantes <= 10 and status_vip == "ativo_gratis":
                    status_vip = "expirando"

                hist = registro.get("historico_pesagens") or []
                hist.append({
                    "data": agora.isoformat(),
                    "peso": dados_bio.get("peso_kg"),
                    "gordura": dados_bio.get("gordura_corporal_pct"),
                    "musculo": dados_bio.get("massa_muscular_kg")
                })

                patch_payload = {
                    "streak_dias": streak,
                    "ultimo_peso": dados_bio.get("peso_kg"),
                    "ultima_gordura_pct": dados_bio.get("gordura_corporal_pct"),
                    "ultimo_musculo_kg": dados_bio.get("massa_muscular_kg"),
                    "dados_bioimpedancia": dados_bio,
                    "status_vip": status_vip,
                    "historico_pesagens": hist[-20:],
                    "updated_at": agora.isoformat()
                }
                await client.patch(
                    f"{SUPABASE_URL}/rest/v1/clientes_balanca?remote_jid=eq.{remote_jid}",
                    headers=headers,
                    json=patch_payload
                )

            return {
                "sucesso": True,
                "streak_dias": 1 if not existente else existente[0].get("streak_dias", 1) + 1,
                "dias_restantes_vip": dias_restantes,
                "status_vip": status_vip,
                "precisa_renovar": dias_restantes <= 10
            }
    except Exception as e:
        print("Erro salvando cliente balanca:", e)
        return {"sucesso": False, "erro": str(e)}

async def verificar_status_vip(telefone: str) -> dict:
    """Consulta se o telefone possui a balança e quantos dias restam dos 3 meses de mentoria VIP."""
    headers = get_supabase_headers()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/clientes_balanca?telefone=eq.{telefone}",
                headers=headers
            )
            if res.status_code == 200 and res.json():
                c = res.json()[0]
                agora = datetime.now()
                data_fim_str = c.get("data_expiracao_vip")
                dias_restantes = 90
                if data_fim_str:
                    try:
                        data_fim_dt = datetime.fromisoformat(data_fim_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        dias_restantes = max(0, (data_fim_dt - agora).days)
                    except Exception:
                        pass
                return {
                    "tem_balanca": True,
                    "nome": c.get("nome_cliente"),
                    "dias_restantes": dias_restantes,
                    "status_vip": c.get("status_vip"),
                    "streak_dias": c.get("streak_dias", 1),
                    "link_renovacao": c.get("link_renovacao", "https://marcaopersonal.com#renovacao-vip"),
                    "ultimo_peso": c.get("ultimo_peso"),
                    "ultima_gordura": c.get("ultima_gordura_pct")
                }

            # Verificação secundária na tabela fichas_alunos
            res_ficha = await client.get(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?telefone=eq.{telefone}",
                headers=headers
            )
            if res_ficha.status_code == 200 and res_ficha.json():
                fa = res_ficha.json()[0]
                return {
                    "tem_balanca": True,
                    "nome": fa.get("nome_aluno"),
                    "dias_restantes": 90,
                    "status_vip": fa.get("status_acompanhamento", "ativo"),
                    "streak_dias": 1,
                    "link_renovacao": "https://marcaopersonal.com#renovacao-vip",
                    "ultimo_peso": None,
                    "ultima_gordura": None
                }
    except Exception:
        pass
    return {"tem_balanca": False, "dias_restantes": 0, "status_vip": "sem_balanca"}

async def processar_lead_scoring_inteligente(remote_jid: str, telefone: str, nome: str, ultima_msg: str, historico: list = None) -> dict:
    """
    Motor Open-Source de Lead Scoring (0-100) e Quebra de Objeções.
    Classifica o lead e gera recomendação certeira de fechamento.
    """
    msg_low = ultima_msg.lower()
    pontuacao = 30
    estagio = "qualificacao"
    objecao = None
    produto = None

    # Detecção de Objeções
    if any(p in msg_low for p in ["caro", "muito caro", "preço alto", "sem dinheiro", "grana curta"]):
        objecao = "preco"
        pontuacao += 15
        estagio = "objecao"
    elif any(p in msg_low for p in ["funciona", "confiável", "seguro", "garantia", "resultado"]):
        objecao = "confianca"
        pontuacao += 20
        estagio = "objecao"
    elif any(p in msg_low for p in ["prazo", "demora", "correios", "chega quando", "frete"]):
        objecao = "prazo_entrega"
        pontuacao += 25
        estagio = "fechamento"
    elif any(p in msg_low for p in ["link", "comprar", "como pago", "pix", "cartão", "boleto", "passa o link"]):
        pontuacao = 90
        estagio = "fechamento"

    # Detecção de Produto de Interesse
    if any(w in msg_low for w in ["balança", "balanca", "bioimpedancia", "peso", "gordura visceral"]):
        produto = "Balança Bioimpedância 360°"
    elif any(w in msg_low for w in ["creatina", "massa", "força", "hipertrofia"]):
        produto = "Creatina Micronizada 100%"
    elif any(w in msg_low for w in ["secar", "azempika", "caneta", "barriga", "fome", "apetite"]):
        produto = "Caneta Azempika Original"
    elif any(w in msg_low for w in ["colageno", "colágeno", "pele", "flacidez", "rugas"]):
        produto = "Colágeno + Hialurônico"
    elif any(w in msg_low for w in ["cabelo", "queda", "iarmonize", "calvície"]):
        produto = "KIT IArmonize Capilar"
    elif any(w in msg_low for w in ["olhos", "visão", "vista cansada", "vision prime"]):
        produto = "Vision Prime"

    # Atualiza Supabase leads_scoring
    headers = get_supabase_headers()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            payload = {
                "remote_jid": remote_jid,
                "telefone": telefone,
                "nome": nome,
                "pontuacao": min(100, pontuacao),
                "estagio_funil": estagio,
                "objecao_atual": objecao,
                "produto_alvo": produto,
                "ultimo_contato": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            await client.post(
                f"{SUPABASE_URL}/rest/v1/leads_scoring?on_conflict=remote_jid",
                headers=headers,
                json=payload
            )
    except Exception as e:
        print("Erro salvando lead scoring:", e)

    return {
        "pontuacao": pontuacao,
        "estagio": estagio,
        "objecao": objecao,
        "produto_alvo": produto
    }

async def obter_metricas_cfo_consolidadas() -> dict:
    """Consolida vendas, custos de Meta Ads e margens para o painel executivo CFO."""
    headers = get_supabase_headers()
    async with httpx.AsyncClient(verify=False) as client:
        # 1. Vendas Braip
        r_pedidos = await client.get(f"{SUPABASE_URL}/rest/v1/pedidos_braip?select=valor_total,comissao,status_pagamento", headers=headers)
        pedidos = r_pedidos.json() if r_pedidos.status_code == 200 else []

        faturamento_bruto = sum(float(p.get("valor_total") or 0) for p in pedidos)
        comissoes_liquidas = sum(float(p.get("comissao") or 0) for p in pedidos)

        # 2. Leads e Clientes VIP
        r_leads = await client.get(f"{SUPABASE_URL}/rest/v1/leads_conversas?select=id", headers=headers)
        total_leads = len(r_leads.json()) if r_leads.status_code == 200 else 0

        r_vip = await client.get(f"{SUPABASE_URL}/rest/v1/clientes_balanca?select=id,status_vip", headers=headers)
        vips = r_vip.json() if r_vip.status_code == 200 else []
        total_vip_ativos = len([v for v in vips if v.get("status_vip") in ["ativo_gratis", "assinante_pago"]])

        # 3. Tráfego Meta Ads (estimado via propostas aprovadas)
        r_aprov = await client.get(f"{SUPABASE_URL}/rest/v1/fila_aprovacoes?status=eq.approved&select=orcamento", headers=headers)
        aprovadas = r_aprov.json() if r_aprov.status_code == 200 else []
        custo_meta = len(aprovadas) * 20.00  # R$ 20/dia por campanha aprovada

        lucro_liquido = comissoes_liquidas - custo_meta
        roas = round(comissoes_liquidas / max(custo_meta, 1.0), 2)

        return {
            "faturamento_bruto": round(faturamento_bruto, 2),
            "comissoes_liquidas": round(comissoes_liquidas, 2),
            "custo_meta_ads": round(custo_meta, 2),
            "lucro_liquido": round(lucro_liquido, 2),
            "roas": roas,
            "total_pedidos": len(pedidos),
            "total_leads": total_leads,
            "total_vip_balanca": total_vip_ativos
        }
