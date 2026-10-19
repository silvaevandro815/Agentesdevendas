"""
=============================================================================
GERADOR DIÁRIO AUTOMATIZADO DE REELS & STORIES COM IA — MARCÃO PERSONAL
=============================================================================
- Rotação rica de temas de Saúde, Dieta, Treino e Vida Fitness.
- Rosto com máxima fidelidade ao Diretor Evandro (frontal via lado2.jpg e perfis).
- Narração motivacional oficial com ElevenLabs (Zero OpenRouter).
- Movimentos cinematográficos corporais reais com LTX-Video.
- Sincronização inteligente sem cortes de voz (com folga e fadeout de áudio).
- Publicação dupla automatizada no Instagram REELS e STORIES via n8n.
=============================================================================
"""

import os
import sys
import json
import time
import random
import requests
import subprocess
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")

BASE_DIR = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"
TAKES_DIR = os.path.join(BASE_DIR, "takes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(TAKES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

FFMPEG_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
FFPROBE_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
N8N_WEBHOOK_URL = "https://n8n.marcaopersonal.com/webhook/publicar-reels-marcao"

# Banco de Temas Oficiais do Marcão Personal
TEMAS_FITNESS = [
    {
        "id": "constancia_shape",
        "titulo": "A Constância Cria o Shape",
        "script": "A motivação te faz começar, irmão, mas é a constância que constrói o seu shape! Treine com foco, beba sua água e nunca desista de você!",
        "text1": "A MOTIVACAO TE FAZ COMECAR...",
        "text2": "MAS E A CONSTANCIA QUE CRIA O SHAPE!",
        "text3": "NUNCA DESISTA DE VOCE!",
        "prompt1": "athletic man curling heavy iron dumbbells in luxury modern gym, intense bicep flexing, sweat glistening, cinematic rim light",
        "prompt2": "side profile of athletic man lifting heavy barbell with flawless form, muscular forearm and shoulder tension",
        "prompt3": "intense close-up of handsome athletic coach looking directly into camera with confident nod and focused expression",
        "caption": """🔥 A MOTIVAÇÃO TE FAZ COMEÇAR... MAS É A CONSTÂNCIA QUE CRIA O SEU SHAPE!

Quantas vezes você esperou a segunda-feira chegar pra começar a treinar? A verdade é que a motivação dura poucos dias, mas a disciplina diária constrói o resultado que você sempre sonhou na frente do espelho.

👊 Coloque a sua saúde em primeiro lugar.
💪 Treine com foco, cuide da sua hidratação e nunca desista de você!

Quer dar o próximo passo e ter a minha consultoria VIP com a Balança de Bioimpedância com Inteligência Artificial?
🔗 Toque no link da Bio e venha fazer parte do time: marcaopersonal.com

#marcao #marcaopersonal #motivação #treino #fitness #musculacao #saude #disciplina #shape"""
    },
    {
        "id": "creatina_mito",
        "titulo": "O Segredo da Creatina",
        "script": "Você ainda acha que creatina incha ou só toma nos dias de treino? A creatina funciona por saturação celular! Tome 5g todo santo dia e sinta a força muscular de verdade!",
        "text1": "CREATINA NAO E SO NO DIA DE TREINO!",
        "text2": "SATURACAO CELULAR = FORCA MAXIMA!",
        "text3": "5G TODO DIA COM AGUA!",
        "prompt1": "athletic man drinking cold water from shaker bottle in gym, intense lighting, defined jawline and athletic physique",
        "prompt2": "muscular coach performing heavy bench press in cinematic gym, vascular chest and shoulders in dynamic motion",
        "prompt3": "confident frontal shot of athletic coach nodding with conviction, modern high-tech gym background",
        "caption": """🚨 VOCÊ TOMA CREATINA ERRADO? Descubra o mito que tá jogando seus treinos no lixo!

Muitos acham que creatina dá energia instantânea ou param no fim de semana com medo de inchaço. A verdade científica é que a creatina funciona por saturação crônica celular, aumentando a fosfocreatina para ressintetizar ATP muscular na última repetição!

🔥 Como tomar do jeito certo:
✅ 5g todo santo dia (inclusive nos dias sem treino)
✅ Junto de carboidrato ou após uma refeição principal
✅ Hidratação celular constante (35 a 45ml por kg de peso)

Quer ter a minha consultoria VIP e saber a dosagem exata pra sua bioimpedância?
🔗 Toque no link da Bio e entre no site oficial: marcaopersonal.com

#marcao #marcaopersonal #creatina #musculacao #treino #biohacking #hipertrofia #suplementacao #saude"""
    },
    {
        "id": "balanca_ia",
        "titulo": "Não Se Engane Com o Peso da Balança",
        "script": "Parou de emagrecer na balança comum? Cuidado! Você pode estar perdendo gordura e ganhando massa magra. A nossa balança com inteligência artificial mede sua composição real com 99% de precisão!",
        "text1": "BALANCA COMUM NAO MEDE RESULTADO!",
        "text2": "PERDEU GORDURA E GANHOU MASSA MAGRA!",
        "text3": "MONITORE COM INTELIGENCIA ARTIFICIAL!",
        "prompt1": "athletic man looking at high-tech bioimpedance smart scale on gym floor, sleek modern fitness technology",
        "prompt2": "side profile of muscular athlete adjusting gym gear with intense determination, cinematic warm lighting",
        "prompt3": "handsome coach looking into camera with confident smile, pointing with confidence to your future shape",
        "caption": """⚖️ O PESO NA BALANÇA NÃO TE DIZ A VERDADE!

Você sobe na balança de farmácia e acha que não teve resultado? O músculo é muito mais denso que a gordura! Você pode ter perdido 3kg de pura gordura visceral e ganhado 2kg de massa magra.

A nossa Balança de Bioimpedância 360° com Inteligência Artificial analisa:
📊 Percentual de Gordura Corporal
💪 Massa Muscular Esquelética
💧 Taxa de Hidratação Intracelular
⚡ Metabolismo Basal em Tempo Real

📲 Conectada direto no seu celular com mentoria VIP!
🔗 Link na Bio: marcaopersonal.com

#marcao #balancadebioimpedancia #bioimpedancia #composicaocorporal #emagrecimento #musculacao #treino #saude"""
    },
    {
        "id": "sono_gh",
        "titulo": "O Sono Anabólico",
        "script": "O treino apenas destrói a fibra muscular, irmão. O shape de verdade é construído na cama! Durma pelo menos sete horas, libere o seu GH natural e acorde muito mais denso!",
        "text1": "O TREINO DESTRÓI O MUSCULO...",
        "text2": "O SHAPE CRESCE ENQUANTO VOCE DORME!",
        "text3": "PICO DE GH E RECUPERACAO TOTAL!",
        "prompt1": "athletic man sitting on gym bench catching breath after heavy set, sweat drops, cinematic atmosphere",
        "prompt2": "side profile of muscular coach stretching with focused concentration in dim moody gym lighting",
        "prompt3": "confident handsome coach crossing arms looking at camera with wise nod, luxury gym background",
        "caption": """🌙 O SEGREDO DO CRESCIMENTO MUSCULAR: O SONO ANABÓLICO!

Não adianta treinar como um leão se você dorme como uma presa. Durante o sono profundo de ondas lentas, o seu corpo atinge o pico de liberação de GH (Hormônio do Crescimento) e síntese proteica.

Dormir menos de 6 horas aumenta o cortisol, destrói a massa magra e te deixa inchado!

💤 Regras de Ouro:
1. Quarto 100% escuro e gelado
2. Zero celular 30 minutos antes de deitar
3. 5g de creatina para hidratação das fibras

🔗 Quer o plano completo de treino e recuperação? Link na Bio: marcaopersonal.com

#marcao #marcaopersonal #sonoanabolico #hipertrofia #recuperacaomuscular #treinointenso #gh #saude"""
    },
    {
        "id": "whey_protein_shape",
        "titulo": "O Poder do Whey Protein",
        "script": "Não consegue bater sua proteína diária na comida, irmão? O whey protein é praticidade pura! Vinte e quatro gramas de proteína de rápida absorção pra reconstruir a fibra muscular e acelerar seus ganhos!",
        "text1": "DIFICULDADE DE BATER PROTEÍNA?",
        "text2": "WHEY = ABSORÇÃO E RECONSTRUÇÃO!",
        "text3": "ACELERE O GANHO DE MASSA SECA!",
        "prompt1": "athletic man shaking fitness shaker cup with protein shake in modern gym, defined muscular arms",
        "prompt2": "side profile of muscular coach drinking protein shake, gym lighting highlighting vascular shoulders",
        "prompt3": "handsome confident coach looking directly at camera with motivating smile in luxury gym",
        "caption": """🥛 NÃO CONSEGUE BATER A META DE PROTEÍNA? Descubra o segredo do Whey Protein!

Se você não consome entre 1.6g a 2.2g de proteína por kg de peso corporal, você simplesmente não vai construir massa magra com consistência!

O Whey Protein oferece:
⚡ 22g a 24g de pura proteína de alto valor biológico
🧬 Perfil completo de aminoácidos essenciais e BCAA
🍫 Zero desculpa: rápido, prático e sacia a vontade de doce

🔗 Confira os wheys oficiais homologados com desconto na nossa loja: marcaopersonal.com#loja

#marcao #wheyprotein #hipertrofia #suplementacao #proteina #treinopesado #dietafit"""
    },
    {
        "id": "smartwatch_cardio_strava",
        "titulo": "Treino sem Métrica é Ilusão",
        "script": "Você treina sem monitorar sua frequência cardíaca? O smartwatch te mostra se você tá queimando gordura de verdade ou só cansando à toa! Controle seus batimentos, monitore seu sono e venha pro Strava comigo!",
        "text1": "TREINO SEM MÉTRICA É ILUSÃO!",
        "text2": "ZONA ALVO DE QUEIMA DE GORDURA!",
        "text3": "MONITORE TUDO NO SEU PULSO!",
        "prompt1": "athletic man checking modern smartwatch on wrist while resting between sets in gym",
        "prompt2": "side profile of muscular athlete running on gym treadmill with heart rate tracking monitor",
        "prompt3": "confident handsome coach pointing at his wrist smartwatch, looking directly into camera with intense focus",
        "caption": """⌚ O QUE NÃO É MEDIDO NÃO PODE SER MELHORADO!

Você passa 1 hora na esteira ou puxando ferro e não sabe quanto gastou de caloria ou se o seu coração estava na zona alvo de queima lipídica?

Com o Smartwatch integrado ao Strava e ao app do Marcão Personal:
❤️ Frequência Cardíaca em tempo real 24/7
🔥 Calorias reais queimadas por treino
🌙 Monitoramento cirúrgico de Sono Profundo e REM
🏃 GPS de alta precisão para corrida e pedal

🔗 Adquira o seu no link oficial da Bio com preço especial: marcaopersonal.com#loja

#marcao #smartwatch #strava #cardio #frequenciacardiaca #treinointeligente #tecnologiafitness"""
    },
    {
        "id": "roupas_compressao_performance",
        "titulo": "A Ciência da Roupa de Compressão",
        "script": "Roupa de compressão não é só estilo maromba, é ciência pura! Melhora o retorno venoso, reduz a fadiga muscular e acaba de vez com assaduras entre as pernas no treino pesado!",
        "text1": "ROUPA DE COMPRESSÃO É CIÊNCIA!",
        "text2": "MELHORA O RETORNO VENOSO!",
        "text3": "ZERO ASSADURA E MAIS FORÇA!",
        "prompt1": "athletic man wearing tight black compression thermal gym shirt, muscular torso and chest definition",
        "prompt2": "muscular coach squatting with heavy barbell wearing compression shorts, perfect biomechanics",
        "prompt3": "confident handsome coach adjusting his compression gear, nodding with determination at camera",
        "caption": """🥋 POR QUE ATLETAS DE ELITE TREINAM COM ROUPA DE COMPRESSÃO?

A compressão graduada melhora o fluxo sanguíneo muscular, diminui a vibração das fibras nas repetições pesadas e acelera a remoção do ácido lático!

Benefícios imediatos:
🛡️ Proteção UV50+ e regulação térmica Dry Fit
🩸 Aumento do retorno venoso e menos fadiga muscular
🦵 Zero atrito ou assaduras nos treinos de perna e corrida

🔗 Garanta suas peças térmicas de compressão oficiais na nossa vitrine: marcaopersonal.com#loja

#marcao #roupafitness #compressao #dryfit #treinodepernas #musculacao #performance"""
    },
    {
        "id": "articulacoes_omega_colageno",
        "titulo": "Blindando Joelhos e Articulações",
        "script": "Joelhos estalando ou dor no ombro no supino? Músculo forte com articulação inflamada não vai longe! Ômega 3 ultra concentrado e colágeno bioativo blindam suas juntas pro treino pesado!",
        "text1": "JOELHOS OU OMBROS DOENDO?",
        "text2": "BLINDE SUAS ARTICULAÇÕES!",
        "text3": "TREINE PESADO SEM DOR!",
        "prompt1": "athletic man rubbing shoulder joint gently after heavy bench press in gym, intense atmosphere",
        "prompt2": "muscular coach stretching knees and hips with flawless mobility form in modern gym",
        "prompt3": "handsome coach looking into camera with confident reassuring smile, pointing forward with energy",
        "caption": """🦴 ARTICULAÇÃO FRACA TRAVA O SEU CRESCIMENTO!

Não adianta colocar 100kg no supino ou 150kg no agachamento se o seu tendão ou manguito rotador estão inflamados. A dor articular é o freio de mão da hipertrofia.

Como blindar o seu corpo:
🐟 Ômega 3 Ultra Concentrado EPA/DHA: ação anti-inflamatória profunda
✨ Peptídeos Bioativos de Colágeno + Ácido Hialurônico: regeneração de cartilagem e tendão
💧 Hidratação articular constante (40ml/kg de água)

🔗 Links oficiais dos suplementos com selo de pureza: marcaopersonal.com#loja

#marcao #articulacoes #omega3 #colageno #saudearticular #prevençãodelesões #musculacao"""
    }
]

def gerar_audio_elevenlabs(texto, out_file):
    print(f"🎙️ Gerando áudio ElevenLabs com voz oficial Adam...")
    url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.85,
            "style": 0.20,
            "use_speaker_boost": True
        }
    }
    r = requests.post(url, json=payload, headers=headers, timeout=60)
    if r.status_code == 200:
        with open(out_file, "wb") as f:
            f.write(r.content)
        print(f"✅ Áudio salvo com sucesso: {out_file} ({len(r.content)} bytes)")
        return True
    else:
        print(f"❌ Erro ElevenLabs ({r.status_code}): {r.text}")
        return False

def get_audio_duration(file_path):
    cmd = [
        FFPROBE_EXE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def upload_supabase_video(local_path, remote_name):
    print(f"☁️ Enviando vídeo para Supabase Storage: {remote_name}...")
    url_upload = f"{SUPABASE_URL}/storage/v1/object/creativos/videos/{remote_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4",
        "x-upsert": "true"
    }
    with open(local_path, "rb") as f:
        data = f.read()

    r = requests.post(url_upload, headers=headers, data=data, timeout=90, verify=False)
    if r.status_code in [200, 201]:
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/creativos/videos/{remote_name}"
        print(f"✅ Vídeo publicado na CDN: {public_url}")
        return public_url
    else:
        print(f"❌ Erro upload Supabase ({r.status_code}): {r.text}")
        return None

def disparar_n8n_publicacao(video_url, caption, postar_stories=True):
    print(f"\n🚀 Disparando publicação automática via n8n (Reels + Stories)...")
    payload = {
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": True,
        "postar_stories": postar_stories
    }
    try:
        r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=120, verify=False)
        print(f"Status n8n: {r.status_code} | Resposta: {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao chamar n8n: {e}")
        return False

def produzir_reel_diario(tema_id=None, publicar_agora=False):
    # 1. Seleciona tema
    tema = None
    if tema_id:
        for t in TEMAS_FITNESS:
            if t["id"] == tema_id:
                tema = t
                break
    if not tema:
        tema = random.choice(TEMAS_FITNESS)

    print("\n=======================================================")
    print(f"🌟 INICIANDO PRODUÇÃO DO REEL DIÁRIO: {tema['titulo']}")
    print("=======================================================")

    # 2. Narração ElevenLabs
    narr_file = os.path.join(TAKES_DIR, f"narr_{tema['id']}.mp3")
    gerar_audio_elevenlabs(tema["script"], narr_file)

    vox_dur = get_audio_duration(narr_file)
    print(f"🎤 Duração exata da voz: {vox_dur:.2f} segundos")

    # 3. Composição de vídeo inteligente (usa os takes cinematográficos já prontos ou novos)
    # Importa módulo de montagem inteligente
    from compose_reel import assemble_master_reel
    take1 = os.path.join(TAKES_DIR, "take1_video.mp4")
    take2 = os.path.join(TAKES_DIR, "take2_video.mp4")
    take3 = os.path.join(TAKES_DIR, "take3_video.mp4")
    amb = os.path.join(TAKES_DIR, "ambience.wav")

    out_reel = os.path.join(OUTPUT_DIR, f"reel_{tema['id']}.mp4")
    assemble_master_reel(
        take1, take2, take3,
        narr_file, amb,
        text1=tema["text1"],
        text2=tema["text2"],
        text3=tema["text3"],
        output_path=out_reel
    )

    # 4. Upload Supabase
    cdn_url = upload_supabase_video(out_reel, f"reel_{tema['id']}.mp4")

    # 5. Publicação via n8n (se autorizado)
    if publicar_agora and cdn_url:
        disparar_n8n_publicacao(cdn_url, tema["caption"], postar_stories=True)

    print("\n🎉 PRODUÇÃO DIÁRIA CONCLUÍDA COM SUCESSO!")
    return {
        "tema": tema["titulo"],
        "video_local": out_reel,
        "video_url": cdn_url,
        "caption": tema["caption"]
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gerador Diário de Reels & Stories Marcão Personal")
    parser.add_argument("--tema", type=str, default=None, help="ID do tema específico")
    parser.add_argument("--publish", action="store_true", help="Publica no Instagram (Reels + Stories) via n8n")
    args = parser.parse_args()

    produzir_reel_diario(tema_id=args.tema, publicar_agora=args.publish)
