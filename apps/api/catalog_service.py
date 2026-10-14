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
    "CREATINA-PRIME": {
        "doses": 100,
        "beneficio_chave": "Acelera ressíntese de ATP, ganho de 20% mais força e recuperação celular sem inchaço subcutâneo.",
        "claims_permitidos": ["Força e explosão muscular", "Ressíntese de ATP", "Hidratação intracelular pura", "Recuperação muscular acelerada"],
        "pitch_diario": "Apenas R$ 1,69 por dia (100 doses no pote), menos que meio café na padaria!"
    },
    "BALANCA-BIO": {
        "doses": 300,
        "beneficio_chave": "Mede 14 parâmetros por microcorrente BIA (Gordura, Gordura Visceral, Massa Magra, Idade Metabólica, TMB) e dá 3 meses de acompanhamento VIP grátis no WhatsApp.",
        "claims_permitidos": ["Métricas corporais precisas BIA", "Sincronização Bluetooth com App", "3 meses de mentoria VIP inclusos"],
        "pitch_diario": "Menos de R$ 0,30 por dia parcelado para destravar seu acompanhamento com o Marcão!"
    },
    "VIP-STRIPE": {
        "doses": 30,
        "beneficio_chave": "Acompanhamento direto e contínuo com o Marcão Personal no WhatsApp (ajustes de rotina, análise de pratos e pesagens).",
        "claims_permitidos": ["Mentoria semanal no WhatsApp", "Análise de evolução corporal", "Suporte VIP"],
        "pitch_diario": "Apenas R$ 0,66 por dia (R$ 19,90/mês) para ter o personal orientando no WhatsApp!"
    },
    "AZEMPIKA-CANETA": {
        "doses": 30,
        "beneficio_chave": "Fórmula natural de suporte à saciedade prolongada e controle da compulsão alimentar noturna.",
        "claims_permitidos": ["Suporte ao controle de saciedade", "Equilíbrio de hábitos alimentares", "Fórmula natural"],
        "pitch_diario": "Cerca de R$ 3,30 por dia para silenciar a compulsão noturna (menos que um lanche)!"
    },
    "COLAGENO-PRIME": {
        "doses": 30,
        "beneficio_chave": "Peptídeos bioativos de colágeno hidrolisado + ácido hialurônico para firmeza dérmica e sustentação tecidual.",
        "claims_permitidos": ["Firmeza e sustentação da pele", "Hidratação tecidual profunda", "Saúde de articulações e unhas"],
        "pitch_diario": "Apenas R$ 5,40 por dia para hidratação e firmeza profunda da pele!"
    },
    "VISION-PRIME": {
        "doses": 60,
        "beneficio_chave": "Nutrição celular com luteína e zeaxantina para alívio de fadiga ocular e proteção contra luz azul.",
        "claims_permitidos": ["Saúde macular", "Proteção contra luz de telas", "Alívio da fadiga visual"],
        "pitch_diario": "Apenas R$ 3,30 por dia para cuidar da visão e combater o cansaço das telas!"
    },
    "IARMONIZE-KIT": {
        "doses": 90,
        "beneficio_chave": "Tratamento capilar bioidêntico completo em 4 fases para nutrição do folículo e estímulo do couro cabeludo.",
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
                "sku": "BALANCA-BIO",
                "name": "Balança de Bioimpedância Bluetooth com App",
                "price": 89.90,
                "affiliate_url": "https://marcaopersonal.com#balanca",
                "custo_dia": 0.30,
                "pitch_diario": "Menos de R$ 0,30 por dia parcelado para destravar 3 meses de acompanhamento VIP no WhatsApp!",
                "beneficio_chave": "14 métricas corporais BIA e liberação de 3 meses de mentoria no WhatsApp."
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
        "Use SEMPRE estes links oficiais e aplique o custo diário no fechamento:"
    ]

    for p in produtos:
        linhas.append(
            f"- {p['name']} (R$ {p['price']:.2f}):\n"
            f"  * Custo por dia: {p['pitch_diario']}\n"
            f"  * Benefício: {p['beneficio_chave']}\n"
            f"  * Link Direto Oficial: {p['affiliate_url']}"
        )

    linhas.append("- Site Oficial da Loja Geral: https://marcaopersonal.com#loja")
    linhas.append("- Assinatura Mensal VIP Stripe (R$ 19,90/mês): https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01")
    linhas.append("\nDISCLOSURE OBRIGATÓRIO (CONAR/META/LEGISLAÇÃO BRASIL):")
    linhas.append("Alguns links são de afiliados oficiais. A entrega e cobrança acontecem com o parceiro indicado com garantia.")

    return "\n".join(linhas)


async def buscar_produto_por_termo(termo: str) -> dict:
    """Localiza o produto mais aderente ao termo citado pelo lead ou pelo chefe."""
    produtos = await obter_produtos_ativos()
    termo_limpo = termo.lower().strip()
    
    for p in produtos:
        if termo_limpo in p["name"].lower() or termo_limpo in p["sku"].lower():
            return p
            
    # Mapeamentos conceituais comuns
    sinonimos = {
        "creatina": "CREATINA-PRIME",
        "balanca": "BALANCA-BIO",
        "balança": "BALANCA-BIO",
        "bioimpedancia": "BALANCA-BIO",
        "bioimpedância": "BALANCA-BIO",
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
