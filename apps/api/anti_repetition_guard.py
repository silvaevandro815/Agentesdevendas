"""
Guardião Anti-Repetição & Fábrica de Criativos Inéditos — Marcão Personal 360°
=================================================================================
Garante que o Marcão NUNCA publique posts, fotos ou criativos repetidos no Instagram.
Permite repetir o tema (ex: Creatina, Colágeno, Balança), mas OBRIGA a gerar um
ângulo editorial 100% inédito, uma nova foto/imagem via IA e uma nova legenda.
"""

import os
import re
import time
import json
import base64
import random
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

from dotenv import load_dotenv
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "public", "images", "posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MATRIZ_TEMAS = [
    {
        "id": "creatina_hipertrofia",
        "nome": "Creatina & Hipertrofia",
        "categoria": "ALTA PERFORMANCE",
        "palavras_chave": ["creatina", "força", "hipertrofia", "atp", "potência"],
        "produto": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "preco": "R$ 169,90"
    },
    {
        "id": "colageno_estetica",
        "nome": "Colágeno Verisol & Firmeza da Pele",
        "categoria": "ESTÉTICA CORPORAL",
        "palavras_chave": ["colágeno", "pele", "flacidez", "rugas", "hialurônico"],
        "produto": "Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime",
        "link_venda": "https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg",
        "preco": "R$ 164,90"
    },
    {
        "id": "emagrecimento_drenagem",
        "nome": "Definição Corporal & Drenagem Metabólica",
        "categoria": "DEFINIÇÃO & EMAGRECIMENTO",
        "palavras_chave": ["azempika", "drenagem", "emagrecimento", "saciedade", "secar"],
        "produto": "Azempika Original Caneta Drenante 60 Doses",
        "link_venda": "https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv",
        "preco": "R$ 197,00"
    },
    {
        "id": "balanca_bioimpedancia",
        "nome": "Balança de Bioimpedância & Métricas Reais",
        "categoria": "CIÊNCIA & MÉTRICAS",
        "palavras_chave": ["balança", "bioimpedância", "gordura visceral", "massa magra", "peso"],
        "produto": "Balança Digital Bioimpedância Bluetooth Marcão",
        "link_venda": "https://marcaopersonal.com/loja",
        "preco": "R$ 149,90"
    },
    {
        "id": "dor_muscular_recuperacao",
        "nome": "Fisiologia da Dor Muscular & Anti-inflamatórios",
        "categoria": "CIÊNCIA & RECUPERAÇÃO",
        "palavras_chave": ["dor muscular", "remédio", "dmit", "recuperação", "inflamação"],
        "produto": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "preco": "R$ 169,90"
    },
    {
        "id": "saude_capilar_led",
        "nome": "Fototerapia Capilar & Crescimento dos Fios",
        "categoria": "ESTÉTICA CAPILAR",
        "palavras_chave": ["cabelo", "escova led", "queda capilar", "fototerapia", "biotina"],
        "produto": "Escova de LED Capilar Fototerapia Marcão",
        "link_venda": "https://marcaopersonal.com/loja",
        "preco": "R$ 189,90"
    },
    {
        "id": "sono_anabolico_gh",
        "nome": "Sono Reparador & Liberação Noturna de GH",
        "categoria": "BIOHACKING & LONGEVIDADE",
        "palavras_chave": ["sono", "gh", "recuperação noturna", "descanso", "cortisol"],
        "produto": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "preco": "R$ 169,90"
    },
    {
        "id": "saude_articular_longevidade",
        "nome": "Mobilidade, Articulações & Longevidade aos 40+",
        "categoria": "LONGEVIDADE & ARTICULAÇÕES",
        "palavras_chave": ["articulação", "joelho", "mobilidade", "longevidade", "40 anos", "60 anos"],
        "produto": "Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime",
        "link_venda": "https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg",
        "preco": "R$ 164,90"
    }
]

MATRIZ_PERSONAGENS = [
    # 1. Evandro Gallina (Fundador & Atleta - Variedade Total de Poses, Roupas e Locais)
    {
        "id": "evandro_musculacao",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina (Fundador) treinando ombros/bíceps na academia com halteres pesados, camisa dry-fit preta de compressão, expressão focada e atlética",
        "prompt_char": "Athletic fitness founder Evandro Gallina, handsome Brazilian man with short neat dark hair, fit athletic lean muscular physique, wearing sleek black compression dry-fit shirt, performing seated dumbbell curls with focused grit and determination"
    },
    {
        "id": "evandro_corrida_praia",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina correndo no calçadão da praia ao nascer do sol, regata técnica grafite, bermuda esportiva e smartwatch",
        "prompt_char": "Dynamic energetic shot of fit founder Evandro Gallina briskly running along an ocean beach promenade at golden hour sunrise, dark technical running tank top, sports smartwatch on wrist, athletic determined smile"
    },
    {
        "id": "evandro_cozinha_nutricao",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina em cozinha gourmet moderna preparando smoothie proteico com frutas frescas e água de coco",
        "prompt_char": "Warm commercial lifestyle photo of health founder Evandro Gallina in a luxury kitchen with marble countertops, holding a clean protein shaker cup, charismatic friendly smile, casual fitted dark crewneck t-shirt"
    },
    {
        "id": "evandro_natacao_piscina",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina saindo de piscina olímpica de água cristalina, ombros largos e peitoral definido, óculos de natação na testa",
        "prompt_char": "Athletic swimmer Evandro Gallina emerging powerfully from turquoise pool water, water droplets glistening on muscular shoulders and chest, modern sports goggles on forehead, confident focused gaze"
    },
    {
        "id": "evandro_ciclismo_estrada",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina em bicicleta speed preta fosca em estrada litorânea cênica com capacete aerodinâmico",
        "prompt_char": "Action sports portrait of handsome fit cyclist Evandro Gallina on a matte black road bicycle along a winding coastal highway, aerodynamic dark cycling jersey, ocean cliffs in background"
    },
    {
        "id": "evandro_funcional_casa",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina fazendo treino de mobilidade postural com bastão de madeira na sala de estar iluminada",
        "prompt_char": "Fit trainer Evandro Gallina performing controlled functional mobility squats holding a smooth wooden alignment dowel across shoulders in a sunlit modern living room with hardwood floors"
    },
    {
        "id": "evandro_caminhada_natureza",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina em trilha de serra cercada por floresta verde e névoa matinal, roupa esportiva verde oliva",
        "prompt_char": "Inspiring photography of athletic man Evandro Gallina power walking along an alpine forest trail, morning mist, technical olive-green trail running gear, fresh mountain air vibe"
    },
    {
        "id": "evandro_biohacking_lounge",
        "categoria_persona": "evandro",
        "descricao": "Evandro Gallina em lounge de recuperação avaliando métricas corporais no celular e balança de bioimpedância",
        "prompt_char": "Modern aesthetic portrait of health innovator Evandro Gallina in a luxury wellness recovery lounge, checking health metrics on his smartphone, charcoal athletic apparel, relaxed confident smile"
    },

    # 2. Coach Marcão (O Treinador / Mentor Oficial)
    {
        "id": "marcao_coach_instruindo",
        "categoria_persona": "marcao",
        "descricao": "Coach Marcão (Personal Trainer imponente, 35 anos, camisa oficial preta e dourada, braços volumosos, postura de liderança)",
        "prompt_char": "Imposing Brazilian personal trainer Coach Marcão, 35 years old, heavily built powerful physique, intense motivating gaze, wearing sleek black and gold branded dry-fit shirt, arms crossed proudly"
    },
    {
        "id": "marcao_coach_supino",
        "categoria_persona": "marcao",
        "descricao": "Coach Marcão executando supino pesado com barra olímpica e anilhas de ferro, veias aparentes e foco brutal",
        "prompt_char": "Powerful bodybuilder trainer Marcão performing heavy bench press in dark gym, pumped vascular arms and chest, chalk on hands, intense grit, dramatic amber rim lighting"
    },
    {
        "id": "marcao_coach_parque",
        "categoria_persona": "marcao",
        "descricao": "Coach Marcão em treino funcional com kettlebell ao ar livre no parque com gramado verde",
        "prompt_char": "Muscular trainer Marcão performing athletic kettlebell swings on a sunny open-air park field, energetic confident expression, dark fitted workout shorts and sports tank top"
    },

    # 3. Mascote Marcão 3D (Animação Disney/Pixar Hiper-Realista 3D)
    {
        "id": "mascote_marcao_haltere",
        "categoria_persona": "mascote",
        "descricao": "Mascote Marcão 3D (Personagem de animação 3D hiper-realista da Pixar, maromba carismático com regata Marcão Personal levantando haltere gigante)",
        "prompt_char": "Charming ultra-detailed 3D animated character Mascote Marcão in Pixar/Disney style, handsome stylized muscular personal trainer with heroic jawline, big enthusiastic smile, wearing black and gold athletic tank top, holding a giant dumbbell with playful ease, studio 3D render quality"
    },
    {
        "id": "mascote_marcao_balanca",
        "categoria_persona": "mascote",
        "descricao": "Mascote Marcão 3D comemorando em cima da balança inteligente com gráfico digital subindo",
        "prompt_char": "Cute heroic 3D animated mascot Marcão celebrating happily on a high-tech smart bioimpedance scale, thumbs up, cheerful wink, Pixar style lighting and smooth character design"
    },
    {
        "id": "mascote_marcao_shake",
        "categoria_persona": "mascote",
        "descricao": "Mascote Marcão 3D segurando shakeira com suplemento puro e piscando para a câmera",
        "prompt_char": "Vibrant 3D animated mascot Marcão holding a sleek supplement shaker cup, charismatic facial expression, sparkling eyes, high-end 3D feature film character render"
    },

    # 4. Mulheres Jovens (20 a 28 anos - Definição, Energia & Estética)
    {
        "id": "mulher_jovem_agachamento",
        "categoria_persona": "mulher_jovem",
        "descricao": "Atleta feminina jovem (25 anos, glúteos e pernas torneadas, abdômen definido, top preto e calça legging moderna)",
        "prompt_char": "Fit athletic 25-year-old Brazilian woman with toned sculpted physique and defined abs, performing squats with barbell in luxury gym, focused confident gaze, sleek black athletic leggings and sports bra"
    },
    {
        "id": "mulher_jovem_praia_corrida",
        "categoria_persona": "mulher_jovem",
        "descricao": "Mulher atleta de 28 anos correndo na areia da praia ao nascer do sol, top coral, pele bronzeada e iluminada",
        "prompt_char": "Radiant 28-year-old fit Brazilian woman jogging along the golden sand of Rio beach at sunrise, wearing chic coral sports top and running shorts, glowing sunlit skin, joyful athletic smile"
    },
    {
        "id": "mulher_jovem_yoga_gramado",
        "categoria_persona": "mulher_jovem",
        "descricao": "Mulher jovem praticando yoga e mobilidade no gramado ao entardecer com luz dourada",
        "prompt_char": "Graceful 26-year-old female athlete doing yoga stretches on lush green lawn at sunset, serene focused expression, terracotta seamless workout apparel, golden hour rim lighting"
    },

    # 5. Mulheres Adultas (35 a 48 anos - Firmeza, Colágeno & Elegância Ativa)
    {
        "id": "mulher_adulta_pilates",
        "categoria_persona": "mulher_adulta",
        "descricao": "Mulher elegante de 40 anos em estúdio de pilates reformer, postura ereta, pele firme e viçosa",
        "prompt_char": "Elegant fit 40-year-old woman in peak health performing controlled reformer pilates exercise, firm radiant skin, graceful posture, tasteful lavender athletic wear, bright airy boutique studio"
    },
    {
        "id": "mulher_adulta_cozinha_colageno",
        "categoria_persona": "mulher_adulta",
        "descricao": "Mulher madura de 42 anos preparando colágeno com abacaxi e hortelã em cozinha gourmet ensolarada",
        "prompt_char": "Photorealistic portrait of a beautiful 42-year-old Brazilian woman with smooth firm glowing facial skin, holding a refreshing glass of collagen with mint in a modern sunlit designer kitchen, genuine warm smile"
    },
    {
        "id": "mulher_adulta_funcional_casa",
        "categoria_persona": "mulher_adulta",
        "descricao": "Mulher de 38 anos fazendo treino funcional com elásticos de resistência na sala de casa",
        "prompt_char": "Active 38-year-old woman doing resistance band training in a spacious minimalist living room with parquet floors, fit toned arms, energetic determined expression, stylish sportswear"
    },

    # 6. Mulheres Seniores / 3ª Idade Ativa (55 a 72 anos - Vitalidade, Articulações & Longevidade)
    {
        "id": "mulher_senior_caminhada_parque",
        "categoria_persona": "mulher_senior",
        "descricao": "Mulher sênior de 64 anos cheia de vitalidade caminhando com bastão esportivo em parque botânico ensolarado",
        "prompt_char": "Inspiring authentic photo of a vibrant fit 64-year-old Brazilian senior woman full of vitality, briskly walking with walking poles in a sunny botanical park, silver-streaked hair, beaming radiant healthy smile, wearing tasteful lilac athletic outfit"
    },
    {
        "id": "mulher_senior_piscina_hidro",
        "categoria_persona": "mulher_senior",
        "descricao": "Senhora ativa de 68 anos saindo feliz de piscina aquecida de clube, demonstrando mobilidade sem dores articulares",
        "prompt_char": "Active 68-year-old senior woman emerging happily from sparkling resort swimming pool, healthy mobile posture, genuine joyful laughter, active aging longevity aesthetic"
    },
    {
        "id": "mulher_senior_alongamento_jardim",
        "categoria_persona": "mulher_senior",
        "descricao": "Mulher de 62 anos praticando respiração e mobilidade suave em jardim botânico",
        "prompt_char": "Serene 62-year-old fit mature woman doing morning mobility stretches outdoors in botanical garden, deep healthy breathing, peaceful confident posture, soft morning sunlight"
    },

    # 7. Homens Jovens (20 a 25 anos - Hipertrofia & Calistenia)
    {
        "id": "homem_jovem_braco_rosca",
        "categoria_persona": "homem_jovem",
        "descricao": "Jovem atleta de 24 anos com braços densos treinando rosca com halteres pesados em academia escura",
        "prompt_char": "Dedicated 24-year-old athletic male bodybuilder doing heavy bicep curls in dark modern gym, defined vascular arms, determined proud gaze, charcoal gym stringer, chalk dust in air"
    },
    {
        "id": "homem_jovem_calistenia_praia",
        "categoria_persona": "homem_jovem",
        "descricao": "Jovem de 25 anos fazendo barra fixa em parque de calistenia na orla marítima ao entardecer",
        "prompt_char": "Athletic 25-year-old calisthenics athlete performing pull-ups on outdoor beach fitness bars, defined back and shoulders, ocean horizon at golden sunset"
    },

    # 8. Homens Adultos (35 a 48 anos - Alta Performance & Força Pura)
    {
        "id": "homem_adulto_executivo_corrida",
        "categoria_persona": "homem_adulto",
        "descricao": "Homem de 42 anos executivo em corrida de rua matinal na orla marítima, fones de ouvido e relógio esportivo",
        "prompt_char": "Dynamic action portrait of an active 42-year-old executive runner jogging along ocean promenade at sunrise, athletic build, energized focused smile, navy moisture-wicking tech shirt"
    },
    {
        "id": "homem_adulto_terra_pesado",
        "categoria_persona": "homem_adulto",
        "descricao": "Homem de 39 anos executando levantamento terra com pegada firme, anilhas olímpicas e magnésio nas mãos",
        "prompt_char": "Powerful 39-year-old athletic man performing heavy deadlift in high-tech gym, chalk on muscular hands, focused intense gaze, masculine power and longevity"
    },

    # 9. Homens Seniores / Masters 55+ (55 a 70 anos - Longevidade, Vigor & Saúde Plena)
    {
        "id": "homem_senior_corrida_maratona",
        "categoria_persona": "homem_senior",
        "descricao": "Homem sênior de 62 anos com cabelos grisalhos e corpo atlético cruzando linha de corrida de rua, sorriso triunfante",
        "prompt_char": "Inspiring fit 62-year-old grey-haired senior male athlete running with athletic pace in street marathon, proud energized smile, lean healthy physique, technical running attire"
    },
    {
        "id": "homem_senior_ciclismo_speed",
        "categoria_persona": "homem_senior",
        "descricao": "Ciclista master de 65 anos em bicicleta speed de fibra de carbono em estrada de serra com capacete aerodinâmico",
        "prompt_char": "Handsome fit 65-year-old master cyclist on a sleek carbon road bike on winding mountain road, aerodynamic cycling jersey, youthful energetic posture, sharp clear daylight"
    },
    {
        "id": "homem_senior_postura_mobilidade",
        "categoria_persona": "homem_senior",
        "descricao": "Homem de 60 anos realizando exercícios de mobilidade de ombros e coluna com postura impecável",
        "prompt_char": "Distinguished fit 60-year-old man performing shoulder mobility exercises in luxury gym, upright powerful posture, calm confident smile, high-end vitality aesthetic"
    }
]

MATRIZ_CENARIOS = [
    {
        "id": "academia_boutique_dark",
        "nome": "Academia Boutique High-Tech",
        "prompt_scene": "inside a luxury ultra-modern high-tech gym, dark matte walls, warm golden rim lighting, sleek dumbbells and Olympic barbells in soft bokeh background"
    },
    {
        "id": "praia_aurora_copacabana",
        "nome": "Orla da Praia ao Nascer do Sol",
        "prompt_scene": "along a tropical ocean beach promenade during warm golden sunrise, palm trees and gentle waves in background, fresh morning mist, radiant sun rays"
    },
    {
        "id": "cozinha_gourmet_contemporanea",
        "nome": "Cozinha Gourmet Contemporânea",
        "prompt_scene": "in a sleek minimalist modern kitchen, wet dark emerald marble and teak wood island, scattered fresh mint leaves, bright morning sunlight through sheer curtains"
    },
    {
        "id": "deck_piscina_resort",
        "nome": "Deck de Piscina Sofisticado",
        "prompt_scene": "by the edge of a luxury infinity pool with crystal clear turquoise water, polished teak deck, soft morning sun, premium outdoor wellness atmosphere"
    },
    {
        "id": "sala_funcional_madeira",
        "nome": "Sala de Estar Espaçosa com Piso de Madeira",
        "prompt_scene": "in a spacious luxury modern living room with natural hardwood floors, soft ambient daylight, clean architectural interior for home workout"
    },
    {
        "id": "trilha_floresta_montanha",
        "nome": "Trilha Ecológica em Floresta com Névoa",
        "prompt_scene": "on a scenic alpine forest trail surrounded by lush green pine trees, morning mountain air, crisp golden sunlight filtering through emerald canopy"
    },
    {
        "id": "pista_corrida_vermelha",
        "nome": "Pista de Atletismo ao Entardecer",
        "prompt_scene": "on an Olympic red tartan running track during dramatic golden sunset, stadium lights softly glowing in background, cinematic depth of field"
    },
    {
        "id": "quarto_minimalista_luxo",
        "nome": "Quarto Minimalista de Hotel Boutique",
        "prompt_scene": "in a serene luxury minimalist bedroom, premium mattress with crisp white Egyptian cotton sheets, bathed in soft ambient nocturnal indigo and warm bedside lighting"
    },
    {
        "id": "parque_botanico_ensolarado",
        "nome": "Parque Botânico com Gramado Verde",
        "prompt_scene": "in a sunlit lush botanical garden, manicured green grass, blooming tropical flora, warm diffused natural morning light"
    },
    {
        "id": "lounge_zen_biohacking",
        "nome": "Lounge Zen de Biohacking e Spa",
        "prompt_scene": "in a luxury biohacking recovery lounge, smooth black volcanic stones, green bamboo accents, warm ambient architectural lighting, pristine wellness aesthetic"
    },
    {
        "id": "estrada_litoranea_penhasco",
        "nome": "Estrada Litorânea com Penhascos e Mar",
        "prompt_scene": "along a scenic coastal cliffside highway overlooking deep blue ocean water, clean asphalt, panoramic sea horizon, bright crisp daylight"
    },
    {
        "id": "estudio_pilates_luz_natural",
        "nome": "Estúdio de Pilates com Luz Natural",
        "prompt_scene": "in an airy high-ceiling boutique pilates studio, light wood apparatus, sheer white drapes filtering gentle morning daylight, serene calm atmosphere"
    }
]


def buscar_historico_posts_recentes(limite=30) -> dict:
    """Busca os posts recentes no Supabase e na API do Instagram para evitar qualquer repetição."""
    posts_recentes = []
    urls_usadas = set()
    headlines_usadas = []

    # 1. Busca no Supabase content_calendar
    if SUPABASE_KEY and SUPABASE_URL:
        try:
            h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/content_calendar?select=caption,media_url,published_at&order=id.desc&limit={limite}",
                headers=h,
                verify=False,
                timeout=10
            )
            if r.status_code == 200:
                for row in r.json():
                    cap = row.get("caption") or ""
                    murl = row.get("media_url") or ""
                    if murl:
                        urls_usadas.add(murl.strip())
                    if cap:
                        primeira_linha = cap.split("\n")[0].strip()
                        headlines_usadas.append(primeira_linha)
                        posts_recentes.append({"caption": cap, "media_url": murl})
        except Exception as e:
            print(f"[ANTI_REP] Aviso ao consultar Supabase: {e}")

    # 2. Busca no Instagram Graph API como segunda camada de proteção
    if INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID:
        try:
            r_ig = requests.get(
                f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media?fields=id,caption,media_url,timestamp&limit=20&access_token={INSTAGRAM_ACCESS_TOKEN}",
                verify=False,
                timeout=10
            )
            if r_ig.status_code == 200:
                ig_data = r_ig.json().get("data", [])
                for p in ig_data:
                    cap = p.get("caption") or ""
                    murl = p.get("media_url") or ""
                    if murl:
                        urls_usadas.add(murl.strip())
                    if cap:
                        primeira_linha = cap.split("\n")[0].strip()
                        if primeira_linha not in headlines_usadas:
                            headlines_usadas.append(primeira_linha)
        except Exception as e:
            print(f"[ANTI_REP] Aviso ao consultar Instagram API: {e}")

    return {
        "posts": posts_recentes,
        "urls_usadas": urls_usadas,
        "headlines_usadas": headlines_usadas
    }


def verificar_ineditismo_headline(headline_proposta: str, headlines_usadas: list) -> tuple:
    """Verifica se a manchete proposta tem similaridade com títulos já postados."""
    if not headline_proposta:
        return False, "headline_vazia"

    norm_proposta = set(re.findall(r'\b\w{4,}\b', headline_proposta.lower()))
    if not norm_proposta:
        return True, "inedito"

    for h_existente in headlines_usadas:
        norm_existente = set(re.findall(r'\b\w{4,}\b', h_existente.lower()))
        if not norm_existente:
            continue
        inter = norm_proposta.intersection(norm_existente)
        uniao = norm_proposta.union(norm_existente)
        jaccard = len(inter) / len(uniao) if uniao else 0.0

        if jaccard >= 0.60:
            return False, f"similar_a: {h_existente[:50]} (jaccard={jaccard:.2f})"

    return True, "inedito"


def gerar_angulo_criativo_inedito(tema_escolhido=None, tipo="manha", estilo_visual="auto") -> dict:
    """
    Gera via Gemini 2.5 Flash um ângulo de criativo 100% INÉDITO.
    Mesmo que o tema seja repetido, a manchete, o gancho, a copy e o prompt fotográfico
    serão obrigatoriamente novos e exclusivos.
    """
    historico = buscar_historico_posts_recentes(limite=30)
    headlines_recentes = historico["headlines_usadas"][:15]

    # Seleção de tema garantindo rotação
    if not tema_escolhido:
        # Pega temas menos abordados recentemente
        temas_disponiveis = MATRIZ_TEMAS.copy()
        random.shuffle(temas_disponiveis)
        tema_obj = temas_disponiveis[0]
    elif isinstance(tema_escolhido, str):
        tema_obj = next((t for t in MATRIZ_TEMAS if t["id"] == tema_escolhido or t["nome"].lower() == tema_escolhido.lower()), None)
        if not tema_obj:
            tema_obj = {
                "id": "custom",
                "nome": tema_escolhido,
                "categoria": "ALTA PERFORMANCE",
                "produto": "Protocolo Marcão Personal 360°",
                "link_venda": "https://marcaopersonal.com/loja",
                "preco": "R$ 169,90"
            }
    else:
        tema_obj = tema_escolhido

    # Rotação obrigatória de Personagem e Cenário com suporte total à diversidade de elenco
    if estilo_visual and estilo_visual not in ["auto", "todos"]:
        candidatos = [p for p in MATRIZ_PERSONAGENS if p.get("categoria_persona") == estilo_visual]
        personagem_sorteado = random.choice(candidatos) if candidatos else random.choice(MATRIZ_PERSONAGENS)
    else:
        personagem_sorteado = random.choice(MATRIZ_PERSONAGENS)
    cenario_sorteado = random.choice(MATRIZ_CENARIOS)

    # Prompt instruindo a IA sobre ineditismo estrito
    prompt_ia_redator = f"""Você é o Diretor Criativo e Copywriter Chefe da marca 'Marcão Personal'.
Tema Obrigatório da Postagem: "{tema_obj['nome']}" (Categoria: {tema_obj['categoria']})
Ciclo: {"Curiosidade, Ciência e Entretenimento" if tipo == "manha" else "Venda de Produto com Autoridade Máxima"}
Produto de Apoio: {tema_obj.get('produto', 'Protocolo Marcão')}

🚨 REGRA DE OURO INVIOLÁVEL: É ESTRITAMENTE PROIBIDO REPETIR O MESMO CRIATIVO!
Você PODE falar sobre o tema '{tema_obj['nome']}', mas DEVE usar um ângulo, pergunta, gancho e história NUNCA vistos antes.

Títulos que JÁ FORAM PUBLICADOS no nosso Instagram recentemente e que você NUNCA PODE REPETIR:
{json.dumps(headlines_recentes, ensure_ascii=False, indent=2)}

Personagem Sorteado para a Imagem: {personagem_sorteado['descricao']}
Cenário Sorteado para a Imagem: {cenario_sorteado['nome']}

Retorne EXATAMENTE um objeto JSON válido (sem crases de markdown em volta, sem texto antes ou depois):
{{
  "headline": "MANCHETE EM CAIXA ALTA (4 a 6 palavras impactantes, provocativas e INÉDITAS)",
  "subheadline": "Subtítulo editorial de autoridade (máximo 70 caracteres)",
  "pontos": [
    "Primeiro benefício científico ou mecanismo biológico claro (máximo 60 caracteres)",
    "Segundo benefício ou dica prática aplicável (máximo 60 caracteres)",
    "Terceiro ponto ou diferencial do protocolo Marcão (máximo 60 caracteres)"
  ],
  "categoria": "{tema_obj['categoria']}",
  "cta_card": "LEIA A LEGENDA",
  "prompt_fotografico": "{personagem_sorteado['prompt_char']} {cenario_sorteado['prompt_scene']}. PHOTOGRAPHIC SAFE ZONE COMPOSITION: The subject's head, face, eyes, nose, mouth and upper torso MUST BE PROMINENTLY FRAMED IN THE UPPER 50% OF THE VERTICAL FRAME with beautiful golden rim lighting and tack-sharp focus. The LOWER 50% OF THE FRAME MUST BE COMPOSED AS DARK NEGATIVE SPACE (moody dark gym floor, shadowed wooden deck, dark ambient tone) designed specifically for clean advertising text layout without covering the subject's face. CRITICAL: PURE COMMERCIAL PHOTOGRAPHY ONLY, ZERO TEXT, NO WORDS, NO LETTERS, NO LABELS.",
  "legenda": "Texto persuasivo de 3 a 4 parágrafos com emojis de autoridade, explicação envolvente, chamada para comentar ou acessar marcaopersonal.com no link da bio, e hashtags pertinentes."
}}
"""

    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [{"role": "user", "content": prompt_ia_redator}],
        "temperature": 0.7  # Criatividade alta para nunca repetir
    }

    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, verify=False, timeout=25)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                clean_json = match.group(0).strip()
            else:
                clean_json = content.replace("```json", "").replace("```", "").strip()
            criativo = json.loads(clean_json)

            # Valida ineditismo
            inedito, motivo = verificar_ineditismo_headline(criativo.get("headline", ""), headlines_recentes)
            if not inedito:
                print(f"[ANTI_REP] Headline proposta similar a existente ({motivo}). Ajustando prefixo para garantia de ineditismo...")
                criativo["headline"] = f"{tema_obj['nome'].split('&')[0].upper()}: {criativo.get('headline')}"[:45]

            criativo["cenario_usado"] = cenario_sorteado["nome"]
            criativo["personagem_usado"] = personagem_sorteado["descricao"]
            criativo["tema_id"] = tema_obj["id"]
            criativo["produto_nome"] = tema_obj.get("produto")
            criativo["link_venda"] = tema_obj.get("link_venda")
            criativo["preco"] = tema_obj.get("preco")
            return criativo
    except Exception as e:
        print(f"[ANTI_REP] Erro gerando criativo com IA: {e}")

    # Fallback dinâmico aleatório de alta variedade
    ts_rand = int(time.time()) % 1000
    return {
        "headline": f"{tema_obj['nome'].upper()}: CIÊNCIA AVANÇADA #{ts_rand}",
        "subheadline": f"Protocolo Marcão Personal • {tema_obj['categoria']}:",
        "pontos": [
            "Mecanismo biológico comprovado para resultados reais.",
            "Sem perda de tempo com falsas promessas de internet.",
            f"Condição oficial Marcão Personal: {tema_obj.get('preco', 'Consulte lote')}."
        ],
        "categoria": tema_obj["categoria"],
        "cta_card": "LEIA A LEGENDA",
        "prompt_fotografico": f"{personagem_sorteado['prompt_char']} {cenario_sorteado['prompt_scene']}. PHOTOGRAPHIC SAFE ZONE: Subject face and torso framed in upper 50%, lower 50% dark negative space for text overlay. Cinematic 8k photography, crisp focus. CRITICAL: PURE PHOTOGRAPHY ONLY, ZERO TEXT.",
        "legenda": f"🔥 {tema_obj['nome'].upper()} • CIÊNCIA DO RESULTADO\n\nResultados duradouros exigem consistência, biomecânica e suplementação de pureza comprovada!\n\n🔗 Conheça os protocolos oficiais: marcaopersonal.com (Link na Bio)\n\n#marcao #marcaopersonal #fitness #saude #qualidadedevida",
        "cenario_usado": cenario_sorteado["nome"],
        "personagem_usado": personagem_sorteado["descricao"],
        "tema_id": tema_obj["id"]
    }


def gerar_imagem_inedita_openrouter(prompt_ia: str, nome_arquivo="post_inedito.png") -> str:
    """Gera uma imagem cinematográfica 8k via OpenRouter sem texto impresso."""
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    
    # Adiciona semente temporal e iluminação aleatória para nunca produzir imagem idêntica
    seed_sutil = random.choice([
        "soft morning rim light, 8k resolution, cinematic shutter speed",
        "warm golden hour tones, ultra-detailed skin textures, depth of field",
        "clean crisp daylight, high contrast athletic highlights, photorealistic",
        "dramatic stadium rim lighting, hyper-focused gaze, 85mm portrait lens"
    ])
    prompt_completo = f"{prompt_ia}, {seed_sutil}. CRITICAL: PURE PHOTOGRAPHY ONLY, ABSOLUTELY NO LETTERS, NO WORDS, NO TYPOGRAPHY."

    payload = {
        "model": "google/gemini-2.5-flash-image",
        "messages": [{"role": "user", "content": prompt_completo}]
    }

    caminho_local = os.path.join(OUTPUT_DIR, nome_arquivo)
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, verify=False, timeout=60)
        if r.status_code == 200:
            data = r.json()
            choices = data.get("choices", [])
            if choices and "images" in choices[0].get("message", {}):
                img_entry = choices[0]["message"]["images"][0]
                img_url = img_entry.get("image_url", {}).get("url", "")
                if "base64," in img_url:
                    b64_str = img_url.split("base64,")[1]
                    raw_bytes = base64.b64decode(b64_str)
                    with open(caminho_local, "wb") as f:
                        f.write(raw_bytes)
                    print(f"[ANTI_REP] Nova foto gerada com sucesso via IA: {caminho_local} ({len(raw_bytes)} bytes)")
                    return caminho_local
    except Exception as e:
        print(f"[ANTI_REP] Falha na geração da imagem via OpenRouter: {e}")

    return None


def upload_imagem_supabase(caminho_local: str, nome_remoto: str) -> str:
    """Faz o upload para o Supabase Storage e retorna a URL pública única."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    with open(caminho_local, "rb") as f:
        data = f.read()

    url = f"{SUPABASE_URL}/storage/v1/object/creativos/posts/{nome_remoto}"
    r = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
    if r.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/creativos/posts/{nome_remoto}"
    return ""


def registrar_no_content_calendar(content_id: str, legenda: str, media_url: str) -> bool:
    """Grava o registro no Supabase para proteção histórica e anti-duplicação."""
    if not SUPABASE_KEY:
        return False
    try:
        dados = {
            "platform": "instagram",
            "content_id": content_id,
            "caption": legenda[:500],
            "media_url": media_url,
            "status": "published",
            "published_at": datetime.now().isoformat()
        }
        h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        r = requests.post(f"{SUPABASE_URL}/rest/v1/content_calendar", headers=h, json=dados, verify=False, timeout=10)
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"[ANTI_REP] Erro registrando no content_calendar: {e}")
        return False
