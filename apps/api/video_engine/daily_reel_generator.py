"""
=============================================================================
GERADOR DIÁRIO AUTOMATIZADO DE REELS & STORIES COM IA — MARCÃO PERSONAL
=============================================================================
- Rotação rica de 8 temas oficiais de Saúde, Nutrição, Treino e Suplementação.
- Rosto de Evandro com máxima fidelidade facial (via referências master).
- Resolução vertical nativa 1080x1920 (9:16) sem recortes borrados.
- Movimento cinematográfico contínuo com nitidez unsharp.
- Legendas dinâmicas queimadas na tela em amarelo ouro e branco (Regra 9).
- Voz oficial em português brasileiro nativo (Zero sotaque estrangeiro).
- Rastreamento anti-repetição contínuo em historico_reels.json e Supabase.
- Publicação dupla no Instagram Reels e Stories via Meta Graph API / n8n.
=============================================================================
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")

BASE_DIR = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"
TAKES_DIR = os.path.join(BASE_DIR, "takes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
HISTORICO_FILE = os.path.join(BASE_DIR, "historico_reels.json")
os.makedirs(TAKES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

FFMPEG_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
FFPROBE_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
N8N_WEBHOOK_URL = "https://n8n.marcaopersonal.com/webhook/publicar-reels-marcao"

sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))
try:
    from marcao_voice import gerar_voz_marcao
except ImportError:
    from apps.api.marcao_voice import gerar_voz_marcao

from compose_reel import assemble_master_reel_hd, get_media_duration


# =============================================================================
# CATÁLOGO DE 8 TEMAS OFICIAIS COM MÁXIMA FIDELIDADE FACIAL DO EVANDRO
# =============================================================================
TEMAS_FITNESS = [
    {
        "id": "balanca_ia",
        "titulo": "Não Se Engane Com o Peso da Balança",
        "script": "Parou de emagrecer na balança comum? Cuidado, meu parceiro! Você pode estar perdendo gordura e ganhando massa magra. A nossa balança com inteligência artificial escaneia sua composição real e te dá três meses de mentoria VIP grátis comigo no WhatsApp!",
        "image_file": os.path.join(TAKES_DIR, "evandro_balanca_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 5.1, "text": "BALANÇA COMUM NÃO MEDE RESULTADO!", "color": "white", "size": 50},
            {"start": 5.2, "end": 10.9, "text": "PERDEU GORDURA E GANHOU MÚSCULO!", "color": "gold", "size": 52},
            {"start": 11.0, "end": 17.2, "text": "MONITORE COM IA E MENTORIA VIP GRÁTIS!", "color": "white", "size": 48}
        ],
        "caption": """⚖️ O PESO NA BALANÇA NÃO TE DIZ A VERDADE!

Você sobe na balança de farmácia e acha que não teve resultado? O músculo é muito mais denso que a gordura! Você pode ter perdido 3kg de pura gordura visceral e ganhado 2kg de massa magra definida.

A Balança de Bioimpedância Xiaomi Mi Scale 2 Oficial analisa 13 biomarcadores:
📊 Percentual de Gordura Corporal e Gordura Visceral
💪 Massa Muscular Esquelética e Idade Metabólica
💧 Taxa de Hidratação Intracelular e Massa Óssea

🎁 BÔNUS EXCLUSIVO DE LANÇAMENTO:
Adquirindo a Balança Xiaomi Mi Scale 2 Oficial por apenas R$ 149,90, você ganha 3 MESES DE MENTORIA VIP INTEIRAMENTE GRÁTIS comigo no WhatsApp!

🔗 Toque no link da Bio e garanta a sua: marcaopersonal.com#balanca

#marcao #marcaopersonal #bioimpedancia #balancaxiaomi #emagrecimento #composicaocorporal #treinointeligente #saude"""
    },
    {
        "id": "creatina_mito",
        "titulo": "O Segredo da Saturação da Creatina",
        "script": "Você ainda toma creatina só nos dias de treino com medo de inchar? A creatina funciona por saturação celular contínua! Tome cinco gramas todo santo dia, beba sua água e sinta a explosão de força muscular na última repetição!",
        "image_file": os.path.join(TAKES_DIR, "evandro_creatina_mito_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 4.8, "text": "CREATINA NÃO É SÓ NO DIA DE TREINO!", "color": "white", "size": 50},
            {"start": 4.9, "end": 10.2, "text": "SATURAÇÃO CELULAR = FORÇA MÁXIMA!", "color": "gold", "size": 52},
            {"start": 10.3, "end": 16.0, "text": "5G TODO DIA POR APENAS R$ 1,68/DIA!", "color": "white", "size": 50}
        ],
        "caption": """🚨 VOCÊ TOMA CREATINA ERRADO? Descubra o mito que tá jogando seus treinos no lixo!

Muitos acham que creatina dá energia instantânea ou param no fim de semana com medo de inchaço. A verdade científica é que a creatina funciona por saturação crônica celular, aumentando a fosfocreatina para ressintetizar ATP muscular na última repetição!

🔥 Como tomar do jeito certo:
✅ 5g todo santo dia (inclusive nos dias sem treino)
✅ Junto de carboidrato ou após uma refeição principal
✅ Hidratação celular constante (35 a 45ml por kg de peso)
💰 Custo diário: apenas R$ 1,68 por dia, menos que meio cafezinho!

🔗 Garanta a Creatina Micronizada 100% Pura no link da Bio: marcaopersonal.com#loja

#marcao #marcaopersonal #creatina #musculacao #treino #biohacking #hipertrofia #suplementacao #saude"""
    },
    {
        "id": "smartwatch_cardio_strava",
        "titulo": "Treino Sem Métrica É Ilusão",
        "script": "Você treina sem monitorar seus batimentos cardíacos? O smartwatch te mostra se você tá na zona real de queima de gordura ou só cansando à toa! Controle seu ritmo, sincronize com o Strava e venha treinar comigo!",
        "image_file": os.path.join(TAKES_DIR, "evandro_smartwatch_cardio_strava_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 4.5, "text": "TREINO SEM MÉTRICA É ILUSÃO!", "color": "white", "size": 52},
            {"start": 4.6, "end": 9.8, "text": "ZONA ALVO REAL DE QUEIMA DE GORDURA!", "color": "gold", "size": 50},
            {"start": 9.9, "end": 15.5, "text": "SINCRONIZE SEUS BATIMENTOS NO STRAVA!", "color": "white", "size": 48}
        ],
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
        "id": "whey_protein_shape",
        "titulo": "Como Bater a Meta de Proteína",
        "script": "Dificuldade de bater proteína na correria do dia a dia? O whey protein é praticidade pura! Vinte e quatro gramas de proteína de altíssimo valor biológico para reconstruir a fibra muscular e acelerar seus ganhos secos!",
        "image_file": os.path.join(TAKES_DIR, "evandro_whey_protein_shape_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 4.2, "text": "DIFICULDADE DE BATER SUA PROTEÍNA?", "color": "white", "size": 50},
            {"start": 4.3, "end": 9.6, "text": "24G DE PURA PROTEÍNA BIOLÓGICA!", "color": "gold", "size": 52},
            {"start": 9.7, "end": 15.2, "text": "RECONSTRUA O MÚSCULO E SEQUE O SHAPE!", "color": "white", "size": 48}
        ],
        "caption": """🥛 NÃO CONSEGUE BATER A META DE PROTEÍNA? Descubra o poder do Whey Protein!

Se você não consome entre 1.6g a 2.2g de proteína por kg de peso corporal, você simplesmente não vai construir massa magra com consistência!

O Whey Protein oferece:
⚡ 22g a 24g de pura proteína de alto valor biológico
🧬 Perfil completo de aminoácidos essenciais e BCAA
🍫 Zero desculpa: rápido, prático e sacia a vontade de doce

🔗 Confira os wheys oficiais homologados com desconto na nossa vitrine: marcaopersonal.com#loja

#marcao #wheyprotein #hipertrofia #suplementacao #proteina #treinopesado #dietafit"""
    },
    {
        "id": "sono_gh",
        "titulo": "O Sono Anabólico e o Pico de GH",
        "script": "O treino na academia apenas destrói a fibra muscular. O shape de verdade cresce enquanto você dorme! Tenha pelo menos sete horas de sono profundo, libere seu pico de GH natural e acorde muito mais denso e recuperado!",
        "image_file": os.path.join(TAKES_DIR, "evandro_sono_gh_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 4.5, "text": "O TREINO SÓ ESTIMULA O MÚSCULO...", "color": "white", "size": 50},
            {"start": 4.6, "end": 9.8, "text": "O SHAPE CRESCE ENQUANTO VOCÊ DORME!", "color": "gold", "size": 50},
            {"start": 9.9, "end": 15.8, "text": "PICO MÁXIMO DE GH E RECUPERAÇÃO TOTAL!", "color": "white", "size": 48}
        ],
        "caption": """🌙 O SEGREDO DO CRESCIMENTO MUSCULAR: O SONO ANABÓLICO!

Não adianta treinar como um leão se você dorme como uma presa. Durante o sono profundo de ondas lentas, o seu corpo atinge o pico de liberação de GH (Hormônio do Crescimento) e síntese proteica.

Dormir menos de 6 horas aumenta o cortisol, destrói a massa magra e te deixa retido!

💤 Regras de Ouro:
1. Quarto 100% escuro e fresco
2. Zero celular 30 minutos antes de deitar
3. Hidratação celular constante com creatina

🔗 Quer o plano completo de treino e recuperação? Link na Bio: marcaopersonal.com

#marcao #marcaopersonal #sonoanabolico #hipertrofia #recuperacaomuscular #treinointenso #gh #saude"""
    },
    {
        "id": "articulacoes_omega_colageno",
        "titulo": "Blindando Joelhos e Articulações",
        "script": "Joelhos estalando no agachamento ou dor no ombro no supino? Músculo forte com junta inflamada não dura! O ômega 3 ultra concentrado e os biopeptídeos de colágeno blindam suas articulações pro treino pesado sem dor!",
        "image_file": os.path.join(TAKES_DIR, "evandro_articulacoes_omega_colageno_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 4.8, "text": "DOR NO JOELHO OU OMBRO ESTALANDO?", "color": "white", "size": 50},
            {"start": 4.9, "end": 10.0, "text": "BLINDE SUAS ARTICULAÇÕES E TENDÕES!", "color": "gold", "size": 50},
            {"start": 10.1, "end": 16.0, "text": "TREINE PESADO COM ÔMEGA 3 E COLÁGENO!", "color": "white", "size": 48}
        ],
        "caption": """🦴 ARTICULAÇÃO FRACA TRAVA O SEU CRESCIMENTO!

Não adianta colocar 100kg no supino ou 150kg no agachamento se o seu tendão ou manguito rotador estão inflamados. A dor articular é o freio de mão da hipertrofia.

Como blindar o seu corpo:
🐟 Ômega 3 Ultra Concentrado EPA/DHA: ação anti-inflamatória profunda
✨ Peptídeos Bioativos de Colágeno + Ácido Hialurônico: regeneração de cartilagem e tendão
💧 Hidratação articular constante (40ml/kg de água)

🔗 Links oficiais dos suplementos com selo de pureza: marcaopersonal.com#loja

#marcao #articulacoes #omega3 #colageno #saudearticular #prevencaodelesoes #musculacao"""
    },
    {
        "id": "roupas_compressao_performance",
        "titulo": "A Ciência da Roupa de Compressão",
        "script": "Roupa de compressão não é só visual fitness, é biomecânica pura! Melhora o retorno venoso, diminui a fadiga muscular e acaba de vez com assaduras entre as pernas no treino pesado de perna e na corrida!",
        "image_file": os.path.join(TAKES_DIR, "evandro_roupas_compressao_performance_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 4.5, "text": "ROUPA DE COMPRESSÃO É BIOMECÂNICA!", "color": "white", "size": 50},
            {"start": 4.6, "end": 9.8, "text": "MELHORA O RETORNO VENOSO E A FORÇA!", "color": "gold", "size": 50},
            {"start": 9.9, "end": 15.6, "text": "ZERO ASSADURAS NO TREINO PESADO!", "color": "white", "size": 50}
        ],
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
        "id": "constancia_shape",
        "titulo": "A Constância Cria o Shape",
        "script": "A motivação te faz começar, meu parceiro, mas é a constância que constrói o seu shape dos sonhos! Coloque sua saúde em primeiro lugar, beba sua água, treine com foco e nunca desista de você!",
        "image_file": os.path.join(TAKES_DIR, "evandro_constancia_shape_take.png"),
        "subtitles": [
            {"start": 0.3, "end": 4.8, "text": "A MOTIVAÇÃO TE FAZ COMEÇAR...", "color": "white", "size": 52},
            {"start": 4.9, "end": 9.8, "text": "MAS É A CONSTÂNCIA QUE CRIA O SHAPE!", "color": "gold", "size": 50},
            {"start": 9.9, "end": 15.2, "text": "NUNCA DESISTA DE VOCÊ!", "color": "white", "size": 54}
        ],
        "caption": """🔥 A MOTIVAÇÃO TE FAZ COMEÇAR... MAS É A CONSTÂNCIA QUE CRIA O SEU SHAPE!

Quantas vezes você esperou a segunda-feira chegar pra começar a treinar? A verdade é que a motivação dura poucos dias, mas a disciplina diária constrói o resultado que você sempre sonhou na frente do espelho.

👊 Coloque a sua saúde em primeiro lugar.
💪 Treine com foco, cuide da sua hidratação e nunca desista de você!

Quer dar o próximo passo e ter a minha consultoria VIP com a Balança de Bioimpedância com Inteligência Artificial?
🔗 Toque no link da Bio e venha fazer parte do time: marcaopersonal.com

#marcao #marcaopersonal #motivação #treino #fitness #musculacao #saude #disciplina #shape"""
    }
]


# =============================================================================
# GESTOR DE ESTADO E ROTAÇÃO ANTI-REPETIÇÃO
# =============================================================================
def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_historico(historico):
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

def selecionar_proximo_tema(tema_id_especifico=None):
    if tema_id_especifico:
        for t in TEMAS_FITNESS:
            if t["id"] == tema_id_especifico:
                return t

    historico = carregar_historico()
    ids_recentes = [h.get("tema_id") for h in historico[-4:] if h.get("tema_id")]

    # Encontra temas que não foram postados recentemente
    temas_disponiveis = [t for t in TEMAS_FITNESS if t["id"] not in ids_recentes]
    if not temas_disponiveis:
        temas_disponiveis = TEMAS_FITNESS

    # Seleciona o tema mais antigo ou que nunca foi postado
    mapa_ultimos = {}
    for h in historico:
        tid = h.get("tema_id")
        if tid:
            mapa_ultimos[tid] = h.get("published_at", "")

    temas_ordenados = sorted(temas_disponiveis, key=lambda t: mapa_ultimos.get(t["id"], ""))
    tema_escolhido = temas_ordenados[0]
    print(f"🎯 Tema selecionado por rotação anti-repetição: '{tema_escolhido['titulo']}' (ID: {tema_escolhido['id']})")
    return tema_escolhido


# =============================================================================
# GERAÇÃO DE ÁUDIO OFICIAL MARCÃO PERSONAL (VOZ BRASILEIRA NATIVA)
# =============================================================================
def sintetizar_voz_marcao(texto, out_file):
    print(f"🎙️ Gerando narração oficial Marcão em português brasileiro...")
    try:
        gerar_voz_marcao(texto, out_file)
        if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
            print(f"✅ Áudio salvo com sucesso: {out_file} ({os.path.getsize(out_file)} bytes)")
            return True
    except Exception as e:
        print(f"⚠️ Erro no motor primário ({e}), acionando ElevenLabs com voz brasileira...")

    url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    payload = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.85, "style": 0.20, "use_speaker_boost": True}
    }
    r = requests.post(url, json=payload, headers=headers, timeout=60)
    if r.status_code == 200:
        with open(out_file, "wb") as f:
            f.write(r.content)
        print(f"✅ Áudio salvo via ElevenLabs: {out_file}")
        return True
    return False


# =============================================================================
# UPLOAD NO SUPABASE STORAGE
# =============================================================================
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


# =============================================================================
# REGISTRO NO CONTENT CALENDAR SUPABASE
# =============================================================================
def registrar_no_content_calendar(tema_id, legenda, media_url):
    if not SUPABASE_KEY:
        return False
    try:
        dados = {
            "platform": "instagram_reels",
            "content_id": f"reel_{tema_id}_{int(time.time())}",
            "caption": legenda[:500],
            "media_url": media_url,
            "status": "published",
            "published_at": datetime.now().isoformat()
        }
        h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        r = requests.post(f"{SUPABASE_URL}/rest/v1/content_calendar", headers=h, json=dados, verify=False, timeout=10)
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"[REELS] Erro registrando no content_calendar: {e}")
        return False


# =============================================================================
# PUBLICADOR OFICIAL NO INSTAGRAM (REELS + STORIES)
# =============================================================================
def aguardar_container_meta(container_id):
    max_tentativas = 30
    for i in range(max_tentativas):
        time.sleep(5)
        url_status = f"https://graph.instagram.com/v21.0/{container_id}?fields=status_code,status&access_token={INSTAGRAM_ACCESS_TOKEN}"
        st_res = requests.get(url_status, verify=False, timeout=15)
        st_data = st_res.json()
        status_code = st_data.get("status_code")
        print(f"   [Processamento Meta {i+1}] Status: {status_code}")

        if status_code == "FINISHED":
            print("✅ Vídeo 100% processado e aprovado pela Meta!")
            return True
        elif status_code == "ERROR":
            print(f"❌ Erro no processamento da Meta: {st_data}")
            return False
    return False

def publicar_instagram_direto(video_url, caption, postar_stories=True):
    print("\n=======================================================")
    print("🚀 PUBLICANDO NO INSTAGRAM REELS & STORIES VIA GRAPH API")
    print("=======================================================")
    if not INSTAGRAM_ACCESS_TOKEN:
        print("❌ INSTAGRAM_ACCESS_TOKEN ausente no .env!")
        return None

    # 1. Publicar Reels
    url_container = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload_reels = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true"
    }

    r = requests.post(url_container, data=payload_reels, verify=False, timeout=35)
    if r.status_code not in [200, 201]:
        print(f"❌ Erro ao criar container Reels: {r.text}")
        return None

    container_id = r.json().get("id")
    print(f"✅ Container Reels criado: {container_id}")

    if not aguardar_container_meta(container_id):
        return None

    url_publish = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    pr = requests.post(url_publish, data={"access_token": INSTAGRAM_ACCESS_TOKEN, "creation_id": container_id}, verify=False, timeout=35)
    reel_id = pr.json().get("id") if pr.status_code in [200, 201] else None
    if reel_id:
        print(f"🎉 REELS PUBLICADO COM SUCESSO! ID: {reel_id}")

    # 2. Publicar Stories
    stories_id = None
    if postar_stories and reel_id:
        print("📸 Publicando também nos Stories do Instagram...")
        time.sleep(3)
        payload_stories = {
            "access_token": INSTAGRAM_ACCESS_TOKEN,
            "media_type": "STORIES",
            "video_url": video_url
        }
        sr = requests.post(url_container, data=payload_stories, verify=False, timeout=35)
        if sr.status_code in [200, 201]:
            s_container_id = sr.json().get("id")
            if aguardar_container_meta(s_container_id):
                spr = requests.post(url_publish, data={"access_token": INSTAGRAM_ACCESS_TOKEN, "creation_id": s_container_id}, verify=False, timeout=35)
                stories_id = spr.json().get("id") if spr.status_code in [200, 201] else None
                if stories_id:
                    print(f"🎉 STORIES PUBLICADO COM SUCESSO! ID: {stories_id}")

    return {"reel_id": reel_id, "stories_id": stories_id}


# =============================================================================
# ORQUESTRADOR PRINCIPAL DO REEL DIÁRIO
# =============================================================================
def produzir_reel_diario(tema_id=None, publicar_agora=False):
    # 1. Seleciona tema por rotação anti-repetição
    tema = selecionar_proximo_tema(tema_id)

    print("\n=======================================================")
    print(f"🌟 INICIANDO PRODUÇÃO DO REEL EM ALTA DEFINIÇÃO: {tema['titulo']}")
    print("=======================================================")

    # 2. Narração oficial
    narr_file = os.path.join(TAKES_DIR, f"narr_{tema['id']}.mp3")
    sintetizar_voz_marcao(tema["script"], narr_file)

    # 3. Composição HD 1080x1920 nativo
    out_reel = os.path.join(OUTPUT_DIR, f"reel_{tema['id']}.mp4")
    image_take = tema["image_file"]

    assemble_master_reel_hd(
        image_path=image_take,
        narration_path=narr_file,
        subtitles=tema["subtitles"],
        output_path=out_reel
    )

    # 4. Upload Supabase Storage
    remote_filename = f"reel_{tema['id']}_{int(time.time())}.mp4"
    cdn_url = upload_supabase_video(out_reel, remote_filename)

    # 5. Publicação real no Instagram se autorizado
    pub_result = None
    if publicar_agora and cdn_url:
        pub_result = publicar_instagram_direto(cdn_url, tema["caption"], postar_stories=True)

    # 6. Grava no histórico local e no Supabase para nunca repetir
    historico = carregar_historico()
    historico.append({
        "tema_id": tema["id"],
        "titulo": tema["titulo"],
        "video_url": cdn_url,
        "video_local": out_reel,
        "publicado_instagram": bool(pub_result and pub_result.get("reel_id")),
        "instagram_reel_id": pub_result.get("reel_id") if pub_result else None,
        "published_at": datetime.now().isoformat()
    })
    salvar_historico(historico)
    registrar_no_content_calendar(tema["id"], tema["caption"], cdn_url)

    print("\n🎉 PRODUÇÃO DIÁRIA EM ALTA DEFINIÇÃO CONCLUÍDA COM SUCESSO!")
    return {
        "tema": tema["titulo"],
        "tema_id": tema["id"],
        "video_local": out_reel,
        "video_url": cdn_url,
        "caption": tema["caption"],
        "pub_result": pub_result
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gerador Diário de Reels & Stories Marcão Personal HD")
    parser.add_argument("--tema", type=str, default=None, help="ID do tema específico (ex: balanca_ia, creatina_mito)")
    parser.add_argument("--publish", action="store_true", help="Publica no Instagram (Reels + Stories)")
    args = parser.parse_args()

    produzir_reel_diario(tema_id=args.tema, publicar_agora=args.publish)
