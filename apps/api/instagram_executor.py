"""
Executor de Postagem Instagram sob Demanda do Chefe Evandro
============================================================
Permite que o Marcão, ao receber um comando de texto ou áudio no WhatsApp do Chefe,
gere o criativo (imagem/card) via IA, redija a legenda persuasiva e publique
imediatamente no Feed, Reels ou Stories da conta oficial @marcaopersonalfitness.
"""

import os
import sys
import re
import time
import json
import base64
import requests
import urllib3
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def interpretar_comando_com_ia(texto_comando: str) -> dict:
    """
    Usa o Gemini 2.5 Flash para interpretar com precisão editorial o comando do Chefe,
    estruturando manchete, subtítulo, pontos de benefício, prompt fotográfico puro e legenda,
    garantindo que o criativo seja 100% INÉDITO e sem repetição de conteúdos anteriores.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    from anti_repetition_guard import buscar_historico_posts_recentes, MATRIZ_PERSONAGENS, MATRIZ_CENARIOS
    import random

    hist = buscar_historico_posts_recentes(limite=20)
    headlines_recentes = hist.get("headlines_usadas", [])[:12]

    p_sorteado = random.choice(MATRIZ_PERSONAGENS)
    c_sorteado = random.choice(MATRIZ_CENARIOS)

    prompt_instrucao = f"""Você é o diretor de arte e copywriter oficial da marca 'Marcão Personal'.
Analise o comando do chefe: "{texto_comando}"

🚨 REGRA INVIOLÁVEL: É ESTRITAMENTE PROIBIDO REPETIR O MESMO CRIATIVO!
O tema pode ser abordado novamente, mas a headline, o gancho e o criativo DEVEM SER 100% INÉDITOS!
Títulos que JÁ FORAM PUBLICADOS no nosso Instagram recentemente e que você NUNCA pode repetir:
{json.dumps(headlines_recentes, ensure_ascii=False, indent=2)}

Personagem Sorteado para a Imagem: {p_sorteado['descricao']}
Cenário Sorteado para a Imagem: {c_sorteado['nome']}

Retorne APENAS um objeto JSON válido (sem crases de markdown em volta, sem texto antes ou depois) no seguinte formato:
{{
  "destino": "FEED",
  "headline": "MANCHETE EM CAIXA ALTA (máximo 4 a 6 palavras impactantes e INÉDITAS)",
  "subheadline": "Metodologia & Biohacking Marcão Personal:",
  "pontos": [
    "Primeiro benefício científico curto (máximo 55 caracteres)",
    "Segundo benefício direto de resultado (máximo 55 caracteres)"
  ],
  "categoria": "ALTA PERFORMANCE",
  "cta_card": "LEIA A LEGENDA",
  "prompt_imagem": "{p_sorteado['prompt_char']} {c_sorteado['prompt_scene']}. PHOTOGRAPHIC SAFE ZONE COMPOSITION: Subject framed in UPPER 50% with face, eyes, nose, mouth and smile perfectly visible, in tack-sharp focus and beautifully lit. LOWER 50% must be dark moody negative space for clean advertising text overlay without covering the subject's face. Warm golden rim lighting, ultra-detailed skin textures, cinematic 85mm portrait, 8k resolution commercial photography. CRITICAL: PURE PHOTOGRAPHY ONLY. ABSOLUTELY NO TEXT, NO LETTERS, NO WORDS, NO SYMBOLS, NO WATERMARKS. CLEAN UNMARKED BACKGROUND.",
  "legenda": "Texto persuasivo de 3 a 4 parágrafos curtos com emojis de alta autoridade, chamada para o site oficial marcaopersonal.com ou link na bio, e hashtags fitness."
}}

Regras Críticas:
1. Para destino "FEED" (post de card único), 'cta_card' DEVE ser OBRIGATORIAMENTE "LEIA A LEGENDA" ou "LINK NA BIO". NUNCA use "ARRASTA PRO LADO" em post único!
2. A manchete DEVE ter palavras completas e ortografia impecável em português. NUNCA divida sílabas de forma errada.
3. Se o comando mencionar 'story' ou 'stories', coloque "destino": "STORIES" e 'cta_card': "COMPRE COM FRETE GRÁTIS".
"""

    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [{"role": "user", "content": prompt_instrucao}],
        "temperature": 0.7
    }

    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20, verify=False)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            clean_json = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            if data.get("destino") != "STORIES":
                data["cta_card"] = "LEIA A LEGENDA"
            return data
    except Exception as e:
        print(f"[INSTA_EXEC] Aviso no parser de IA: {e}")

    # Fallback determinístico resiliente
    txt_l = texto_comando.lower()
    destino = "STORIES" if ("story" in txt_l or "stories" in txt_l) else "FEED"
    
    tema_fallback = "CREATINA & TREINO PESADO"
    if "creatina" in txt_l:
        tema_fallback = "CREATINA & FORÇA MÁXIMA"
    elif "balança" in txt_l or "bioimpedancia" in txt_l:
        tema_fallback = "BIOIMPEDÂNCIA & RESULTADOS"
    elif "colágeno" in txt_l:
        tema_fallback = "COLÁGENO & FIRMEZA TOTAL"

    return {
        "destino": destino,
        "headline": tema_fallback,
        "subheadline": "Metodologia & Biohacking Marcão Personal:",
        "pontos": [
            "Acelera a ressíntese de ATP e ganho de força pura.",
            "Recuperação celular rápida sem retenção na pele."
        ],
        "categoria": "ALTA PERFORMANCE",
        "cta_card": "LEIA A LEGENDA" if destino == "FEED" else "COMPRAR COM FRETE GRÁTIS",
        "prompt_imagem": (
            "Ultra-realistic cinematic 8k commercial fitness photography of athletic muscular male trainer Marcão "
            "working out with heavy barbell in an elite luxury modern gym. Focused expression, golden rim lights, "
            "deep dark obsidian shadows. CRITICAL: PURE PHOTOGRAPHY ONLY, ZERO TEXT, NO WORDS, NO LETTERS."
        ),
        "legenda": f"🔥 {tema_fallback} • METODOLOGIA MARCÃO PERSONAL\n\nResultados reais com precisão metabólica e biomecânica!\n\n🔗 Conheça os protocolos oficiais: marcaopersonal.com\n\n#marcao #marcaopersonal #fitness #treino #hipertrofia"
    }


def gerar_imagem_com_openrouter(prompt_ia: str, nome_arquivo="post_solicitado.png") -> str:
    """
    Gera uma imagem cinematográfica 8k via OpenRouter, garantindo que seja fotografia pura sem letras/textos.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    prompt_completo = prompt_ia
    if "PURE PHOTOGRAPHY ONLY" not in prompt_completo:
        prompt_completo += " CRITICAL: PURE PHOTOGRAPHY ONLY. ABSOLUTELY NO TEXT, NO LETTERS, NO WORDS, NO TYPOGRAPHY."

    payload = {
        "model": "google/gemini-2.5-flash-image",
        "messages": [{"role": "user", "content": prompt_completo}]
    }

    caminho_local = os.path.join(OUTPUT_DIR, nome_arquivo)
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60, verify=False)
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


def executar_postagem_solicitada(texto_comando: str) -> dict:
    """
    Fluxo Inteligente Completo:
    1. Interpretação editorial via IA (manchete correta, pontos, prompt fotográfico e legenda).
    2. Geração da foto pura via OpenRouter (zero texto gerado por IA na foto).
    3. Composição gráfica de alta precisão via Pillow (Bebas Neue auto-ajustável + Segoe UI).
    4. Upload para CDN Supabase.
    5. Publicação oficial no Instagram (@marcaopersonalfitness).
    """
    print(f"[INSTA_EXEC] Interpretando comando do Chefe com Diretor de Arte IA...")
    plano = interpretar_comando_com_ia(texto_comando)
    print(f"[INSTA_EXEC] Plano Editorial: Headline='{plano.get('headline')}' | Destino='{plano.get('destino')}' | CTA='{plano.get('cta_card')}'")

    ts = int(time.time())
    img_local = gerar_imagem_com_openrouter(plano.get("prompt_imagem", ""), f"raw_chefe_{ts}.png")
    if not img_local or not os.path.exists(img_local):
        return {"sucesso": False, "motivo": "falha_geracao_imagem"}

    card_editorial_local = os.path.join(OUTPUT_DIR, f"editorial_chefe_{ts}.jpg")
    try:
        from creative_factory import criar_card_unico, criar_story

        prod_img = None
        preco = None
        cmd_lower = (texto_comando + " " + plano.get("headline", "")).lower()
        base_img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "public", "images")
        if "creatina" in cmd_lower:
            prod_img = os.path.join(base_img_dir, "creatina.jpg")
            preco = "R$ 169,90"
        elif "colágeno" in cmd_lower or "colageno" in cmd_lower:
            prod_img = os.path.join(base_img_dir, "colageno.png")
            preco = "R$ 164,90"
        elif "azempika" in cmd_lower or "caneta" in cmd_lower:
            prod_img = os.path.join(base_img_dir, "azempika.jpg")
            preco = "R$ 99,00"
        elif "iarmonize" in cmd_lower or "capilar" in cmd_lower:
            prod_img = os.path.join(base_img_dir, "iarmonize.jpg")
            preco = "R$ 1.256,00"

        if plano.get("destino") == "STORIES":
            criar_story(
                headline=plano.get("headline"),
                subheadline=plano.get("subheadline", "Metodologia Marcão Personal 360°:"),
                pontos=plano.get("pontos", []),
                categoria=plano.get("categoria", "ALTA PERFORMANCE"),
                cta_texto=plano.get("cta_card", "COMPRAR COM FRETE GRÁTIS"),
                out_path=card_editorial_local,
                bg_path=img_local,
                produto_img_path=prod_img,
                preco=preco
            )
        else:
            criar_card_unico(
                headline=plano.get("headline"),
                subheadline=plano.get("subheadline", "Metodologia & Biohacking Marcão Personal:"),
                pontos=plano.get("pontos", []),
                categoria=plano.get("categoria", "ALTA PERFORMANCE"),
                cta_texto=plano.get("cta_card", "LEIA A LEGENDA"),
                out_path=card_editorial_local,
                bg_path=img_local,
                produto_img_path=prod_img,
                preco=preco
            )
        img_final = card_editorial_local
    except Exception as e_comp:
        print(f"[INSTA_EXEC] Erro no compositor editorial, usando imagem pura: {e_comp}")
        img_final = img_local

    url_publica = upload_imagem_supabase(img_final, f"post_chefe_{ts}.jpg")
    if not url_publica:
        return {"sucesso": False, "motivo": "falha_upload_supabase"}

    caption = plano.get("legenda", "")

    # 1. Cria o container no Instagram Graph API
    url_container = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media"
    
    if plano.get("destino") == "STORIES":
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

    # 2. Publica o container (com espera/retry para o Instagram processar a mídia)
    url_pub = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media_publish"
    ultimo_erro = ""
    for tentativa in range(1, 5):
        time.sleep(4)
        pr = requests.post(url_pub, data={"access_token": TOKEN, "creation_id": container_id}, verify=False, timeout=30)
        if pr.status_code in [200, 201]:
            pub_id = pr.json().get("id")
            print(f"[INSTA_EXEC] Post publicado com sucesso na tentativa {tentativa}! ID: {pub_id}")
            try:
                from anti_repetition_guard import registrar_no_content_calendar
                registrar_no_content_calendar(pub_id, caption, url_publica)
            except Exception as e_reg:
                print(f"[INSTA_EXEC] Aviso ao registrar no content_calendar: {e_reg}")
            return {
                "sucesso": True,
                "post_id": pub_id,
                "headline": plano.get("headline"),
                "destino": plano.get("destino"),
                "media_url": url_publica
            }
        ultimo_erro = pr.text
        print(f"[INSTA_EXEC] Tentativa {tentativa} aguardando processamento do Instagram...")

    return {"sucesso": False, "motivo": ultimo_erro}
