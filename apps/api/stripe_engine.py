"""
Motor de Pagamentos & Assinaturas Recorrentes Stripe (Marcão Personal)
========================================================================
Permite gerar links de checkout e assinaturas recorrentes oficiais no Stripe
para a Consultoria VIP do Marcão (ex: R$ 19,90/mês após a Balança de Bioimpedância).

Funcionalidades:
- Criação e consulta de Produtos e Preços Recorrentes no Stripe
- Geração de Sessões de Checkout (modo assinatura) personalizadas por cliente
- Criação de Payment Links permanentes (reutilizáveis para o site e WhatsApp)
- Consulta do status da assinatura de um cliente
"""

import os
import requests
import urllib3

urllib3.disable_warnings()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_API_BASE = "https://api.stripe.com/v1"

HEADERS = {
    "Authorization": f"Bearer {STRIPE_SECRET_KEY}"
}


def obter_ou_criar_produto_vip(nome="Protocolo VIP Marcão Personal (Biohacking & Treino)", valor_reais=19.90):
    """
    Busca se o produto e preço de assinatura já existem no Stripe; caso não existam, cria-os.
    Retorna o price_id correspondente.
    """
    valor_centavos = int(round(valor_reais * 100))

    # 1. Lista produtos existentes
    r = requests.get(f"{STRIPE_API_BASE}/products", headers=HEADERS, verify=False, timeout=15)
    if r.status_code == 200:
        for p in r.json().get("data", []):
            if nome.lower() in p.get("name", "").lower():
                pid = p["id"]
                # Busca o preço associado
                pr = requests.get(f"{STRIPE_API_BASE}/prices?product={pid}&active=true", headers=HEADERS, verify=False, timeout=15)
                if pr.status_code == 200:
                    for price in pr.json().get("data", []):
                        if price.get("unit_amount") == valor_centavos and price.get("recurring"):
                            return price["id"]

    # 2. Se não existir, cria o produto
    print(f"[STRIPE] Criando novo produto oficial: {nome}...")
    prod_payload = {
        "name": nome,
        "description": "Acesso VIP ao Marcão Personal no WhatsApp: Ajuste de treinos, metas de bioimpedância e acompanhamento de saúde.",
        "active": "true"
    }
    pr_res = requests.post(f"{STRIPE_API_BASE}/products", headers=HEADERS, data=prod_payload, verify=False, timeout=15)
    if pr_res.status_code not in [200, 201]:
        print(f"[STRIPE] Erro ao criar produto: {pr_res.text}")
        return None

    prod_id = pr_res.json().get("id")

    # 3. Cria o preço recorrente mensal
    print(f"[STRIPE] Criando preço recorrente de R$ {valor_reais:.2f}/mês...")
    price_payload = {
        "product": prod_id,
        "unit_amount": valor_centavos,
        "currency": "brl",
        "recurring[interval]": "month"
    }
    p_res = requests.post(f"{STRIPE_API_BASE}/prices", headers=HEADERS, data=price_payload, verify=False, timeout=15)
    if p_res.status_code in [200, 201]:
        price_id = p_res.json().get("id")
        print(f"[STRIPE] Preço criado com sucesso: {price_id}")
        return price_id

    return None


def gerar_checkout_sessao(price_id=None, cliente_nome=None, cliente_whatsapp=None, email=None):
    """
    Gera um link de pagamento Stripe Checkout exclusivo para o cliente assinar.
    Pode ser enviado pelo Marcão ou Sofia diretamente no WhatsApp.
    """
    if not price_id:
        price_id = obter_ou_criar_produto_vip()

    payload = {
        "mode": "subscription",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
        "success_url": "https://marcaopersonal.com/?status=sucesso&session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": "https://marcaopersonal.com/?status=cancelado",
        "payment_method_types[0]": "card"
    }

    if email:
        payload["customer_email"] = email
    if cliente_nome or cliente_whatsapp:
        metadata = {}
        if cliente_nome:
            metadata["cliente_nome"] = cliente_nome
        if cliente_whatsapp:
            metadata["cliente_whatsapp"] = cliente_whatsapp
        for k, v in metadata.items():
            payload[f"metadata[{k}]"] = v
            payload[f"subscription_data[metadata][{k}]"] = v

    r = requests.post(f"{STRIPE_API_BASE}/checkout/sessions", headers=HEADERS, data=payload, verify=False, timeout=20)
    if r.status_code in [200, 201]:
        data = r.json()
        return {
            "sucesso": True,
            "checkout_url": data.get("url"),
            "session_id": data.get("id")
        }
    else:
        return {
            "sucesso": False,
            "erro": r.text
        }


def obter_ou_criar_link_permanente(price_id=None):
    """
    Cria ou recupera um Link de Pagamento Permanente (ex: https://buy.stripe.com/...)
    que pode ser colocado fixo no site ou enviado para qualquer pessoa assinar sem expirar.
    """
    if not price_id:
        price_id = obter_ou_criar_produto_vip()

    # Busca links existentes
    r = requests.get(f"{STRIPE_API_BASE}/payment_links?active=true", headers=HEADERS, verify=False, timeout=15)
    if r.status_code == 200:
        for pl in r.json().get("data", []):
            lines = pl.get("line_items", {}).get("data", [])
            for item in lines:
                if item.get("price", {}).get("id") == price_id:
                    return pl.get("url")

    # Cria novo payment link
    payload = {
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1
    }
    pr = requests.post(f"{STRIPE_API_BASE}/payment_links", headers=HEADERS, data=payload, verify=False, timeout=20)
    if pr.status_code in [200, 201]:
        return pr.json().get("url")

    return None


if __name__ == "__main__":
    print("--- Testando Motor Stripe Marcão Personal ---")
    pid = obter_ou_criar_produto_vip()
    print("Price ID Ativo:", pid)
    
    link_perm = obter_ou_criar_link_permanente(pid)
    print("Link Permanente de Assinatura (buy.stripe.com):", link_perm)
    
    sessao = gerar_checkout_sessao(pid, cliente_nome="Cliente VIP Teste", cliente_whatsapp="5532984587255")
    print("Sessão Checkout Gerada:", sessao.get("checkout_url"))
