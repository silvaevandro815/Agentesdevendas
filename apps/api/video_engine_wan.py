"""
Motor de Geração de Vídeo Open-Source Wan 2.1 & Pipeline Instagram Reels
========================================================================
Utiliza o modelo Open-Source Wan 2.1 (Apache 2.0) desenvolvido pela Wan-AI / Alibaba,
capaz de gerar vídeos ultra-realistas com consistência física e de movimento (nível Veo 3 / Sora).

Suporta:
- Text-to-Video (T2V) em resolução vertical 720x1280 (padrão Instagram Reels / Stories).
- Image-to-Video (I2V) animando fotos (ex: fotos do Evandro ou de produtos de saúde/fitness).
- Upload automático do vídeo renderizado para o Supabase Storage.
- Envio para o pipeline de publicação do Instagram (@marcaopersonalfitness).
"""

import os
import time
import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

DIR_OUTPUT_VIDEOS = Path(__file__).resolve().parent / "output" / "videos"
DIR_OUTPUT_VIDEOS.mkdir(parents=True, exist_ok=True)


def refinar_prompt_com_gemini(tema: str, eh_ciencia: bool = True) -> str:
    """
    Usa a chave Google (Gemini 3.5 Flash) do Evandro para gerar um prompt visual
    cinematográfico otimizado para o motor Wan 2.1 em inglês.
    """
    if not GOOGLE_API_KEY:
        return f"Cinematic 4k vertical shot of {tema}, luxury modern fitness science laboratory, soft dramatic lighting, photorealistic."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GOOGLE_API_KEY}"
    prompt_instrucao = (
        f"You are a Hollywood AI cinematographer and biomechanics visualizer. "
        f"Write a single prompt in English (maximum 40 words) describing a photorealistic 9:16 vertical video about: '{tema}'. "
        f"Include realistic physical motion, camera pan, cinematic lighting, 8k resolution, macro depth of field. Do not use quotes."
    )
    payload = {"contents": [{"parts": [{"text": prompt_instrucao}]}]}

    try:
        r = requests.post(url, json=payload, timeout=10, verify=False)
        if r.status_code == 200:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[WAN VIDEO] Aviso ao refinar prompt no Gemini: {e}")

    return f"Cinematic 9:16 vertical video of {tema}, hyper-realistic motion, glowing microscopic particles, 8k commercial quality."


def upload_video_para_supabase(caminho_local_video: str, nome_arquivo_remoto: str) -> str:
    """
    Faz o upload do arquivo MP4 para o bucket público 'creativos/videos/' no Supabase Storage
    e retorna a URL pública acessível para a API do Instagram.
    """
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4",
        "x-upsert": "true"
    }

    url = f"{SUPABASE_URL}/storage/v1/object/creativos/videos/{nome_arquivo_remoto}"
    with open(caminho_local_video, "rb") as f:
        video_data = f.read()

    r = requests.post(url, headers=headers, data=video_data, verify=False)
    if r.status_code in [200, 201]:
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/creativos/videos/{nome_arquivo_remoto}"
        print(f"[WAN VIDEO] Vídeo salvo no Supabase com sucesso: {public_url}")
        return public_url
    else:
        print(f"[WAN VIDEO] Erro no upload Supabase ({r.status_code}): {r.text[:200]}")
        return ""


def gerar_video_wan21_async(prompt: str, tamanho: str = "720*1280", imagem_referencia: str = None) -> str:
    """
    Chama o modelo Open-Source Wan 2.1 via Gradio Client (ZeroGPU).
    Retorna o caminho local do arquivo MP4 ou URL pública.
    """
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        print("[WAN VIDEO] gradio_client não instalado.")
        return ""

    print(f"[WAN VIDEO] Conectando ao cluster do modelo Open-Source Wan 2.1...")
    client = Client("Wan-AI/Wan2.1", ssl_verify=False)

    if imagem_referencia and os.path.exists(imagem_referencia):
        print(f"[WAN VIDEO] Disparando Image-to-Video com imagem base: {imagem_referencia}")
        client.predict(
            prompt=prompt,
            image=handle_file(imagem_referencia),
            watermark_wan=False,
            seed=-1,
            api_name="/i2v_generation_async"
        )
    else:
        print(f"[WAN VIDEO] Disparando Text-to-Video (720x1280 Reels): {prompt[:80]}...")
        client.predict(
            prompt=prompt,
            size=tamanho,
            watermark_wan=False,
            seed=-1,
            api_name="/t2v_generation_async"
        )

    # Monitora o processamento até a conclusão
    print("[WAN VIDEO] Aguardando renderização do vídeo...")
    max_tentativas = 40  # ~3 a 5 minutos
    for i in range(max_tentativas):
        time.sleep(8)
        status_res = client.predict(api_name="/status_refresh")
        video_info = status_res[0] if status_res else None

        if isinstance(video_info, dict) and video_info.get("value"):
            video_path = video_info["value"].get("video")
            if video_path and os.path.exists(video_path):
                print(f"[WAN VIDEO] Vídeo renderizado com sucesso: {video_path}")
                return video_path

    print("[WAN VIDEO] Timeout na fila de renderização.")
    return ""
