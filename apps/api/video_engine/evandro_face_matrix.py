"""
=============================================================================
MATRIZ DE FIDELIDADE FACIAL TRIPLA DO EVANDRO (FRONT + LADO2)
GERADOR DE CENAS MULTI-LOCAIS E ÂNGULOS CINEMATOGRÁFICOS COM IA
=============================================================================
Utiliza a triangulação fotográfica de alta definição de frente.jpg e lado2.jpg
para garantir fidelidade facial 100% autêntica em múltiplos ambientes:
- Praia / Orla (corrida ao pôr do sol)
- Trilha / Natureza / Montanha
- Parque Urbano / Futebol / Lazer
- Cozinha / Home Living (nutrição e descanso)
- Academia Moderna de Luxo (força e performance)
=============================================================================
"""

import os
import sys
import base64
import httpx
import certifi
import shutil
import time
from PIL import Image
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['HF_TOKEN'] = HF_TOKEN

BASE_DIR = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"
TAKES_DIR = os.path.join(BASE_DIR, "takes")
ASSETS_EVANDRO = r"c:\Users\User\Desktop\Agentes de venda\assets\evandro"

FRENTE_PATH = os.path.join(ASSETS_EVANDRO, "frente.jpg")
LADO2_PATH = os.path.join(ASSETS_EVANDRO, "lado2.jpg")

# Codificar fotos mestres em base64
def get_b64(path):
    # Redimensiona para resolução ideal se muito pesado
    with Image.open(path) as img:
        img.thumbnail((1200, 1600), Image.Resampling.LANCZOS)
        tmp_path = path.replace(".jpg", "_opt.jpg")
        img.save(tmp_path, "JPEG", quality=92)
    with open(tmp_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    return data

def generate_evandro_scene_photo(scene_prompt, output_image_path):
    """
    Gera foto vertical 9:16 com fidelidade facial estrita a partir de frente.jpg e lado2.jpg
    """
    print(f"\n=======================================================")
    print("📸 GERANDO CENA COM MÁXIMA FIDELIDADE FACIAL DO EVANDRO")
    print(f"Cena: {scene_prompt}")
    print("=======================================================")

    b64_frente = get_b64(FRENTE_PATH)
    b64_lado2 = get_b64(LADO2_PATH)

    system_instruction = (
        "CRITICAL IDENTITY MANDATE: You must preserve the EXACT facial structure, bone shape, "
        "dark eyes, nose bridge, jawline, dark hair, skin tone and athletic physique of the Brazilian man "
        "shown in the two reference photos (Reference 1: front view, Reference 2: 3/4 angle side view). "
        "The generated image MUST be unmistakably the SAME individual. Do not generate a generic model. "
        "Maintain photographic 8k realism in vertical 9:16 aspect ratio."
    )

    payload = {
        "model": "google/gemini-2.5-flash-image",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": f"{system_instruction}\n\nScene to generate: {scene_prompt}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_frente}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_lado2}"}}
            ]
        }]
    }

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    with httpx.Client(verify=False, timeout=90) as client:
        r = client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if r.status_code == 200:
            d = r.json()
            imgs = d["choices"][0]["message"].get("images", [])
            if imgs:
                b64_res = imgs[0]["image_url"]["url"].split("base64,")[1]
                with open(output_image_path, "wb") as f_out:
                    f_out.write(base64.b64decode(b64_res))
                print(f"✅ Foto de cena com fidelidade facial gerada: {output_image_path} ({os.path.getsize(output_image_path)} bytes)")
                return output_image_path
        print(f"❌ Erro gerando imagem: {r.status_code} - {r.text[:300]}")
        return None


def animate_evandro_scene_to_video(image_path, motion_prompt, output_video_path, duration=3.5):
    """
    Transforma a imagem em take de vídeo com movimento cinematográfico real via LTX-Video
    """
    import gradio_client
    from gradio_client import handle_file

    print(f"\n🎬 Animando take com IA LTX-Video: {motion_prompt}...")
    client = gradio_client.Client(
        'Lightricks/ltx-video-distilled',
        token=HF_TOKEN,
        httpx_kwargs={"timeout": 300.0}
    )

    res = client.predict(
        prompt=motion_prompt,
        negative_prompt="worst quality, blurry, jittery, distorted, morphing, deformed face, unnatural movements, cartoon, static image",
        input_image_filepath=handle_file(image_path),
        input_video_filepath=None,
        height_ui=704,
        width_ui=512,
        mode="image-to-video",
        duration_ui=duration,
        ui_frames_to_use=9,
        seed_ui=42,
        randomize_seed=True,
        ui_guidance_scale=1.1,
        improve_texture_flag=True,
        api_name="/image_to_video"
    )

    video_tmp = res[0]["video"]
    shutil.copy(video_tmp, output_video_path)
    print(f"✅ Take animado de vídeo salvo: {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
    return output_video_path
