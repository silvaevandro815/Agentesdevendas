import os
import requests
import json
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")
key = os.getenv("ELEVENLABS_API_KEY")

if not key:
    print("ERRO: ELEVENLABS_API_KEY não encontrada no .env!")
    sys.exit(1)

# Voice: Adam (Dominant, Firm, social_media)
voice_id = "pNInz6obpgDQGcFmaJgB"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

texto_narracao = "A motivação te faz começar... mas é a constância que constrói o seu melhor shape. Treine pesado, cuide da sua saúde e nunca desista de você!"

payload = {
    "text": texto_narracao,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.60,
        "similarity_boost": 0.85,
        "style": 0.40,
        "use_speaker_boost": True
    }
}

headers = {
    "xi-api-key": key,
    "Content-Type": "application/json"
}

output_path = "c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/narration.mp3"

print("Gerando narração ElevenLabs fitness...")
r = requests.post(url, json=payload, headers=headers)
if r.status_code == 200:
    with open(output_path, "wb") as f:
        f.write(r.content)
    print(f"Narração gerada com sucesso em: {output_path} ({len(r.content)} bytes)")
else:
    print(f"Erro ElevenLabs: {r.status_code} - {r.text}")
