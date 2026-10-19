import os
import certifi
import shutil
import sys
import gradio_client
from gradio_client import handle_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

print("Conectando ao modelo LTX-Video de alta performance...")
client = gradio_client.Client(
    'Lightricks/ltx-video-distilled',
    httpx_kwargs={"timeout": 300.0}
)

takes = [
    {
        'idx': 1,
        'img': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take1.jpg',
        'prompt': 'Cinematic vertical shot of the muscular man curling dumbbells in the gym, slow controlled breathing, intense eyes, subtle muscular contraction, warm golden gym lighting, cinematic camera drift',
        'out': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take1_video.mp4'
    },
    {
        'idx': 2,
        'img': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take2.jpg',
        'prompt': 'Cinematic side profile of the athletic man lifting a barbell in the gym, defined jawline and muscular arms in motion, warm atmospheric lighting, subtle dust motes floating',
        'out': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take2_video.mp4'
    },
    {
        'idx': 3,
        'img': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take3.jpg',
        'prompt': 'Cinematic frontal shot of the athletic handsome coach smiling with arms crossed, slow subtle camera push-in, confident nod, modern gym background, inspiring lighting',
        'out': 'c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/take3_video.mp4'
    }
]

for t in takes:
    if os.path.exists(t['out']) and os.path.getsize(t['out']) > 20000:
        print(f"Take {t['idx']} já existe ({t['out']}), pulando...")
        continue

    print(f"\n==========================================")
    print(f"🎬 Gerando Take {t['idx']} com IA (LTX-Video)...")
    print(f"Prompt: {t['prompt']}")
    print(f"==========================================")

    res = client.predict(
        prompt=t['prompt'],
        negative_prompt='worst quality, inconsistent motion, blurry, jittery, distorted, morphing, deformed face, unnatural movements',
        input_image_filepath=handle_file(t['img']),
        input_video_filepath=None,
        height_ui=704,
        width_ui=512,
        mode='image-to-video',
        duration_ui=3.4,
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

print("\n🎉 Todos os takes de vídeo foram gerados com sucesso!")
