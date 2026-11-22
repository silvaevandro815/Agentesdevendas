"""
=============================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
CANVA PUBLISHER SERVICE (EXPORTAÇÃO DIRETA DO CANVA PARA O INSTAGRAM)
=============================================================================
Garante que a imagem REAL e APROVADA no Canva (100% fiel ao layout visual)
seja exportada em alta resolução, convertida para os padrões da Meta Graph API,
e publicada no Feed (4:5) e nos Stories (9:16) do Instagram @marcaopersonalfitness.
=============================================================================
"""

import os
import sys
import time
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
FONTS_DIR = os.path.join(PROJECT_ROOT, "assets", "fonts")


def upload_supabase_storage(caminho_local: str, nome_remoto: str) -> str:
    """Faz upload de imagem para o storage público do Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    with open(caminho_local, "rb") as f:
        data = f.read()

    url = f"{SUPABASE_URL}/storage/v1/object/creativos/posts/{nome_remoto}"
    r = requests.post(url, headers=headers, data=data, timeout=30)
    if r.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/creativos/posts/{nome_remoto}"
    r_put = requests.put(url, headers=headers, data=data, timeout=30)
    if r_put.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/creativos/posts/{nome_remoto}"
    return ""


def gerar_story_do_card_canva(feed_card_path: str, out_story_path: str, titulo: str = "NOVO NO FEED") -> str:
    """
    Gera a versão 9:16 (1080x1920) oficial do Story a partir da arte real do Canva,
    enquadrada perfeitamente na safe area dos Stories do Instagram.
    """
    W, H = 1080, 1920
    story = Image.new("RGBA", (W, H), (12, 14, 18, 255))
    
    card = Image.open(feed_card_path).convert("RGBA")
    # Centraliza na área segura (y: 285 a 1635)
    story.paste(card, (0, 285))

    draw = ImageDraw.Draw(story)
    f_tag = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"), 22)
    f_alert = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat-Black.ttf"), 30)
    f_cta = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat-Black.ttf"), 24)

    # Top Header
    draw.rounded_rectangle([140, 130, 940, 195], radius=32, fill=(18, 22, 28, 240), outline=(249, 115, 22), width=2)
    top_txt = "🦁 TREINADOR MARCÃO  •  NUTRIÇÃO INTELIGENTE"
    bbox = draw.textbbox((0, 0), top_txt, font=f_tag)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 148), top_txt, fill=(255, 180, 100), font=f_tag)

    # Título do post
    alert_txt = f"{titulo.upper()} 🔥"
    bbox_al = draw.textbbox((0, 0), alert_txt, font=f_alert)
    draw.text(((W - (bbox_al[2] - bbox_al[0])) // 2, 220), alert_txt, fill=(255, 255, 255), font=f_alert)

    # Rodapé CTA
    draw.rounded_rectangle([100, 1695, 980, 1785], radius=24, fill=(249, 115, 22, 250), outline=(254, 215, 170), width=2)
    cta_story = "TOQUE AQUI PARA LER O POST COMPLETO NO FEED 👆"
    bbox_cta = draw.textbbox((0, 0), cta_story, font=f_cta)
    draw.text(((W - (bbox_cta[2] - bbox_cta[0])) // 2, 1725), cta_story, fill=(15, 23, 42), font=f_cta)

    story_rgb = story.convert("RGB")
    story_rgb.save(out_story_path, quality=98)
    return out_story_path


def publicar_arte_canva_no_instagram(caminho_imagem_canva: str, legenda: str, titulo_story: str = "NOVO NO FEED") -> dict:
    """
    Recebe o arquivo local da arte exportada do Canva, prepara para o Feed e Story,
    e publica oficialmente no Instagram via Meta Graph API.
    """
    ts = int(time.time())
    scratch_dir = os.path.join(PROJECT_ROOT, "scratch")
    os.makedirs(scratch_dir, exist_ok=True)

    # Converter imagem base para JPG 1080x1350
    feed_jpg_path = os.path.join(scratch_dir, f"feed_canva_{ts}.jpg")
    im = Image.open(caminho_imagem_canva).convert("RGB")
    if im.size != (1080, 1350):
        im = im.resize((1080, 1350), Image.Resampling.LANCZOS)
    im.save(feed_jpg_path, quality=98)

    # Gerar Story 9:16
    story_jpg_path = os.path.join(scratch_dir, f"story_canva_{ts}.jpg")
    gerar_story_do_card_canva(feed_jpg_path, story_jpg_path, titulo_story)

    # Uploads para Supabase CDN
    url_feed = upload_supabase_storage(feed_jpg_path, f"feed_canva_{ts}.jpg")
    url_story = upload_supabase_storage(story_jpg_path, f"story_canva_{ts}.jpg")

    if not url_feed:
        return {"sucesso": False, "erro": "Falha no upload do Feed para CDN"}

    # Aguardar 2s para propagação do CDN
    time.sleep(2)

    container_url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media"
    pub_url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"

    feed_post_id = None
    permalink = None
    story_post_id = None

    # Publicar Feed
    try:
        r_c = requests.post(container_url, data={
            "image_url": url_feed,
            "caption": legenda,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }, timeout=30)
        if r_c.status_code == 200:
            c_id = r_c.json().get("id")
            for _ in range(8):
                time.sleep(2)
                st = requests.get(f"https://graph.instagram.com/v21.0/{c_id}?fields=status_code&access_token={INSTAGRAM_ACCESS_TOKEN}").json().get("status_code")
                if st == "FINISHED":
                    break
            r_pub = requests.post(pub_url, data={
                "creation_id": c_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }, timeout=30)
            if r_pub.status_code == 200:
                feed_post_id = r_pub.json().get("id")
                p_info = requests.get(f"https://graph.instagram.com/v21.0/{feed_post_id}?fields=permalink&access_token={INSTAGRAM_ACCESS_TOKEN}").json()
                permalink = p_info.get("permalink")
    except Exception as e:
        print("[ERRO FEED]", e)

    # Publicar Story
    if url_story:
        try:
            r_sc = requests.post(container_url, data={
                "image_url": url_story,
                "media_type": "STORIES",
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }, timeout=30)
            if r_sc.status_code == 200:
                sc_id = r_sc.json().get("id")
                for _ in range(8):
                    time.sleep(2)
                    st = requests.get(f"https://graph.instagram.com/v21.0/{sc_id}?fields=status_code&access_token={INSTAGRAM_ACCESS_TOKEN}").json().get("status_code")
                    if st == "FINISHED":
                        break
                r_spub = requests.post(pub_url, data={
                    "creation_id": sc_id,
                    "access_token": INSTAGRAM_ACCESS_TOKEN
                }, timeout=30)
                if r_spub.status_code == 200:
                    story_post_id = r_spub.json().get("id")
        except Exception as e:
            print("[ERRO STORY]", e)

    # Registrar no banco Supabase
    if feed_post_id and SUPABASE_KEY:
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/content_calendar", headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }, json={
                "platform": "instagram",
                "content_id": feed_post_id,
                "caption": legenda[:100],
                "media_url": url_feed,
                "status": "published",
                "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }, timeout=15)
        except Exception as e:
            print("[ERRO SUPABASE CALENDAR]", e)

    return {
        "sucesso": bool(feed_post_id),
        "feed_post_id": feed_post_id,
        "permalink": permalink,
        "story_post_id": story_post_id,
        "url_feed": url_feed,
        "url_story": url_story
    }
