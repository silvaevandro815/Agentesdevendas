"""
Catalog Service - Provedor de Catálogo Unificado Marcão AI
===========================================================
Garante que a memória de produtos e ofertas esteja 100% sincronizada
e em comum acordo entre WhatsApp, Instagram (Feed, Stories, Directs e Comentários)
e Site Oficial.
"""

import os
import time
import httpx
from datetime import datetime
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Cache local em memória (60 segundos)
_CACHE_PRODUTOS = None
_CACHE_TIMESTAMP = 0
CACHE_TTL_SEGUNDOS = 60

# Metadados complementares de enriquecimento (doses, benefícios científicos e claims regulatórios)
METADADOS_CONHECIDOS = {
    "BALANCA-BIOIMPEDANCIA-SHOPEE": {
        "doses": 365,
        "beneficio_chave": "Balança Inteligente de Bioimpedância Clínica com 13 biomarcadores corporais (massa muscular, gordura visceral profunda, hidratação celular, taxa metabólica) e 3 Meses de Mentoria VIP Grátis no WhatsApp com o Marcão Personal.",
        "claims_permitidos": ["13 biomarcadores clínicos", "Leitura de gordura visceral dos órgãos", "4 eletrodos BIA de alta condutividade", "Sincronização Bluetooth com app", "3 Meses de Mentoria VIP Marcão Inclusa"],
        "pitch_diario": "Apenas R$ 0,24 por dia (menos que uma bala!) para ter a balança inteligente de bioimpedância e 3 meses de mentoria VIP comigo!"
    },
    "BALANCA-XIAOMI-AMAZON": {
        "doses": 365,
        "beneficio_chave": "Balança Xiaomi Mi Body Composition Scale 2 oficial com 13 parâmetros de bioimpedância de alta precisão (sensor de manganês) e 3 meses de acompanhamento VIP grátis no WhatsApp.",
        "claims_permitidos": ["Precisão clínica G-sensor de manganês", "Teste de equilíbrio corporal", "Sincronização automática Bluetooth", "Mentoria VIP Marcão inclusa"],
        "pitch_diario": "Apenas R$ 0,41 por dia para ter a tecnologia Xiaomi de bioimpedância e 3 meses de mentoria VIP comigo!"
    },
    "CREATINA-PRIME": {
        "doses": 100,
        "beneficio_chave": "Acelera ressíntese de ATP, ganho de 20% mais força e recuperação celular sem retenção subcutânea.",
        "claims_permitidos": ["Força e explosão muscular", "Ressíntese de ATP", "Hidratação intracelular pura", "Recuperação muscular acelerada"],
        "pitch_diario": "Apenas R$ 1,69 por dia (100 doses no pote), menos que meio café na padaria!"
    },
    "CREATINA-CREAPURE-DUX": {
        "doses": 83,
        "beneficio_chave": "Creatina Creapure® alemã 100% pura da DUX Nutrition, padrão ouro mundial de biodisponibilidade e ganho de força seca.",
        "claims_permitidos": ["Selo Creapure alemão", "Zero impurezas", "Força máxima", "Absorção imediata"],
        "pitch_diario": "Apenas R$ 1,68 por dia para ter a Creapure alemã no seu treino diário!"
    },
    "WHEY-MAX-TITANIUM": {
        "doses": 30,
        "beneficio_chave": "100% Whey Pure Max Titanium com 21g de proteína por dose, 4.8g de BCAA e alto valor biológico para ganho de massa seca e saciedade.",
        "claims_permitidos": ["21g proteína por dose", "4.8g BCAA", "Recuperação muscular rápida", "Padrão ouro nacional"],
        "pitch_diario": "Apenas R$ 3,33 por dia (30 doses) para garantir sua meta de proteína com padrão ouro!"
    },
    "WHEY-DUX-CONCENTRADO": {
        "doses": 30,
        "beneficio_chave": "Whey Concentrado DUX Nutrition com matéria-prima importada 100% pura, sabor premium inigualável e 22g de proteína de alta absorção.",
        "claims_permitidos": ["Matéria-prima importada", "Sabor premium", "22g proteína", "Perfil completo de aminoácidos"],
        "pitch_diario": "Apenas R$ 4,99 por dia para saborear o whey mais cremoso e puro do Brasil!"
    },
    "WHEY-GOLD-OPTIMUM": {
        "doses": 30,
        "beneficio_chave": "100% Whey Gold Standard Optimum Nutrition, o whey nº 1 do planeta com predomínio de whey isolado e 24g de pura proteína microfiltrada.",
        "claims_permitidos": ["Nº 1 do mundo", "Predomínio de isolado", "24g proteína microfiltrada", "Digestão perfeita"],
        "pitch_diario": "R$ 8,33 por dia para colocar no seu corpo o padrão ouro mundial absoluto de proteína!"
    },
    "SMARTWATCH-XIAOMI-BAND": {
        "doses": 365,
        "beneficio_chave": "Xiaomi Smart Band 8 com monitoramento contínuo de frequência cardíaca, SpO2, rastreio de sono profundo, mais de 150 esportes e sincronização com Strava.",
        "claims_permitidos": ["Monitor cardíaco 24/7", "Integração Strava e App", "Análise de sono profundo", "Bateria de até 16 dias"],
        "pitch_diario": "Apenas R$ 0,65 por dia (diluído em 1 ano) para monitorar seus batimentos e evolução aeróbica!"
    },
    "SMARTWATCH-AMAZFIT-BIP": {
        "doses": 365,
        "beneficio_chave": "Smartwatch Amazfit Bip 5 com GPS integrado de 4 satélites, tela ultragrande de 1.91 polegadas, chamadas Bluetooth e monitor esportivo completo.",
        "claims_permitidos": ["GPS integrado preciso", "Tela HD 1.91 polegadas", "Chamadas no pulso", "Monitoramento de VO2Max"],
        "pitch_diario": "Apenas R$ 1,09 por dia para ter um computador de treino com GPS no seu pulso!"
    },
    "ROUPA-COMPRESSAO-UV50": {
        "doses": 180,
        "beneficio_chave": "Camiseta Térmica Segunda Pele Compressão UV50+ Dry Fit: melhora o retorno venoso, previne assaduras, regula a temperatura e destaca o shape atlético.",
        "claims_permitidos": ["Proteção solar UV50+", "Compressão muscular ativa", "Tecido Dry Fit respirável", "Secagem ultrarrápida"],
        "pitch_diario": "Apenas R$ 0,27 por dia para treinar com máxima performance térmica e postura firme!"
    },
    "BERMUDA-COMPRESSAO-FIT": {
        "doses": 180,
        "beneficio_chave": "Bermuda Térmica de Compressão Fitness com Bolso para Celular: suporte total ao quadríceps e posterior, zero atrito entre as pernas e firmeza nos treinos de perna e corrida.",
        "claims_permitidos": ["Bolso interno antifurto", "Zero atrito/assadura", "Sustentação muscular", "Elasticidade 4 vias"],
        "pitch_diario": "Apenas R$ 0,33 por dia para treinar pernas ou correr sem nenhum incômodo!"
    },
    "OMEGA3-ULTRA-CONCENTRADO": {
        "doses": 60,
        "beneficio_chave": "Ômega 3 Ultra Concentrado DUX com 1000mg de puro óleo de peixe com alto teor de EPA e DHA com selo MEG-3, combate inflamação nas articulações, joelhos e tendões.",
        "claims_permitidos": ["Selo MEG-3 de pureza", "Alto EPA e DHA", "Anti-inflamatório articular", "Saúde cardiovascular e cerebral"],
        "pitch_diario": "Apenas R$ 1,66 por dia para blindar suas articulações, joelhos e ligamentos contra o desgaste dos treinos!"
    },
    "MELATONINA-MAGNESIO-SONO": {
        "doses": 60,
        "beneficio_chave": "Complexo Sono Reparador Melatonina + Magnésio Dimalato: relaxamento muscular profundo do sistema nervoso, combate à insônia e estímulo ao pico de GH noturno.",
        "claims_permitidos": ["Sono profundo reparador", "Relaxamento muscular", "Pico de GH noturno", "Zero sonolência diurna"],
        "pitch_diario": "Apenas R$ 1,16 por dia para ter noites anabólicas e acordar 100% recuperado!"
    },
    "VIP-STRIPE": {
        "doses": 30,
        "beneficio_chave": "Acompanhamento direto e contínuo com o Marcão Personal no WhatsApp (ajustes de rotina, análise de pratos e pesagens).",
        "claims_permitidos": ["Mentoria semanal no WhatsApp", "Análise de evolução corporal", "Suporte VIP"],
        "pitch_diario": "Apenas R$ 0,66 por dia (R$ 19,90/mês) para ter o personal orientando no WhatsApp!"
    },
    "AZEMPIKA-CANETA": {
        "doses": 30,
        "beneficio_chave": "Fórmula natural de suporte à saciedade prolongada, controle da compulsão alimentar noturna e vigor masculino.",
        "claims_permitidos": ["Suporte ao controle de saciedade", "Equilíbrio de hábitos alimentares", "Fórmula natural e vigor"],
        "pitch_diario": "Cerca de R$ 3,30 por dia para silenciar a compulsão noturna e recuperar o vigor!"
    },
    "COLAGENO-PRIME": {
        "doses": 30,
        "beneficio_chave": "Peptídeos bioativos de colágeno hidrolisado + ácido hialurônico para firmeza dérmica, sustentação tecidual e elasticidade articular.",
        "claims_permitidos": ["Firmeza e sustentação da pele", "Hidratação tecidual profunda", "Saúde de articulações e unhas"],
        "pitch_diario": "Apenas R$ 5,40 por dia para hidratação, firmeza profunda da pele e saúde articular!"
    },
    "VISION-PRIME": {
        "doses": 60,
        "beneficio_chave": "Nutrição celular com luteína e zeaxantina para alívio de fadiga ocular e proteção contra luz azul de telas.",
        "claims_permitidos": ["Saúde macular", "Proteção contra luz de telas", "Alívio da fadiga visual"],
        "pitch_diario": "Apenas R$ 3,30 por dia para cuidar da visão e combater o cansaço das telas!"
    },
    "IARMONIZE-KIT": {
        "doses": 90,
        "beneficio_chave": "Tratamento capilar bioidêntico completo em 4 fases para nutrição do folículo, combate à calvície e estímulo ao couro cabeludo.",
        "claims_permitidos": ["Revitalização folicular", "Força e densidade capilar", "Tratamento antiqueda intensivo"],
        "pitch_diario": "Cerca de R$ 13,95 por dia para recuperação e densidade capilar clínica!"
    }
}


def invalidar_cache():
    """Força a invalidação do cache em memória."""
    global _CACHE_TIMESTAMP, _CACHE_PRODUTOS
    _CACHE_PRODUTOS = None
    _CACHE_TIMESTAMP = 0


async def obter_produtos_ativos() -> list:
    """
    Busca todos os produtos ativos cadastrados no Supabase com enriquecimento dinâmico.
    Utiliza cache em memória de 60 segundos para performance e baixo consumo de rede.
    """
    global _CACHE_PRODUTOS, _CACHE_TIMESTAMP

    agora = time.time()
    if _CACHE_PRODUTOS is not None and (agora - _CACHE_TIMESTAMP) < CACHE_TTL_SEGUNDOS:
        return _CACHE_PRODUTOS

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    produtos = []
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.get(f"{SUPABASE_URL}/rest/v1/products?select=*&order=price.asc", headers=headers)
            if res.status_code == 200:
                raw_produtos = res.json()
                for p in raw_produtos:
                    sku = p.get("sku", "")
                    preco = float(p.get("price") or 0.0)
                    meta = METADADOS_CONHECIDOS.get(sku, {})
                    
                    # Cálculo automático de custo diário
                    doses = meta.get("doses", 30)
                    custo_dia = preco / doses if doses > 0 else preco / 30.0
                    
                    pitch_diario = meta.get("pitch_diario")
                    if not pitch_diario:
                        pitch_diario = f"Apenas R$ {custo_dia:.2f} por dia (menos que uma água mineral)!"

                    produtos.append({
                        "id": p.get("id"),
                        "sku": sku,
                        "name": p.get("name"),
                        "price": preco,
                        "affiliate_url": p.get("affiliate_url"),
                        "model": p.get("model", "afiliado"),
                        "commission_pct": float(p.get("commission_pct") or 0.0),
                        "doses": doses,
                        "custo_dia": round(custo_dia, 2),
                        "pitch_diario": pitch_diario,
                        "beneficio_chave": meta.get("beneficio_chave", "Saúde, performance e resultados estéticos com padrão ouro."),
                        "claims_permitidos": meta.get("claims_permitidos", ["Hábitos saudáveis", "Estética e performance"]),
                    })
    except Exception as e:
        print("[CATALOG_SERVICE] Erro ao carregar produtos do Supabase:", e)

    # Fallback seguro caso o Supabase falhe momentaneamente
    if not produtos:
        produtos = [
            {
                "sku": "BALANCA-BIOIMPEDANCIA-SHOPEE",
                "name": "Balança Inteligente Bioimpedância Bluetooth BIA (Shopee)",
                "price": 89.90,
                "affiliate_url": "https://s.shopee.com.br/2BFoInIBeb",
                "custo_dia": 0.24,
                "pitch_diario": "Apenas R$ 0,24 por dia (menos que uma bala!) para ter a balança inteligente de bioimpedância e 3 meses de mentoria VIP comigo!",
                "beneficio_chave": "13 biomarcadores corporais BIA (massa muscular, gordura visceral, água celular, metabolismo) e liberação de 3 meses de mentoria VIP no WhatsApp."
            },
            {
                "sku": "BALANCA-XIAOMI-AMAZON",
                "name": "Balança Xiaomi Mi Body Composition Scale 2",
                "price": 149.90,
                "affiliate_url": "https://www.amazon.com.br/dp/B07T48Z4TN?tag=marcaopersona-20",
                "custo_dia": 0.41,
                "pitch_diario": "Apenas R$ 0,41 por dia para ter a tecnologia Xiaomi de bioimpedância e 3 meses de mentoria VIP comigo!",
                "beneficio_chave": "13 métricas corporais BIA de precisão clínica e liberação de 3 meses de mentoria VIP no WhatsApp."
            },
            {
                "sku": "CREATINA-PRIME",
                "name": "Creatina Micronizada 100% Pura 300g",
                "price": 169.90,
                "affiliate_url": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
                "custo_dia": 1.69,
                "pitch_diario": "Apenas R$ 1,69 por dia (100 doses no pote), menos que meio café na padaria!",
                "beneficio_chave": "Força explosiva, ressíntese de ATP e 20% mais rendimento sem retenção de líquidos prejudicial."
            },
            {
                "sku": "VIP-STRIPE",
                "name": "Assinatura VIP Mensal Marcão Personal",
                "price": 19.90,
                "affiliate_url": "https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01",
                "custo_dia": 0.66,
                "pitch_diario": "Apenas R$ 0,66 por dia para ter o personal no seu WhatsApp toda semana!",
                "beneficio_chave": "Acompanhamento contínuo no WhatsApp após os 3 meses gratuitos."
            }
        ]

    _CACHE_PRODUTOS = produtos
    _CACHE_TIMESTAMP = agora
    return produtos


async def obter_catalogo_para_prompt() -> str:
    """
    Gera o bloco formatado em texto para ser injetado nos System Prompts
    de IA (WhatsApp marcao_engine, n8n Instagram Directs, Comentários, etc.).
    """
    produtos = await obter_produtos_ativos()
    
    linhas = [
        "CATÁLOGO OFICIAL UNIFICADO & LINKS DE VENDAS ATIVOS (MEMÓRIA COMPARTILHADA WHATSAPP & INSTAGRAM):",
        "Use SEMPRE estes links oficiais e aplique o custo diário no fechamento:\n"
    ]

    for p in produtos:
        linhas.append(
            f"- {p['name']} (R$ {p['price']:.2f}):\n"
            f"  * Custo por dia: {p['pitch_diario']}\n"
            f"  * Benefício: {p['beneficio_chave']}\n"
            f"  * Link Direto Oficial: {p['affiliate_url']}"
        )

    linhas.append("\n- Site Oficial da Loja Geral: https://marcaopersonal.com#loja")
    linhas.append("- Assinatura Mensal VIP Stripe (R$ 19,90/mês): https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01")

    linhas.append("\nMATRIZ DE DISPARO AUTÔNOMO DE VENDAS (A DOR DO LEAD -> A SOLUÇÃO IMEDIATA DO MARCÃO):")
    linhas.append("Você tem autonomia plena e contínua para vender. Identifique a dor, queixa ou desejo do interlocutor e prescreva a solução com o link na lata:")
    linhas.append("1. DOR NO JOELHO, ARTICULAÇÕES, TENDÕES, ESTALO: Prescreva Ômega 3 Ultra Concentrado (Dux) ou Colágeno com Ácido Hialurônico (Nature's Prime). Link direto na mensagem!")
    linhas.append("2. CANSAÇO, FALTA DE FORÇA, TREINO NÃO RENDE: Prescreva Creatina (Creatina Prime Braip ou Creatina Creapure Dux Amazon). Explique a saturação de ATP e custo diário de R$ 1,69/dia!")
    linhas.append("3. NÃO BATE META DE PROTEÍNA, DIFICULDADE DE CRESCER SECO, FOME DE DOCE: Prescreva Whey Protein (Max Titanium R$ 99,90 ou Dux Concentrado R$ 149,90 ou Gold Standard R$ 249,90). Ensine receitas de brigadeiro proteico!")
    linhas.append("4. PAROU DE EMAGRECER, DÚVIDA SE PERDEU GORDURA OU MÚSCULO, QUER AVALIAÇÃO DE SHAPE: Prescreva a BALANÇA DE BIOIMPEDÂNCIA XIAOMI MI SCALE 2 (Amazon R$ 149,90, apenas R$ 0,41/dia). CARRO-CHEFE Nº 1: DESTACA QUE COMPRANDO A BALANÇA GANHA 3 MESES DE MENTORIA VIP GRÁTIS COM O MARCÃO NO WHATSAPP! Link: https://www.amazon.com.br/dp/B07T48Z4TN?tag=marcaopersona-20")
    linhas.append("5. QUER CORRER, MONITORAR BATIMENTOS CARDÍACOS, QUEIMA CALÓRICA, STRAVA OU SONO: Prescreva o Smartwatch Xiaomi Smart Band 8 ou Amazfit Bip 5 com GPS. Custa centavos de real por dia!")
    linhas.append("6. ASSADURAS ENTRE AS PERNAS, SUOR EXCESSIVO, ROUPA PESADA, POSTURA FIRME: Prescreva Camiseta Térmica Compressão UV50+ ou Bermuda Térmica de Compressão com Bolso antifurto.")
    linhas.append("7. COMPULSÃO ALIMENTAR NOTURNA, VONTADE DESCONTROLADA DE COMER / VIGOR MASCULINO: Prescreva Caneta Azempika (apenas para maiores de 18 anos).")
    linhas.append("8. QUEDA DE CABELO, CABELO FRACO, CALVÍCIE: Prescreva o Kit IArmonize Capilar em 4 Fases.")
    linhas.append("9. INSÔNIA, ACORDA CANSADO, SONO LEVE: Prescreva o Complexo Sono Melatonina + Magnésio Dimalato para pico de GH.")

    linhas.append("\nDISCLOSURE OBRIGATÓRIO (CONAR/META/LEGISLAÇÃO BRASIL):")
    linhas.append("Alguns links são de parceiros afiliados oficiais da marca. A entrega, garantia e cobrança acontecem com o parceiro indicado com nota fiscal e total segurança.")

    return "\n".join(linhas)


async def buscar_produto_por_termo(termo: str) -> dict:
    """Localiza o produto mais aderente ao termo citado pelo lead ou pelo chefe."""
    produtos = await obter_produtos_ativos()
    termo_limpo = termo.lower().strip()
    
    for p in produtos:
        if termo_limpo in p["name"].lower() or termo_limpo in p["sku"].lower():
            return p
            
    # Mapeamentos conceituais comuns (sinônimos de dores, queixas e categorias)
    sinonimos = {
        "creatina": "CREATINA-PRIME",
        "creapure": "CREATINA-CREAPURE-DUX",
        "balanca": "BALANCA-XIAOMI-AMAZON",
        "balança": "BALANCA-XIAOMI-AMAZON",
        "bioimpedancia": "BALANCA-XIAOMI-AMAZON",
        "bioimpedância": "BALANCA-XIAOMI-AMAZON",
        "xiaomi": "BALANCA-XIAOMI-AMAZON",
        "whey": "WHEY-MAX-TITANIUM",
        "whey protein": "WHEY-MAX-TITANIUM",
        "proteina": "WHEY-MAX-TITANIUM",
        "proteína": "WHEY-MAX-TITANIUM",
        "dux": "WHEY-DUX-CONCENTRADO",
        "gold": "WHEY-GOLD-OPTIMUM",
        "optimum": "WHEY-GOLD-OPTIMUM",
        "relogio": "SMARTWATCH-XIAOMI-BAND",
        "relógio": "SMARTWATCH-XIAOMI-BAND",
        "smartwatch": "SMARTWATCH-XIAOMI-BAND",
        "band": "SMARTWATCH-XIAOMI-BAND",
        "cardiaco": "SMARTWATCH-XIAOMI-BAND",
        "cardíaco": "SMARTWATCH-XIAOMI-BAND",
        "batimento": "SMARTWATCH-XIAOMI-BAND",
        "strava": "SMARTWATCH-XIAOMI-BAND",
        "gps": "SMARTWATCH-AMAZFIT-BIP",
        "amazfit": "SMARTWATCH-AMAZFIT-BIP",
        "roupa": "ROUPA-COMPRESSAO-UV50",
        "camisa compressao": "ROUPA-COMPRESSAO-UV50",
        "camisa compressão": "ROUPA-COMPRESSAO-UV50",
        "segunda pele": "ROUPA-COMPRESSAO-UV50",
        "dry fit": "ROUPA-COMPRESSAO-UV50",
        "dry-fit": "ROUPA-COMPRESSAO-UV50",
        "bermuda": "BERMUDA-COMPRESSAO-FIT",
        "short": "BERMUDA-COMPRESSAO-FIT",
        "assadura": "BERMUDA-COMPRESSAO-FIT",
        "joelho": "OMEGA3-ULTRA-CONCENTRADO",
        "articulacao": "OMEGA3-ULTRA-CONCENTRADO",
        "articulação": "OMEGA3-ULTRA-CONCENTRADO",
        "tendao": "OMEGA3-ULTRA-CONCENTRADO",
        "tendão": "OMEGA3-ULTRA-CONCENTRADO",
        "omega 3": "OMEGA3-ULTRA-CONCENTRADO",
        "ômega 3": "OMEGA3-ULTRA-CONCENTRADO",
        "sono": "MELATONINA-MAGNESIO-SONO",
        "insonia": "MELATONINA-MAGNESIO-SONO",
        "insônia": "MELATONINA-MAGNESIO-SONO",
        "dormir": "MELATONINA-MAGNESIO-SONO",
        "magnesio": "MELATONINA-MAGNESIO-SONO",
        "magnésio": "MELATONINA-MAGNESIO-SONO",
        "melatonina": "MELATONINA-MAGNESIO-SONO",
        "vip": "VIP-STRIPE",
        "assinatura": "VIP-STRIPE",
        "colageno": "COLAGENO-PRIME",
        "colágeno": "COLAGENO-PRIME",
        "pele": "COLAGENO-PRIME",
        "azempika": "AZEMPIKA-CANETA",
        "secar": "AZEMPIKA-CANETA",
        "cabelo": "IARMONIZE-KIT",
        "queda": "IARMONIZE-KIT",
        "visao": "VISION-PRIME",
        "visão": "VISION-PRIME"
    }
    
    for k, sku_ref in sinonimos.items():
        if k in termo_limpo:
            for p in produtos:
                if p["sku"] == sku_ref:
                    return p

    return produtos[0] if produtos else {}


async def salvar_ou_atualizar_produto(
    sku: str,
    name: str,
    price: float,
    affiliate_url: str,
    model: str = "afiliado",
    commission_pct: float = 0.0,
    doses: int = 30,
    beneficio_chave: str = None
) -> dict:
    """
    Insere ou atualiza um produto no Supabase e invalida o cache imediatamente.
    Disponível tanto para novos afiliados da Amazon, Magalu, Shopee, Mercado Livre, quanto Braip.
    """
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    # Normaliza model para a constraint do Supabase
    s_model = (model or "").lower()
    if "amazon" in s_model or "amzn" in s_model:
        model_final = "afiliado_amazon"
    elif "magalu" in s_model:
        model_final = "afiliado_magalu"
    elif "mercadolivre" in s_model or "meli" in s_model or "ml" in s_model:
        model_final = "afiliado_ml"
    elif "shopee" in s_model:
        model_final = "afiliado_shopee"
    elif "braip" in s_model:
        model_final = "braip"
    elif "stripe" in s_model or "proprio" in s_model:
        model_final = "proprio"
    else:
        model_final = "afiliado_ml"

    payload = {
        "sku": sku,
        "name": name,
        "price": price,
        "affiliate_url": affiliate_url,
        "model": model_final,
        "commission_pct": commission_pct
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/products",
                headers=headers,
                json=payload
            )
            if res.status_code in [200, 201]:
                if beneficio_chave or doses:
                    METADADOS_CONHECIDOS[sku] = {
                        "doses": doses or 30,
                        "beneficio_chave": beneficio_chave or "Produto testado e selecionado para saúde e estética.",
                        "pitch_diario": f"Apenas R$ {(price / (doses or 30)):.2f} por dia!",
                        "claims_permitidos": ["Uso seguro", "Resultados progressivos"]
                    }
                invalidar_cache()
                return {"sucesso": True, "sku": sku, "name": name, "price": price}
            else:
                return {"sucesso": False, "status": res.status_code, "erro": res.text}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}
