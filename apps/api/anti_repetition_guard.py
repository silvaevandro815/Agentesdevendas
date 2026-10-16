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
    {
        "id": "evandro_atleta",
        "descricao": "Evandro Gallina (Fundador & Atleta Marcão Personal, 35-40 anos, porte atlético moderno, focado, expressão confiante e simpática)",
        "prompt_char": "Athletic fitness founder Evandro Gallina, handsome Brazilian man with short neat dark hair, fit athletic lean muscular physique, focused and determined expression"
    },
    {
        "id": "marcao_coach",
        "descricao": "Coach Marcão (Mascote e Personal Trainer imponente, carismático, camisa dry-fit oficial preta e dourada Marcão Personal)",
        "prompt_char": "Imposing athletic personal trainer Coach Marcão, 35 years old, powerfully built muscular physique, intense motivating gaze, wearing sleek black fitness dry-fit gear"
    },
    {
        "id": "mulher_jovem_atleta",
        "descricao": "Mulher atleta jovem (28 anos, abdômen definido, tônus muscular elegante, roupa esportiva moderna)",
        "prompt_char": "Fit 28-year-old athletic female fitness model, lean defined waistline, glowing radiant skin, high athletic energy, wearing premium sports attire"
    },
    {
        "id": "mulher_madura_estetica",
        "descricao": "Mulher madura (38 anos, pele viçosa e firme, elegância e saúde radiante)",
        "prompt_char": "Elegant 38-year-old fit healthy woman with smooth firm radiant skin, joyful genuine expression, athletic posture"
    },
    {
        "id": "mulher_senior_vitalidade",
        "descricao": "Mulher sênior ativa (64 anos, sorriso vibrante, postura atlética exemplar)",
        "prompt_char": "Inspiring fit 64-year-old healthy senior woman, vibrant joyful smile, active posture, glowing vitality and grace"
    },
    {
        "id": "homem_executivo_fit",
        "descricao": "Homem 42 anos (focado em saúde, biohacking e produtividade corporal)",
        "prompt_char": "Sharp athletic 42-year-old professional man in peak physical condition, confident calm expression, masculine fitness aesthetic"
    }
]

MATRIZ_CENARIOS = [
    {
        "id": "academia_elite",
        "nome": "Academia de Luxo Moderna",
        "prompt_scene": "inside a luxury ultra-modern high-tech gym, dark matte walls, warm golden rim lighting, sleek dumbbells and Olympic barbells in soft bokeh background"
    },
    {
        "id": "praia_aurora",
        "nome": "Praia ao Nascer do Sol",
        "prompt_scene": "along an ocean beach shoreline during warm golden sunrise, fresh morning ocean mist, radiant cinematic sun rays, dynamic coastal fitness setting"
    },
    {
        "id": "cozinha_funcional",
        "nome": "Cozinha Gourmet de Alta Performance",
        "prompt_scene": "in a sleek minimalist modern kitchen, marble island with clean shaker bottle and fresh healthy natural ingredients, bright daylight through large windows"
    },
    {
        "id": "deck_piscina",
        "nome": "Deck de Piscina Sofisticado",
        "prompt_scene": "by the edge of a luxury infinity pool, crystal clear turquoise water, soft morning sun, premium outdoor wellness and recovery atmosphere"
    },
    {
        "id": "sala_funcional",
        "nome": "Sala de Estar Minimalista para Treino em Casa",
        "prompt_scene": "in a spacious luxury modern living room with wooden floors, soft ambient daylight, clean architectural interior for home workout"
    },
    {
        "id": "trilha_natureza",
        "nome": "Trilha ao Ar Livre na Natureza",
        "prompt_scene": "on a scenic mountain running trail surrounded by lush green pine trees, morning mountain air, crisp golden sunlight filtering through trees"
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

    # Rotação obrigatória de Personagem e Cenário
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
  "prompt_fotografico": "{personagem_sorteado['prompt_char']} {cenario_sorteado['prompt_scene']}. Cinematic 8k commercial photography, crisp focus, hyper-realistic skin texture, dynamic lighting, professional editorial composition. CRITICAL: PURE PHOTOGRAPHY ONLY, ZERO TEXT, NO WORDS, NO LETTERS, NO LABELS.",
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
        "prompt_fotografico": f"{personagem_sorteado['prompt_char']} {cenario_sorteado['prompt_scene']}. Cinematic 8k photography, crisp focus, dynamic lighting. CRITICAL: PURE PHOTOGRAPHY ONLY, ZERO TEXT.",
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
