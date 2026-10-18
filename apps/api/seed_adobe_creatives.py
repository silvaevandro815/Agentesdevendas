"""
========================================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
SEMEADOR DE CRIATIVOS ADOBE CREATIVE ENGINE 2.0 (FEED 4:5, STORY 9:16 & CARROSSEL 3 SLIDES)
========================================================================================
Gera masterpieces gráficas inéditas, respeitando estritamente a Lei de Proteção Facial,
faz upload para a CDN do Supabase Storage e alimenta a fila 'ready' em content_calendar.
========================================================================================
"""

import os
import sys
import time
import json
import random
import requests
import urllib3
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

urllib3.disable_warnings()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(BASE_DIR, "apps", "api"))

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from adobe_creative_engine import (
    renderizar_criativo_masterpiece,
    renderizar_slide_carrossel_masterpiece
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
STORAGE_BUCKET = "creativos"
DIR_OUTPUT = os.path.join(BASE_DIR, "apps", "site", "public", "images", "posts")
os.makedirs(DIR_OUTPUT, exist_ok=True)

# Banco de Imagens de Alta Resolução de Background com Personas Diversas (100% IA)
FOTOS_BACKGROUND = [
    os.path.join(BASE_DIR, "apps", "site", "public", "images", "posts", "bg_CREATINA-MICRONIZADA-300G_marcao_1792021461.png"),
    os.path.join(BASE_DIR, "apps", "site", "public", "images", "posts", "bg_colageno_25anos_evandro_1792077478.png"),
    os.path.join(BASE_DIR, "apps", "site", "public", "images", "posts", "bg_dor_muscular_remedio_evandro_1792026645.png"),
    os.path.join(BASE_DIR, "apps", "site", "public", "images", "posts", "bg_balanca_ilusao_evandro_1792250193.png"),
    os.path.join(BASE_DIR, "apps", "site", "public", "images", "posts", "bg_homem_maduro_grisalho.png")
]

# Imagens de Produtos Oficiais
PROD_CREATINA = os.path.join(BASE_DIR, "apps", "site", "public", "images", "creatina.jpg")
PROD_COLAGENO = os.path.join(BASE_DIR, "apps", "site", "public", "images", "colageno.png")
PROD_AZEMPIKA = os.path.join(BASE_DIR, "apps", "site", "public", "images", "azempika.jpg")
PROD_IARMONIZE = os.path.join(BASE_DIR, "apps", "site", "public", "images", "iarmonize.jpg")

# Matriz de Temas Editorial & Produtos (Google Trends Brasil + Protocolos Oficiais Marcão)
MASTER_TEMAS = [
    {
        "id": "creatina_mito_retencao",
        "categoria": "ALTA PERFORMANCE",
        "tema": "Creatina Retém Líquido ou Dá Inchaço?",
        "preco": "R$ 169,90",
        "produto_img": PROD_CREATINA,
        "produto_nome": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://marcaopersonal.com#creatina",
        "slides": [
            {
                "titulo": "TOMAR CREATINA INCHA\nOU DÁ RETENÇÃO NA PELE?",
                "sub": "O mito que impede milhares de pessoas de ter resultados:",
                "pontos": [
                    "A creatina retém água DENTRO da célula muscular (hidratação intracelular).",
                    "Ela NÃO causa retenção hídrica subcutânea (abaixo da pele).",
                    "Músculo hidratado = 20% a 30% mais força e tônus muscular acelerado.",
                    "Sua pele continua fina e com máxima definição aparente!"
                ],
                "cta": "ARRASTE E ENTENDA A CIÊNCIA DA FORÇA ››"
            },
            {
                "titulo": "O QUE A CIÊNCIA PROVA\nSOBRE A FORÇA MUSCULAR?",
                "sub": "Mecanismo biológico da fosfocreatina e ressíntese de ATP:",
                "pontos": [
                    "Ressíntese acelerada de ATP celular para aguentar as últimas repetições.",
                    "Proteção contra o catabolismo muscular em fases de queima de gordura.",
                    "Absorção e saturação segura sem necessidade de sobrecarga renal.",
                    "Padrão ouro mundial em suplementação para homens e mulheres."
                ],
                "cta": "COMO ESCOLHER A PURA? VEJA O LAUDO ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\n100% PURA COM LAUDO OFICIAL",
                "sub": "Protocolo de pureza laboratorial para resultados garantidos:",
                "pontos": [
                    "Creatina Micronizada 100% Pura Nature's Prime (pote 300g / 100 doses).",
                    "Menos de R$ 1,70 por dia para você treinar com potência máxima.",
                    "Sem açúcares, sem maltodextrina e com laudo laboratorial aprovado.",
                    "Apenas R$ 169,90 com envio rápido pelos Correios para todo o Brasil."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 CREATINA DÁ INCHAÇO OU ENGORDA? Desmistificando o maior erro das academias!\n\n"
            "Se você ainda tem receio de tomar creatina achando que vai ficar com aspecto 'inchado' ou reter líquido na barriga, preste muita atenção na fisiologia:\n\n"
            "A creatina puxa água exclusivamente para o meio INTRACELULAR (para dentro da fibra muscular). Músculo hidratado é músculo potente, metabolicamente ativo e protegido contra lesões. O inchaço indesejado é fruto de retenção extracelular por excesso de sódio ou ultraprocessados!\n\n"
            "💡 Protocolo Oficial Marcão Personal:\n"
            "• 5g todos os dias (inclusive nos dias em que não treinar).\n"
            "• Consumo de 35ml a 45ml de água por kg de peso corporal.\n"
            "• Matéria-prima micronizada de altíssima pureza com laudo oficial.\n\n"
            "💬 Você já toma creatina todo dia ou ainda tinha essa dúvida? Deixe seu comentário aqui embaixo! 👇\n\n"
            "👉 Garanta a Creatina Micronizada 100% Pura Nature's Prime (300g / 100 doses) por R$ 169,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\" para receber no Direct! 📲\n\n"
            "#marcao #marcaopersonal #creatina #hipertrofia #treinopesado #biohacking #definicaomuscular #suplementos"
        )
    },
    {
        "id": "dor_muscular_antiinflamatorio",
        "categoria": "CIÊNCIA & RECUPERAÇÃO",
        "tema": "Tomar Remédio Pós-Treino Trava o Ganho Muscular?",
        "preco": "R$ 169,90",
        "produto_img": PROD_CREATINA,
        "produto_nome": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://marcaopersonal.com#creatina",
        "slides": [
            {
                "titulo": "TOMOU ANTI-INFLAMATÓRIO?\nSEU TREINO FOI PARA O LIXO!",
                "sub": "O erro de farmácia que joga semanas de esforço no ralo:",
                "pontos": [
                    "A dor de 24h a 48h após o treino chama-se Dor Tardia (DMIT).",
                    "Ela ocorre por microlesões fisiológicas que o corpo precisa regenerar.",
                    "Remédios comuns desligam as enzimas necessárias para a síntese proteica.",
                    "Você alivia a dor momentânea, mas paralisa o crescimento muscular!"
                ],
                "cta": "ARRASTE E ENTENDA O BLOQUEIO BIOLÓGICO ››"
            },
            {
                "titulo": "O QUE ACONTECE NA FIBRA\nQUANDO VOCÊ TOMA REMÉDIO?",
                "sub": "A paralisia da via de reparação celular explicada pelo Marcão:",
                "pontos": [
                    "A enzima COX-2 é bloqueada, travando a fabricação de novas proteínas.",
                    "As células satélites não se fundem para engrossar o músculo.",
                    "O estômago e o fígado sofrem sobrecarga química inútil.",
                    "A inflamação fisiológica controlada é sua MAIOR aliada para evoluir."
                ],
                "cta": "COMO ALIVIAR SEM REMÉDIOS? VEJA A SEGUIR ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\nRECUPERAÇÃO SEM REMÉDIOS",
                "sub": "Protocolo celular de regeneração rápida e sem dor travada:",
                "pontos": [
                    "Creatina Micronizada pura: hidratação das fibras e ATP renovado.",
                    "Banho morno, sono reparador de 7-8h e cardio leve regenerativo.",
                    "Zero remédios que sabotam a sua hipertrofia.",
                    "Apenas R$ 169,90 no pote de 300g (100 doses oficiais)."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🚨 SENTIU AQUELA DOR BRUTAL NO DIA SEGUINTE E TOMOU UM REMÉDIO? CUIDADO!\n\n"
            "Quando você treina pesado, ocorrem micro-fissuras normais e benéficas nas fibras musculares. Essa inflamação fisiológica é o gatilho biológico que o corpo usa para avisar: 'precisamos construir um músculo maior e mais forte'.\n\n"
            "Ao tomar remédios anti-inflamatórios de farmácia (ibuprofeno, diclofenaco, etc.), você desliga a cascata enzimática e mata a síntese de novas fibras musculares. Você anestesia a dor temporária, mas anula o benefício do treino!\n\n"
            "✅ Como recuperar de verdade sem estragar seu ganho:\n"
            "1. Hidratação intracelular profunda com Creatina Micronizada 100% Pura.\n"
            "2. Sono profundo na faixa de 7 a 8 horas (onde o GH é sintetizado).\n"
            "3. Cardio leve de 20 minutos para oxigenar e acelerar a drenagem de lactato.\n\n"
            "💬 Você costuma tomar remédio quando o treino dói? Comente aqui embaixo!\n\n"
            "👉 Garanta a Creatina Micronizada oficial por R$ 169,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\" aqui embaixo! 📲\n\n"
            "#marcao #dormuscular #recuperacaomuscular #treinopesado #hipertrofia #creatina #biohacking"
        )
    },
    {
        "id": "colageno_flacidez_estetica",
        "categoria": "ESTÉTICA & LONGEVIDADE",
        "tema": "Flacidez Pós-Emagrecimento: Como Evitar a Pele Frouxa?",
        "preco": "R$ 164,90",
        "produto_img": PROD_COLAGENO,
        "produto_nome": "Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime",
        "link_venda": "https://marcaopersonal.com#colageno",
        "slides": [
            {
                "titulo": "EMAGRECEU MAS A PELE\nFICOU FLÁCIDA E FROUXA?",
                "sub": "A quebra do colágeno na derme que ninguém te ensina a tratar:",
                "pontos": [
                    "A partir dos 25 anos, o corpo perde 1% de colágeno ao ano.",
                    "No emagrecimento rápido sem suporte celular, a pele perde a ancoragem.",
                    "Cremes comuns não penetram na camada profunda da derme.",
                    "A nutrição precisa vir de dentro para fora com peptídeos bioativos!"
                ],
                "cta": "ARRASTE E VEJA A CIÊNCIA DA FIRMEZA DÉRMICA ››"
            },
            {
                "titulo": "POR QUE ASSOCIAR COLÁGENO\nCOM ÁCIDO HIALURÔNICO?",
                "sub": "A sinergia que reconstrói a matriz extracelular da pele:",
                "pontos": [
                    "O Ácido Hialurônico retém até 1.000x o seu peso em água na derme.",
                    "Os Peptídeos de Colágeno estimulam fibroblastos a produzir elastina.",
                    "Redução visível de linhas de expressão, flacidez nos braços e abdômen.",
                    "Fortalecimento conjunto de unhas, cabelos e cartilagens articulares."
                ],
                "cta": "CONHEÇA O PROTOCOLO OFICIAL DE HOJE ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\nFIRMEZA DÉRMICA TOTAL",
                "sub": "Fórmula enriquecida com vitaminas antioxidantes essenciais:",
                "pontos": [
                    "Colágeno Hidrolisado Verisol® + Ácido Hialurônico Concentrado.",
                    "Apenas R$ 164,90 no pote com dosagem diária de alta absorção.",
                    "Zero açúcar, sabor agradável e dissolução instantânea.",
                    "Envio rastreado pelos Correios para todo o território nacional."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "✨ EMAGRECEU E NOTOU AQUELA PELE MAIS FLÁCIDA NO ABDÔMEN OU NOS BRAÇOS?\n\n"
            "Quando perdemos peso, a gordura subcutânea diminui, mas a pele precisa de suporte elástico para retrair e colar no músculo. Se a sua derme estiver desidratada e pobre em colágeno, o resultado é aspecto frouxo e rugosidade!\n\n"
            "A partir dos 25 anos, nossa produção natural de colágeno despenca ano após ano. Cremes hidratantes só agem na camada superficial; a verdadeira reestruturação acontece de dentro para fora com Peptídeos Bioativos de Colágeno combinados com Ácido Hialurônico.\n\n"
            "💎 Benefícios comprovados do protocolo:\n"
            "• Firmeza dérmica e redução de flacidez no abdômen, pernas e glúteos.\n"
            "• Preenchimento celular e viço radiante no rosto.\n"
            "• Saúde articular para treinar sem incômodo nos joelhos e ombros.\n\n"
            "👉 Garanta o Colágeno Hidrolisado + Ácido Hialurônico por R$ 164,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\" que eu te mando agora! 📲\n\n"
            "#marcao #colageno #acidohialuronico #flacidez #pelebonita #esteticacorporal #emagrecimento #longevidade"
        )
    },
    {
        "id": "balanca_bioimpedancia_ilusao",
        "categoria": "CIÊNCIA & MÉTRICAS",
        "tema": "A Ilusão da Balança Comum de Farmácia: Por Que Ela Te Engana?",
        "preco": "R$ 89,90",
        "produto_img": None,
        "produto_nome": "Balança Digital de Bioimpedância Bluetooth Marcão Personal",
        "link_venda": "https://marcaopersonal.com#balanca",
        "slides": [
            {
                "titulo": "A BALANÇA DE FARMÁCIA\nESTÁ TE ENGANANDO TODO DIA!",
                "sub": "O erro de medir apenas o peso bruto na hora de se pesar:",
                "pontos": [
                    "O peso da balança comum mistura gordura, água, fezes e músculo.",
                    "Você pode perder 2kg na balança comum e ter perdido apenas MÚSCULO.",
                    "Ou ganhar 1kg de pura MASSA MAGRA achando que engordou.",
                    "Parar de se guiar pelo peso cego é o primeiro passo para ter resultado!"
                ],
                "cta": "ARRASTE E ENTENDA O QUE É BIOIMPEDÂNCIA ››"
            },
            {
                "titulo": "COMO A BIOIMPEDÂNCIA IA\nENXERGA SEU CORPO POR DENTRO?",
                "sub": "Microcorrente segura através de 4 eletrodos de precisão:",
                "pontos": [
                    "Mede exatamente seu % de Gordura Corporal e Gordura Visceral.",
                    "Informa sua Massa Muscular esquelética e taxa metabólica basal.",
                    "Conecta via Bluetooth no smartphone com gráficos de evolução.",
                    "Permite ao Marcão ajustar seu treino e dieta com precisão cirúrgica."
                ],
                "cta": "CONHEÇA A BALANÇA OFICIAL DO MARCÃO ››"
            },
            {
                "titulo": "BALANÇA BLUETOOTH MARCÃO IA\nCOM 3 MESES DE CONSULTORIA",
                "sub": "O equipamento oficial para acompanhar sua evolução de verdade:",
                "pontos": [
                    "Design premium ultra-fino em vidro temperado com display LED oculto.",
                    "Apenas R$ 89,90 (menos de R$ 0,30 por dia!).",
                    "Acompanhamento VIP grátis no WhatsApp diretamente com o Marcão.",
                    "Envio imediato com garantia de 1 ano e suporte completo."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "⚖️ VOCÊ AINDA SOFRE SUBINDO NA BALANÇA COMUM DE FARMÁCIA?\n\n"
            "Pare agora mesmo de se torturar com o número que a balança comum mostra! Ela é cega: não sabe a diferença entre 1kg de gordura e 1kg de músculo, nem se você bebeu 1 litro de água antes de se pesar.\n\n"
            "Muitos desanimam da dieta porque o peso 'travou', quando na verdade perderam 2kg de gordura pura e ganharam 2kg de massa magra definida! A única forma de saber a verdade é através da Bioimpedância Multifrequencial.\n\n"
            "📊 A Balança de Bioimpedância Bluetooth Marcão Personal mede:\n"
            "1. Percentual de Gordura Corporal e Gordura Visceral (a perigosa).\n"
            "2. Massa Muscular Esquelética e Idade Metabólica.\n"
            "3. Taxa de Hidratação Celular e Massa Óssea.\n"
            "E o melhor: você ganha 3 MESES de acompanhamento com o Marcão no WhatsApp!\n\n"
            "👉 Garanta a sua por apenas R$ 89,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\"! 📲\n\n"
            "#marcao #bioimpedancia #balancainteligente #emagrecimento #composicaocorporal #treinointeligente #saude"
        )
    },
    {
        "id": "azempika_potencia_masculina",
        "categoria": "POTÊNCIA & SAÚDE MASCULINA 40+",
        "tema": "Homem Maduro 40+: Como Recuperar a Firmeza e o Vigor na Hora H?",
        "preco": "R$ 99,00",
        "produto_img": PROD_AZEMPIKA,
        "produto_nome": "Caneta Peniana Azempika Original (Clinical Formula 20ml)",
        "link_venda": "https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv",
        "slides": [
            {
                "titulo": "HOMEM MADURO 40+:\nPERDENDO A POTÊNCIA NA HORA H?",
                "sub": "A queda vascular de óxido nítrico que afeta milhões de homens maduros:",
                "pontos": [
                    "Após os 40 anos, a circulação nos corpos cavernosos cai até 45%.",
                    "Ereções fracas e insegurança não são falta de masculinidade.",
                    "A verdadeira solução é o estímulo vasodilatador tópico direto!"
                ],
                "cta": "ARRASTE E VEJA COMO USAR NA PRÁTICA ››"
            },
            {
                "titulo": "MODO DE USO NA PRÁTICA:\nCANETA PENIANA AZEMPIKA",
                "sub": "Fórmula clínica tópica de ação imediata em 20ml (Clinical Formula):",
                "pontos": [
                    "1. GIRE O DOSADOR: Aplicação limpa, precisa e sem nenhum desperdício.",
                    "2. APLIQUE NA HASTE: Espalhe diretamente no membro 10 a 15 min antes.",
                    "3. MASSAGEM DE 1 A 2 MIN: Estimula os corpos cavernosos até absorção total."
                ],
                "cta": "VEJA A OFERTA OFICIAL DISCRETA ››"
            },
            {
                "titulo": "CANETA PENIANA AZEMPIKA\nFIRMEZA & VIGOR MASCULINO",
                "sub": "Clinical Formula concentrada para homens que exigem o seu melhor:",
                "pontos": [
                    "Ação tópica direta: máxima potência sem sobrecarga cardíaca.",
                    "Apenas R$ 99,00 no frasco dosador oficial de 20ml.",
                    "Envio 100% discreto em embalagem lacrada sem identificação."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🔥 HOMEM MADURO 40+: PERDENDO A POTÊNCIA E A FIRMEZA NA HORA H?\n\n"
            "Papo reto de parceiro: depois dos 40 anos, o estresse, o cansaço do trabalho e a queda natural do fluxo vascular afetam diretamente a circulação dos corpos cavernosos. Não é falta de masculinidade nem falta de vontade — é puramente fisiologia e vasodilatação sanguínea!\n\n"
            "Muitos recorrem a pílulas azuis de farmácia que disparam o coração, causam taquicardia, dor de cabeça e criam uma dependência psicológica perigosa. Mas existe uma via clínica moderna, tópica e muito mais inteligente.\n\n"
            "⚡ CANETA PENIANA AZEMPIKA (Clinical Formula 20ml):\n"
            "Desenvolvida especificamente para devolver rigidez máxima, firmeza duradoura e confiança absoluta na hora H através de bioativos concentrados de dilatação cavernosa local.\n\n"
            "📖 COMO USAR (MODO DE APLICAÇÃO CORRETO):\n"
            "1. Gire o dosador da caneta para liberar a quantidade exata.\n"
            "2. Aplique diretamente na haste peniana cerca de 10 a 15 minutos antes da intimidade.\n"
            "3. Massageie suavemente por 1 a 2 minutos até completa absorção celular.\n"
            "👉 Dica do Marcão: também pode ser usada diariamente após o banho como manutenção contínua da saúde vascular íntima!\n\n"
            "🛡️ GARANTIA BLINDADA DE 90 DIAS E ENTREGA 100% DISCRETA:\n"
            "O produto chega na sua casa em embalagem totalmente descaracterizada, sem nenhuma menção externa ao conteúdo.\n\n"
            "💬 Ficou com alguma dúvida? Comente \"QUERO\" aqui embaixo que eu mesmo te chamo no Direct com total discrição e sigilo! 📲\n\n"
            "👉 Garanta a sua Caneta Peniana Azempika Original por apenas R$ 99,00 no LINK DA BIO em marcaopersonal.com ou pelo Direct! 🛒\n\n"
            "#marcao #marcaopersonal #potenciamasculina #saudemasculina #homensmaduros #homens40mais #homens50mais #vigor #confiança #biohacking"
        )
    },
    {
        "id": "sono_anabolico_gh",
        "categoria": "BIOHACKING & RECUPERAÇÃO",
        "tema": "O Sono Anabólico e a Síntese Noturna de GH",
        "preco": "R$ 169,90",
        "produto_img": PROD_CREATINA,
        "produto_nome": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://marcaopersonal.com#creatina",
        "slides": [
            {
                "titulo": "DORME MENOS DE 7 HORAS?\nSEU MÚSCULO NÃO VAI CRESCER!",
                "sub": "A janela hormonal noturna de regeneração profunda:",
                "pontos": [
                    "80% do GH (hormônio do crescimento) é liberado no sono REM profundo.",
                    "Noites mal dormidas elevam o cortisol e aumentam o acúmulo de gordura abdominal.",
                    "A síntese proteica depende da recuperação do sistema nervoso central.",
                    "Descansar não é perder tempo: é quando a mágica do treino acontece!"
                ],
                "cta": "ARRASTE E ENTENDA O CICLO NOTURNO ››"
            },
            {
                "titulo": "COMO POTENCIALIZAR A\nRESSÍNTESE DE ATP NO SONO?",
                "sub": "A sinergia entre saturação celular de creatina e sono profundo:",
                "pontos": [
                    "A creatina mantém a célula muscular saturada e hidratada durante o jejum noturno.",
                    "Redução da fadiga neural e despertar com energia renovada.",
                    "Zero câimbras ou sensação de peso nas pernas pela manhã.",
                    "Padrão científico para hipertrofia sem desgaste excessivo."
                ],
                "cta": "VEJA A DICA DE OURO DO MARCÃO ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\nRECUPERAÇÃO CELULAR 360°",
                "sub": "Protocolo de sono profundo e creatina pura oficial:",
                "pontos": [
                    "Creatina Micronizada 100% Pura Nature's Prime (300g / 100 doses).",
                    "Apenas R$ 169,90 no pote oficial com laudo laboratorial.",
                    "Dormir 7h a 8h no escuro absoluto e banho morno relaxante.",
                    "Envio rápido pelos Correios para todo o Brasil."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🌙 VOCÊ TREINA PESADO, MAS NA HORA DE DORMIR NÃO CONSEGUE DESCANSAR?\n\n"
            "O treino na academia é apenas o estímulo de degradação: o crescimento muscular e a queima de gordura acontecem enquanto você dorme! Durante os estágios profundos de sono (ondas lentas), o corpo atinge o pico de secreção do hormônio do crescimento (GH) e inicia a reparação celular.\n\n"
            "Quando você dorme menos de 7 horas, o cortisol permanece elevado, gerando quebra de massa muscular e retenção de líquidos.\n\n"
            "💡 Dica de Ouro Marcão Personal:\n"
            "• Quarto 100% escuro e fresco.\n"
            "• Saturação constante com Creatina Micronizada Pura para hidratação das fibras.\n"
            "• Corte de telas e celulares 30 minutos antes de deitar.\n\n"
            "👉 Garanta a Creatina Micronizada oficial por R$ 169,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\"! 📲\n\n"
            "#marcao #sonoanabolico #gh #recuperacaomuscular #creatina #biohacking #treinopesado #saude"
        )
    },
    {
        "id": "saude_articular_40mais",
        "categoria": "LONGEVIDADE & ARTICULAÇÕES",
        "tema": "Treinar aos 40+ Sem Dor nos Joelhos e Ombros",
        "preco": "R$ 164,90",
        "produto_img": PROD_COLAGENO,
        "produto_nome": "Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime",
        "link_venda": "https://marcaopersonal.com#colageno",
        "slides": [
            {
                "titulo": "JOELHOS ESTALANDO E\nOMBRO DOENDO NO SUPINO?",
                "sub": "O desgaste da cartilagem aos 40+ que trava seus treinos:",
                "pontos": [
                    "A densidade do colágeno articular diminui naturalmente com a idade.",
                    "Tendões menos hidratados sofrem mais atrito e geram tendinites.",
                    "Parar de treinar é o pior erro: o músculo fraco sobrecarrega a junta.",
                    "A solução é blindar as articulações com colágeno de alta absorção!"
                ],
                "cta": "ARRASTE E ENTENDA A RECONSTRUÇÃO ARTICULAR ››"
            },
            {
                "titulo": "COMO O ÁCIDO HIALURÔNICO\nLUBRIFICA A CARTILAGEM?",
                "sub": "O líquido sinovial precisa de hidratação contínua para amortecer impacto:",
                "pontos": [
                    "O Ácido Hialurônico atua como óleo lubrificante nas juntas corporais.",
                    "Redução do atrito ósseo e alívio do incômodo pós-agachamento.",
                    "Recuperação da flexibilidade e amplitude completa do movimento.",
                    "Sem remédios de farmácia que agridem o estômago."
                ],
                "cta": "CONHEÇA A FÓRMULA OFICIAL MARCÃO ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\nLONGEVIDADE ARTICULAR TOTAL",
                "sub": "Peptídeos bioativos com Ácido Hialurônico e vitaminas C e E:",
                "pontos": [
                    "Colágeno Hidrolisado Verisol® + Ácido Hialurônico Concentrado.",
                    "Apenas R$ 164,90 no pote oficial de alta densidade.",
                    "Mais firmeza na pele e proteção completa das cartilagens.",
                    "Frete rastreado e suporte oficial Marcão Personal."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "💪 QUEM DISSE QUE DEPOIS DOS 40 VOCÊ NÃO PODE TREINAR PESADO?\n\n"
            "O segredo para manter força e estética impecável aos 40, 50 ou 60 anos não é diminuir o ritmo: é proteger as cartilagens e os tendões! Com o passar dos anos, o líquido sinovial diminui e o atrito articular causa aquelas dores chatas no ombro e no joelho.\n\n"
            "A associação entre Peptídeos de Colágeno Hidrolisado e Ácido Hialurônico atua na lubrificação das articulações e na sustentação da derme, permitindo que você agache e supine com confiança e sem dor no dia seguinte.\n\n"
            "👉 Garanta o Colágeno Hidrolisado + Ácido Hialurônico por R$ 164,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\"! 📲\n\n"
            "#marcao #longevidade #saudearticular #colageno #acidohialuronico #fitness40mais #treinopesado #qualidadedevida"
        )
    },
    {
        "id": "iarmonize_queda_capilar",
        "categoria": "ESTÉTICA CAPILAR & BARBA",
        "tema": "Queda de Cabelo e Entradas: A Fototerapia Funciona?",
        "preco": "R$ 189,90",
        "produto_img": PROD_IARMONIZE,
        "produto_nome": "Escova de LED Capilar Fototerapia Marcão",
        "link_venda": "https://marcaopersonal.com#loja",
        "slides": [
            {
                "titulo": "NOTOU O CABELO RALANDO\nE ENTRADAS AUMENTANDO?",
                "sub": "A miniaturização folicular que você precisa frear antes que o folículo morra:",
                "pontos": [
                    "O folículo capilar perde oxigenação e vai afinando gradativamente.",
                    "Shampoos comuns lavam a superfície mas não ativam o bulbo na raiz.",
                    "A fototerapia por LED vermelho penetra na derme e estimula ATP capilar.",
                    "Tratamento não-invasivo clinicamente validado pela dermatologia."
                ],
                "cta": "ARRASTE E VEJA A AÇÃO DA FOTOTERAPIA ››"
            },
            {
                "titulo": "COMO O LED VERMELHO\nACELERA O CRESCIMENTO DOS FIOS?",
                "sub": "Microcorrente e fotobiomodulação celular direta no couro cabeludo:",
                "pontos": [
                    "Estímulo da circulação sanguínea na raiz com microvibrações suaves.",
                    "Aumento da densidade dos fios e preenchimento de falhas na barba.",
                    "Uso simples de 10 minutos ao dia enquanto relaxa em casa.",
                    "Sem efeitos colaterais hormonais ou dependência de loções caras."
                ],
                "cta": "VEJA O PROTOCOLO OFICIAL DE HOJE ››"
            },
            {
                "titulo": "ESCOVA DE LED CAPILAR MARCÃO\nTECNOLOGIA DE FOTOTERAPIA IA",
                "sub": "O gadget oficial de biohacking para fortalecimento capilar:",
                "pontos": [
                    "Laser / LED Vermelho e Azul com função massageadora.",
                    "Apenas R$ 189,90 com garantia e frete grátis nacional.",
                    "Ideal para homens e mulheres com queda precoce ou falhas.",
                    "Atendimento direto com o Marcão pelo WhatsApp."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🦁 CABELO CAINDO NO BANHO OU ENTRADAS COMEÇANDO A APARECER? NÃO ESPERE PIORAR!\n\n"
            "A queda de cabelo acontece por um processo chamado miniaturização folicular: o vaso que irriga a raiz vai encolhendo, o fio nasce cada vez mais fino até parar de crescer.\n\n"
            "A fotobiomodulação por LED Vermelho (650nm) atua diretamente nas mitocôndrias das células do couro cabeludo, oxigenando o bulbo e despertando folículos em fase de dormência.\n\n"
            "💡 Protocolo Marcão Personal:\n"
            "• 10 minutos diários de fototerapia com a Escova de LED.\n"
            "• Estímulo da circulação local sem agressão química.\n"
            "• Fortalecimento de dentro para fora.\n\n"
            "👉 Garanta a sua Escova de LED Capilar por R$ 189,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\"! 📲\n\n"
            "#marcao #quedadecabelo #calvicie #fototerapia #cabeloforte #esteticamasculina #barba #biohacking"
        )
    },
    {
        "id": "creatina_mulheres_definicao",
        "categoria": "ALTA PERFORMANCE FEMININA",
        "tema": "Creatina para Mulheres: Músculos Firmes Sem Engordar",
        "preco": "R$ 169,90",
        "produto_img": PROD_CREATINA,
        "produto_nome": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://marcaopersonal.com#creatina",
        "slides": [
            {
                "titulo": "MULHER PODE TOMAR CREATINA\nOU VAI FICAR COM CORPO MASCULINO?",
                "sub": "O maior mito que afasta as mulheres do melhor suplemento do mundo:",
                "pontos": [
                    "A creatina NÃO altera hormônios e NÃO causa virilização.",
                    "Ela não engorda: zero calorias e zero acúmulo de gordura.",
                    "Ajuda a colar a pele no músculo, dando tônus nas pernas e glúteos.",
                    "Aumenta a resistência para fazer aquele treino de perna de verdade!"
                ],
                "cta": "ARRASTE E ENTENDA O TÔNUS FEMININO ››"
            },
            {
                "titulo": "COMO A CREATINA MODELA\nO GLÚTEO E AS COXAS?",
                "sub": "A hidratação da fibra muscular cria firmeza e combate a flacidez:",
                "pontos": [
                    "Mais força para agachar com carga e estímulo no bumbum.",
                    "Recuperação mais rápida entre as séries sem cansaço excessivo.",
                    "Melhora comprovada na cognição, foco mental e clareza diária.",
                    "Recomendada por ginecologistas e nutricionistas esportivas."
                ],
                "cta": "VEJA COMO TOMAR DO JEITO CERTO ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\nCREATINA MICRONIZADA 100% PURA",
                "sub": "Qualidade premium para resultados visíveis em semanas:",
                "pontos": [
                    "Pote com 300g (100 doses oficiais de 3g a 5g).",
                    "Apenas R$ 169,90 (menos de R$ 1,70 por dose diária!).",
                    "Dissolução instantânea, sem gosto e sem açúcar.",
                    "Despacho rápido pelos Correios para todo o Brasil."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "💖 MULHERES, ATENÇÃO: CREATINA NÃO ENGORDA E NÃO TE DEIXA 'MASCULINIZADA'!\n\n"
            "Se você quer coxas firmes, glúteos desenhados e abdômen durinho, a Creatina Micronizada é sua maior aliada! O mito de que 'creatina é só para homens que querem ficar gigantes' já foi derrubado há anos pela ciência.\n\n"
            "A creatina apenas fornece energia pura (ATP) para as suas células musculares, permitindo treinos mais eficientes e recuperação acelerada sem nenhuma alteração hormonal.\n\n"
            "✨ Resultados para o corpo feminino:\n"
            "• Redução da flacidez e aspecto de tônus firme nas pernas.\n"
            "• Disposição renovada para o dia a dia e treinos intensos.\n"
            "• Benefícios cognitivos comprovados para foco e memória.\n\n"
            "👉 Garanta a Creatina Micronizada 100% Pura por R$ 169,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\"! 📲\n\n"
            "#marcao #creatinafeminina #treinofeminino #gluteos #hipertrofiafeminina #tonusmuscular #fitnessparamulheres"
        )
    },
    {
        "id": "longevidade_senior_forca",
        "categoria": "LONGEVIDADE ATIVA 60+",
        "tema": "Musculação e Força na Terceira Idade: O Remédio Antienvelhecimento",
        "preco": "R$ 169,90",
        "produto_img": PROD_CREATINA,
        "produto_nome": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://marcaopersonal.com#creatina",
        "slides": [
            {
                "titulo": "PASSOU DOS 60 ANOS?\nA MUSCULAÇÃO É SUA POUPANÇA DE VIDA!",
                "sub": "A sarcopenia (perda de massa muscular) é o maior perigo na terceira idade:",
                "pontos": [
                    "A perda de massa muscular enfraquece ossos e aumenta risco de quedas.",
                    "Musculação orientada é o exercício mais seguro e eficaz para seniores.",
                    "Recupera o equilíbrio, a autonomia para caminhar e a vitalidade.",
                    "Nunca é tarde para começar a construir músculos fortes!"
                ],
                "cta": "ARRASTE E VEJA A CIÊNCIA DA LONGEVIDADE ››"
            },
            {
                "titulo": "POR QUE MÉDICOS GERIATRAS\nINDICAM CREATINA PARA SENIORES?",
                "sub": "Proteção neuromuscular e celular comprovada em estudos clínicos:",
                "pontos": [
                    "Aumenta a força de preensão manual e estabilidade nas pernas.",
                    "Preserva a massa magra mesmo em períodos de menos atividade.",
                    "Benefícios neurológicos comprovados na proteção da memória.",
                    "Fácil de tomar: basta misturar 3g a 5g na água ou no suco diário."
                ],
                "cta": "CONHEÇA O PROTOCOLO SÊNIOR MARCÃO ››"
            },
            {
                "titulo": "PADRÃO OURO MARCÃO PERSONAL\nAUTONOMIA E FORÇA VITAL",
                "sub": "Creatina Micronizada 100% Pura de grau laboratorial:",
                "pontos": [
                    "Pote de 300g (100 doses oficiais).",
                    "Apenas R$ 169,90 com garantia de procedência oficial.",
                    "Laudo laboratorial aprovado, zero sódio e zero conservantes.",
                    "Acompanhamento e consultoria pelo WhatsApp Marcão Personal."
                ],
                "cta": "LINK NA BIO: marcaopersonal.com • COMENTE QUERO ››"
            }
        ],
        "legenda": (
            "🌟 FORÇA, EQUILÍBRIO E AUTONOMIA APÓS OS 60 ANOS: O PODER DA MUSCULAÇÃO!\n\n"
            "O maior perigo do envelhecimento não é a idade no documento, mas a perda progressiva de massa muscular (sarcopenia). Quando os músculos enfraquecem, as articulações sofrem, a marcha fica lenta e as quedas se tornam frequentes.\n\n"
            "A musculação combinada com a suplementação de Creatina Micronizada 100% Pura é hoje considerada pelos maiores geriatras do mundo a intervenção número 1 para garantir independência, força nas pernas e clareza mental!\n\n"
            "👵 Benefícios comprovados para quem tem 60+:\n"
            "• Firmeza para levantar de cadeiras e subir escadas sem cansaço.\n"
            "• Proteção contra a osteoporose e fortalecimento da estrutura óssea.\n"
            "• Mais energia e disposição para aproveitar a vida com a família.\n\n"
            "👉 Garanta a Creatina Micronizada 100% Pura por R$ 169,90 no LINK DA BIO em marcaopersonal.com ou comente \"QUERO\"! 📲\n\n"
            "#marcao #longevidadeativa #terceiraidade #saude60mais #creatina #qualidadedevida #envelhecimentosaudavel"
        )
    }
]


def upload_arquivo_supabase(caminho_local: str, nome_remoto: str) -> str:
    """Faz o upload para o Supabase Storage e retorna a URL pública permanente."""
    if not SUPABASE_KEY or not os.path.exists(caminho_local):
        return None

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/png" if caminho_local.endswith(".png") else "image/jpeg",
        "x-upsert": "true"
    }

    url_storage = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/posts/{nome_remoto}"
    with open(caminho_local, "rb") as f:
        conteudo = f.read()

    try:
        r = requests.post(url_storage, headers=headers, data=conteudo, verify=False, timeout=30)
        if r.status_code in [200, 201]:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/posts/{nome_remoto}"
            print(f"  [STORAGE] Upload OK: {nome_remoto}")
            return public_url
        else:
            # Tentar PUT se já existir
            r_put = requests.put(url_storage, headers=headers, data=conteudo, verify=False, timeout=30)
            if r_put.status_code in [200, 201]:
                return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/posts/{nome_remoto}"
            print(f"  [STORAGE] Erro upload {nome_remoto}: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"  [STORAGE] Exceção no upload {nome_remoto}: {e}")
    return None


def salvar_criativo_no_content_calendar(registro: dict) -> bool:
    """Grava o criativo na fila 'ready' da tabela content_calendar no Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/content_calendar",
            headers=headers,
            json=registro,
            verify=False,
            timeout=15
        )
        if r.status_code in [200, 201]:
            print(f"  [DB] Masterpiece enfileirada no content_calendar com sucesso (ID: {r.json()[0].get('id')})")
            return True
        else:
            print(f"  [DB] Erro ao gravar content_calendar: {r.status_code} - {r.text[:150]}")
    except Exception as e:
        print(f"  [DB] Exceção ao gravar no Supabase: {e}")
    return False


def semear_biblioteca_adobe():
    """Renderiza carrosséis de 3 slides e cards 4:5 no padrão Adobe 2.0 e salva no Supabase."""
    print("=" * 70)
    print("🚀 INICIANDO SEMEADURA DA ADOBE CREATIVE ENGINE 2.0 NO SUPABASE")
    print("=" * 70)

    total_gerados = 0

    for idx_tema, tema in enumerate(MASTER_TEMAS):
        ts = int(time.time()) + idx_tema
        if tema["id"] == "azempika_potencia_masculina":
            bg_sorteado = os.path.join(DIR_OUTPUT, "bg_homem_maduro_grisalho.png")
            autor_criativo = "MARCÃO PERSONAL"
        else:
            bg_sorteado = FOTOS_BACKGROUND[idx_tema % len(FOTOS_BACKGROUND)]
            autor_criativo = "EVANDRO GALLINA"
        print(f"\n[{idx_tema+1}/{len(MASTER_TEMAS)}] Produzindo Carrossel: '{tema['tema']}'")
        print(f"  Background selecionado: {os.path.basename(bg_sorteado)}")

        # 1. Renderizar os 3 Slides do Carrossel
        slides_gerados = []
        for idx_slide, s in enumerate(tema["slides"]):
            num_slide = idx_slide + 1
            nome_arquivo = f"carrossel_{tema['id']}_s{num_slide}_{ts}.png"
            caminho_local = os.path.join(DIR_OUTPUT, nome_arquivo)

            # Slide 1 recebe o fundo fotográfico com Zona Facial Protegida
            # Slide 3 recebe o produto com sombra e pedestal
            bg_para_slide = bg_sorteado if num_slide == 1 else None
            prod_para_slide = tema["produto_img"] if num_slide == 3 else None
            preco_para_slide = tema["preco"] if num_slide == 3 else None

            renderizar_slide_carrossel_masterpiece(
                titulo=s["titulo"],
                subtitulo=s["sub"],
                pontos=s["pontos"],
                cta_slide=s["cta"],
                num_slide=num_slide,
                total_slides=3,
                categoria=tema["categoria"],
                out_path=caminho_local,
                bg_path=bg_para_slide,
                produto_img_path=prod_para_slide,
                preco=preco_para_slide,
                formato_slide="feed",
                estilo_cor="gold_dark"
            )
            slides_gerados.append((caminho_local, nome_arquivo))

        # 2. Renderizar Story Vertical 9:16 Correspondente
        story_arquivo = f"story_{tema['id']}_{ts}.png"
        story_local = os.path.join(DIR_OUTPUT, story_arquivo)
        renderizar_criativo_masterpiece(
            headline=tema["slides"][0]["titulo"].split("\n")[0],
            subheadline=tema["slides"][0]["sub"],
            pontos_beneficio=tema["slides"][0]["pontos"][:3],
            categoria=tema["categoria"],
            cta_texto=f"COMPRE POR {tema['preco']}",
            bg_path=bg_sorteado,
            produto_img_path=tema["produto_img"],
            preco=tema["preco"],
            nome_autor=autor_criativo,
            out_path=story_local,
            formato="story",
            estilo_cor="gold_dark"
        )

        # 3. Upload de todos os slides e do story para a CDN do Supabase
        urls_slides = []
        for c_local, n_remoto in slides_gerados:
            url_cdn = upload_arquivo_supabase(c_local, n_remoto)
            if url_cdn:
                urls_slides.append(url_cdn)

        url_story = upload_arquivo_supabase(story_local, story_arquivo)

        # 4. Registrar na fila 'ready' do Supabase content_calendar
        if len(urls_slides) == 3:
            metadata_content = {
                "format": "carrossel",
                "slides": urls_slides,
                "story_url": url_story,
                "tema_id": tema["id"],
                "categoria": tema["categoria"],
                "produto_nome": tema.get("produto_nome"),
                "preco": tema.get("preco"),
                "link_venda": tema.get("link_venda")
            }

            registro_db = {
                "platform": "instagram",
                "content_id": json.dumps(metadata_content, ensure_ascii=False),
                "caption": tema["legenda"],
                "media_url": urls_slides[0],
                "status": "ready",
                "scheduled_at": datetime.now().isoformat()
            }

            if salvar_criativo_no_content_calendar(registro_db):
                total_gerados += 1

    print("\n" + "=" * 70)
    print(f"✨ CONCLUÍDO! Total de {total_gerados} Carrosséis Masterpieces enfileirados como 'ready'!")
    print("=" * 70)


if __name__ == "__main__":
    semeador = semear_biblioteca_adobe()
