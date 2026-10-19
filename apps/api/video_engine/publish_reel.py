import os
import time
import requests
import urllib3
import sys
from dotenv import load_dotenv

urllib3.disable_warnings()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")

ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
VIDEO_URL = "https://qkopgftfrfftoyndhhfj.supabase.co/storage/v1/object/public/creativos/videos/reel_evandro_motivacional_10s.mp4"

CAPTION_FITNESS = """🔥 A MOTIVAÇÃO TE FAZ COMEÇAR... MAS É A CONSTÂNCIA QUE CRIA O SEU SHAPE!

Quantas vezes você esperou a segunda-feira chegar pra começar a treinar? A verdade é que a motivação dura poucos dias, mas a disciplina diária constrói o resultado que você sempre sonhou na frente do espelho.

👊 Coloque a sua saúde em primeiro lugar.
💪 Treine com intensidade, cuide da sua hidratação e nunca desista de você!

Quer dar o próximo passo e ter a minha consultoria VIP com a Balança de Bioimpedância com Inteligência Artificial?
🔗 Toque no link da Bio e venha fazer parte do time: marcaopersonal.com

#marcao #marcaopersonal #motivação #treino #fitness #musculacao #saude #disciplina #shape #bodybuilding"""

def publicar_reel_instagram(video_url=VIDEO_URL, caption=CAPTION_FITNESS, share_to_feed=True):
    print("==========================================================")
    print("🚀 PUBLICADOR OFICIAL DE REELS NO INSTAGRAM — MARCÃO PERSONAL")
    print("==========================================================")
    print(f"Vídeo URL: {video_url}")
    print(f"Instagram Account ID: {ACCOUNT_ID}")

    if not TOKEN:
        print("❌ ERRO: INSTAGRAM_ACCESS_TOKEN ausente no .env!")
        return None

    # 1. Criação do container de Reels
    url_container = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media"
    payload = {
        "access_token": TOKEN,
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true" if share_to_feed else "false"
    }

    print("\n1. Criando container de Reels no Instagram...")
    r = requests.post(url_container, data=payload, verify=False, timeout=35)
    print(f"Status ({r.status_code}): {r.text}")

    if r.status_code not in [200, 201]:
        print("❌ Falha na criação do container.")
        return None

    container_id = r.json().get("id")
    print(f"✅ Container ID criado: {container_id}")

    # 2. Aguardar processamento do vídeo pela Meta
    print("\n2. Aguardando a Meta codificar e processar o vídeo...")
    max_tentativas = 25
    for i in range(max_tentativas):
        time.sleep(5)
        url_status = f"https://graph.instagram.com/v21.0/{container_id}?fields=status_code,status&access_token={TOKEN}"
        st_res = requests.get(url_status, verify=False, timeout=15)
        st_data = st_res.json()
        status_code = st_data.get("status_code")
        print(f"   [Checagem {i+1}] Status: {status_code}")

        if status_code == "FINISHED":
            print("✅ Vídeo 100% processado e pronto para publicação!")
            break
        elif status_code == "ERROR":
            print(f"❌ Erro no processamento da Meta: {st_data}")
            return None
    else:
        print("⏳ Tempo limite de processamento atingido.")
        return None

    # 3. Publicação do container
    print("\n3. Publicando Reels no perfil @marcaopersonalfitness...")
    url_publish = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media_publish"
    pub_payload = {
        "access_token": TOKEN,
        "creation_id": container_id
    }
    pr = requests.post(url_publish, data=pub_payload, verify=False, timeout=35)
    print(f"Status Publicação ({pr.status_code}): {pr.text}")

    if pr.status_code in [200, 201]:
        published_id = pr.json().get("id")
        print(f"\n🎉 REELS PUBLICADO COM SUCESSO NO INSTAGRAM!")
        print(f"ID da Publicação: {published_id}")
        return published_id
    else:
        print("❌ Erro ao publicar o container.")
        return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Publicar Reels Fitness no Instagram")
    parser.add_argument("--exec", action="store_true", help="Executa a publicação real no Instagram")
    args = parser.parse_args()

    if args.exec:
        publicar_reel_instagram()
    else:
        print("[AVISO] Para publicar de verdade no Instagram, execute com a flag: --exec")
