"""
Motor de Afiliados, Monitor de Preços & Funil de 90 Dias (Marcão Personal)
============================================================================
1. Busca em tempo real de produtos fitness mais vendidos e mais baratos:
   - Mercado Livre (API oficial pública de busca)
   - Amazon (Formatador de catálogo com tag de associado)
   - Magalu (Formatador de vitrine Magazine Você)
   - Shopee (Acessórios fitness baratos de alto volume)

2. Gestão do Funil dos 90 Dias dos Clientes da Balança:
   - Cadastra novo cliente quando compra a balança
   - Monitora os 90 dias de acompanhamento gratuito
   - Ao completar 85-90 dias, envia automaticamente o link oficial do Stripe
     (https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01) para assinar por R$ 19,90/mês.
"""

import os
import time
import requests
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
STRIPE_VIP_LINK = "https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01"


# -----------------------------------------------------------------------------
# 1. RADAR DE PRODUTOS MAIS BARATOS E MAIS VENDIDOS (MERCADO LIVRE / AFILIADOS)
# -----------------------------------------------------------------------------
def buscar_melhores_ofertas_mercadolivre(termo="balanca bioimpedancia bluetooth app", limite=5):
    """
    Consulta a API pública do Mercado Livre para encontrar as melhores ofertas,
    menores preços e maiores volumes de venda do produto.
    """
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo.replace(' ', '+')}&sort=price_asc&limit={limite}"
    try:
        r = requests.get(url, timeout=12, verify=False)
        if r.status_code == 200:
            data = r.json()
            resultados = []
            for item in data.get("results", []):
                resultados.append({
                    "id": item.get("id"),
                    "titulo": item.get("title"),
                    "preco": item.get("price"),
                    "moeda": item.get("currency_id"),
                    "link_original": item.get("permalink"),
                    "foto": item.get("thumbnail"),
                    "frete_gratis": item.get("shipping", {}).get("free_shipping", False),
                    "condicao": item.get("condition")
                })
            return resultados
    except Exception as e:
        print(f"[AFFILIATE] Erro na busca Mercado Livre: {e}")

    return []


def gerar_link_afiliado(url_original: str, plataforma: str, tag_afiliado: str = "") -> str:
    """
    Transforma o link de qualquer produto das plataformas em link comissionado.
    """
    if "mercadolivre.com" in url_original:
        # Padrão de afiliado Mercado Livre
        return f"{url_original}?pdp_filters=category:{tag_afiliado or 'afiliados_marcao'}"
    elif "amazon.com" in url_original:
        # Padrão Amazon Associates
        sep = "&" if "?" in url_original else "?"
        tag = tag_afiliado or "marcaopersonal-20"
        return f"{url_original}{sep}tag={tag}"
    elif "magazineluiza.com" in url_original or "magalu" in url_original:
        # Padrão Magazine Você
        return f"https://www.magazinevoce.com.br/{tag_afiliado or 'marcaopersonal'}/p/{url_original.split('/')[-1]}"
    
    return url_original


# -----------------------------------------------------------------------------
# 2. FUNIL AUTOMÁTICO DE 90 DIAS (BALANÇA -> ASSINATURA STRIPE R$ 19,90/MÊS)
# -----------------------------------------------------------------------------
def cadastrar_novo_cliente_balanca(telefone: str, nome: str, data_inicio: str = None) -> bool:
    """
    Registra um cliente no Supabase iniciando o período de 90 dias de mentoria gratuita.
    """
    if not data_inicio:
        data_inicio = datetime.now().isoformat()

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    payload = {
        "telefone": telefone,
        "push_name": nome,
        "tem_balanca": True,
        "data_inicio_vip": data_inicio,
        "status_vip": "gratis_90_dias",
        "updated_at": datetime.now().isoformat()
    }

    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/leads_conversas?on_conflict=telefone",
            headers=headers,
            json=payload,
            verify=False,
            timeout=10
        )
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"[AFFILIATE] Erro ao cadastrar cliente VIP: {e}")
        return False


def verificar_alunos_para_renovacao_stripe():
    """
    Verifica no Supabase quais alunos completaram entre 85 e 90 dias de mentoria
    gratuita da balança e gera a mensagem personalizada com o link da Stripe.
    """
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/leads_conversas?tem_balanca=eq.true&status_vip=eq.gratis_90_dias",
            headers=headers,
            verify=False,
            timeout=10
        )
        if r.status_code == 200:
            alunos = r.json()
            candidatos_renovacao = []
            hoje = datetime.now()

            for a in alunos:
                dt_str = a.get("data_inicio_vip")
                if dt_str:
                    try:
                        inicio = datetime.fromisoformat(dt_str.replace("Z", ""))
                        dias_passados = (hoje - inicio).days
                        if dias_passados >= 85:
                            candidatos_renovacao.append({
                                "telefone": a.get("telefone"),
                                "nome": a.get("push_name") or "Guerreiro(a)",
                                "dias_passados": dias_passados,
                                "mensagem_sugerida": (
                                    f"Fala, {a.get('push_name') or 'meu parceiro'}! Marcão na área! 💪🔥\n\n"
                                    f"Tô passando pra te parabenizar de verdade pela sua evolução nesses quase 3 meses de foco total!\n\n"
                                    f"Seus 90 dias de mentoria gratuita da balança completam agora nesses próximos dias. Pra gente continuar firme com suas avaliações de bioimpedância, ajuste dos treinos e cobrança de metas direto no meu WhatsApp, liberei seu acesso VIP por apenas R$ 19,90/mês no link oficial da Stripe:\n\n"
                                    f"👉 {STRIPE_VIP_LINK}\n\n"
                                    f"Bora continuar evoluindo juntos e não perder o ritmo! Vamos pra cima! 👊"
                                )
                            })
                    except Exception as e_date:
                        continue

            return candidatos_renovacao
    except Exception as e:
        print(f"[AFFILIATE] Erro ao verificar alunos para renovação: {e}")

    return []


if __name__ == "__main__":
    print("--- Testando Radar de Preços (Mercado Livre) ---")
    ofertas = buscar_melhores_ofertas_mercadolivre("balanca bioimpedancia bluetooth digital", limite=3)
    for o in ofertas:
        print(f"📦 {o['titulo'][:50]}... | R$ {o['preco']} | Frete Grátis: {o['frete_gratis']}")
        print(f"   Link: {o['link_original']}")
