"""
Watcher Wan 2.1 - Monitor de Renderização do Vídeo de Difusão Pura
==================================================================
Monitora a conclusão da renderização no cluster Wan-AI/Wan2.1 (ZeroGPU),
baixa o arquivo MP4 quando finalizado, faz o upload no Supabase Storage
e notifica o Diretor Evandro no WhatsApp.
"""

import os
import sys
import time
import httpx
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")

OUTPUT_DIR = os.path.join(_base_dir, "output", "videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def notificar_evandro(msg: str):
    """Envia mensagem no WhatsApp de Evandro."""
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": "5532984587255",
        "text": msg
    }
    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            await client.post(f"{EVOLUTION_API_URL}/message/sendText/sofia", headers=headers, json=payload)
    except Exception as e:
        print("Erro notificando Evandro:", e)

def upload_supabase_video(video_path: str, remote_name: str) -> str:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4",
        "x-upsert": "true"
    }
    url = f"{SUPABASE_URL}/storage/v1/object/creativos/videos/{remote_name}"
    with open(video_path, "rb") as f:
        data = f.read()
    r = httpx.post(url, headers=headers, content=data, verify=False, timeout=60)
    if r.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/creativos/videos/{remote_name}"
    return ""

def monitorar():
    import asyncio
    from gradio_client import Client
    
    print("[WATCHER] Conectando ao Wan-AI/Wan2.1...")
    client = Client("Wan-AI/Wan2.1", ssl_verify=False)
    
    max_loops = 150  # ~30 minutos
    for i in range(max_loops):
        try:
            res = client.predict(api_name="/status_refresh")
            video_info = res[0]
            label = res[3].get("label") if len(res) > 3 and isinstance(res[3], dict) else ""
            print(f"[WATCHER #{i+1}] Status: {label}")
            
            if isinstance(video_info, dict) and video_info.get("value"):
                v_path = video_info["value"].get("video")
                if v_path and os.path.exists(v_path):
                    print(f"[WATCHER] VÍDEO CONCLUÍDO! Local: {v_path}")
                    remote_name = f"marcao_wan21_{int(time.time())}.mp4"
                    pub_url = upload_supabase_video(v_path, remote_name)
                    print(f"[WATCHER] Upload Supabase: {pub_url}")
                    
                    msg_chefe = (
                        f"🎬 *VÍDEO DE IA PURA (WAN 2.1) FINALIZADO!*\n\n"
                        f"Chefe, o vídeo em formato vertical Reels com movimentação contínua por inteligência artificial (sem fotos estáticas) acabou de ser renderizado pelo cluster!\n\n"
                        f"🔗 *Link direto para assistir:* {pub_url}\n\n"
                        f"Dê uma olhada no resultado e me diga se aprovou para colocarmos no Feed e Stories! 🔥"
                    )
                    asyncio.run(notificar_evandro(msg_chefe))
                    return pub_url
        except Exception as e:
            print(f"[WATCHER] Erro checando status: {e}")
            
        time.sleep(12)
        
    print("[WATCHER] Tempo limite de espera atingido.")
    return ""

if __name__ == "__main__":
    monitorar()
