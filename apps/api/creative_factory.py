import os
import re
import sys
import time
import json
import base64
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw, ImageFont
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

# Paleta Visual Cyber Marcão Personal
COR_NAVY = (10, 14, 23)
COR_CYAN = (0, 210, 255)
COR_GREEN = (57, 240, 140)
COR_ORANGE = (255, 138, 0)
COR_WHITE = (255, 255, 255)
COR_TEXT_MUTED = (160, 180, 205)

# Diretórios de Mídia
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DIR_OUTPUT = os.path.join(ROOT_DIR, "apps", "site", "public", "images", "posts")
LOGO_PATH = os.path.join(ROOT_DIR, "apps", "admin", "public", "images", "logo_marcao.jpg")
MASCOTE_PATH = os.path.join(ROOT_DIR, "apps", "admin", "public", "images", "mascote_marcao.jpg")

os.makedirs(DIR_OUTPUT, exist_ok=True)

# -------------------------------------------------------------------------
# 1. BÚSSOLA DE TEMAS E TENDÊNCIAS FITNESS BRASIL (GOOGLE TRENDS)
# -------------------------------------------------------------------------
TEMAS_CURIOSIDADES = [
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
# 3. GERAÇÃO DE IMAGEM ULTRA-REALISTA VIA OPENROUTER
# -------------------------------------------------------------------------
def gerar_imagem_ultra_realista(prompt, nome_arquivo="gen_image.png"):
    """
    Gera imagem cinematográfica 8k via OpenRouter (google/gemini-2.5-flash-image)
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
    payload = {
        "model": "google/gemini-2.5-flash-image",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        print(f"[AI IMAGE] Solicitando geração de imagem ultra-realista via OpenRouter...")
        with httpx.Client(verify=False, timeout=50) as client:
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


def criar_slide_carrossel(titulo, subtitulo, pontos, cta_slide, num_slide, total_slides, categoria, out_path, bg_path=None):
    """
    Gera um slide individual de carrossel (1080x1080) com padrão visual estético de alta tecnologia.
    """
    # 1. Base da Imagem
    if bg_path and os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA").resize((1080, 1080))
    else:
        bg = Image.new("RGBA", (1080, 1080), (10, 14, 23, 255))
        draw_grid = ImageDraw.Draw(bg)
        for i in range(0, 1080, 120):
            draw_grid.line([(i, 0), (i, 1080)], fill=(20, 28, 45, 60))
            draw_grid.line([(0, i), (1080, i)], fill=(20, 28, 45, 60))

    # 2. Gradiente Glassmorphism Dark
    overlay = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(0, 1080):
        alpha = int(185 + 70 * (y / 1080))
        draw_ov.line([(0, y), (1080, y)], fill=(8, 12, 20, alpha))

    im = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(im)

    # 3. Logo Marcão Oficial
    logo = carregar_logo_arredondado((100, 100))
    if logo:
        im.paste(logo, (50, 50), logo)

    # 4. Fontes
    try:
        font_badge = ImageFont.truetype("arialbd.ttf", 20)
        font_counter = ImageFont.truetype("arialbd.ttf", 22)
        font_title = ImageFont.truetype("arialbd.ttf", 44)
        font_sub = ImageFont.truetype("arialbd.ttf", 26)
        font_p = ImageFont.truetype("arial.ttf", 25)
        font_cta = ImageFont.truetype("arialbd.ttf", 22)
    except Exception:
        font_badge = font_counter = font_title = font_sub = font_p = font_cta = ImageFont.load_default()

    # 5. Badge de Categoria Neon Cyan
    cat_texto = sanitizar_texto_pillow(categoria).upper()
    largura_badge = 200 + len(cat_texto) * 11
    draw.rounded_rectangle([170, 75, 170 + largura_badge, 125], radius=25, fill=(10, 22, 38, 230), outline=COR_CYAN, width=2)
    draw.text((195, 88), cat_texto, fill=COR_CYAN, font=font_badge)

    # 6. Contador do Slide (ex: 1/3)
    draw.text((960, 75), f"{num_slide}/{total_slides}", fill=COR_TEXT_MUTED, font=font_counter)

    # 7. Título e Subtítulo Sanitizados
    titulo_limpo = sanitizar_texto_pillow(titulo)
    sub_limpo = sanitizar_texto_pillow(subtitulo)
    draw.text((60, 220), titulo_limpo, fill=COR_WHITE, font=font_title)
    if sub_limpo:
        draw.text((60, 330), sub_limpo, fill=COR_GREEN, font=font_sub)

    # 8. Pontos / Tópicos com Bullets Geométricos Neon
    y_pos = 420
    for p in pontos:
        p_limpo = sanitizar_texto_pillow(p)
        draw.ellipse([60, y_pos + 4, 80, y_pos + 24], fill=(0, 210, 255, 60), outline=COR_CYAN, width=2)
        draw.text((95, y_pos), p_limpo, fill=(225, 235, 245), font=font_p)
        y_pos += 80

    # 9. Barra Inferior de Ação (CTA)
    cta_limpo = sanitizar_texto_pillow(cta_slide)
    draw.rounded_rectangle([50, 960, 1030, 1030], radius=14, fill=(12, 24, 42, 240), outline=COR_CYAN, width=2)
    draw.text((80, 982), cta_limpo, fill=COR_CYAN, font=font_cta)

    im.convert("RGB").save(out_path, quality=95)
    print(f"[STUDIO] Slide {num_slide}/{total_slides} salvo: {out_path}")
    return out_path


def criar_card_unico(headline, subheadline, pontos, categoria, cta_texto, out_path, bg_path=None):
    """
    Gera um Card Único de Alto Impacto (1080x1080) com foco em headline marcante e CTA claro.
    """
    if bg_path and os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA").resize((1080, 1080))
    else:
        bg = Image.new("RGBA", (1080, 1080), (10, 14, 23, 255))

    overlay = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(0, 1080):
        alpha = int(140 + 115 * (y / 1080))
        draw_ov.line([(0, y), (1080, y)], fill=(8, 12, 20, alpha))

    im = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(im)

    # Logo
    logo = carregar_logo_arredondado((100, 100))
    if logo:
        im.paste(logo, (50, 50), logo)

    # Fontes
    try:
        font_badge = ImageFont.truetype("arialbd.ttf", 20)
        font_title = ImageFont.truetype("arialbd.ttf", 46)
        font_sub = ImageFont.truetype("arialbd.ttf", 28)
        font_p = ImageFont.truetype("arial.ttf", 26)
        font_cta = ImageFont.truetype("arialbd.ttf", 24)
    except Exception:
        font_badge = font_title = font_sub = font_p = font_cta = ImageFont.load_default()

    # Badge Superior
    cat_texto = sanitizar_texto_pillow(categoria).upper()
    largura_badge = 180 + len(cat_texto) * 11
    draw.rounded_rectangle([170, 75, 170 + largura_badge, 125], radius=25, fill=(10, 22, 38, 230), outline=COR_CYAN, width=2)
    draw.text((195, 88), cat_texto, fill=COR_CYAN, font=font_badge)

    # Título Principal
    head_limpo = sanitizar_texto_pillow(headline)
    draw.text((50, 680), head_limpo, fill=COR_WHITE, font=font_title)

    # Subtítulo Neon Verde
    sub_limpo = sanitizar_texto_pillow(subheadline)
    draw.text((50, 760), sub_limpo, fill=COR_GREEN, font=font_sub)

    # Ponto de Destaque
    if pontos:
        p_limpo = sanitizar_texto_pillow(pontos[0])
        draw.text((50, 825), f"• {p_limpo}", fill=(225, 235, 245), font=font_p)

    # Botão de Ação Inferior
    cta_limpo = sanitizar_texto_pillow(cta_texto)
    draw.rounded_rectangle([50, 895, 1030, 970], radius=16, fill=(10, 22, 38, 240), outline=COR_CYAN, width=2)
    draw.text((80, 920), cta_limpo, fill=COR_CYAN, font=font_cta)

    im.convert("RGB").save(out_path, quality=95)
    print(f"[STUDIO] Card Único salvo: {out_path}")
    return out_path


def criar_story(headline, subheadline, pontos, categoria, cta_texto, out_path, bg_path=None):
    """
    Gera imagem de Story vertical (1080x1920 - 9:16) no padrão Marcão Personal.
    """
    story = Image.new("RGBA", (1080, 1920), (10, 14, 23, 255))
    if bg_path and os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGBA").resize((1080, 1080), Image.Resampling.LANCZOS)
        story.paste(bg_img, (0, 180))

    draw_grad = ImageDraw.Draw(story)
    for y in range(0, 320):
        alpha = int(255 * (1 - (y / 320)))
        draw_grad.line([(0, y), (1080, y)], fill=(10, 14, 23, alpha))
    for y in range(1000, 1920):
        alpha = min(255, int(160 + 95 * ((y - 1000) / 920)))
        draw_grad.line([(0, y), (1080, y)], fill=(10, 14, 23, alpha))

    logo = carregar_logo_arredondado((110, 110))
    if logo:
        story.paste(logo, (50, 45), logo)

    draw = ImageDraw.Draw(story)
    try:
        font_badge = ImageFont.truetype("arialbd.ttf", 22)
        font_title = ImageFont.truetype("arialbd.ttf", 44)
        font_sub = ImageFont.truetype("arialbd.ttf", 26)
        font_p = ImageFont.truetype("arial.ttf", 24)
        font_btn = ImageFont.truetype("arialbd.ttf", 26)
    except Exception:
        font_badge = font_title = font_sub = font_p = font_btn = ImageFont.load_default()

    cat_limpa = sanitizar_texto_pillow(categoria).upper()
    draw.rounded_rectangle([180, 70, 180 + len(cat_limpa) * 16, 125], radius=25, fill=(10, 22, 38, 230), outline=COR_CYAN, width=2)
    draw.text((205, 84), cat_limpa, fill=COR_CYAN, font=font_badge)

    draw.rounded_rectangle([40, 1100, 1040, 1850], radius=24, fill=(13, 19, 31, 245), outline=COR_CYAN, width=2)
    draw.text((70, 1140), sanitizar_texto_pillow(headline), fill=COR_WHITE, font=font_title)
    draw.text((70, 1210), sanitizar_texto_pillow(subheadline), fill=COR_GREEN, font=font_sub)

    y_pos = 1280
    for p in pontos:
        p_limpo = sanitizar_texto_pillow(p)
        draw.ellipse([70, y_pos + 4, 90, y_pos + 24], fill=(0, 210, 255, 60), outline=COR_CYAN, width=2)
        draw.text((105, y_pos), p_limpo, fill=(225, 235, 245), font=font_p)
        y_pos += 85

    draw.rounded_rectangle([70, 1660, 1010, 1780], radius=20, fill=COR_CYAN, outline=COR_WHITE, width=2)
    draw.text((115, 1700), sanitizar_texto_pillow(cta_texto), fill=COR_NAVY, font=font_btn)

    story.convert("RGB").save(out_path, quality=95)
    print(f"[STUDIO] Story salvo: {out_path}")
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
def executar_ciclo_manha(indice=None, formato="carrossel", usar_ia=True, dry_run=False):
    """
    Executa o Post da Manhã (11:30): Curiosidade, Ciência & Entretenimento.
    """
    temas_ativos = [t for t in TEMAS_CURIOSIDADES if not t.get("desativado")]
    if indice is None:
        indice = datetime.now().day % len(temas_ativos)
    tema = temas_ativos[indice % len(temas_ativos)]

    print(f"\n[FÁBRICA 11:30] Iniciando produção do Post de Curiosidade: '{tema['tema']}'")

    # 1. Obter imagem base (IA Ultra-Realista ou Fallback)
    bg_local = None
    if usar_ia:
        nome_ia = f"bg_{tema['id']}_{int(time.time())}.png"
        bg_local = gerar_imagem_ultra_realista(tema["prompt_ia"], nome_ia)

    if not bg_local or not os.path.exists(bg_local):
        bg_local = MASCOTE_PATH if os.path.exists(MASCOTE_PATH) else None

    # 2. Renderizar formato escolhido
    timestamp = int(time.time())
    urls_publicadas = []

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

        # Upload dos slides para o Supabase Storage
        for s_path in slides_gerados:
            url_storage = upload_supabase_storage(s_path)
            if url_storage:
                urls_publicadas.append(url_storage)

        if dry_run:
            return {"sucesso": True, "modo": "dry_run", "slides": urls_publicadas, "legenda": tema["legenda"]}

        # Publicar Carrossel
        res_pub = publicar_carrossel_instagram(urls_publicadas, tema["legenda"])
        return res_pub

    else:
        # Card Único
        out_file = os.path.join(DIR_OUTPUT, f"card_{tema['id']}_{timestamp}.jpg")
        criar_card_unico(
            headline=tema["headline"],
            subheadline=tema["subheadline"],
            pontos=tema["pontos_card"],
            categoria=tema["categoria"],
            cta_texto="LEIA A LEGENDA COMPLETA • LINK NA BIO: marcaopersonal.com",
            out_path=out_file,
            bg_path=bg_local
        )
        url_storage = upload_supabase_storage(out_file)
        if dry_run:
            return {"sucesso": True, "modo": "dry_run", "imagem": url_storage, "legenda": tema["legenda"]}

        res_pub = publicar_card_instagram(url_storage, tema["legenda"])
        return res_pub


def executar_ciclo_noite(indice=None, formato="card", usar_ia=True, dry_run=False):
    """
    Executa o Post da Noite (19:30): Venda de Produto & Conversão Direta.
    Este post fica automaticamente elegível para o Rui impulsionar no Meta Ads!
    """
    produtos_ativos = [p for p in PRODUTOS_CATALOGO if not p.get("desativado")]
    if indice is None:
        indice = datetime.now().day % len(produtos_ativos)
    prod = produtos_ativos[indice % len(produtos_ativos)]

    print(f"\n[FÁBRICA 19:30] Iniciando produção do Post de Venda: '{prod['nome']}'")

    # Montar copy persuasiva da Lia
    if "Creatina" in prod["nome"]:
        headline = "CREATINA 100% PURA NATURE'S PRIME"
        sub = "Mais força, tônus no glúteo e definição sem retenção hídrica"
        pontos = ["Pureza micronizada com laudo oficial.", "R$ 169,90 com 100 doses diárias."]
    elif "Azempika" in prod["nome"]:
        headline = "CANETA AZEMPIKA ORIGINAL"
        sub = "Biohacking da circulação e firmeza sem riscos cardíacos"
        pontos = [
            "Vasodilatação transdérmica rápida nos corpos cavernosos.",
            "Aplicação prática de 1 a 2 cliques cerca de 15 min antes.",
            "100% seguro: zero taquicardia, palpitação ou risco cardíaco."
        ]
    elif "Colágeno" in prod["nome"]:
        headline = "COLÁGENO + ÁCIDO HIALURÔNICO"
        sub = "Pele firme, viçosa e sem flacidez no sabor Abacaxi com Hortelã"
        pontos = ["Biopeptídeos de renovação dérmica.", "Apenas R$ 164,90."]
    elif "Capilar" in prod["nome"]:
        headline = "KIT IARMONIZE CAPILAR CLÍNICO"
        sub = "Protocolo clínico antiqueda e estimulação folicular profunda"
        pontos = ["Nutrição de dentro para fora.", "Em até 12x no cartão com Frete Grátis."]
    else:
        headline = prod["nome"].upper()
        sub = f"Protocolo oficial Marcão Personal por {prod['preco']}"
        pontos = ["Entrega rápida e rastreada pelos Correios."]

    legenda = (
        f"🎯 {headline} — CONDIÇÃO EXCLUSIVA DE HOJE! ⚡\n\n"
        f"{sub}.\n\n"
        f"Se você busca resultados corporais de alto nível sem perder tempo com promessas vazias, "
        f"a qualidade dos protocolos recomendados pelo Marcão é inegociável.\n\n"
        f"💎 {prod['preco']} com envio rápido e seguro pelos Correios para todo o Brasil!\n\n"
        f"👉 Quer garantir o seu antes que o lote promocional acabe?\n"
        f"Toque agora no LINK DA BIO em marcaopersonal.com ou COMENTE \"QUERO\" aqui embaixo que eu te envio o link direto no seu Direct! 📲\n\n"
        f"#marcao #suplementos #saude #estetica #performance #qualidadedevida #fitness"
    )

    # 1. Imagem Ultra-Realista
    bg_local = None
    if usar_ia:
        nome_ia = f"bg_{prod['sku']}_{int(time.time())}.png"
        bg_local = gerar_imagem_ultra_realista(prod["prompt_ia"], nome_ia)

    timestamp = int(time.time())

    if formato == "carrossel":
        # Carrossel de Venda
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
                categoria=prod["categoria"],
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
            return {"sucesso": True, "modo": "dry_run", "slides": urls_publicadas, "legenda": legenda}

        res_pub = publicar_carrossel_instagram(urls_publicadas, legenda)
        res_pub["elegivel_para_trafego_rui"] = True
        return res_pub

    else:
        # Card Único
        out_file = os.path.join(DIR_OUTPUT, f"card_{prod['sku']}_{timestamp}.jpg")
        criar_card_unico(
            headline=headline,
            subheadline=sub,
            pontos=pontos,
            categoria=prod["categoria"],
            cta_texto=f"GARANTA POR {prod['preco']} • LINK NA BIO: marcaopersonal.com",
            out_path=out_file,
            bg_path=bg_local
        )
        url_storage = upload_supabase_storage(out_file)
        if dry_run:
            return {"sucesso": True, "modo": "dry_run", "imagem": url_storage, "legenda": legenda}

        res_pub = publicar_card_instagram(url_storage, legenda)
        res_pub["elegivel_para_trafego_rui"] = True
        return res_pub


# -------------------------------------------------------------------------
# 8. INTERFACE DE LINHA DE COMANDO (CLI)
# -------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fábrica de Criativos Ultra-Realistas Marcão Personal")
    parser.add_argument("--tipo", choices=["manha", "noite", "auto"], default="auto", help="Tipo de post (manha=curiosidade, noite=venda)")
    parser.add_argument("--formato", choices=["card", "carrossel"], default="carrossel", help="Formato do criativo")
    parser.add_argument("--sem-ia", action="store_true", help="Desabilitar geração via IA e usar backgrounds padrão")
    parser.add_argument("--dry-run", action="store_true", help="Gerar imagens e fazer upload sem publicar no Instagram")
    parser.add_argument("--indice", type=int, default=None, help="Índice específico do tema ou produto")

    args = parser.parse_args()

    tipo = args.tipo
    if tipo == "auto":
        hora = datetime.now().hour
        tipo = "manha" if hora < 15 else "noite"

    usar_ia = not args.sem_ia

    print("=" * 60)
    print(f"🎬 FÁBRICA DE CRIATIVOS MARCÃO PERSONAL 360°")
    print(f"Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Ciclo: {tipo.upper()} | Formato: {args.formato.upper()} | IA: {'ATIVADA' if usar_ia else 'DESATIVADA'}")
    print("=" * 60)

    if tipo == "manha":
        res = executar_ciclo_manha(indice=args.indice, formato=args.formato, usar_ia=usar_ia, dry_run=args.dry_run)
    else:
        res = executar_ciclo_noite(indice=args.indice, formato=args.formato, usar_ia=usar_ia, dry_run=args.dry_run)

    print("\n[RESULTADO]:", json.dumps(res, indent=2, ensure_ascii=False))
