import os
import certifi
import shutil
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")
hf_token = os.getenv("HF_TOKEN")

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['HF_TOKEN'] = hf_token or ""

import gradio_client
from gradio_client import handle_file

print(f"🎬 Conectando ao modelo LTX-Video autenticado com HF_TOKEN...")
client = gradio_client.Client(
    'Lightricks/ltx-video-distilled',
    token=hf_token,
    httpx_kwargs={"timeout": 300.0}
)

takes = [
    {
        'idx': 1,
        'img': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take1.jpg',
        'prompt': 'The athletic muscular man is curling heavy iron dumbbells in the gym, bicep muscles flexing and contracting realistically, controlled breathing, subtle head and chest movement, cinematic gym lighting, 8k movie still in motion',
        'out': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take1_video.mp4'
    },
    {
        'idx': 2,
        'img': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take2.jpg',
        'prompt': 'Cinematic side profile of the athletic man lifting a heavy barbell in the gym, defined jawline and muscular arms in powerful motion, warm atmospheric lighting, natural movement',
        'out': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take2_video.mp4'
    },
    {
        'idx': 3,
        'img': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take3.jpg',
        'prompt': 'Cinematic frontal shot of the athletic handsome coach smiling with arms crossed, slow subtle natural breathing, confident nod into camera, modern luxury gym background, inspiring lighting',
        'out': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take3_video.mp4'
    }
]

# Copiar Take 1 que já foi gerado
take1_raw = 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take1_real_ltx.mp4'
if os.path.exists(take1_raw) and not os.path.exists(takes[0]['out']):
    shutil.copy(take1_raw, takes[0]['out'])
    print(f"Take 1 reaproveitado com sucesso de {take1_raw}!")

for t in takes:
    if os.path.exists(t['out']) and os.path.getsize(t['out']) > 50000:
        print(f"Take {t['idx']} já existe ({t['out']}), pulando...")
        continue

    print(f"\n==========================================")
    print(f"🎬 Gerando Take {t['idx']} com IA LTX-Video...")
    print(f"Prompt: {t['prompt']}")
    print(f"==========================================")

    res = client.predict(
        prompt=t['prompt'],
        negative_prompt='worst quality, inconsistent motion, blurry, jittery, distorted, morphing, deformed face, unnatural movements, cartoon, static image',
        input_image_filepath=handle_file(t['img']),
        input_video_filepath=None,
        height_ui=512,
        width_ui=704,
        mode='image-to-video',
        duration_ui=3.2,
        ui_frames_to_use=9,
        seed_ui=100 + t['idx'],
        randomize_seed=True,
        ui_guidance_scale=1.1,
        improve_texture_flag=True,
        api_name='/image_to_video'
    )

    video_tmp = res[0]['video']
    shutil.copy(video_tmp, t['out'])
    print(f"✅ Take {t['idx']} salvo com sucesso em: {t['out']} (Tamanho: {os.path.getsize(t['out'])} bytes)")

print("\n🎉 Todos os takes de vídeo com movimento cinematográfico real foram gerados com sucesso!")
