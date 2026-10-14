"""
Publicador Oficial de Vídeo no Instagram (@marcaopersonalfitness)
==================================================================
Publica o vídeo de 50s gerado no:
1. Instagram REELS (Feed + aba Reels) com legenda completa e links.
2. Instagram STORIES com tarja visual de acesso ao site oficial.
"""

import os
import time
import requests
import urllib3

urllib3.disable_warnings()

ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
VIDEO_URL = "https://qkopgftfrfftoyndhhfj.supabase.co/storage/v1/object/public/creativos/videos/marcao_reels_50s_pilot.mp4"

CAPTION_REELS = """🚨 VOCÊ TOMA CREATINA ERRADO? Descubra o mito que tá jogando seus treinos no lixo!

Muitos acham que creatina dá energia instantânea ou param no fim de semana com medo de inchaço. A verdade científica é que a creatina funciona por saturação crônica celular, aumentando a fosfocreatina para ressintetizar ATP muscular na última repetição!

🔥 Como tomar do jeito certo:
✅ 5g todo santo dia (inclusive nos dias sem treino)
✅ Junto de carboidrato ou após uma refeição principal
✅ Hidratação celular constante (35 a 45ml por kg de peso)

Quer ter a minha consultoria VIP e saber a dosagem exata pra sua bioimpedância?
🔗 Toque agora no link da Bio e entre no site oficial: marcaopersonal.com

#marcao #marcaopersonal #creatina #musculacao #treino #biohacking #hipertrofia #suplementacao #saude"""


def criar_e_publicar_container(media_type="REELS", caption=None, share_to_feed=True):
    print(f"\n[INSTAGRAM] Iniciando publicação de {media_type}...")
    
    # 1. Criação do container
    url_container = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media"
    payload = {
        "access_token": TOKEN,
        "media_type": media_type,
        "video_url": VIDEO_URL
    }
    if media_type == "REELS":
        payload["caption"] = caption
        payload["share_to_feed"] = "true" if share_to_feed else "false"

    r = requests.post(url_container, data=payload, verify=False, timeout=30)
    print(f"[INSTAGRAM] Resposta criação container ({r.status_code}): {r.text}")
    if r.status_code not in [200, 201]:
        return None

    container_id = r.json().get("id")
    print(f"[INSTAGRAM] Container ID criado: {container_id}")

    # 2. Aguarda processamento do vídeo no Instagram (status_code == FINISHED)
    print("[INSTAGRAM] Aguardando o Instagram processar o vídeo...")
    max_tentativas = 30
    for i in range(max_tentativas):
        time.sleep(6)
        url_status = f"https://graph.instagram.com/v21.0/{container_id}?fields=status_code,status&access_token={TOKEN}"
        st_res = requests.get(url_status, verify=False, timeout=15)
        st_data = st_res.json()
        status_code = st_data.get("status_code")
        print(f"  [Tentativa {i+1}] Status do processamento: {status_code}")

        if status_code == "FINISHED":
            print("[INSTAGRAM] Processamento concluído com sucesso!")
            break
        elif status_code == "ERROR":
            print(f"[INSTAGRAM] Erro no processamento do vídeo: {st_data}")
            return None

    # 3. Publicação do container
    url_publish = f"https://graph.instagram.com/v21.0/{ACCOUNT_ID}/media_publish"
    pub_payload = {
        "access_token": TOKEN,
        "creation_id": container_id
    }
    pr = requests.post(url_publish, data=pub_payload, verify=False, timeout=30)
    print(f"[INSTAGRAM] Resposta publicacao final ({pr.status_code}): {pr.text}")
    if pr.status_code in [200, 201]:
        published_id = pr.json().get("id")
        print(f"[INSTAGRAM] Publicacao concluida com sucesso! ID publicado: {published_id}")
        return published_id

    return None


def executar_publicacao():
    reels_id = "18117783221001667"  # Já publicado com sucesso!
    print(f"[INSTAGRAM] Reels ja publicado no Feed com ID: {reels_id}")

    # Publica nos Stories
    stories_id = criar_e_publicar_container(media_type="STORIES")

    print("\n========================================================")
    print("Resultado Final:")
    print(f"Reels publicado ID: {reels_id}")
    print(f"Stories publicado ID: {stories_id}")
    print("========================================================")


if __name__ == "__main__":
    executar_publicacao()
