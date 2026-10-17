import os
import re
import sys
import time
import json
import base64
import random
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import httpx
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
STORAGE_BUCKET = "creativos"

# Paleta Visual Editorial Marcão Personal (@caiqueness inspired - Foco em Venda & Beleza)
COR_BG_DEEP = (7, 10, 16)           # Obsidiana escuro
COR_AMBER = (255, 122, 0)           # Sunset Amber vibrante (predominante para venda, vitalidade e apetite)
COR_AMBER_LIGHT = (255, 175, 55)    # Dourado brilhante para destaque
COR_CREAM = (255, 246, 235)         # Marfim de luxo
COR_CYAN = (0, 229, 255)            # Neon Cyan biohacking cirúrgico
COR_WHITE = (255, 255, 255)
COR_TEXT_MUTED = (165, 185, 210)
COR_NAVY = (10, 14, 23)
COR_GREEN = (57, 240, 140)
COR_ORANGE = (255, 138, 0)

# Diretórios de Mídia e Fontes Editoriais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DIR_OUTPUT = os.path.join(ROOT_DIR, "apps", "site", "public", "images", "posts")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
FONT_BEBAS = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")
FONT_ANTON = os.path.join(FONTS_DIR, "Anton-Regular.ttf")
FONT_MONTSERRAT = os.path.join(FONTS_DIR, "Montserrat-Variable.ttf")
LOGO_PATH = os.path.join(ROOT_DIR, "apps", "admin", "public", "images", "logo_marcao.jpg")
MASCOTE_PATH = os.path.join(ROOT_DIR, "apps", "admin", "public", "images", "mascote_marcao.jpg")

os.makedirs(DIR_OUTPUT, exist_ok=True)

def desenhar_seta_minimalista(draw, x, y, cor, tamanho=14):
    """Desenha seta moderna vetorial -> com alta nitidez."""
    draw.line([(x, y), (x + tamanho, y)], fill=cor, width=3)
    draw.line([(x + tamanho - 5, y - 5), (x + tamanho, y)], fill=cor, width=3)
    draw.line([(x + tamanho - 5, y + 5), (x + tamanho, y)], fill=cor, width=3)


def obter_tendencias_google_trends(termo="fitness"):
    """Consulta sugestões em tempo real do Google Trends / Google Suggest Brasil."""
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&q={termo}&gl=br&hl=pt-BR"
    try:
        with httpx.Client(verify=False, timeout=8) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = json.loads(resp.content.decode("latin-1"))
                return data[1][:6] if len(data) > 1 else []
    except Exception:
        pass
    return []


# -------------------------------------------------------------------------
# 1. BÚSSOLA DE TEMAS E TENDÊNCIAS FITNESS BRASIL (GOOGLE TRENDS)
# -------------------------------------------------------------------------
TEMAS_CURIOSIDADES = [
    {
        "id": "dor_muscular_remedio",
        "categoria": "CIÊNCIA & RECUPERAÇÃO",
        "tema": "Dor Muscular Pós-Treino: Posso Tomar Anti-inflamatório?",
        "headline": "TOMAR REMÉDIO PÓS-TREINO TRAVA A HIPERTROFIA?",
        "subheadline": "O erro de farmácia que joga semanas de treino no ralo",
        "pontos_card": [
            "Anti-inflamatórios comuns bloqueiam as enzimas e matam o ganho muscular.",
            "A inflamação do treino é exatamente o gatilho biológico para o músculo crescer.",
            "Solução correta: hidratação profunda com creatina pura e recuperação ativa."
        ],
        "slides_carrossel": [
            {
                "titulo": "TOMOU ANTI-INFLAMATÓRIO?\nSEU TREINO FOI PARA O LIXO!",
                "sub": "A bioquímica da dor muscular tardia explicada pelo Marcão:",
                "pontos": [
                    "A dor de 24h a 48h após o treino chama-se Dor Tardia (DMIT).",
                    "Ela ocorre por microfissuras benéficas que o corpo precisa regenerar.",
                    "Remédios comuns (ibuprofeno, diclofenaco) desligam os sinais de reparação.",
                    "Você alivia a dor passageira, mas joga seu ganho de massa no ralo!"
                ],
                "cta": "ARRASTE E ENTENDA O MECANISMO BIOLÓGICO ››"
            },
            {
                "titulo": "O QUE ACONTECE NA FIBRA\nQUANDO VOCÊ TOMA REMÉDIO?",
                "sub": "Bloqueio hormonal comprovado pela fisiologia:",
                "pontos": [
                    "A enzima COX-2 é paralisada: zero síntese de novas fibras musculares.",
                    "As células satélites não se fundem: seu músculo não engrossa.",
                    "O estômago e os rins sofrem sobrecarga química desnecessária.",
                    "A inflamação fisiológica controlada é sua MAIOR aliada para crescer."
                ],
                "cta": "COMO ALIVIAR SEM PREJUDICAR? VEJA A SEGUIR ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\nRECUPERAÇÃO SEM REMÉDIOS",
                "sub": "Padrão de regeneração celular com creatina pura:",
                "pontos": [
                    "Creatina Micronizada 100% Pura: hidratação das fibras e força renovada.",
                    "Banho morno, sono profundo de 7-8h e hidratação com eletrólitos.",
                    "Cardio leve regenerativo para oxigenar e acelerar a circulação.",
                    "Apenas R$ 169,90 no pote de 300g (100 doses oficiais)."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 Sentiu aquela dor muscular insuportável no dia seguinte e correu para tomar um remédio? CUIDADO: você pode estar destruindo seus resultados!\n\n"
            "Um dos tópicos mais buscados no Google Trends Brasil desmascarado pela ciência:\n\n"
            "Quando você treina pesado, ocorrem micro-lesões normais nas fibras musculares. Essa inflamação fisiológica é exatamente o sinal biológico que avisa ao seu corpo: 'precisamos construir um músculo maior e mais forte'.\n\n"
            "Ao tomar anti-inflamatórios comuns (como Ibuprofeno ou Diclofenaco), você desliga a via das prostaglandinas e paralisa a síntese proteica. Ou seja: a dor alivia na hora, mas seu ganho de massa muscular é travado!\n\n"
            "💡 O que fazer de verdade para acelerar a recuperação sem estragar o treino:\n"
            "1. Hidratar as fibras de dentro para fora com Creatina Micronizada pura.\n"
            "2. Ingerir água abundante e priorizar o sono profundo (onde o GH é liberado).\n"
            "3. Fazer cardio leve regenerativo (caminhada/bike) para circular oxigênio.\n\n"
            "💬 Você já cometeu o erro de tomar remédio após um treino pesado? Me conta aqui nos comentários!\n\n"
            "👉 Para garantir a Creatina Micronizada 100% Pura Nature's Prime por R$ 169,90, acesse o LINK NA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo que eu te envio! 📲\n\n"
            "#marcao #dormuscular #hipertrofia #recuperacaomuscular #creatina #treinopesado #biohacking #fitness"
        ),
        "prompt_ia": (
            "Inspiring 8k photography of fit athlete Evandro performing intense dumbbell curls with determination and grit, "
            "modern gym setting with dynamic rim lighting, sweat glistens on toned arms, photorealistic"
        )
    },
    {
        "id": "perder_barriga_pochete",
        "categoria": "EMAGRECIMENTO DEFINITIVO",
        "tema": "Como Perder a Barriga Pochete sem Ficar Flácido",
        "headline": "O SEGREDO PARA SECAR A POCHETE SEM FLACIDEZ",
        "subheadline": "Por que fazer 500 abdominais por dia nunca vai secar sua barriga",
        "pontos_card": [
            "Não existe queima de gordura localizada: o abdômen seca no déficit calórico.",
            "Aeróbio excessivo sem treino de força queima músculo e deixa o corpo flácido.",
            "Manter massa magra e tônus muscular mantém seu metabolismo acelerado 24h."
        ],
        "slides_carrossel": [
            {
                "titulo": "POR QUE FAZER ABDOMINAL\nNÃO SECA A BARRIGA POCHETE?",
                "sub": "O mito do emagrecimento localizado desvendado:",
                "pontos": [
                    "O abdômen é um músculo como outro qualquer, não um queimador de gordura.",
                    "Fazer 500 abdominais só fortalece a parede interna sob a gordura.",
                    "A gordura subcutânea só é metabolizada com balanço calórico negativo.",
                    "Passar fome em dietas líquidas destrói o metabolismo basal."
                ],
                "cta": "ARRASTE E VEJA COMO ATIVAR A QUEIMA REAL ››"
            },
            {
                "titulo": "A TRÍADE DE OURO PARA SECAR\nMANTENDO A PELE COLADA",
                "sub": "Estratégia de elite para perder gordura sem flacidez:",
                "pontos": [
                    "Musculação focada em grandes grupos para exigir alto gasto energético.",
                    "Cardio moderado diário (calçadão, corrida ou bike ao ar livre).",
                    "Aporte proteico e creatina pura para blindar as fibras contra o catabolismo.",
                    "Colágeno e hidratação profunda para colar a pele no músculo."
                ],
                "cta": "CONHEÇA O PROTOCOLO COMPLETO A SEGUIR ››"
            },
            {
                "titulo": "PROTOCOLO DEFINIÇÃO TOTAL\nMARCÃO PERSONAL & EVANDRO",
                "sub": "Resultados reais com suporte científico comprovado:",
                "pontos": [
                    "Treinos rápidos e metabólicos de 40 minutos para o seu dia a dia.",
                    "Suplementação limpa sem açúcar, sem retenção e com laudo oficial.",
                    "Acompanhamento personalizado para destravar seu shape.",
                    "Acesse agora os protocolos completos no site oficial."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 Cansou de fazer 500 abdominais e ver a barriga pochete continuar lá?\n\n"
            "A verdade sobre emagrecimento e queima de gordura no abdômen explicada pelo Marcão:\n\n"
            "Não existe queima de gordura localizada! Fazer abdominal fortalece o músculo por baixo da camada adiposa, mas não queima a capa de gordura que fica por cima.\n\n"
            "Pior ainda: quem faz horas de cardio em jejum e passa fome acaba perdendo massa muscular em vez de gordura, ficando com o aspecto flácido e metabolismo travado.\n\n"
            "Para secar a pochete e ficar com a pele firme:\n"
            "1. Treino de força para acelerar o gasto calórico até em repouso.\n"
            "2. Cardio moderado constante (corrida no calçadão, caminhada rápida).\n"
            "3. Suplementação inteligente com Creatina e Colágeno para preservar o tônus.\n\n"
            "💬 Qual é a sua maior dificuldade para secar a região abdominal? Comenta aqui embaixo!\n\n"
            "👉 Conheça nossos protocolos oficiais tocando no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲\n\n"
            "#marcao #perderbarriga #emagrecer #treinoaoarlivre #corrida #definicaomuscular #saude #pochete"
        ),
        "prompt_ia": (
            "Dynamic 8k sports photography of athletic runner Evandro jogging on a vibrant beach boardwalk at sunrise, "
            "athletic posture, energetic morning golden light, palm trees and ocean in background, photorealistic"
        )
    },
    {
        "id": "creatina_mito",
        "categoria": "CIÊNCIA & PERFORMANCE",
        "tema": "Mito da Creatina Feminina & Inchaço",
        "headline": "CREATINA NÃO INCHA MULHER",
        "subheadline": "A maior mentira do fitness desmascarada pelo Marcão",
        "pontos_card": [
            "A creatina NÃO retém água na pele: ela hidrata dentro do músculo.",
            "Resultado prático: muito mais firmeza no glúteo e força no treino.",
            "Laudo de pureza 100% livre de sódio e sem açúcar."
        ],
        "slides_carrossel": [
            {
                "titulo": "MENINA, QUEM DISSE QUE\nCREATINA ENGORDA OU INCHA?",
                "sub": "O maior mito fitness derrubado pela bioquímica:",
                "pontos": [
                    "Inchaço na pele é retenção inflamatória de açúcar e sódio ruim.",
                    "A creatina pura puxa água para DENTRO da célula muscular.",
                    "Sua pele fica colada no músculo com aspecto denso e durinho.",
                    "Treinar sem creatina deixa até 40% do seu resultado na mesa."
                ],
                "cta": "ARRASTE PARA O LADO E ENTENDA O EFEITO ››"
            },
            {
                "titulo": "O QUE ACONTECE NA FIBRA\nCOM A CREATINA PURA?",
                "sub": "Mecanismo biológico comprovado pela ciência:",
                "pontos": [
                    "Aumento de 30% nos estoques de fosfocreatina no músculo.",
                    "Recuperação acelerada: zero dores incapacitantes no dia seguinte.",
                    "Você sustenta cargas maiores e queima o dobro de calorias.",
                    "Glúteo mais firme, tônus evidente e coxas definidas."
                ],
                "cta": "QUAL É A MELHOR CREATINA? VEJA A SEGUIR ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\n100% PURA NATURE'S PRIME",
                "sub": "Pureza micronizada com laudo de laboratório oficial:",
                "pontos": [
                    "Dissolução instantânea em água sem empelotar.",
                    "Pote de 300g rende 100 doses diárias completas.",
                    "Envio imediato com frete rastreado para todo o Brasil.",
                    "Apenas R$ 169,90 no lote oficial do site."
                ],
                "cta": "ACESSE O LINK NA BIO: marcaopersonal.com ››"
            }
        ],
        "legenda": (
            "🔥 Menina, quem te falou que Creatina engorda ou incha?\n\n"
            "A maior mentira do mundo fitness desmascarada pelo Marcão:\n\n"
            "A creatina NÃO retém água debaixo da pele (isso é inchaço inflamatório causado por ultraprocessados e sódio ruim)!\n\n"
            "A creatina pura puxa água para DENTRO da fibra muscular. Sabe o que isso significa na prática?\n\n"
            "1. Muito mais tônus e firmeza no glúteo e nas pernas.\n"
            "2. Mais força e explosão para queimar o dobro de calorias no treino.\n"
            "3. Recuperação acelerada sem fadiga muscular no dia seguinte.\n\n"
            "Quem treina sem creatina micronizada de pureza comprovada está deixando 40% dos resultados na mesa!\n\n"
            "💬 Você já toma creatina todos os dias ou ainda tinha medo de inchar? Me conta aqui nos comentários!\n\n"
            "👉 Para garantir a Creatina Micronizada 100% Pura Nature's Prime com laudo oficial, toque no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo que eu te envio no Direct! 📲\n\n"
            "#marcao #personal #fitness #creatina #treinofeminino #hipertrofia #suplementos #saude #biohacking"
        ),
        "prompt_ia": (
            "Cinematic 8k photorealistic portrait of athletic Brazilian trainer Marcão in modern fitness gym with neon cyan lighting, "
            "wearing navy compression shirt, confident friendly smile, holding modern fitness shaker cup, dramatic rim lighting, depth of field"
        )
    },
    {
        "id": "fome_doces_22h",
        "desativado": True,  # Vendia a Azempika como inibidor de apetite (incorreto). Reescrever com dados oficiais do fabricante.
        "categoria": "METABOLISMO & BIOHACKING",
        "tema": "A Fome Incontrolável de Doce às 22h",
        "headline": "FOME DE DOCE ÀS 22H NÃO É FALTA DE FOCO",
        "subheadline": "Entenda a bioquímica do cortisol e da glicose cerebral",
        "pontos_card": [
            "O estresse do dia eleva o cortisol e derruba a glicose noturna.",
            "O cérebro em pânico pede energia rápida: aí vem a compulsão.",
            "Reprogramar o apetite não exige passar fome com dietas malucas."
        ],
        "slides_carrossel": [
            {
                "titulo": "POR QUE VOCÊ TEM FOME DE\nDOCE EXATAMENTE ÀS 22H?",
                "sub": "A bioquímica do estresse e do cortisol explicada:",
                "pontos": [
                    "Ao longo do dia, o estresse acumula cortisol elevado no sangue.",
                    "À noite, a glicose cerebral cai e o cérebro entra em modo alerta.",
                    "O corpo não pede comida: ele grita por energia química rápida!",
                    "Dietas malucas de passar fome só pioram esse ciclo vicioso."
                ],
                "cta": "ARRASTE PARA O LADO E VEJA O CICLO DA COMPULSÃO ››"
            },
            {
                "titulo": "O CICLO DA COMPULSÃO\nNOTURNA DESVENDADO",
                "sub": "O que acontece ao ceder à tentação do açúcar à noite:",
                "pontos": [
                    "Pico violento de insulina bloqueia a queima de gordura no sono.",
                    "A melatonina cai: o sono profundo reparador é destruído.",
                    "Você acorda cansado, desmotivado e com o dobro de fome.",
                    "Solução real: modular os receptores de saciedade e queima suave."
                ],
                "cta": "COMO ACABAR COM ISSO? VEJA O PROTOCOLO ››"
            },
            {
                "titulo": "PROTOCOLO MARCÃO PERSONAL\nCANETA AZEMPIKA ORIGINAL",
                "sub": "Reprograme seu apetite noturno com fórmula termogênica:",
                "pontos": [
                    "Modulação suave da saciedade sem efeitos colaterais agressivos.",
                    "Despacho rápido em embalagem térmica direto do laboratório.",
                    "Lote promocional exclusivo por apenas R$ 99,00.",
                    "Acompanhamento personalizado para destravar seus resultados."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 Por que você sente uma vontade incontrolável de comer doce às 22h?\n\n"
            "Não é falta de vergonha na cara ou fraqueza: é BIOQUÍMICA DESREGULADA!\n\n"
            "Ao longo do dia, a correria eleva seu cortisol. Quando a noite chega, a glicose cerebral sofre uma queda abrupta e seu cérebro entra em modo de emergência pedindo energia instantânea.\n\n"
            "É exatamente aí que você ataca a despensa ou pede sobremesa no delivery.\n\n"
            "Reprogramar esse apetite não exige passar fome com dietas restritivas, e sim modular a saciedade térmica e os receptores gástricos.\n\n"
            "💬 Qual é a hora do dia que sua vontade de comer doce mais ataca? Escreve aqui embaixo!\n\n"
            "👉 Para conhecer a Caneta Azempika Original por apenas R$ 99,00 no lote de hoje, acesse o LINK NA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲\n\n"
            "#marcao #emagrecimento #fomenoturna #metabolismo #saciedade #compulsaoalimentar #saude"
        ),
        "prompt_ia": (
            "Cinematic 8k commercial photography of a sleek high-tech Caneta Azempika device on a dark carbon surface with orange and cyan neon ambient glow, studio lighting, hyper detailed"
        )
    },
    {
        "id": "colageno_25anos",
        "categoria": "ESTÉTICA FACIAL & DÉRMICA",
        "tema": "A Queda Invisível de Colágeno aos 25 Anos",
        "headline": "A PARTIR DOS 25 VOCÊ PERDE 1% DE COLÁGENO",
        "subheadline": "Por que o colágeno barato de farmácia não devolve firmeza",
        "pontos_card": [
            "Aos 25 anos a síntese natural de sustentação dérmica desacelera.",
            "Colágeno comum é degradado pelo suco gástrico antes de agir.",
            "Para fazer efeito real, precisa de Ácido Hialurônico e biopeptídeos."
        ],
        "slides_carrossel": [
            {
                "titulo": "A PARTIR DOS 25 ANOS\nSEU CORPO PERDE 1% DE COLÁGENO",
                "sub": "A fábrica natural de sustentação da pele desacelera:",
                "pontos": [
                    "A cada ano após os 25, a matriz dérmica perde densidade.",
                    "Surgem as primeiras linhas finas na testa e ao redor dos olhos.",
                    "A flacidez facial e corporal começa de forma silenciosa.",
                    "A alimentação do dia a dia não repõe a fração bioativa necessária."
                ],
                "cta": "ARRASTE E DESCUBRA O ERRO DO COLÁGENO BARATO ››"
            },
            {
                "titulo": "POR QUE COLÁGENO BARATO\nDE FARMÁCIA NÃO FUNCIONA?",
                "sub": "A verdade que os rótulos comuns não revelam:",
                "pontos": [
                    "Moléculas grandes são destruídas pelo estômago antes da absorção.",
                    "Pós com excesso de maltodextrina inflamam a derme em vez de tratar.",
                    "Para agir na sustentação, precisa de peptídeos hidrolisados Verisol.",
                    "A união com Ácido Hialurônico retém água e hidratação nas camadas profundas."
                ],
                "cta": "VEJA A SOLUÇÃO COMPLETA A SEGUIR ››"
            },
            {
                "titulo": "COLÁGENO + ÁCIDO HIALURÔNICO\nNATURE'S PRIME CLINICAL",
                "sub": "Nutrição de dentro para fora no sabor Abacaxi com Hortelã:",
                "pontos": [
                    "30 doses diárias de renovação celular e firmeza tecidual.",
                    "Biopeptídeos de rápida absorção com Ácido Hialurônico puro.",
                    "Pele mais firme, viçosa e cabelos/unhas fortalecidos.",
                    "Apenas R$ 164,90 com envio rápido para todo o país."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 A partir dos 25 anos seu corpo perde 1% de colágeno todo santo ano!\n\n"
            "Por que aquele colágeno barato de farmácia cheio de açúcar não funciona na sua pele?\n\n"
            "Depois dos 25, a fábrica natural de fibroblastos e sustentação dérmica desacelera. O resultado? Primeiras linhas de expressão, flacidez e perda de viço.\n\n"
            "Mas atenção: tomar colágeno não hidrolisado ou sem Ácido Hialurônico é dinheiro jogado fora, porque o ácido gástrico destrói a proteína antes de ela chegar na derme.\n\n"
            "Para fazer efeito real de sustentação, a molécula precisa de biopeptídeos ativos micronizados combinados com Ácido Hialurônico puro.\n\n"
            "💬 Você já começou a cuidar da sua reposição de colágeno ou ainda achava cedo? Me conta aqui embaixo!\n\n"
            "👉 Para garantir o Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime por R$ 164,90, acesse o LINK NA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲\n\n"
            "#marcao #colageno #acidohialuronico #estetica #pelesaudavel #skincare #rejuvenescimento"
        ),
        "prompt_ia": (
            "Cinematic 8k commercial photography of luxury white bottle of Colageno Hidrolisado with pure green mint and pineapple slices, illuminated by soft morning sunlight in aesthetic clinic spa, 85mm lens"
        )
    },
    {
        "id": "xampu_antiqueda_mito",
        "categoria": "TERAPIA CAPILAR CLÍNICA",
        "tema": "O Mito do Xampu Antiqueda",
        "headline": "XAMPU ANTIQUEDA NÃO FAZ NASCER CABELO",
        "subheadline": "Entenda a ciência da matriz folicular e do silício inteligente",
        "pontos_card": [
            "O xampu fica 2 minutos no couro cabeludo e desce pelo ralo.",
            "Miniaturização dos fios é causada por carência nutricional na raiz.",
            "Recuperar fios exige nutrição celular interna e bioestimulação tópica."
        ],
        "slides_carrossel": [
            {
                "titulo": "XAMPU ANTIQUEDA NÃO FAZ\nNASCER CABELO NOVO!",
                "sub": "A verdade que a indústria cosmética não te conta:",
                "pontos": [
                    "O xampu atua por 2 minutos na superfície e vai para o ralo.",
                    "Ele serve para higienizar o couro cabeludo, não para nutrir a raiz.",
                    "Se o fio está afinando ou as entradas abrindo, o problema é folicular.",
                    "Nenhum cosmético de supermercado reverte a miniaturização dos fios."
                ],
                "cta": "ARRASTE E ENTENDA COMO NUTRIR A RAIZ ››"
            },
            {
                "titulo": "COMO REVERTER A QUEDA\nE ENGROSSAR OS FIOS?",
                "sub": "A ciência da revitalização capilar de 4 fases:",
                "pontos": [
                    "Bloqueio da micro-inflamação folicular na raiz do cabelo.",
                    "Aporte de Silício Orgânico Inteligente, Biotina e Zinco quelado.",
                    "Oxigenação acelerada da microcirculação do couro cabeludo.",
                    "Fase de crescimento ativa (Anágena) prolongada por meses."
                ],
                "cta": "CONHEÇA O PROTOCOLO CLÍNICO A SEGUIR ››"
            },
            {
                "titulo": "KIT IARMONIZE CAPILAR CLÍNICO\nPROTOCOLO EM 4 FASES",
                "sub": "Tratamento clínico antiqueda de máxima tecnologia:",
                "pontos": [
                    "Combinação sinérgica de cápsulas orais, sérum e bioestimulação.",
                    "Fórmula aprovada e desenvolvida para frear a queda em até 21 dias.",
                    "Acompanhamento e consultoria de especialista no WhatsApp.",
                    "Em até 12x no cartão com Frete Grátis Correios para todo o Brasil."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 Xampu antiqueda não faz nascer cabelo novo. Entenda a ciência:\n\n"
            "A maior ilusão dos produtos convencionais desfeita pelo Marcão:\n\n"
            "O xampu passa 2 minutos na sua cabeça e vai embora pelo ralo. Ele serve exclusivamente para higienizar o couro cabeludo, não para reverter miniaturização folicular!\n\n"
            "Se o fio está afinando, caindo no banho ou as entradas estão abrindo, a causa está na carência de silício inteligente, biotina e oxigenação da matriz celular na raiz do folículo.\n\n"
            "Tratar calvície e queda acelerada exige nutrição de dentro para fora somada a bioestimulação tópica profunda.\n\n"
            "💬 Você já gastou rios de dinheiro com xampu prometendo milagre e não viu resultado? Me conta sua experiência nos comentários!\n\n"
            "👉 Para conhecer o KIT IArmonize Capilar Clínico em 4 Fases, acesse o LINK NA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲\n\n"
            "#marcao #quedadecabelo #terapiacapilar #cabelosaudavel #calvicie #iarmonize #biohacking"
        ),
        "prompt_ia": (
            "Cinematic 8k macro photography of clinical medical laboratory serum with micro-droplets on hair follicle model, hyper detailed, dramatic blue and cyan neon backlighting, high-tech dermocosmetics"
        )
    },
    {
        "id": "balanca_ilusao",
        "categoria": "BIOHACKING & COMPOSIÇÃO",
        "tema": "A Ilusão da Balança de Banheiro Comum",
        "headline": "O PESO NA BALANÇA MENTE PARA VOCÊ",
        "subheadline": "Você pode ter mantido o mesmo peso e ter emagrecido muito",
        "pontos_card": [
            "1 kg de gordura ocupa o triplo do espaço de 1 kg de músculo.",
            "Quando você ganha músculo e queima gordura, o ponteiro não mexe.",
            "O que importa de verdade é seu percentual de gordura e bioimpedância."
        ],
        "slides_carrossel": [
            {
                "titulo": "O PESO NA BALANÇA COMUM\nMENTE PARA VOCÊ TODO DIA!",
                "sub": "Você sabia que pode emagrecer sem o ponteiro mexer?",
                "pontos": [
                    "1 kg de gordura ocupa três vezes o volume de 1 kg de músculo denso.",
                    "Na balança de banheiro, água, massa magra e gordura são a mesma coisa.",
                    "Muitas pessoas desistem da dieta achando que estagnaram.",
                    "Mas no espelho, a cintura afinou e as medidas despencaram!"
                ],
                "cta": "ARRASTE E VEJA A DIFERENÇA DE DENSIDADE ››"
            },
            {
                "titulo": "RECOMPOSIÇÃO CORPORAL:\nQUEIMA DE GORDURA E GANHO MAGRO",
                "sub": "O que realmente acontece quando você treina com o Marcão:",
                "pontos": [
                    "Aporte correto de proteínas estimula a síntese de fibras musculares.",
                    "O déficit calórico estratégico consome os depósitos de gordura.",
                    "A taxa metabólica basal aumenta: você queima calorias até dormindo.",
                    "Avaliar o corpo pelo peso total é o erro número 1 de quem treina."
                ],
                "cta": "COMO MONITORAR DE FORMA PRECISA? VEJA A SEGUIR ››"
            },
            {
                "titulo": "BALANÇA DE BIOIMPEDÂNCIA BLUETOOTH\nCOM CONEXÃO DIRETA AO APP",
                "sub": "Tecnologia de biohacking para monitorar seu corpo com precisão:",
                "pontos": [
                    "Mede percentual de gordura, massa muscular, água corporal e TMB.",
                    "Sincronização imediata via Bluetooth com gráficos no celular.",
                    "Acompanhamento integrado com as orientações do Marcão Personal.",
                    "Apenas R$ 129,90 com frete seguro para todo o Brasil."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 O peso na balança mente para você todos os dias!\n\n"
            "Você sabia que pode ter mantido exatamente o mesmo peso e ter emagrecido muito?\n\n"
            "1 kg de gordura ocupa o triplo do volume de 1 kg de massa muscular no seu corpo!\n\n"
            "Quando você começa a treinar certo e comer proteína, você ganha músculo denso e queima gordura mole ao mesmo tempo. Na balança comum, o peso mal se move, mas no espelho a cintura afinou, as roupas folgaram e o abdômen começou a desenhar!\n\n"
            "Pare de se pesar na balança comum: avalie sua bioimpedância, percentual de gordura e taxa metabólica.\n\n"
            "💬 Você é daquelas pessoas que sobem na balança todo dia ou prefere olhar pelas roupas e pelo espelho? Comenta aqui embaixo!\n\n"
            "👉 Para garantir a Balança de Bioimpedância Bluetooth com App por R$ 129,90, acesse o LINK NA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲\n\n"
            "#marcao #bioimpedancia #emagrecimento #composicaocorporal #balanca #treino #definicaomuscular"
        ),
        "prompt_ia": (
            "Cinematic 8k photograph of athletic Brazilian trainer Marcão holding a sleek ultra-modern glass Bluetooth smart bioimpedance scale, standing in an elite high-tech gym, photorealistic, sharp lighting"
        )
    }
]

# 6 Produtos Oficiais do Marcão Personal
PRODUTOS_CATALOGO = [
    {
        "id": 1,
        "sku": "CREATINA-MICRONIZADA-300G",
        "nome": "Creatina Micronizada 100% Pura Nature's Prime (300g)",
        "preco": "R$ 169,90",
        "categoria": "FORÇA & TÔNUS MUSCULAR",
        "link": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "image_fallback": "https://marcaopersonal.com/images/creatina.jpg",
        "image_local": os.path.join(ROOT_DIR, "apps", "site", "public", "images", "creatina.jpg"),
        "prompt_ia": "Cinematic 8k photorealistic close up of a luxury black bottle of Creatina Micronizada 100% Pura Nature Prime on a sleek modern dark slate pedestal, neon cyan lighting, water droplets, commercial photography"
    },
    {
        "id": 2,
        "sku": "AZEMPIKA-CANETA",
        "nome": "Caneta Azempika Original (Vigor & Performance Masculina)",
        "preco": "R$ 99,00",
        "categoria": "SAÚDE & VIGOR MASCULINO",
        "link": "https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv",
        "image_fallback": "https://qkopgftfrfftoyndhhfj.supabase.co/storage/v1/object/public/creativos/card_azempika_feed.jpg",
        "image_local": os.path.join(ROOT_DIR, "apps", "site", "public", "images", "azempika.jpg"),
        "prompt_ia": "Cinematic 8k commercial photography of an attractive happy Brazilian couple in their 40s, handsome athletic confident man smiling tenderly with his beautiful partner, luxury modern bedroom aesthetic, sleek dark wellness applicator pen on the wooden nightstand, romantic vitality mood"
    },
    {
        "id": 3,
        "sku": "COLAGENO-ACIDO-HIALURONICO",
        "nome": "Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime",
        "preco": "R$ 164,90",
        "categoria": "ESTÉTICA FACIAL & DÉRMICA",
        "link": "https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg",
        "image_fallback": "https://marcaopersonal.com/images/colageno.png",
        "image_local": os.path.join(ROOT_DIR, "apps", "site", "public", "images", "colageno.png"),
        "prompt_ia": "Cinematic 8k commercial photography of luxury white bottle of Colageno Hidrolisado with fresh pineapple and green mint leaves, bright aesthetic wellness laboratory, studio lighting"
    },
    {
        "id": 4,
        "sku": "IARMONIZE-CAPILAR-KIT",
        "nome": "KIT IArmonize Capilar Clínico (4 Fases)",
        "preco": "R$ 1.256,00",
        "categoria": "TECNOLOGIA ANTIQUEDA",
        "link": "https://marcaopersonal.com#capilar",
        "image_fallback": "https://marcaopersonal.com/images/iarmonize.jpg",
        "image_local": os.path.join(ROOT_DIR, "apps", "site", "public", "images", "iarmonize.jpg"),
        "prompt_ia": "Cinematic 8k photograph of clinical luxury trichology kit bottles with amber glass and golden accents on a dark marble surface, blue laser medical backlighting"
    },
    {
        "id": 5,
        "sku": "VISION-PRIME-60CAPS",
        "nome": "Vision Prime 60 Cápsulas",
        "preco": "R$ 147,00",
        "categoria": "SAÚDE OCULAR & FOCO",
        "link": "https://marcaopersonal.com#visao",
        "image_fallback": "https://marcaopersonal.com/images/vision.jpg",
        "image_local": os.path.join(ROOT_DIR, "apps", "site", "public", "images", "vision.jpg"),
        "prompt_ia": "Cinematic 8k photography of luxury supplement bottle Vision Prime with subtle optic lens reflection and golden accents, dark modern medical setting"
    },
    {
        "id": 6,
        "sku": "BALANCA-BIOIMPEDANCIA-BT",
        "nome": "Balança de Bioimpedância Bluetooth com App",
        "preco": "R$ 129,90",
        "categoria": "BIOHACKING & COMPOSIÇÃO",
        "link": "https://marcaopersonal.com#balanca",
        "image_fallback": "https://marcaopersonal.com/images/mascote_marcao.jpg",
        "image_local": os.path.join(ROOT_DIR, "apps", "site", "public", "images", "mascote_marcao.jpg"),
        "prompt_ia": "Cinematic 8k photograph of athletic personal trainer Marcão holding a sleek high-tech Bluetooth smart scale in an elite gym background, crisp lighting"
    }
]


# -------------------------------------------------------------------------
# 2. SANITIZAÇÃO DE TEXTO PARA PILLOW (SEM EMOJI BOXES NO WINDOWS)
# -------------------------------------------------------------------------
def sanitizar_texto_pillow(texto):
    """
    Remove caracteres de emoji que não existem nas fontes nativas do Windows,
    evitando que apareçam caixinhas vazias (□) na arte final.
    """
    if not texto:
        return ""
    # Remove faixas Unicode de emojis e símbolos especiais não suportados
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        "\U0001F680-\U0001F6FF"  # transporte & mapas
        "\U0001F1E0-\U0001F1FF"  # bandeiras
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # emojis suplementares
        "\U0001FA70-\U0001FAFF"  # símbolos adicionais
        "\u2600-\u26FF"          # símbolos miscelâneos (ex: ⚡, ☕, 🕒)
        "\u2700-\u27BF"
        "]+",
        flags=re.UNICODE
    )
    limpo = emoji_pattern.sub("", texto)
    limpo = limpo.replace("👉", ">").replace("📲", "").replace("🔥", "").replace("⚡", "").replace("💎", "").replace("🚀", "")
    return limpo.strip()


# -------------------------------------------------------------------------
# 3. GERAÇÃO DE IMAGEM ULTRA-REALISTA VIA OPENROUTER & MATRIZ DE 5 ESTILOS
# -------------------------------------------------------------------------
DIR_FOTOS_EVANDRO = os.path.join(ROOT_DIR, "assets", "evandro")
os.makedirs(DIR_FOTOS_EVANDRO, exist_ok=True)

ESTILOS_VISUAIS = [
    "evandro",          # 1. Rosto do Fundador Evandro em cenários de alta autoridade & saúde
    "marcao",           # 2. Marcão Personal (Mascote e personal maromba de 35 anos)
    "pessoas_ia",       # 3. Pessoas reais geradas por IA (diversidade de homens e mulheres em evolução)
    "produto_only",     # 4. Apenas o produto em foto comercial de luxo / Still sem pessoas
    "infografico_trends"# 5. Infográfico científico dark neon com dados do Google Trends
]

def obter_fotos_referencia_evandro():
    """Retorna lista de fotos de referência de rosto do Evandro disponíveis para a IA."""
    caminhos = []
    pastas = [DIR_FOTOS_EVANDRO, os.path.join(BASE_DIR, "assets", "evandro")]
    for p in pastas:
        if os.path.exists(p):
            for f in os.listdir(p):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    full = os.path.join(p, f)
                    if full not in caminhos:
                        caminhos.append(full)
    return sorted(caminhos)

# ============================================================================
# MATRIZ EXPANDIDA DE CENÁRIOS, AÇÕES, LUGARES E ROSTOS (FÁBRICA VISUAL 360°)
# ============================================================================

CENARIOS_ATLETICOS_EVANDRO = [
    {
        "id": "musculacao_academia",
        "keywords": ["creatina", "força", "músculo", "hipertrofia", "treino", "dor", "braço", "peito", "ombro", "carga", "academia"],
        "prompt": (
            "Cinematic 8k sports action photography of athletic muscular athlete Evandro intensely training in a luxury high-tech gym. "
            "He is performing seated heavy dumbbell shoulder presses with intense focus and grit, toned vascular arms and pumped shoulders, "
            "sweat glistening on skin, wearing a sleek black compression dry-fit shirt. "
            "Dramatic warm rim lighting, blurred modern gym equipment and weight plates in the background, 85mm lens, f/1.8, high-end fitness magazine cover quality, photorealistic."
        )
    },
    {
        "id": "corrida_praia_calcadao",
        "keywords": ["emagrecimento", "perder barriga", "cardio", "corrida", "jejum", "pochete", "gordura", "secar", "aerobico", "praia", "calçadão"],
        "prompt": (
            "Dynamic 8k sports action shot of athletic handsome runner Evandro running at full energetic pace along a coastal tropical beach boardwalk at golden hour sunrise. "
            "Athletic running attire, dark technical breathable running tank top, athletic shorts, modern smartwatch on wrist. "
            "Golden sunlight illuminating ocean waves and palm trees in the background, motion blur in the background, sharp athletic focus on his face, determined smile, photorealistic commercial photography."
        )
    },
    {
        "id": "natacao_piscina",
        "keywords": ["fôlego", "respiração", "água", "resistência", "articulação", "colágeno", "piscina", "natação", "pele"],
        "prompt": (
            "Cinematic 8k photography of athletic swimmer Evandro emerging powerfully from crystal-clear turquoise water in an Olympic training pool. "
            "Water droplets splashing off athletic defined chest and shoulders, intense focused gaze, glistening skin, modern competition goggles resting on his forehead. "
            "Bright sun rays refracting through blue water reflections, high-end sports magazine cover quality, photorealistic."
        )
    },
    {
        "id": "treino_casa_funcional",
        "keywords": ["casa", "funcional", "vassoura", "cadeira", "polichinelo", "sem equipamento", "mobilidade", "alongamento"],
        "prompt": (
            "Authentic 8k lifestyle sports photograph of fit athlete Evandro performing disciplined functional exercises at home in a bright sunlit living room with wooden floors. "
            "Using a wooden broomstick across his shoulders for perfect thoracic mobility and posture alignment, or doing controlled bodyweight squats near a modern ergonomic chair. "
            "Wearing athletic charcoal dry-fit shorts and fitted workout shirt, confident focused coach expression, morning sunlight streaming through large patio windows, clean interior design, photorealistic."
        )
    },
    {
        "id": "caminhada_revigorante_natureza",
        "keywords": ["floresta", "trilha", "natureza", "caminhada", "ar livre", "energia", "parque", "montanha"],
        "prompt": (
            "Inspiring 8k photography of fit athlete Evandro briskly power walking and jogging along a lush green forest trail surrounded by tall majestic trees and morning mist. "
            "Wearing technical trail running shoes, moisture-wicking dark olive athletic apparel and a sports hydration flask in hand, energetic breathing, fresh mountain air ambiance. "
            "Golden sunbeams filtering through emerald canopy leaves, high depth of field, National Geographic / Nike trail aesthetic, photorealistic."
        )
    },
    {
        "id": "nutricao_cozinha_fitness",
        "keywords": ["comida", "comendo", "receita", "nutrição", "shake", "dieta", "smoothie", "alimentação", "refeição"],
        "prompt": (
            "Warm cinematic 8k commercial photography of health founder Evandro in a luxury modern kitchen with clean marble and dark oak countertops. "
            "He is smiling charismatically while preparing an organic protein smoothie with fresh berries, sliced pineapple, green mint leaves and clean shaker cup. "
            "Wearing a casual fitted dark crewneck t-shirt, glowing healthy skin, natural sunlight illuminating fresh whole foods and blender, lifestyle fitness magazine editorial quality."
        )
    },
    {
        "id": "sono_anabolico_quarto",
        "keywords": ["sono", "dormindo", "descanso", "gh", "recuperação", "noite", "relaxamento", "dormir"],
        "prompt": (
            "Serene 8k cinematic photography of athletic man Evandro peacefully sleeping in a luxury minimalist bedroom. "
            "Resting on a comfortable premium mattress with crisp white Egyptian cotton sheets, peaceful calm facial expression, room bathed in soft ambient nocturnal indigo and warm bedside lighting. "
            "Atmosphere conveying deep restorative anabolic REM sleep where GH is naturally released, high aesthetic wellness and recovery photography."
        )
    },
    {
        "id": "ciclismo_estrada",
        "keywords": ["ciclismo", "pedal", "pernas", "velocidade", "endurance", "bicicleta", "bike"],
        "prompt": (
            "Action sports photography of handsome fit cyclist Evandro on a high-end matte black road bicycle along a scenic winding coastal road. "
            "Aerodynamic sleek dark cycling jersey, sports sunglasses pushed up, confident athletic posture, ocean cliffs in the background, cinematic daylight, 8k resolution, crisp detail."
        )
    },
    {
        "id": "recuperacao_biohacking",
        "keywords": ["bioimpedância", "balança", "cortisol", "metabolismo", "dados", "avaliação"],
        "prompt": (
            "Modern aesthetic 8k photograph of health innovator Evandro sitting comfortably on a wooden bench in a luxury biohacking recovery lounge. "
            "Wearing a minimalist black athletic crewneck, smiling charismatically while checking health metrics on his smartwatch, warm ambient wooden aesthetics, soft architectural lighting, photorealistic."
        )
    }
]

# Cenários adicionais para outras pessoas de IA (diversidade demográfica completa)
CENARIOS_PESSOAS_IA_DIVERSAS = [
    {
        "perfil": "mulher_jovem_praia",
        "prompt": (
            "Hyper-realistic 8k commercial photography of an athletic 28-year-old Brazilian woman with radiant glowing skin, toned abs and athletic physique. "
            "She is enjoying a refreshing morning walk on the golden sand of Rio de Janeiro beach, wearing a chic coral athletic sports bra and running shorts. "
            "Holding a fresh coconut with straw, joyful natural smile, ocean surf in background, warm tropical sunlight, Vogue Fitness style, 85mm lens."
        )
    },
    {
        "perfil": "mulher_madura_cozinha",
        "prompt": (
            "Photorealistic 8k portrait of an elegant 38-year-old woman with radiant firm skin and vibrant energy in a sunlit architectural designer kitchen. "
            "She is preparing a refreshing glass of collagen with mint and lemon slices, genuine warm smile, casual beige silk loungewear, soft morning light, ultra-detailed skin texture, luxury lifestyle."
        )
    },
    {
        "perfil": "mulher_senior_ativa_64",
        "prompt": (
            "Inspiring authentic 8k photograph of a vibrant active 64-year-old Brazilian woman full of vitality, performing light mobility exercises with a walking stick in a sunny botanical park. "
            "Wearing tasteful lilac athletic wear, silver-highlighted hair, beaming radiant healthy smile, confident posture showing strength and functional longevity, photorealistic."
        )
    },
    {
        "perfil": "homem_jovem_academia_24",
        "prompt": (
            "Cinematic 8k photograph of a dedicated 24-year-old athletic male athlete resting between heavy bench press sets in an elite bodybuilding gym. "
            "Defined vascular biceps, determined proud gaze, wearing a dark grey gym stringer, chalk on hands, moody cinematic rim lighting, photorealistic fitness cover."
        )
    },
    {
        "perfil": "homem_adulto_corrida_42",
        "prompt": (
            "Dynamic 8k action portrait of an active 42-year-old executive and marathon runner running along an ocean promenade at sunrise. "
            "Athletic build, energized focused smile, wearing a navy moisture-wicking running shirt and GPS sports watch, golden sunrise reflections on the sea, commercial fitness quality."
        )
    }
]

# Cenários de alta atratividade para exibição de produtos (SEM FUNDO BRANCO SEM VIDA!)
CENARIOS_PRODUTOS_LIFESTYLE = [
    {
        "ambiente": "cozinha_gourmet",
        "prompt_template": (
            "Luxury commercial product photography of {produto} displayed elegantly on a wet dark emerald marble and natural teak wood kitchen island. "
            "Surrounded by fresh organic yellow pineapple slices, vibrant fresh green mint leaves, scattered water droplets, soft morning sunbeams through sheer curtains, "
            "crisp 8k advertising shoot, zero artificial flat backgrounds, cinematic depth of field."
        )
    },
    {
        "ambiente": "borda_piscina_resort",
        "prompt_template": (
            "High-end resort commercial advertising shot of {produto} resting proudly on a polished teak wood poolside deck next to crystal-clear sparkling turquoise pool water. "
            "Golden hour warm sunlight reflecting sparkling water caustic patterns, chilled mist droplets on the container, luxurious tropical wellness ambiance, 8k resolution."
        )
    },
    {
        "ambiente": "banco_madeira_academia",
        "prompt_template": (
            "Moody high-end fitness commercial photograph of {produto} placed on a rustic dark gym bench alongside a pair of heavy knurled steel dumbbells and a clean shaker bottle. "
            "Warm amber dramatic backlighting, dark textured concrete gym walls softly blurred in the background, commercial supplement ad standard, photorealistic 8k."
        )
    },
    {
        "ambiente": "spa_zen_wellness",
        "prompt_template": (
            "Serene luxury spa commercial shot of {produto} surrounded by smooth volcanic black massage stones, fresh green bamboo leaves and a folded crisp white waffle towel. "
            "Soft zen candlelight and gentle warm morning diffused lighting, high-end dermatological clinic aesthetic, pristine 8k detail."
        )
    }
]


def montar_prompt_por_estilo(estilo: str, item: dict, eh_venda: bool = False) -> tuple:
    """
    Constrói prompt e seleciona imagem de referência com base na matriz expandida:
    - evandro: Rosto de Evandro com foto de referência em cenários múltiplos (academia, casa, praia, piscina, trilha, cozinha, sono).
    - marcao: Mascote Marcão hiper-realista e imponente.
    - pessoas_ia: Diversidade completa de faixas etárias e gêneros (jovem, madura, 64 anos, atletas).
    - produto_only / produto_lifestyle: Produtos em cenários requintados (SEM fundo branco!).
    Retorna (prompt_formatado, imagem_referencia_path).
    """
    ref_path = None
    fotos_evandro = obter_fotos_referencia_evandro()

    nome_item = item.get("nome") or item.get("tema") or "Fitness & Saúde"
    categoria = item.get("categoria", "SAÚDE")
    texto_busca = (nome_item + " " + categoria + " " + str(item.get("pontos", "")) + " " + str(item.get("headline", ""))).lower()

    if estilo == "evandro":
        if fotos_evandro:
            ref_path = fotos_evandro[0]
            instrucao_face = (
                "CRITICAL INSTRUCTION: Replicate the exact facial structure, facial features, hair, eyes and identity "
                "of the person shown in this reference photo. Render this exact person in the following dynamic athletic sports scene: "
            )
        else:
            instrucao_face = (
                "Cinematic 8k action photography of athletic health founder Evandro Gallina in the following dynamic sports scene: "
            )

        # Seleciona o melhor cenário esportivo alinhado com o tema ou faz rotação dinâmica
        cenario_escolhido = None
        for c in CENARIOS_ATLETICOS_EVANDRO:
            if any(kw in texto_busca for kw in c["keywords"]):
                cenario_escolhido = c
                break

        if not cenario_escolhido:
            idx_rot = (datetime.now().day + datetime.now().hour) % len(CENARIOS_ATLETICOS_EVANDRO)
            cenario_escolhido = CENARIOS_ATLETICOS_EVANDRO[idx_rot]

        prompt = f"{instrucao_face}{cenario_escolhido['prompt']}"

    elif estilo == "marcao":
        cenarios_marcao = [
            f"Cinematic 8k photograph of athletic muscular personal trainer Marcão (35 years old, fit, fierce and charismatic) posing confidently with crossed arms in an elite high-tech gym, energetic motivational atmosphere, warm dramatic rim lighting, hyper-realistic photography.",
            f"Hyper-realistic photograph of muscular coach Marcão jogging along the beach shoreline at sunrise, encouraging runners, wearing modern athletic dry-fit gear, natural ocean lighting, vibrant athletic energy.",
            f"Warm inspiring 8k photo of coach Marcão in a modern kitchen demonstrating healthy fitness nutrition, holding fresh ingredients with a friendly encouraging smile, clean lifestyle photography.",
            f"Action shot of Marcão demonstrating home bodyweight functional training in a living room, coaching proper posture with total enthusiasm and care, cinematic daylight."
        ]
        idx_m = (datetime.now().day + datetime.now().hour) % len(cenarios_marcao)
        prompt = cenarios_marcao[idx_m]

    elif estilo == "pessoas_ia":
        # Rotação inteligente por público e faixa etária
        if any(w in texto_busca for w in ["60", "64", "idoso", "articular", "menopausa", "caminhada"]):
            sel_p = CENARIOS_PESSOAS_IA_DIVERSAS[2]  # Mulher 64 anos
        elif any(w in texto_busca for w in ["colágeno", "pele", "flacidez", "estética", "rugas"]):
            sel_p = CENARIOS_PESSOAS_IA_DIVERSAS[1]  # Mulher 38 anos
        elif any(w in texto_busca for w in ["secar", "biquini", "gluteo", "cintura", "barriga"]):
            sel_p = CENARIOS_PESSOAS_IA_DIVERSAS[0]  # Mulher 28 anos
        elif any(w in texto_busca for w in ["creatina", "hipertrofia", "supino", "braço", "carga"]):
            sel_p = CENARIOS_PESSOAS_IA_DIVERSAS[3]  # Homem 24 anos
        else:
            sel_p = CENARIOS_PESSOAS_IA_DIVERSAS[4]  # Homem 42 anos corrida
        prompt = sel_p["prompt"]

    elif estilo in ["produto_only", "produto_lifestyle"]:
        idx_amb = (datetime.now().day + datetime.now().hour) % len(CENARIOS_PRODUTOS_LIFESTYLE)
        amb = CENARIOS_PRODUTOS_LIFESTYLE[idx_amb]
        prompt = amb["prompt_template"].format(produto=nome_item)

    else:  # infografico_trends
        prompt = (
            f"Futuristic dark cybernetic background with glowing cyan and emerald bioluminescent particles, soft medical grid lines, "
            f"minimalist high-tech aesthetic for fitness science and Google Trends queries regarding '{nome_item}', zero text, crisp 8k render."
        )

    return prompt, ref_path

def gerar_imagem_ultra_realista(prompt, nome_arquivo="gen_image.png", imagem_referencia_path=None):
    """
    Gera imagem cinematográfica 8k via OpenRouter (google/gemini-2.5-flash-image)
    com suporte multimodal a imagens de referência de rosto (ex: Evandro).
    Retorna o caminho local da imagem gerada, ou None se falhar.
    """
    if not OPENROUTER_API_KEY:
        print("[AI IMAGE] OpenRouter API Key ausente.")
        return None

    caminho_final = os.path.join(DIR_OUTPUT, nome_arquivo)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Se houver imagem de referência de rosto
    if imagem_referencia_path and os.path.exists(imagem_referencia_path):
        try:
            with open(imagem_referencia_path, "rb") as rf:
                ref_bytes = rf.read()
                ref_b64 = base64.b64encode(ref_bytes).decode("utf-8")
            ext = "jpeg" if imagem_referencia_path.lower().endswith((".jpg", ".jpeg")) else "png"
            content = [
                {
                    "type": "text",
                    "text": (
                        f"CRITICAL INSTRUCTION: Replicate the exact facial structure, facial features, hair, eyes and identity "
                        f"of the person shown in this reference image. Render this exact person in the following scene with hyper-realistic photography quality: "
                        f"{prompt}"
                    )
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{ext};base64,{ref_b64}"}
                }
            ]
        except Exception as e:
            print(f"[AI IMAGE] Erro carregando foto de referência: {e}")
            content = prompt
    else:
        content = prompt

    payload = {
        "model": "google/gemini-2.5-flash-image",
        "messages": [{"role": "user", "content": content}]
    }

    try:
        print(f"[AI IMAGE] Solicitando geração de imagem ultra-realista via OpenRouter...")
        with httpx.Client(verify=False, timeout=55) as client:
            resp = client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices and "images" in choices[0].get("message", {}):
                    img_entry = choices[0]["message"]["images"][0]
                    img_url = img_entry.get("image_url", {}).get("url", "")
                    if "base64," in img_url:
                        b64_str = img_url.split("base64,")[1]
                        raw_bytes = base64.b64decode(b64_str)
                        with open(caminho_final, "wb") as f:
                            f.write(raw_bytes)
                        print(f"[AI IMAGE] Imagem salva com sucesso: {caminho_final} ({len(raw_bytes)} bytes)")
                        return caminho_final
            else:
                print(f"[AI IMAGE] Erro OpenRouter {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[AI IMAGE] Falha na requisição OpenRouter: {e}")

    return None


# -------------------------------------------------------------------------
# 4. COMPOSITOR VISUAL CYBERNETIC (PILLOW)
# -------------------------------------------------------------------------
def carregar_logo_arredondado(tamanho=(110, 110)):
    """Carrega o logo oficial e aplica cantos arredondados suaves."""
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize(tamanho, Image.Resampling.LANCZOS)
            mascara = Image.new("L", tamanho, 0)
            ImageDraw.Draw(mascara).rounded_rectangle([0, 0, tamanho[0], tamanho[1]], radius=22, fill=255)
            logo.putalpha(mascara)
            return logo
        except Exception as e:
            print("[LOGO] Erro ao carregar logo:", e)
    return None


def obter_fontes_editoriais(tamanho_hero=120, tamanho_sub=28, tamanho_body=24):
    """Carrega as fontes editoriais oficiais do Marcão (Bebas Neue Display + Segoe UI / Arial de suporte)."""
    try:
        f_hero = ImageFont.truetype(FONT_BEBAS, tamanho_hero) if os.path.exists(FONT_BEBAS) else ImageFont.truetype("arialbd.ttf", tamanho_hero)
    except Exception:
        f_hero = ImageFont.load_default()

    try:
        font_bold = "segoeuib.ttf" if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else "arialbd.ttf"
        font_regular = "segoeui.ttf" if os.path.exists(r"C:\Windows\Fonts\segoeui.ttf") else "arial.ttf"
        f_tag = ImageFont.truetype(font_bold, 20)
        f_num = ImageFont.truetype(FONT_BEBAS, 44) if os.path.exists(FONT_BEBAS) else ImageFont.truetype("arialbd.ttf", 44)
        f_sub = ImageFont.truetype(font_bold, tamanho_sub)
        f_body = ImageFont.truetype(font_bold, tamanho_body)
        f_footer = ImageFont.truetype(font_bold, 18)
        f_cta = ImageFont.truetype(font_bold, 20)
    except Exception:
        f_tag = f_num = f_sub = f_body = f_footer = f_cta = ImageFont.load_default()

    return f_hero, f_tag, f_num, f_sub, f_body, f_footer, f_cta


def quebrar_linhas_por_palavras(texto, font, max_largura, draw):
    """Quebra o texto em linhas respeitando limites de palavras sem cortar sílabas."""
    palavras = [p for p in texto.split() if p.strip()]
    if not palavras:
        return []
    
    linhas = []
    linha_atual = []
    
    for p in palavras:
        teste = " ".join(linha_atual + [p])
        bbox = draw.textbbox((0, 0), teste, font=font)
        largura = bbox[2] - bbox[0]
        
        if largura <= max_largura:
            linha_atual.append(p)
        else:
            if linha_atual:
                linhas.append(" ".join(linha_atual))
                linha_atual = [p]
            else:
                linhas.append(p)
                linha_atual = []
                
    if linha_atual:
        linhas.append(" ".join(linha_atual))
        
    return linhas


def obter_fundo_editorial(bg_path=None):
    """
    Retorna uma imagem base 1080x1080. NUNCA retorna um fundo preto liso.
    Se bg_path existir, usa-o. Caso contrário, busca backgrounds fotográficos existentes
    do Marcão ou gera um gradiente de estúdio de alta profundidade.
    """
    if bg_path and os.path.exists(bg_path):
        try:
            return Image.open(bg_path).convert("RGBA").resize((1080, 1080), Image.Resampling.LANCZOS)
        except Exception:
            pass

    candidatos = [
        os.path.join(DIR_OUTPUT, "clean_bg_test.png"),
        os.path.join(DIR_OUTPUT, "test_marcao_gen.png"),
        os.path.join(ROOT_DIR, "apps", "api", "output", "clean_bg_test.png"),
        os.path.join(ROOT_DIR, "apps", "site", "public", "images", "posts", "test_marcao_gen.png"),
        MASCOTE_PATH
    ]
    for c in candidatos:
        if c and os.path.exists(c):
            try:
                return Image.open(c).convert("RGBA").resize((1080, 1080), Image.Resampling.LANCZOS)
            except Exception:
                pass

    # Gradiente obsidiana cinematográfico com sutil iluminação ambiente
    base = Image.new("RGBA", (1080, 1080), COR_BG_DEEP)
    draw_b = ImageDraw.Draw(base)
    for y in range(1080):
        val = int(8 + 14 * (y / 1080))
        draw_b.line([(0, y), (1080, y)], fill=(val, val + 3, val + 10, 255))
    return base


def obter_angulo_fallback(prod: dict) -> dict:
    """
    Retorna um ângulo criativo e persuasivo a partir de um pool variado para o produto.
    Garante que mesmo sem conexão externa haja diversidade editorial.
    """
    preco = prod.get("preco", "")
    sku = prod.get("sku", "")

    pool = {
        "CREATINA-MICRONIZADA-300G": [
            {
                "headline": "ATP: O COMBUSTÍVEL CELULAR",
                "subheadline": "Como a creatina micronizada transforma sua força muscular no treino:",
                "pontos": [
                    "Ressíntese acelerada de ATP nas séries mais pesadas.",
                    "Zero retenção extracelular: definição e tônus real."
                ],
                "categoria": "CIÊNCIA & HIPERTROFIA",
                "legenda": (
                    f"🔥 ATP: O Combustível Secreto das Séries Pesadas!\n\n"
                    f"Você sabia que seu músculo esgota a reserva primária de energia em menos de 8 segundos de esforço máximo?\n\n"
                    f"É exatamente aí que entra a Creatina Micronizada 100% Pura Nature's Prime. Ela acelera a ressíntese de fosfocreatina nas células musculares, permitindo mais repetições, mais carga e uma recuperação muscular muito mais rápida.\n\n"
                    f"💎 Pote oficial de 300g (100 doses diárias) por {preco}.\n\n"
                    f"👉 Quer garantir o lote com laudo oficial de pureza? Toque no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲"
                )
            },
            {
                "headline": "AUMENTO DE FORÇA EXPLOSIVA",
                "subheadline": "Mais densidade e volume muscular com pureza padrão laboratorial:",
                "pontos": [
                    "Pureza 100% testada em laudo oficial certificado.",
                    "Rende 100 doses diárias no pote de 300g."
                ],
                "categoria": "FORÇA & TÔNUS MUSCULAR",
                "legenda": (
                    f"💪 Mais força, mais carga e recuperação celular acelerada!\n\n"
                    f"A Creatina Micronizada Nature's Prime entrega pureza absoluta com laudo oficial. Não se trata apenas de puxar peso, mas de fornecer ao músculo a matéria-prima biológica para superar platôs de rendimento.\n\n"
                    f"💎 {preco} em até 12x no cartão com envio rastreado para todo o Brasil.\n\n"
                    f"👉 Acesse o LINK DA BIO em marcaopersonal.com ou comente \"QUERO\" para receber o link direto no seu direct! 📲"
                )
            }
        ],
        "AZEMPIKA-CANETA": [
            {
                "headline": "VASODILATAÇÃO ATIVA & VIGOR",
                "subheadline": "A ciência da circulação e firmeza masculina sem riscos ao coração:",
                "pontos": [
                    "Estímulo transdérmico de óxido nítrico localizado.",
                    "Aplicação prática em cliques: 100% seguro para a saúde."
                ],
                "categoria": "SAÚDE & VIGOR MASCULINO",
                "legenda": (
                    f"⚡ Vigor masculino e circulação ativa com segurança clínica inegociável!\n\n"
                    f"A Caneta Azempika Original atua através de bioestimulação transdérmica direta, promovendo vasodilatação natural sem exigir sobrecarga cardíaca ou causar taquicardia.\n\n"
                    f"💎 Apenas {preco} no lote promocional com embalagem discreta e envio seguro.\n\n"
                    f"👉 Toque no LINK NA BIO em marcaopersonal.com ou comente \"QUERO\" para receber no Direct! 📲"
                )
            }
        ],
        "COLAGENO-ACIDO-HIALURONICO": [
            {
                "headline": "RENOVAÇÃO DÉRMICA PROFUNDA",
                "subheadline": "Biopeptídeos ativos + ácido hialurônico para firmeza de dentro para fora:",
                "pontos": [
                    "Biopeptídeos que reativam a produção celular dérmica.",
                    "Sabor delicioso e refrescante de Abacaxi com Hortelã."
                ],
                "categoria": "ESTÉTICA FACIAL & DÉRMICA",
                "legenda": (
                    f"✨ Pele firme, hidratada e com viço radiante!\n\n"
                    f"A partir dos 25 anos, o corpo reduz drasticamente a síntese natural de colágeno. O Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime devolve a firmeza da pele e protege a flexibilidade articular com sabor irresistível de abacaxi com hortelã.\n\n"
                    f"💎 Apenas {preco} com garantia de procedência.\n\n"
                    f"👉 Link na bio em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲"
                )
            }
        ],
        "IARMONIZE-CAPILAR-KIT": [
            {
                "headline": "TERAPIA CAPILAR EM 4 FASES",
                "subheadline": "Protocolo clínico para interrupção de queda e oxigenação folicular:",
                "pontos": [
                    "Silício inteligente e complexo de biotina ativa.",
                    "Reativação direta da matriz biológica na raiz capilar."
                ],
                "categoria": "TECNOLOGIA ANTIQUEDA",
                "legenda": (
                    f"🌿 Chega de xampus milagrosos que vão embora pelo ralo!\n\n"
                    f"O Kit IArmonize Capilar Clínico atua em 4 fases integradas: nutrição interna profunda, bioestimulação folicular e revitalização do couro cabeludo.\n\n"
                    f"💎 Condição oficial em até 12x sem juros no site.\n\n"
                    f"👉 Link na bio em marcaopersonal.com ou comente \"QUERO\"! 📲"
                )
            }
        ],
        "VISION-PRIME-60CAPS": [
            {
                "headline": "PROTEÇÃO & ACUIDADE VISUAL",
                "subheadline": "Luteína e zeaxantina para combater o cansaço ocular das telas:",
                "pontos": [
                    "Filtragem ativa da luz azul artificial e raios UV.",
                    "Aumenta a nitidez, o contraste e o descanso ocular."
                ],
                "categoria": "SAÚDE OCULAR & FOCO",
                "legenda": (
                    f"👁️ Seus olhos passam mais de 8 horas por dia expostos a telas e luz azul?\n\n"
                    f"O Vision Prime fornece carotenoides nobres de alta pureza (luteína e zeaxantina) que formam um escudo protetor para a sua retina, combatendo ressecamento, fadiga e perda de foco.\n\n"
                    f"💎 Apenas {preco} por pote com 60 cápsulas.\n\n"
                    f"👉 Acesse marcaopersonal.com ou comente \"QUERO\"! 📲"
                )
            }
        ],
        "BALANCA-BIOIMPEDANCIA-BT": [
            {
                "headline": "O PESO NA BALANÇA MENTE",
                "subheadline": "Monitore percentual de gordura e massa magra em tempo real no app:",
                "pontos": [
                    "Mede bioimpedância completa via Bluetooth.",
                    "1 kg de gordura ocupa o triplo do volume muscular."
                ],
                "categoria": "BIOHACKING & COMPOSIÇÃO",
                "legenda": (
                    f"⚖️ Pare de se enganar com o peso bruto na balança comum!\n\n"
                    f"A Balança de Bioimpedância Bluetooth sincroniza com o celular e revela exatamente sua composição corporal: gordura visceral, massa muscular magra, hidratação e taxa metabólica.\n\n"
                    f"💎 Apenas {preco} com envio rápido para todo o país.\n\n"
                    f"👉 Garanta a sua no link da bio em marcaopersonal.com ou comente \"QUERO\"! 📲"
                )
            }
        ]
    }

    lista = pool.get(sku)
    if lista:
        escolhido = lista[int(time.time()) % len(lista)]
        return {
            "headline": escolhido["headline"],
            "subheadline": escolhido["subheadline"],
            "pontos": escolhido["pontos"],
            "categoria": escolhido["categoria"],
            "legenda": escolhido["legenda"]
        }

    return {
        "headline": prod.get("nome", "SUPLEMENTO").upper()[:35],
        "subheadline": f"Protocolo oficial Marcão Personal por {preco}:",
        "pontos": ["Padrão laboratorial com matéria-prima certificada.", "Envio rápido e seguro pelos Correios."],
        "categoria": prod.get("categoria", "SAÚDE & PERFORMANCE"),
        "legenda": f"🎯 Conheça {prod.get('nome')} no link da bio em marcaopersonal.com ou comente QUERO!"
    }


def gerar_angulo_criativo_com_ia(prod: dict) -> dict:
    """
    Gera dinamicamente um ângulo criativo, científico, persuasivo e NUNCA repetitivo
    para o produto usando Gemini 2.5 Flash via OpenRouter.
    """
    if not OPENROUTER_API_KEY:
        return obter_angulo_fallback(prod)

    nome_prod = prod.get("nome", "Suplemento")
    preco_prod = prod.get("preco", "")
    categoria_prod = prod.get("categoria", "BIOHACKING")

    prompt = (
        f"Você é o Diretor Criativo Sênior do Marcão Personal (@marcaopersonalfitness).\n"
        f"Crie um ângulo NOVO, CRIATIVO, INÉDITO e PERSUASIVO para um post de Instagram sobre o produto '{nome_prod}' ({preco_prod}).\n"
        f"CRÍTICO: NÃO use clichês repetidos como 'mais força, tônus no glúteo e definição sem retenção hídrica'.\n"
        f"Inove! Foque em ciência esportiva, biohacking, mecanismo fisiológico, energia celular ou rotina prática.\n\n"
        f"Retorne ESTRITAMENTE um JSON no seguinte formato (sem markdown):\n"
        f"{{\n"
        f'  "headline": "MANCHETE EM CAIXA ALTA (máximo 4 a 5 palavras impactantes)",\n'
        f'  "subheadline": "Gancho instigante em tom de autoridade (máximo 70 chars):",\n'
        f'  "pontos": [\n'
        f'    "Benefício fisiológico 1 direto (máximo 50 chars)",\n'
        f'    "Benefício fisiológico 2 direto (máximo 50 chars)"\n'
        f'  ],\n'
        f'  "categoria": "{categoria_prod}",\n'
        f'  "legenda": "Legenda completa, persuasiva, com quebras de linha naturais, emojis pontuais e chamada clara: toque no link da bio em marcaopersonal.com ou comente QUERO."\n'
        f"}}"
    )

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "google/gemini-2.5-flash",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8
        }
        with httpx.Client(verify=False, timeout=18) as client:
            resp = client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                raw = resp.json()["choices"][0]["message"]["content"]
                clean = re.sub(r"```json\s*", "", raw)
                clean = re.sub(r"```\s*", "", clean).strip()
                data = json.loads(clean)
                if data.get("headline") and data.get("pontos"):
                    print(f"[IA CREATIVE] Novo ângulo dinâmico gerado com sucesso para '{nome_prod}': {data['headline']}")
                    return data
    except Exception as e:
        print(f"[IA CREATIVE] Falha ao gerar ângulo dinâmico ({e}). Usando pool criativo de fallback.")

    return obter_angulo_fallback(prod)


def criar_slide_carrossel(titulo, subtitulo, pontos, cta_slide, num_slide, total_slides, categoria, out_path, bg_path=None, produto_img_path=None, preco=None):
    """
    Gera slide de carrossel (1080x1080) no estilo editorial moderno (@caiqueness inspired).
    Se for o slide final com produto, compõe o mockup no pedestal à direita mantendo o design limpo.
    """
    f_hero, f_tag, f_num, f_sub, f_body, f_footer, f_cta = obter_fontes_editoriais(tamanho_hero=90, tamanho_sub=26, tamanho_body=24)

    base = obter_fundo_editorial(bg_path)

    # Vinheta Dark Glassmorphism para leitura cristalina
    overlay = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    if num_slide == 1 and bg_path:
        # No Slide 1 (onde fica o rosto/personagem), preserva a área superior sem véu escuro
        for y in range(0, 1080):
            if y < 450:
                alpha = 25  # Quase transparente, rosto e ação 100% visíveis e iluminados
            else:
                alpha = int(25 + 215 * ((y - 450) / (1080 - 450)))
            draw_ov.line([(0, y), (1080, y)], fill=(7, 10, 16, alpha))
    else:
        for y in range(0, 1080):
            alpha = int(215 + 35 * (y / 1080))
            draw_ov.line([(0, y), (1080, y)], fill=(7, 10, 16, alpha))

    im = Image.alpha_composite(base, overlay)

    # Se for o slide de oferta com produto, adiciona brilho âmbar no lado direito
    tem_produto = produto_img_path and os.path.exists(produto_img_path) and (num_slide == total_slides)
    if tem_produto:
        try:
            glow_p = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
            draw_gp = ImageDraw.Draw(glow_p)
            for r in range(350, 0, -25):
                alpha_g = int(45 * (1 - r / 350))
                draw_gp.ellipse([820 - r, 540 - r, 820 + r, 540 + r], fill=(255, 120, 0, alpha_g))
            im = Image.alpha_composite(im, glow_p)

            p_img = Image.open(produto_img_path)
            if p_img.mode != "RGBA":
                p_img = p_img.convert("RGBA")
                mask = Image.new("L", p_img.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle([0, 0, p_img.width, p_img.height], radius=24, fill=255)
                p_img.putalpha(mask)

            p_img.thumbnail((360, 360), Image.Resampling.LANCZOS)
            sombra = Image.new("RGBA", (p_img.width + 60, 60), (0, 0, 0, 0))
            draw_sombra = ImageDraw.Draw(sombra)
            draw_sombra.ellipse([15, 15, p_img.width + 45, 50], fill=(0, 0, 0, 190))
            sombra = sombra.filter(ImageFilter.GaussianBlur(radius=14))

            pos_x = 1080 - p_img.width - 60
            pos_y = 420
            im.paste(sombra, (pos_x - 30, pos_y + p_img.height - 25), sombra)
            im.paste(p_img, (pos_x, pos_y), p_img)
        except Exception as e:
            print(f"[STUDIO] Aviso ao compor produto no slide: {e}")

    draw = ImageDraw.Draw(im)

    # 1. Topo: Tag de Categoria e Contador
    cat_str = f"BIOHACKING  •  PASSO 0{num_slide}" if num_slide < total_slides else f"BIOHACKING  •  OFERTA OFICIAL"
    draw.rounded_rectangle([60, 55, 410, 100], radius=22, fill=(14, 22, 36, 220), outline=COR_AMBER, width=2)
    draw.text((85, 67), cat_str, fill=COR_AMBER_LIGHT, font=f_tag)

    if preco and num_slide == total_slides:
        bbox_pr = draw.textbbox((0, 0), f"LOTE: {preco}", font=f_tag)
        pr_w = bbox_pr[2] - bbox_pr[0]
        draw.rounded_rectangle([980 - pr_w - 30, 55, 1020, 100], radius=22, fill=(14, 22, 36, 220), outline=COR_CYAN, width=2)
        draw.text((980 - pr_w - 15, 67), f"LOTE: {preco}", fill=COR_CYAN, font=f_tag)
    else:
        draw.text((980, 60), f"{num_slide}/{total_slides}", fill=COR_TEXT_MUTED, font=f_num)

    # 2. Título do Slide em Bebas Neue (quebra dinâmica)
    max_w_tit = 620 if tem_produto else 960
    titulo_limpo = sanitizar_texto_pillow(titulo).upper()
    linhas_titulo = quebrar_linhas_por_palavras(titulo_limpo, f_hero, max_w_tit, draw)
    if not linhas_titulo:
        linhas_titulo = [titulo_limpo]

    y_text = 150
    for linha in linhas_titulo[:2]:
        draw.text((60, y_text), linha, fill=COR_WHITE, font=f_hero)
        y_text += 85

    # 3. Subtítulo em Destaque Âmbar
    sub_limpo = sanitizar_texto_pillow(subtitulo)
    if sub_limpo:
        y_text += 8
        draw.text((60, y_text), sub_limpo, fill=COR_AMBER_LIGHT, font=f_sub)
        y_text += 45

    # 4. Tópicos em Cards Individuais com Bullets Cyan
    card_w = 620 if tem_produto else 1020
    text_w = 520 if tem_produto else 870
    y_pos = y_text + 15
    for p in pontos[:4]:
        p_limpo = sanitizar_texto_pillow(p)
        draw.rounded_rectangle([60, y_pos, card_w, y_pos + 82], radius=14, 
                               fill=(15, 23, 38, 230), outline=(35, 50, 75), width=1)
        draw.ellipse([85, y_pos + 32, 103, y_pos + 50], fill=COR_CYAN)
        linhas_p = quebrar_linhas_por_palavras(p_limpo, f_body, text_w, draw)
        y_p = y_pos + 18 if len(linhas_p) > 1 else y_pos + 26
        for lp in linhas_p[:2]:
            draw.text((120, y_p), lp, fill=COR_CREAM, font=f_body)
            y_p += 26
        y_pos += 95

    # 5. Rodapé Editorial & CTA com Blindagem Total Contra Colisão
    draw.line([(60, 985), (1020, 985)], fill=(35, 48, 70, 200), width=1)
    brand_text = "@MARCAOPERSONALFITNESS   |   marcaopersonal.com"
    draw.text((60, 1012), brand_text, fill=COR_TEXT_MUTED, font=f_footer)
    bbox_brand = draw.textbbox((0, 0), brand_text, font=f_footer)
    brand_right = 60 + (bbox_brand[2] - bbox_brand[0])

    cta_limpo = sanitizar_texto_pillow(cta_slide).replace("››", "").replace(">", "").strip()

    # Padronização de alta elegância editorial para rodapé:
    # Se for slide intermediário, usa 'ARRASTE'. Se for final, usa 'LINK NA BIO'.
    if "ARRAST" in cta_limpo.upper():
        cta_limpo = "ARRASTE"
    elif "BIO" in cta_limpo.upper() or "LINK" in cta_limpo.upper():
        cta_limpo = "LINK NA BIO"
    elif len(cta_limpo) > 16:
        cta_limpo = "ARRASTE" if num_slide < total_slides else "SAIBA MAIS"

    bbox_cta = draw.textbbox((0, 0), cta_limpo, font=f_cta)
    cta_w = bbox_cta[2] - bbox_cta[0]
    cta_x = 985 - cta_w

    # Blindagem matemática: zona de respiro mínima de 45px do endereço do site
    if cta_x <= brand_right + 45:
        cta_limpo = "ARRASTE" if num_slide < total_slides else "CONFIRA"
        bbox_cta = draw.textbbox((0, 0), cta_limpo, font=f_cta)
        cta_w = bbox_cta[2] - bbox_cta[0]
        cta_x = 985 - cta_w

    draw.text((cta_x, 1010), cta_limpo, fill=COR_AMBER, font=f_cta)
    desenhar_seta_minimalista(draw, 995, 1022, COR_AMBER, tamanho=15)

    im.convert("RGB").save(out_path, quality=96)
    print(f"[STUDIO] Slide Editorial {num_slide}/{total_slides} salvo: {out_path}")
    return out_path


def criar_card_unico(headline, subheadline, pontos, categoria, cta_texto, out_path, bg_path=None, produto_img_path=None, preco=None):
    """
    Gera um Card Único de Altíssimo Impacto Visual no padrão Adobe Creative Engine 2.0 (Feed 4:5 - 1080x1350).
    Composição profissional com tipografia de alta autoridade, selo de laudo e botão 3D.
    """
    try:
        from adobe_creative_engine import renderizar_criativo_masterpiece
        return renderizar_criativo_masterpiece(
            headline=headline,
            subheadline=subheadline,
            pontos_beneficio=pontos,
            categoria=categoria,
            cta_texto=cta_texto if cta_texto else "LEIA A LEGENDA",
            bg_path=bg_path,
            produto_img_path=produto_img_path,
            preco=preco,
            out_path=out_path,
            formato="feed",
            estilo_cor="gold_dark"
        )
    except Exception as e_master:
        print(f"[ADOBE ENGINE] Aviso: usando fallback legado no card único ({e_master})")

    # 1. Base (nunca preto liso)
    base = obter_fundo_editorial(bg_path)

    # 2. Iluminação Âmbar Quente + Vinheta de Fundo Gradual
    glow = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
    draw_glow = ImageDraw.Draw(glow)
    center_glow_x = 700 if produto_img_path else 540
    center_glow_y = 380 if produto_img_path else 300
    for r in range(480, 0, -25):
        alpha = int(48 * (1 - r / 480))
        draw_glow.ellipse([center_glow_x - r, center_glow_y - r, center_glow_x + r, center_glow_y + r], fill=(255, 120, 0, alpha))

    vignette = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
    draw_vig = ImageDraw.Draw(vignette)
    for y in range(0, 1080):
        if y < 180:
            a = int(170 * (1 - y / 180))
        elif y > (440 if produto_img_path else 380):
            lim_inf = 440 if produto_img_path else 380
            a = int(245 * ((y - lim_inf) / (1080 - lim_inf)))
        else:
            a = 35
        draw_vig.line([(0, y), (1080, y)], fill=(6, 9, 15, a))

    im = Image.alpha_composite(base, glow)
    im = Image.alpha_composite(im, vignette)

    # 3. Composição do Produto Real (se fornecido)
    if produto_img_path and os.path.exists(produto_img_path):
        try:
            p_img = Image.open(produto_img_path)
            # Se for imagem RGB sem transparência (banner), adiciona cantos arredondados elegantes
            if p_img.mode != "RGBA":
                p_img = p_img.convert("RGBA")
                mask = Image.new("L", p_img.size, 0)
                draw_m = ImageDraw.Draw(mask)
                draw_m.rounded_rectangle([0, 0, p_img.width, p_img.height], radius=24, fill=255)
                p_img.putalpha(mask)

            # REGRA MANDATÓRIA DE ARTE: ZONA DE EXCLUSÃO FACIAL
            # NUNCA posicionar produtos no terço superior (y: 50 a 550), onde ficam o rosto e os olhos do personagem!
            # O produto é posicionado no canto inferior direito com pedestal e iluminação própria.
            p_img.thumbnail((320, 320), Image.Resampling.LANCZOS)

            # Sombra suave com Gaussian Blur
            sombra = Image.new("RGBA", (p_img.width + 60, 60), (0, 0, 0, 0))
            draw_sombra = ImageDraw.Draw(sombra)
            draw_sombra.ellipse([15, 15, p_img.width + 45, 50], fill=(0, 0, 0, 180))
            sombra = sombra.filter(ImageFilter.GaussianBlur(radius=12))

            pos_x = 1080 - p_img.width - 50
            pos_y = 1080 - p_img.height - 120
            im.paste(sombra, (pos_x - 30, pos_y + p_img.height - 30), sombra)
            im.paste(p_img, (pos_x, pos_y), p_img)
        except Exception as e:
            print(f"[STUDIO] Aviso ao compor produto: {e}")

    draw = ImageDraw.Draw(im)

    # 4. Topo: Badge de Categoria e Lote Oficial / Preço
    f_tag = ImageFont.truetype("segoeuib.ttf", 20) if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else ImageFont.truetype("arialbd.ttf", 20)
    cat_str = f"BIOHACKING  •  {categoria.upper()}"
    bbox_tag = draw.textbbox((0, 0), cat_str, font=f_tag)
    tag_w = bbox_tag[2] - bbox_tag[0]

    if preco:
        # Categoria à esquerda
        tag_x = 60
        draw.rounded_rectangle([tag_x, 50, tag_x + tag_w + 36, 96], radius=20, 
                               fill=(12, 18, 30, 220), outline=COR_AMBER, width=2)
        draw.text((tag_x + 18, 63), cat_str, fill=COR_AMBER_LIGHT, font=f_tag)

        # Preço à direita
        preco_str = f"LOTE OFICIAL: {preco}"
        bbox_p = draw.textbbox((0, 0), preco_str, font=f_tag)
        pw = bbox_p[2] - bbox_p[0]
        draw.rounded_rectangle([1020 - pw - 36, 50, 1020, 96], radius=20,
                               fill=(12, 18, 30, 220), outline=COR_CYAN, width=2)
        draw.text((1020 - pw - 18, 63), preco_str, fill=COR_CYAN, font=f_tag)
    else:
        # Centralizado
        tag_x = (1080 - tag_w) // 2
        draw.rounded_rectangle([tag_x - 24, 55, tag_x + tag_w + 24, 102], radius=23, 
                               fill=(12, 18, 30, 220), outline=COR_AMBER, width=2)
        draw.text((tag_x, 68), cat_str, fill=COR_AMBER_LIGHT, font=f_tag)

    # 5. Headline Auto-Ajustável (Bebas Neue)
    max_w_head = 960
    tamanho_hero = 100 if produto_img_path else 110
    font_hero_path = FONT_BEBAS if os.path.exists(FONT_BEBAS) else "arialbd.ttf"
    f_hero = ImageFont.truetype(font_hero_path, tamanho_hero)

    head_limpo = sanitizar_texto_pillow(headline).upper()
    linhas_head = quebrar_linhas_por_palavras(head_limpo, f_hero, max_w_head, draw)
    while any((draw.textbbox((0, 0), l, font=f_hero)[2] - draw.textbbox((0, 0), l, font=f_hero)[0]) > max_w_head for l in linhas_head) and tamanho_hero > 60:
        tamanho_hero -= 5
        f_hero = ImageFont.truetype(font_hero_path, tamanho_hero)
        linhas_head = quebrar_linhas_por_palavras(head_limpo, f_hero, max_w_head, draw)

    if produto_img_path:
        y_text = 545 if len(linhas_head) <= 2 else 510
        max_linhas_head = 2
    else:
        y_text = 490 if len(linhas_head) <= 2 else 440
        max_linhas_head = 3

    line_h = int(tamanho_hero * 0.95)
    for linha in linhas_head[:max_linhas_head]:
        for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 4)]:
            draw.text((60 + ox, y_text + oy), linha, fill=(0, 0, 0, 240), font=f_hero)
        draw.text((60, y_text), linha, fill=COR_WHITE, font=f_hero)
        y_text += line_h

    # 6. Subheadline
    f_sub = ImageFont.truetype("segoeuib.ttf", 26) if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else ImageFont.truetype("arialbd.ttf", 26)
    sub_limpo = sanitizar_texto_pillow(subheadline)
    if sub_limpo:
        y_text += 8
        draw.text((60, y_text), sub_limpo, fill=COR_AMBER_LIGHT, font=f_sub)
        y_text += 44

    # 7. Benefícios em Cards com Bullets Neon Cyan
    f_body = ImageFont.truetype("segoeuib.ttf", 22) if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else ImageFont.truetype("arial.ttf", 22)
    for p in (pontos or [])[:2]:
        p_limpo = sanitizar_texto_pillow(p)
        y_text += 10
        linhas_p = quebrar_linhas_por_palavras(p_limpo, f_body, 870, draw)
        card_h = 58 if len(linhas_p) == 1 else 82
        draw.rounded_rectangle([60, y_text, 1020, y_text + card_h], radius=14, 
                               fill=(14, 22, 36, 235), outline=COR_CYAN, width=2)
        draw.ellipse([85, y_text + 21, 101, y_text + 37], fill=COR_CYAN)
        
        y_p = y_text + (17 if len(linhas_p) == 1 else 13)
        for lp in linhas_p:
            draw.text((115, y_p), lp, fill=COR_CREAM, font=f_body)
            y_p += 28
        y_text += card_h

    # 8. Rodapé Editorial & CTA
    f_footer = ImageFont.truetype("segoeuib.ttf", 18) if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else ImageFont.truetype("arialbd.ttf", 18)
    f_cta = ImageFont.truetype("segoeuib.ttf", 20) if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else ImageFont.truetype("arialbd.ttf", 20)
    draw.line([(60, 985), (1020, 985)], fill=(35, 48, 70, 200), width=1)
    brand_text = "@MARCAOPERSONALFITNESS   |   marcaopersonal.com"
    draw.text((60, 1012), brand_text, fill=COR_TEXT_MUTED, font=f_footer)
    bbox_brand = draw.textbbox((0, 0), brand_text, font=f_footer)
    brand_right = 60 + (bbox_brand[2] - bbox_brand[0])

    cta_limpo = sanitizar_texto_pillow(cta_texto).replace("››", "").replace(">", "").strip()
    if not cta_limpo or "ARRASTA" in cta_limpo.upper():
        cta_limpo = "LEIA A LEGENDA"

    # Prevenção de colisão de rodapé
    bbox_cta = draw.textbbox((0, 0), cta_limpo, font=f_cta)
    cta_w = bbox_cta[2] - bbox_cta[0]
    cta_x = 985 - cta_w
    if cta_x <= brand_right + 60:
        cta_limpo = "SAIBA MAIS"
        bbox_cta = draw.textbbox((0, 0), cta_limpo, font=f_cta)
        cta_w = bbox_cta[2] - bbox_cta[0]
        cta_x = 985 - cta_w

    draw.text((cta_x, 1010), cta_limpo, fill=COR_AMBER, font=f_cta)
    desenhar_seta_minimalista(draw, 1005, 1022, COR_AMBER, tamanho=15)

    im.convert("RGB").save(out_path, quality=96)
    print(f"[STUDIO] Card Único Editorial salvo: {out_path}")
    return out_path


def criar_card_feed_4x5(headline, subheadline, pontos, categoria, cta_texto, out_path, bg_path=None, produto_img_path=None, preco=None, nome_autor="EVANDRO GALLINA"):
    """
    Gera imagem de Feed Portrait (1080x1350 - 4:5) no padrão Adobe Creative Engine 2.0.
    Garante foto do personagem 100% nítida e iluminada, tipografia de alta autoridade,
    selo circular de procedência oficial, cartões glassmorphism e botão de conversão 3D.
    """
    try:
        from adobe_creative_engine import renderizar_criativo_masterpiece
        return renderizar_criativo_masterpiece(
            headline=headline,
            subheadline=subheadline,
            pontos_beneficio=pontos,
            categoria=categoria,
            cta_texto=cta_texto if cta_texto else "LEIA A LEGENDA",
            bg_path=bg_path,
            produto_img_path=produto_img_path,
            preco=preco,
            nome_autor=nome_autor,
            out_path=out_path,
            formato="feed",
            estilo_cor="gold_dark"
        )
    except Exception as e_master:
        print(f"[ADOBE ENGINE] Aviso: usando fallback legado no feed 4:5 ({e_master})")

    f_hero, f_tag, _, f_sub, f_body, f_footer, _ = obter_fontes_editoriais(tamanho_hero=78, tamanho_sub=25, tamanho_body=22)

    W, H = 1080, 1350
    canvas = Image.new("RGBA", (W, H), COR_BG_DEEP)

    # 1. Base da Imagem com o rosto e tronco no topo
    if bg_path and os.path.exists(bg_path):
        try:
            bg_img = Image.open(bg_path).convert("RGBA")
            scale = W / bg_img.width
            new_h = int(bg_img.height * scale)
            bg_scaled = bg_img.resize((W, new_h), Image.Resampling.LANCZOS)
            canvas.paste(bg_scaled, (0, 0))
        except Exception as e:
            print(f"[STUDIO] Aviso ao compor fundo 4:5: {e}")

    # 2. Gradiente suave para o card na base (y=560 a y=860)
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_grad = ImageDraw.Draw(grad)
    for y in range(560, 860):
        alpha = int(255 * ((y - 560) / 300))
        d_grad.line([(0, y), (W, y)], fill=(8, 12, 20, alpha))
    for y in range(860, H):
        d_grad.line([(0, y), (W, y)], fill=(8, 12, 20, 255))
    canvas = Image.alpha_composite(canvas, grad)
    draw = ImageDraw.Draw(canvas)

    # 3. Top Tag
    top_badge = f"GOOGLE TRENDS BRASIL  •  {categoria.upper()}" if categoria else f"{nome_autor.upper()}  •  MARCÃO PERSONAL"
    bbox_t = draw.textbbox((0, 0), top_badge, font=f_tag)
    tw = bbox_t[2] - bbox_t[0]
    tx = (W - tw) // 2
    draw.rounded_rectangle([tx - 24, 45, tx + tw + 24, 90], radius=20, fill=(10, 15, 26, 215), outline=COR_AMBER, width=2)
    draw.text((tx, 56), top_badge, fill=COR_AMBER_LIGHT, font=f_tag)

    # 4. Card Glassmorphic de Explicação (y=800 a y=1275)
    draw.rounded_rectangle([45, 800, 1035, 1275], radius=24, fill=(12, 18, 30, 245), outline=COR_AMBER, width=2)

    # Headline
    head_limpo = sanitizar_texto_pillow(headline).upper()
    linhas_head = quebrar_linhas_por_palavras(head_limpo, f_hero, 920, draw)
    y_t = 825
    for l in (linhas_head or [head_limpo])[:2]:
        for ox, oy in [(-2, -2), (2, -2), (0, 3)]:
            draw.text((75 + ox, y_t + oy), l, fill=(0, 0, 0, 235), font=f_hero)
        draw.text((75, y_t), l, fill=COR_WHITE, font=f_hero)
        y_t += 70

    # Subheadline
    sub_limpo = sanitizar_texto_pillow(subheadline)
    if sub_limpo:
        draw.text((75, y_t + 2), sub_limpo, fill=COR_AMBER_LIGHT, font=f_sub)
        y_t += 40

    # Bullets de explicação com marcadores neon cyan
    y_pos = y_t + 10
    for p in (pontos or [])[:3]:
        p_limpo = sanitizar_texto_pillow(p)
        draw.rounded_rectangle([75, y_pos, 1005, y_pos + 56], radius=12, fill=(18, 26, 42, 220), outline=(35, 48, 70), width=1)
        draw.ellipse([95, y_pos + 19, 113, y_pos + 37], fill=COR_CYAN)
        linhas_p = quebrar_linhas_por_palavras(p_limpo, f_body, 850, draw)
        if linhas_p:
            draw.text((128, y_pos + 15), linhas_p[0], fill=COR_WHITE, font=f_body)
        y_pos += 66

    # Se houver produto (mockup)
    if produto_img_path and os.path.exists(produto_img_path):
        try:
            p_img = Image.open(produto_img_path)
            if p_img.mode != "RGBA":
                p_img = p_img.convert("RGBA")
            p_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            canvas.paste(p_img, (810, 680), p_img)
        except Exception:
            pass

    # 5. Rodapé com Blindagem Total Contra Colisão
    draw.line([(60, 1295), (1020, 1295)], fill=(35, 48, 70, 200), width=1)
    brand_text = "@MARCAOPERSONALFITNESS   |   marcaopersonal.com"
    draw.text((60, 1312), brand_text, fill=COR_TEXT_MUTED, font=f_footer)
    bbox_brand = draw.textbbox((0, 0), brand_text, font=f_footer)
    brand_right = 60 + (bbox_brand[2] - bbox_brand[0])

    cta_limpo = sanitizar_texto_pillow(cta_texto).replace("››", "").replace(">", "").strip()
    if len(cta_limpo) > 22 or "BIO" in cta_limpo.upper():
        cta_limpo = "LINK NA BIO"
    elif not cta_limpo:
        cta_limpo = "LEIA A LEGENDA"

    cta_str = f"{cta_limpo} ››"
    bbox_cta = draw.textbbox((0, 0), cta_str, font=f_footer)
    cw = bbox_cta[2] - bbox_cta[0]
    cta_x = 1020 - cw
    if cta_x <= brand_right + 60:
        cta_str = "LEIA A LEGENDA ››"
        bbox_cta = draw.textbbox((0, 0), cta_str, font=f_footer)
        cw = bbox_cta[2] - bbox_cta[0]
        cta_x = 1020 - cw

    draw.text((cta_x, 1312), cta_str, fill=COR_AMBER_LIGHT, font=f_footer)

    canvas.convert("RGB").save(out_path, quality=96)
    print(f"[STUDIO] Card Feed 4:5 salvo com sucesso: {out_path}")
    return out_path


def criar_story(headline, subheadline, pontos, categoria, cta_texto, out_path, bg_path=None, produto_img_path=None, preco=None, nome_autor="EVANDRO GALLINA"):
    """
    Gera imagem de Story vertical (1080x1920 - 9:16) no padrão Adobe Creative Engine 2.0.
    Enquadra a foto de ação esportiva com zona de foco no topo, tipografia editorial,
    selo circular metálico, cartões glassmorphism e sticker botão 3D de alta conversão.
    """
    try:
        from adobe_creative_engine import renderizar_criativo_masterpiece
        return renderizar_criativo_masterpiece(
            headline=headline,
            subheadline=subheadline,
            pontos_beneficio=pontos,
            categoria=categoria,
            cta_texto=cta_texto if cta_texto else "TOQUE NO LINK",
            bg_path=bg_path,
            produto_img_path=produto_img_path,
            preco=preco,
            nome_autor=nome_autor,
            out_path=out_path,
            formato="story",
            estilo_cor="gold_dark"
        )
    except Exception as e_master:
        print(f"[ADOBE ENGINE] Aviso: usando fallback legado no story ({e_master})")

    f_hero, f_tag, _, f_sub, f_body, _, f_btn = obter_fontes_editoriais(tamanho_hero=84, tamanho_sub=25, tamanho_body=23)

    W, H = 1080, 1920
    story = Image.new("RGBA", (W, H), COR_BG_DEEP)

    # 1. Base da Imagem - Escala para cobrir topo com largura total sem barras pretas
    if bg_path and os.path.exists(bg_path):
        try:
            bg_img = Image.open(bg_path).convert("RGBA")
            target_w = 1080
            target_h = int(bg_img.height * (target_w / bg_img.width))
            bg_scaled = bg_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            story.paste(bg_scaled, (0, 0))
        except Exception:
            pass

    # 2. Gradiente suave e contínuo de transição da foto para o card (y=700 a y=1200)
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_grad = ImageDraw.Draw(grad)
    for y in range(700, 1200):
        alpha = int(255 * ((y - 700) / 500))
        d_grad.line([(0, y), (W, y)], fill=(8, 12, 20, alpha))
    for y in range(1200, H):
        d_grad.line([(0, y), (W, y)], fill=(8, 12, 20, 255))

    story = Image.alpha_composite(story, grad)
    draw = ImageDraw.Draw(story)

    # 3. Top Tag Translúcida com Badge do Google Trends / Autor
    top_badge = f"GOOGLE TRENDS BRASIL  •  {categoria.upper()}" if categoria else f"{nome_autor.upper()}  •  MARCÃO PERSONAL"
    bbox_t = draw.textbbox((0, 0), top_badge, font=f_tag)
    tw = bbox_t[2] - bbox_t[0]
    tx = (W - tw) // 2
    draw.rounded_rectangle([tx - 24, 70, tx + tw + 24, 116], radius=22, fill=(10, 15, 26, 215), outline=COR_AMBER, width=2)
    draw.text((tx, 82), top_badge, fill=COR_AMBER_LIGHT, font=f_tag)

    # 4. Container Editorial Dark Glassmorphic na Base (y=1120 a 1855)
    draw.rounded_rectangle([45, 1120, 1035, 1855], radius=28, fill=(12, 18, 30, 240), outline=COR_AMBER, width=2)

    # Headline em Bebas Neue com sombra de alto relevo
    head_limpo = sanitizar_texto_pillow(headline).upper()
    linhas_head = quebrar_linhas_por_palavras(head_limpo, f_hero, 910, draw)
    if not linhas_head:
        linhas_head = [head_limpo]

    y_t = 1155
    for linha in linhas_head[:2]:
        for ox, oy in [(-2, -2), (2, -2), (0, 3)]:
            draw.text((80 + ox, y_t + oy), linha, fill=(0, 0, 0, 235), font=f_hero)
        draw.text((80, y_t), linha, fill=COR_WHITE, font=f_hero)
        y_t += 84

    sub_limpo = sanitizar_texto_pillow(subheadline)
    if sub_limpo:
        draw.text((80, y_t + 5), sub_limpo, fill=COR_AMBER_LIGHT, font=f_sub)
        y_t += 48

    # 5. Micro-Cards Estilizados para os Bullets (sem vazios)
    y_pos = y_t + 10
    for p in (pontos or [])[:3]:
        p_limpo = sanitizar_texto_pillow(p)
        draw.rounded_rectangle([75, y_pos, 1005, y_pos + 62], radius=14, fill=(18, 26, 42, 220), outline=(35, 48, 70), width=1)
        draw.ellipse([95, y_pos + 22, 113, y_pos + 40], fill=COR_CYAN)
        linhas_p = quebrar_linhas_por_palavras(p_limpo, f_body, 850, draw)
        if linhas_p:
            draw.text((128, y_pos + 17), linhas_p[0], fill=COR_WHITE, font=f_body)
        y_pos += 72

    # Se houver mockup de produto, adiciona com sombra realista
    if produto_img_path and os.path.exists(produto_img_path):
        try:
            p_img = Image.open(produto_img_path)
            if p_img.mode != "RGBA":
                p_img = p_img.convert("RGBA")
            p_img.thumbnail((210, 210), Image.Resampling.LANCZOS)
            pos_x, pos_y = 800, 940
            story.paste(p_img, (pos_x, pos_y), p_img)
        except Exception:
            pass

    # 6. Botão / Link Sticker de Alta Conversão no Instagram
    btn_y = 1715
    draw.rounded_rectangle([75, btn_y, 1005, btn_y + 105], radius=24, fill=(234, 88, 12), outline=COR_WHITE, width=2)
    cta_limpo = sanitizar_texto_pillow(cta_texto).replace("››", "").replace(">", "").strip()
    if not cta_limpo or "ARRASTA" in cta_limpo.upper():
        cta_limpo = "TOQUE PARA ACESSAR"
    btn_str = f"{cta_limpo}  •  marcaopersonal.com  >"
    bbox_btn = draw.textbbox((0, 0), btn_str, font=f_btn)
    btn_w = bbox_btn[2] - bbox_btn[0]
    btn_x = (W - btn_w) // 2
    draw.text((btn_x, btn_y + 36), btn_str, fill=COR_WHITE, font=f_btn)

    story.convert("RGB").save(out_path, quality=96)
    print(f"[STUDIO] Story Editorial salvo: {out_path}")
    return out_path



# -------------------------------------------------------------------------
# 5. UPLOAD PARA SUPABASE STORAGE (BUCKET PÚBLICO: CREATIVOS)
# -------------------------------------------------------------------------
def upload_supabase_storage(caminho_arquivo, nome_remoto=None):
    """
    Faz upload de um arquivo para o bucket público 'creativos' no Supabase Storage.
    Retorna a URL pública permanente na CDN do Supabase.
    """
    if not SUPABASE_KEY:
        print("[STORAGE] SUPABASE_KEY não configurada para upload.")
        return None

    if not nome_remoto:
        nome_remoto = os.path.basename(caminho_arquivo)

    url_upload = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{nome_remoto}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg"
    }

    try:
        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()

        with httpx.Client(verify=False, timeout=30) as client:
            resp = client.post(url_upload, headers=headers, content=conteudo)
            if resp.status_code in [200, 201]:
                url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{nome_remoto}"
                print(f"[STORAGE] Upload concluído com sucesso: {url_publica}")
                return url_publica
            else:
                # Se já existir, tentar sobrescrever com PUT
                resp_put = client.put(url_upload, headers=headers, content=conteudo)
                if resp_put.status_code in [200, 201]:
                    url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{nome_remoto}"
                    print(f"[STORAGE] Atualizado com sucesso: {url_publica}")
                    return url_publica
                print(f"[STORAGE] Erro no upload: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[STORAGE] Falha no upload para Supabase Storage: {e}")

    return None


# -------------------------------------------------------------------------
# 6. PUBLICADOR OFICIAL NO INSTAGRAM GRAPH API (CARROSSEL OU CARD)
# -------------------------------------------------------------------------
def publicar_card_instagram(image_url, legenda):
    """
    Publica um Card Único de imagem no Instagram (@marcaopersonalfitness).
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        return {"sucesso": False, "erro": "Credenciais do Instagram ausentes"}

    url_container = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": legenda,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    try:
        with httpx.Client(verify=False, timeout=30) as client:
            r = client.post(url_container, data=payload)
            if r.status_code != 200:
                return {"sucesso": False, "etapa": "container", "erro": r.text}

            creation_id = r.json().get("id")

            # Aguardar status FINISHED
            for _ in range(8):
                time.sleep(3)
                st = client.get(f"https://graph.instagram.com/v21.0/{creation_id}", params={"fields": "status_code", "access_token": INSTAGRAM_ACCESS_TOKEN}).json()
                if st.get("status_code") == "FINISHED":
                    break

            # Publicar
            r_pub = client.post(f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media_publish", data={
                "creation_id": creation_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            })
            if r_pub.status_code != 200:
                return {"sucesso": False, "etapa": "publicacao", "erro": r_pub.text}

            post_id = r_pub.json().get("id")

            # Obter permalink
            r_info = client.get(f"https://graph.instagram.com/v21.0/{post_id}", params={"fields": "permalink", "access_token": INSTAGRAM_ACCESS_TOKEN}).json()
            permalink = r_info.get("permalink", f"https://www.instagram.com/p/{post_id}/")

            registrar_no_content_calendar(post_id, legenda, image_url, permalink, "single_card")

            return {
                "sucesso": True,
                "post_id": post_id,
                "permalink": permalink,
                "media_type": "IMAGE"
            }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def publicar_carrossel_instagram(image_urls, legenda):
    """
    Publica um Álbum Carrossel de 2 a 10 imagens no Instagram (@marcaopersonalfitness).
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        return {"sucesso": False, "erro": "Credenciais do Instagram ausentes"}

    if len(image_urls) < 2:
        return publicar_card_instagram(image_urls[0], legenda)

    try:
        with httpx.Client(verify=False, timeout=40) as client:
            item_ids = []

            # 1. Criar container de cada item do carrossel
            for idx, img_url in enumerate(image_urls):
                res_item = client.post(f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media", data={
                    "image_url": img_url,
                    "is_carousel_item": "true",
                    "access_token": INSTAGRAM_ACCESS_TOKEN
                })
                if res_item.status_code != 200:
                    return {"sucesso": False, "etapa": f"item_{idx+1}", "erro": res_item.text}
                item_ids.append(res_item.json().get("id"))

            # 2. Aguardar processamento de todos os itens
            for it_id in item_ids:
                for _ in range(8):
                    time.sleep(2)
                    st = client.get(f"https://graph.instagram.com/v21.0/{it_id}", params={"fields": "status_code", "access_token": INSTAGRAM_ACCESS_TOKEN}).json()
                    if st.get("status_code") == "FINISHED":
                        break

            # 3. Criar container pai do Carrossel
            children_str = ",".join(item_ids)
            res_parent = client.post(f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media", data={
                "media_type": "CAROUSEL",
                "children": children_str,
                "caption": legenda,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            })
            if res_parent.status_code != 200:
                return {"sucesso": False, "etapa": "parent_carousel", "erro": res_parent.text}

            carousel_creation_id = res_parent.json().get("id")

            # 4. Aguardar status do container do carrossel
            for _ in range(8):
                time.sleep(3)
                st_car = client.get(f"https://graph.instagram.com/v21.0/{carousel_creation_id}", params={"fields": "status_code", "access_token": INSTAGRAM_ACCESS_TOKEN}).json()
                if st_car.get("status_code") == "FINISHED":
                    break

            # 5. Publicar o Carrossel
            res_pub = client.post(f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media_publish", data={
                "creation_id": carousel_creation_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            })
            if res_pub.status_code != 200:
                return {"sucesso": False, "etapa": "publicar_carrossel", "erro": res_pub.text}

            post_id = res_pub.json().get("id")

            # 6. Obter permalink
            r_info = client.get(f"https://graph.instagram.com/v21.0/{post_id}", params={"fields": "permalink", "access_token": INSTAGRAM_ACCESS_TOKEN}).json()
            permalink = r_info.get("permalink", f"https://www.instagram.com/p/{post_id}/")

            registrar_no_content_calendar(post_id, legenda, image_urls[0], permalink, "carousel_album")

            return {
                "sucesso": True,
                "post_id": post_id,
                "permalink": permalink,
                "media_type": "CAROUSEL_ALBUM",
                "total_slides": len(image_urls)
            }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def publicar_story_instagram(image_url):
    """
    Publica uma imagem no Instagram Stories (@marcaopersonalfitness).
    Requer imagem na proporção 9:16 (1080x1920).
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        return {"sucesso": False, "erro": "Credenciais do Instagram ausentes"}

    try:
        with httpx.Client(verify=False, timeout=30) as client:
            r_cont = client.post(f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media", data={
                "image_url": image_url,
                "media_type": "STORIES",
                "access_token": INSTAGRAM_ACCESS_TOKEN
            })
            if r_cont.status_code != 200:
                return {"sucesso": False, "etapa": "story_container", "erro": r_cont.text}

            creation_id = r_cont.json().get("id")

            for _ in range(8):
                time.sleep(3)
                st = client.get(f"https://graph.instagram.com/v21.0/{creation_id}", params={"fields": "status_code", "access_token": INSTAGRAM_ACCESS_TOKEN}).json()
                if st.get("status_code") == "FINISHED":
                    break

            r_pub = client.post(f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media_publish", data={
                "creation_id": creation_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            })
            if r_pub.status_code != 200:
                return {"sucesso": False, "etapa": "story_publish", "erro": r_pub.text}

            story_id = r_pub.json().get("id")
            registrar_no_content_calendar(story_id, "Story Instagram", image_url, "https://www.instagram.com/stories/marcaopersonalfitness/", "story")

            return {
                "sucesso": True,
                "story_id": story_id,
                "media_type": "STORIES"
            }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def registrar_no_content_calendar(post_id, legenda, media_url, permalink, formato):
    """Registra a postagem no banco de dados Supabase."""
    if not SUPABASE_KEY:
        return
    try:
        dados = {
            "platform": "instagram",
            "content_id": post_id,
            "caption": legenda[:500],
            "media_url": media_url,
            "status": "published",
            "published_at": datetime.now().isoformat()
        }
        with httpx.Client(verify=False, timeout=10) as client:
            client.post(
                f"{SUPABASE_URL}/rest/v1/content_calendar",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                json=dados
            )
    except Exception:
        pass


# -------------------------------------------------------------------------
# 7. CICLOS DIÁRIOS DE PRODUÇÃO (MANHÃ 11:30 & NOITE 19:30)
# -------------------------------------------------------------------------
def executar_ciclo_manha(indice=None, formato="carrossel", usar_ia=True, dry_run=False, estilo_visual="evandro", postar_story=True):
    """
    Executa o Post da Manhã (11:30): Curiosidade, Ciência & Entretenimento.
    Por padrão utiliza o rosto de Evandro Gallina em cenários de alta autoridade científica
    e publica automaticamente nos Stories do Instagram.
    """
    temas_ativos = [t for t in TEMAS_CURIOSIDADES if not t.get("desativado")]
    if indice is None:
        indice = datetime.now().day % len(temas_ativos)
    tema = temas_ativos[indice % len(temas_ativos)]

    PERSONAS_DIVERSIDADE = [
        "evandro", "marcao", "mascote",
        "mulher_jovem", "mulher_adulta", "mulher_senior",
        "homem_jovem", "homem_adulto", "homem_senior"
    ]
    estilo_escolhido = estilo_visual if estilo_visual != "auto" else random.choice(PERSONAS_DIVERSIDADE)

    print(f"\n[FÁBRICA 11:30] Iniciando produção do Post de Curiosidade: '{tema['tema']}' | Estilo: {estilo_escolhido.upper()}")

    # 1. Obter imagem base e criativo com proteção Anti-Repetição
    bg_local = None
    if usar_ia:
        try:
            from anti_repetition_guard import gerar_angulo_criativo_inedito, gerar_imagem_inedita_openrouter
            criativo_inedito = gerar_angulo_criativo_inedito(tema_escolhido=tema.get("tema"), tipo="manha", estilo_visual=estilo_escolhido)
            tema["headline"] = criativo_inedito.get("headline", tema["headline"])
            tema["subheadline"] = criativo_inedito.get("subheadline", tema["subheadline"])
            tema["pontos_card"] = criativo_inedito.get("pontos", tema["pontos_card"])
            tema["categoria"] = criativo_inedito.get("categoria", tema["categoria"])
            tema["legenda"] = criativo_inedito.get("legenda", tema["legenda"])
            nome_ia = f"bg_{tema['id']}_{estilo_escolhido}_{int(time.time())}.png"
            bg_local = gerar_imagem_inedita_openrouter(criativo_inedito.get("prompt_fotografico", ""), nome_ia)
        except Exception as e_ia:
            print(f"[FÁBRICA 11:30] Falha no gerador inédito IA: {e_ia}")
            prompt_estilo, ref_img = montar_prompt_por_estilo(estilo_escolhido, tema, eh_venda=False)
            nome_ia = f"bg_{tema['id']}_{estilo_escolhido}_{int(time.time())}.png"
            bg_local = gerar_imagem_ultra_realista(prompt_estilo, nome_ia, imagem_referencia_path=ref_img)

    if not bg_local or not os.path.exists(bg_local):
        bg_local = MASCOTE_PATH if os.path.exists(MASCOTE_PATH) else None

    # 2. Renderizar formato escolhido
    timestamp = int(time.time())
    res_final = {}

    if formato == "carrossel":
        slides_gerados = []
        for idx, s in enumerate(tema["slides_carrossel"]):
            out_file = os.path.join(DIR_OUTPUT, f"slide_{tema['id']}_{idx+1}_{timestamp}.jpg")
            criar_slide_carrossel(
                titulo=s["titulo"],
                subtitulo=s["sub"],
                pontos=s["pontos"],
                cta_slide=s["cta"],
                num_slide=idx+1,
                total_slides=len(tema["slides_carrossel"]),
                categoria=tema["categoria"],
                out_path=out_file,
                bg_path=bg_local if idx == 0 else None
            )
            slides_gerados.append(out_file)

        urls_publicadas = []
        for s_path in slides_gerados:
            url_storage = upload_supabase_storage(s_path)
            if url_storage:
                urls_publicadas.append(url_storage)

        if dry_run:
            res_final = {"sucesso": True, "modo": "dry_run", "slides": urls_publicadas, "legenda": tema["legenda"]}
        else:
            res_pub = publicar_carrossel_instagram(urls_publicadas, tema["legenda"])
            res_final = res_pub

    else:
        # Card Feed 4:5 com Paridade Total em Relação ao Story
        out_file = os.path.join(DIR_OUTPUT, f"card_{tema['id']}_{timestamp}.jpg")
        criar_card_feed_4x5(
            headline=tema["headline"],
            subheadline=tema["subheadline"],
            pontos=tema["pontos_card"],
            categoria=tema["categoria"],
            cta_texto="LEIA A LEGENDA COMPLETA",
            out_path=out_file,
            bg_path=bg_local,
            nome_autor="EVANDRO GALLINA" if estilo_escolhido == "evandro" else "MARCÃO PERSONAL"
        )
        url_storage = upload_supabase_storage(out_file)
        if dry_run:
            res_final = {"sucesso": True, "modo": "dry_run", "imagem": url_storage, "legenda": tema["legenda"]}
        else:
            res_pub = publicar_card_instagram(url_storage, tema["legenda"])
            res_final = res_pub

    # Geração e Publicação Obrigatória nos Stories
    if postar_story:
        story_file = os.path.join(DIR_OUTPUT, f"story_{tema['id']}_{timestamp}.jpg")
        criar_story(
            headline=tema["headline"],
            subheadline=tema["subheadline"],
            pontos=tema["pontos_card"],
            categoria=tema["categoria"],
            cta_texto="LEIA O POST COMPLETO",
            out_path=story_file,
            bg_path=bg_local,
            nome_autor="EVANDRO GALLINA" if estilo_escolhido == "evandro" else "MARCÃO PERSONAL"
        )
        url_story = upload_supabase_storage(story_file)
        if url_story:
            if dry_run:
                res_final["story"] = {"sucesso": True, "modo": "dry_run", "imagem": url_story}
            else:
                res_story = publicar_story_instagram(url_story)
                res_final["story"] = res_story

    return res_final


def executar_ciclo_noite(indice=None, formato="carrossel", usar_ia=True, dry_run=False, estilo_visual="evandro", postar_story=True):
    """
    Executa o Post da Noite (19:30): Venda de Produto & Conversão Direta.
    Gera ângulos criativos dinâmicos com IA, compõe o mockup real do produto no card,
    utiliza o rosto de Evandro Gallina para máxima autoridade e publica nos Stories.
    Este post fica automaticamente elegível para o Rui impulsionar no Meta Ads!
    """
    produtos_ativos = [p for p in PRODUTOS_CATALOGO if not p.get("desativado")]
    if indice is None:
        indice = (datetime.now().day + datetime.now().hour) % len(produtos_ativos)
    prod = produtos_ativos[indice % len(produtos_ativos)]

    PERSONAS_DIVERSIDADE = [
        "evandro", "marcao", "mascote",
        "mulher_jovem", "mulher_adulta", "mulher_senior",
        "homem_jovem", "homem_adulto", "homem_senior"
    ]
    estilo_escolhido = estilo_visual if estilo_visual != "auto" else random.choice(PERSONAS_DIVERSIDADE)

    print(f"\n[FÁBRICA 19:30] Iniciando produção do Post de Venda: '{prod['nome']}' | Estilo: {estilo_escolhido.upper()}")

    # 1. Ângulo Criativo Inédito & Nova Imagem com Proteção Anti-Repetição
    bg_local = None
    if usar_ia:
        try:
            from anti_repetition_guard import gerar_angulo_criativo_inedito, gerar_imagem_inedita_openrouter
            criativo_inedito = gerar_angulo_criativo_inedito(tema_escolhido=prod.get("nome"), tipo="noite", estilo_visual=estilo_escolhido)
            headline = criativo_inedito.get("headline", prod["nome"].upper()[:35])
            sub = criativo_inedito.get("subheadline", f"Protocolo oficial Marcão Personal por {prod['preco']}:")
            pontos = criativo_inedito.get("pontos", ["Matéria-prima de padrão laboratorial.", f"Lote oficial por {prod['preco']}."])
            categoria = criativo_inedito.get("categoria", prod["categoria"])
            legenda = criativo_inedito.get("legenda")
            nome_ia = f"bg_{prod['sku']}_{estilo_escolhido}_{int(time.time())}.png"
            bg_local = gerar_imagem_inedita_openrouter(criativo_inedito.get("prompt_fotografico", ""), nome_ia)
        except Exception as e_ia:
            print(f"[FÁBRICA 19:30] Falha no gerador inédito IA: {e_ia}")
            angulo = gerar_angulo_criativo_com_ia(prod)
            headline = angulo.get("headline", prod["nome"].upper()[:35])
            sub = angulo.get("subheadline", f"Protocolo oficial Marcão Personal por {prod['preco']}:")
            pontos = angulo.get("pontos", ["Matéria-prima de padrão laboratorial.", f"Lote oficial por {prod['preco']}."])
            categoria = angulo.get("categoria", prod["categoria"])
            legenda = angulo.get("legenda")
            prompt_estilo, ref_img = montar_prompt_por_estilo(estilo_escolhido, prod, eh_venda=True)
            nome_ia = f"bg_{prod['sku']}_{estilo_escolhido}_{int(time.time())}.png"
            bg_local = gerar_imagem_ultra_realista(prompt_estilo, nome_ia, imagem_referencia_path=ref_img)
    else:
        angulo = obter_angulo_fallback(prod)
        headline = angulo.get("headline", prod["nome"].upper()[:35])
        sub = angulo.get("subheadline", f"Protocolo oficial Marcão Personal por {prod['preco']}:")
        pontos = angulo.get("pontos", ["Matéria-prima de padrão laboratorial.", f"Lote oficial por {prod['preco']}."])
        categoria = angulo.get("categoria", prod["categoria"])
        legenda = angulo.get("legenda")

    if not legenda:
        legenda = (
            f"🎯 {headline} — CONDIÇÃO EXCLUSIVA DE HOJE! ⚡\n\n"
            f"{sub}\n\n"
            f"Se você busca resultados corporais de alto nível sem perder tempo com promessas vazias, "
            f"a qualidade dos protocolos recomendados pelo Marcão é inegociável.\n\n"
            f"💎 {prod['preco']} com envio rápido e seguro pelos Correios para todo o Brasil!\n\n"
            f"👉 Quer garantir o seu antes que o lote promocional acabe?\n"
            f"Toque agora no LINK DA BIO em marcaopersonal.com ou COMENTE \"QUERO\" aqui embaixo que eu te envio o link direto no seu Direct! 📲\n\n"
            f"#marcao #suplementos #saude #estetica #performance #qualidadedevida #fitness"
        )

    timestamp = int(time.time())
    res_final = {}

    if formato == "carrossel":
        slides = [
            {
                "titulo": f"O SEGREDO DO RESULTADO:\n{headline}",
                "sub": sub,
                "pontos": [
                    "Fórmula desenvolvida com padrão farmacêutico de pureza.",
                    "Recomendado pelo protocolo oficial Marcão Personal 360°.",
                    "Absorção acelerada para quem treina de verdade.",
                    "Resultados comprovados por centenas de alunos."
                ],
                "cta": "ARRASTE E VEJA OS BENEFÍCIOS CLÍNICOS ››"
            },
            {
                "titulo": "POR QUE ESTE SUPLEMENTO\nÉ DIFERENTE DOS OUTROS?",
                "sub": "A garantia inegociável de laudo e matéria-prima:",
                "pontos": [
                    "Zero adição de açúcares, corantes ou conservantes ruins.",
                    "Laudo laboratorial disponível para cada lote fabricado.",
                    "Embalagem selada e proteção térmica no transporte.",
                    "Excelente custo-benefício por dose ativa."
                ],
                "cta": "COMO GARANTIR O SEU? VEJA A OFERTA ››"
            },
            {
                "titulo": f"OFERTA OFICIAL MARCÃO PERSONAL\n{prod['preco']} COM FRETE RASTREADO",
                "sub": "Garanta a condição de hoje direto do fabricante:",
                "pontos": [
                    f"Valor especial do lote: {prod['preco']}.",
                    "Despacho rápido pelos Correios em todo o Brasil.",
                    "Garantia oficial de procedência e nota fiscal.",
                    "Atendimento direto com o Marcão pelo WhatsApp e Direct."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ]
        slides_gerados = []
        for idx, s in enumerate(slides):
            out_file = os.path.join(DIR_OUTPUT, f"slide_{prod['sku']}_{idx+1}_{timestamp}.jpg")
            criar_slide_carrossel(
                titulo=s["titulo"],
                subtitulo=s["sub"],
                pontos=s["pontos"],
                cta_slide=s["cta"],
                num_slide=idx+1,
                total_slides=3,
                categoria=categoria,
                out_path=out_file,
                bg_path=bg_local if idx == 0 else None,
                produto_img_path=prod.get("image_local") if idx == 2 else None,
                preco=prod.get("preco") if idx == 2 else None
            )
            slides_gerados.append(out_file)

        urls_publicadas = []
        for s_path in slides_gerados:
            url_storage = upload_supabase_storage(s_path)
            if url_storage:
                urls_publicadas.append(url_storage)

        if dry_run:
            res_final = {"sucesso": True, "modo": "dry_run", "slides": urls_publicadas, "legenda": legenda}
        else:
            res_pub = publicar_carrossel_instagram(urls_publicadas, legenda)
            res_pub["elegivel_para_trafego_rui"] = True
            res_final = res_pub

    else:
        # Card Feed 4:5 com Paridade Total em Relação ao Story
        out_file = os.path.join(DIR_OUTPUT, f"card_{prod['sku']}_{timestamp}.jpg")
        criar_card_feed_4x5(
            headline=headline,
            subheadline=sub,
            pontos=pontos,
            categoria=categoria,
            cta_texto=f"COMPRE POR {prod['preco']}",
            out_path=out_file,
            bg_path=bg_local,
            produto_img_path=prod.get("image_local"),
            preco=prod.get("preco"),
            nome_autor="EVANDRO GALLINA" if estilo_escolhido == "evandro" else "MARCÃO PERSONAL"
        )
        url_storage = upload_supabase_storage(out_file)
        if dry_run:
            res_final = {"sucesso": True, "modo": "dry_run", "imagem": url_storage, "legenda": legenda}
        else:
            res_pub = publicar_card_instagram(url_storage, legenda)
            res_pub["elegivel_para_trafego_rui"] = True
            res_final = res_pub

    # Geração e Publicação Obrigatória nos Stories
    if postar_story:
        story_file = os.path.join(DIR_OUTPUT, f"story_{prod['sku']}_{timestamp}.jpg")
        criar_story(
            headline=headline,
            subheadline=sub,
            pontos=pontos,
            categoria=categoria,
            cta_texto=f"COMPRE POR {prod['preco']}",
            out_path=story_file,
            bg_path=bg_local,
            produto_img_path=prod.get("image_local"),
            preco=prod.get("preco"),
            nome_autor="EVANDRO GALLINA" if estilo_escolhido == "evandro" else "MARCÃO PERSONAL"
        )
        url_story = upload_supabase_storage(story_file)
        if url_story:
            if dry_run:
                res_final["story"] = {"sucesso": True, "modo": "dry_run", "imagem": url_story}
            else:
                res_story = publicar_story_instagram(url_story)
                res_final["story"] = res_story

    return res_final


# -------------------------------------------------------------------------
# 8. INTERFACE DE LINHA DE COMANDO (CLI)
# -------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fábrica de Criativos Ultra-Realistas Marcão Personal")
    parser.add_argument("--tipo", choices=["manha", "noite", "auto"], default="auto", help="Tipo de post (manha=curiosidade, noite=venda)")
    parser.add_argument("--formato", choices=["card", "carrossel"], default="carrossel", help="Formato do criativo (card ou carrossel)")
    parser.add_argument("--estilo", choices=ESTILOS_VISUAIS + ["auto"], default="evandro", help="Estilo visual da imagem (padrão: evandro)")
    parser.add_argument("--sem-ia", action="store_true", help="Desabilitar geração via IA e usar backgrounds padrão")
    parser.add_argument("--sem-story", action="store_true", help="Desabilitar publicação simultânea nos Stories")
    parser.add_argument("--dry-run", action="store_true", help="Gerar imagens e fazer upload sem publicar no Instagram")
    parser.add_argument("--indice", type=int, default=None, help="Índice específico do tema ou produto")

    args = parser.parse_args()

    tipo = args.tipo
    if tipo == "auto":
        hora = datetime.now().hour
        tipo = "manha" if hora < 15 else "noite"

    usar_ia = not args.sem_ia
    postar_story = not args.sem_story
    estilo_visual = args.estilo

    print("=" * 60)
    print(f"🎬 FÁBRICA DE CRIATIVOS MARCÃO PERSONAL 360°")
    print(f"Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Ciclo: {tipo.upper()} | Formato: {args.formato.upper()} | Estilo: {estilo_visual.upper()} | Stories: {'ATIVADO' if postar_story else 'DESATIVADO'}")
    print("=" * 60)

    if tipo == "manha":
        res = executar_ciclo_manha(
            indice=args.indice,
            formato=args.formato,
            usar_ia=usar_ia,
            dry_run=args.dry_run,
            estilo_visual=estilo_visual,
            postar_story=postar_story
        )
    else:
        res = executar_ciclo_noite(
            indice=args.indice,
            formato=args.formato,
            usar_ia=usar_ia,
            dry_run=args.dry_run,
            estilo_visual=estilo_visual,
            postar_story=postar_story
        )

    print("\n[RESULTADO]:", json.dumps(res, indent=2, ensure_ascii=False))
