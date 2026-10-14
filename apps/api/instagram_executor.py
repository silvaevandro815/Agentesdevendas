"""
Executor de Postagem Instagram sob Demanda do Chefe Evandro
============================================================
Permite que o Marcão, ao receber um comando de texto ou áudio no WhatsApp do Chefe,
gere o criativo (imagem/card) via IA, redija a legenda persuasiva e publique
imediatamente no Feed, Reels ou Stories da conta oficial @marcaopersonalfitness.
"""

import os
import re
import time
import base64
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extrair_tema_e_destino(texto_comando: str) -> tuple:
    """
    Identifica o destino (FEED, STORIES, REELS) e o tema solicitado pelo Chefe.
    """
    txt = texto_comando.lower()
    
    destino = "FEED"
    if "story" in txt or "stories" in txt:
        destino = "STORIES"
    elif "reels" in txt or "vídeo" in txt or "video" in txt:
        destino = "REELS"
    elif "feed" in txt or "post" in txt or "card" in txt or "foto" in txt:
        destino = "FEED"

    # Remove termos comuns de comando com limites de palavras (\b) para não cortar palavras como 'academia' ou 'treino'
    palavras_remover = [
        r'\bmarc[aã]o\b', r'\bposte?\b', r'\bpostar\b', r'\bpublic[ae]\b', r'\bpublicar\b',
        r'\bcri[ae]\b', r'\bcriar\b', r'\bgere?\b', r'\bgerar\b', r'\bfaz(er)?\b',
        r'\buma?\b', r'\bposts?\b', r'\bcards?\b', r'\bfotos?\b', r'\bimagens?\b',
        r'\bnos?\b', r'\bnas?\b', r'\bnuma?\b', r'\bstor(y|ies)\b', r'\bfeed\b',
        r'\binstagram\b', r'\binsta\b', r'\breels\b', r'\bsobre\b', r'\bde\b',
        r'\bpra mim\b', r'\bpor favor\b', r'\bagora\b'
    ]
    limpo = txt
    for p in palavras_remover:
        limpo = re.sub(p, ' ', limpo, flags=re.IGNORECASE)

    tema = " ".join(limpo.split()).strip()
    if not tema or len(tema) < 3:
        tema = "Foco Total na Creatina e Musculação de Alta Performance"

    return tema, destino


def gerar_imagem_com_openrouter(tema: str, nome_arquivo="post_solicitado.png") -> str:
    """
    Gera uma imagem cinematográfica 8k via OpenRouter com base no tema.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"High-fashion editorial fitness commercial photography for elite brand 'Marcão Personal' about: '{tema}'. "
        f"Inspired by luxury athletic editorial campaigns (Nike / GQ / Caique Ness). Dynamic low-angle shot, athletic physique, "
        f"warm cinematic golden rim lighting, deep obsidian shadows with radiant amber backlight, ultra-realistic skin textures, "
        f"8k commercial masterpiece, clean composition."
    )

    payload = {
        "model": "google/gemini-2.5-flash-image",
        "messages": [{"role": "user", "content": prompt}]
    }

    caminho_local = os.path.join(OUTPUT_DIR, nome_arquivo)
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=50, verify=False)
        if r.status_code == 200:
            data = r.json()
            choices = data.get("choices", [])
            if choices and "images" in choices[0].get("message", {}):
                img_entry = choices[0]["message"]["images"][0]
                img_url = img_entry.get("image_url", {}).get("url", "")
                if "base64," in img_url:
                    b64_str = img_url.split("base64,")[1]
                    raw_bytes = base64.b64decode(b64_str)
                    with open(caminho_local, "wb") as f:
                        f.write(raw_bytes)
                    return caminho_local
    except Exception as e:
        print(f"[INSTA_EXEC] Erro gerando imagem no OpenRouter: {e}")

    # Fallback caso dê timeout: usa a foto oficial do Marcão
    fallback_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "public", "images", "posts", "test_marcao_gen.png")
    if os.path.exists(fallback_img):
        return fallback_img

    return None


def upload_imagem_supabase(caminho_local: str, nome_remoto: str) -> str:
    """Faz o upload para o Supabase Storage e retorna a URL pública."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    with open(caminho_local, "rb") as f:
        data = f.read()

    url = f"{SUPABASE_URL}/storage/v1/object/creativos/posts/{nome_remoto}"
    r = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
    if r.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/creativos/posts/{nome_remoto}"
    return ""


try:
    from catalog_service import buscar_produto_por_termo
except ImportError:
    from apps.api.catalog_service import buscar_produto_por_termo
import asyncio

def gerar_legenda_persuasiva(tema: str, produto: dict = None) -> str:
    """Gera legenda envolvente com chamada para o site oficial e disclosure regulatório."""
    detalhe_produto = ""
    if produto and produto.get("name"):
        detalhe_produto = f"\n💡 Destaque do dia: {produto.get('name')} — {produto.get('pitch_diario')}\n"

    return f"""🔥 {tema.upper()} • METODOLOGIA MARCÃO PERSONAL
{detalhe_produto}
Você quer resultados estéticos e de saúde reais sem enrolação e sem jogar dinheiro fora?
O segredo não é treinar até desmaiar, é alinhar biomecânica, nutrição celular de alta pureza e acompanhamento de verdade!

💪 Quer destravar seu potencial com o meu acompanhamento direto no WhatsApp?
🔗 Toque agora no link da nossa Bio e conheça os protocolos oficiais: marcaopersonal.com

ℹ️ Transparência CONAR/Meta: Alguns links são de parceiros e afiliados oficiais. A entrega e cobrança acontecem com garantia do parceiro indicado.

#marcao #marcaopersonal #fitness #musculacao #treino #biohacking #saude #hipertrofia #lifestyle"""


def executar_postagem_solicitada(texto_comando: str) -> dict:
    """
    Fluxo completo: interpreta comando -> busca dados no catálogo unificado -> gera imagem fotográfica -> aplica compositor editorial @caiqueness -> posta no Instagram.
    """
    tema, destino = extrair_tema_e_destino(texto_comando)
    print(f"[INSTA_EXEC] Executando comando do Chefe: Tema='{tema}' | Destino='{destino}'")

    produto = {}
    try:
        produto = asyncio.run(buscar_produto_por_termo(tema))
    except Exception as e_p:
        print(f"[INSTA_EXEC] Erro buscando produto no catálogo: {e_p}")

    ts = int(time.time())
    img_local = gerar_imagem_com_openrouter(tema, f"raw_chefe_{ts}.png")
    if not img_local or not os.path.exists(img_local):
        return {"sucesso": False, "motivo": "falha_geracao_imagem"}

    # Aplica o compositor editorial @caiqueness
    card_editorial_local = os.path.join(OUTPUT_DIR, f"editorial_chefe_{ts}.jpg")
    try:
        from creative_factory import criar_card_unico, criar_story
        
        pontos_card = [
            produto.get("beneficio_chave", "Resultados visíveis com precisão metabólica e biomecânica."),
            produto.get("pitch_diario", "Invista na sua saúde por menos de um café ao dia.")
        ] if produto else ["Resultados visíveis com precisão metabólica e biomecânica."]

        if destino == "STORIES":
            criar_story(
                headline=tema,
                subheadline="Metodologia Marcão Personal 360°:",
                pontos=pontos_card + ["Mentoria direta no WhatsApp comigo por 3 meses grátis."],
                categoria="PROTOCOLO VIP",
                cta_texto="COMPRAR COM FRETE GRÁTIS",
                out_path=card_editorial_local,
                bg_path=img_local
            )
        else:
            criar_card_unico(
                headline=tema,
                subheadline="Metodologia & Biohacking Marcão Personal:",
                pontos=pontos_card[:2],
                categoria="ALTA PERFORMANCE",
                cta_texto="ARRASTA PRO LADO",
                out_path=card_editorial_local,
                bg_path=img_local
            )
        img_final = card_editorial_local
    except Exception as e_comp:
        print(f"[INSTA_EXEC] Erro no compositor editorial, usando imagem pura: {e_comp}")
        img_final = img_local

    url_publica = upload_imagem_supabase(img_final, f"post_chefe_{ts}.jpg")
    if not url_publica:
        return {"sucesso": False, "motivo": "falha_upload_supabase"}

    caption = gerar_legenda_persuasiva(tema, produto)

    # 1. Cria o container no Instagram Graph API
    url_container = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media"
    
    if destino == "STORIES":
        payload = {
            "access_token": TOKEN,
            "media_type": "STORIES",
            "image_url": url_publica
        }
    else:
        payload = {
            "access_token": TOKEN,
            "image_url": url_publica,
            "caption": caption
        }

    r = requests.post(url_container, data=payload, verify=False, timeout=30)
    if r.status_code not in [200, 201]:
        print(f"[INSTA_EXEC] Erro container: {r.text}")
        return {"sucesso": False, "motivo": r.text}

    container_id = r.json().get("id")

    # 2. Publica o container
    url_pub = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media_publish"
    pr = requests.post(url_pub, data={"access_token": TOKEN, "creation_id": container_id}, verify=False, timeout=30)
    if pr.status_code in [200, 201]:
        pub_id = pr.json().get("id")
        print(f"[INSTA_EXEC] Post publicado com sucesso! ID: {pub_id}")
        return {
            "sucesso": True,
            "post_id": pub_id,
            "tema": tema,
            "destino": destino,
            "media_url": url_publica
        }

    return {"sucesso": False, "motivo": pr.text}
