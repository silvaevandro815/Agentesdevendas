import os
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Mapeamento Geográfico Estratégico do Brasil para E-commerce de Saúde e Estética
ESTADOS_ALTA_DEMANDA_BR = {
    "SUDESTE_SUL": [
        {"uf": "SP", "nome": "São Paulo", "peso_demanda": "Máximo (32% do volume nacional)"},
        {"uf": "RJ", "nome": "Rio de Janeiro", "peso_demanda": "Muito Alto (14% do volume)"},
        {"uf": "MG", "nome": "Minas Gerais", "peso_demanda": "Muito Alto (12% do volume - Hub Sofia)"},
        {"uf": "PR", "nome": "Paraná", "peso_demanda": "Alto (8% do volume)"},
        {"uf": "RS", "nome": "Rio Grande do Sul", "peso_demanda": "Alto (7% do volume)"},
        {"uf": "SC", "nome": "Santa Catarina", "peso_demanda": "Alto (6% do volume)"}
    ],
    "CENTRO_OESTE_NORDESTE": [
        {"uf": "DF", "nome": "Distrito Federal", "peso_demanda": "Ticket Médio Mais Alto do País"},
        {"uf": "GO", "nome": "Goiás", "peso_demanda": "Alto em Estética e Fitness"},
        {"uf": "BA", "nome": "Bahia", "peso_demanda": "Líder de Busca no Nordeste"},
        {"uf": "PE", "nome": "Pernambuco", "peso_demanda": "Alto em Saúde e Suplementação"}
    ]
}


def obter_produtos_supabase():
    """
    Consulta o catálogo dinâmico no Supabase (products e cerebro_conhecimento).
    """
    if not SUPABASE_KEY:
        return []

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        with httpx.Client(verify=False, timeout=12) as client:
            r_prod = client.get(f"{SUPABASE_URL}/rest/v1/products?order=price.desc", headers=headers)
            produtos = r_prod.json() if r_prod.status_code == 200 else []

            catalogo_completo = []
            for p in produtos:
                sku = p.get("sku", "")
                nome = p.get("name", "")
                preco = p.get("price", 0)
                link = p.get("affiliate_url", "https://marcaopersonal.com")

                termos_busca = []
                faixa_etaria = "25-55"
                genero = "Todos"
                categoria = "Geral"

                if "AZEMPIKA" in sku or "emagrecimento" in nome.lower() or "azempika" in nome.lower():
                    termos_busca = ["azempic", "caneta emagrecedora", "compulsao alimentar", "tirar fome doce", "emagrecimento rapido"]
                    faixa_etaria = "25-55"
                    genero = "Mulheres (70%) e Homens (30%)"
                    categoria = "Emagrecimento & Saciedade"
                elif "CREATINA" in sku or "creatina" in nome.lower():
                    termos_busca = ["creatina monohidratada", "creatina feminina", "creatina pura", "hipertrofia", "tonus muscular"]
                    faixa_etaria = "20-45"
                    genero = "Homens e Mulheres (50/50)"
                    categoria = "Força & Tônus Muscular"
                elif "COLAGENO" in sku or "colágeno" in nome.lower() or "pele" in nome.lower():
                    termos_busca = ["colageno hidrolisado", "acido hialuronico pele", "flacidez rosto", "firmeza da pele", "rejuvenescimento"]
                    faixa_etaria = "28-55"
                    genero = "Mulheres (85%) e Homens (15%)"
                    categoria = "Estética & Firmeza da Pele"
                elif "IARMONIZE" in sku or "capilar" in nome.lower() or "cabelo" in nome.lower():
                    termos_busca = ["queda de cabelo", "calvicie tratamento", "alopecia", "crescer cabelo", "fortalecer foliculos"]
                    faixa_etaria = "30-58"
                    genero = "Homens e Mulheres (50/50)"
                    categoria = "Tecnologia Capilar"
                elif "VISION" in sku or "visao" in nome.lower() or "ocular" in nome.lower():
                    termos_busca = ["visao turva", "vista cansada", "saude ocular", "luteina zeaxantina", "fadiga visual"]
                    faixa_etaria = "40-70"
                    genero = "Homens e Mulheres"
                    categoria = "Saúde Ocular & Visão"
                elif "BALANCA" in sku:
                    termos_busca = ["balanca bioimpedancia", "pesar gordura corporal", "balanca bluetooth", "taxa metabolica"]
                    faixa_etaria = "20-50"
                    genero = "Homens e Mulheres"
                    categoria = "Biohacking & Avaliação"

                catalogo_completo.append({
                    "id": p.get("id"),
                    "sku": sku,
                    "nome": nome,
                    "preco": f"R$ {preco:.2f}".replace(".", ","),
                    "preco_num": preco,
                    "link": link,
                    "categoria": categoria,
                    "termos_busca": termos_busca,
                    "faixa_etaria": faixa_etaria,
                    "genero": genero
                })

            return catalogo_completo
    except Exception as e:
        print("Erro ao consultar produtos no Supabase:", e)
        return []


def pesquisar_tendencias_google(keyword):
    """
    Consulta sugestões em tempo real do Google Brasil para descobrir o que as pessoas estão pesquisando.
    """
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&q={keyword}&gl=br&hl=pt-BR"
    try:
        with httpx.Client(verify=False, timeout=8) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = json.loads(resp.content.decode("latin-1"))
                return data[1][:6] if len(data) > 1 else []
    except Exception:
        pass
    return []


def gerar_inteligencia_completa_produto(produto):
    """
    Combina dados do produto, buscas ao vivo do Google e estratégia de funil de 2 fases.
    """
    buscas_quentes = []
    for termo in produto.get("termos_busca", [])[:3]:
        sugestoes = pesquisar_tendencias_google(termo)
        buscas_quentes.extend(sugestoes[:2])
    buscas_quentes = list(dict.fromkeys(buscas_quentes))[:5]

    nome = produto["nome"]
    preco = produto["preco"]
    link = produto["link"]

    if "Azempika" in nome or "AZEMPIKA" in produto["sku"]:
        fase1_headline = "Você não tem falta de disciplina: tem pico de ansiedade alimentar 🔥"
        fase1_copy = (
            "Aquela vontade incontrolável de assaltar a geladeira à noite ou comer um doce após o almoço "
            "é um disparo hormonal de saciedade desregulada. A Caneta Azempika Original atua modulando a saciedade "
            "e gerando queima térmica suave. Veja como reprogramar o seu apetite sem passar fome."
        )
        fase1_cta = "Entender Como Funciona"

        fase2_headline = "Diga adeus à compulsão: Caneta Azempika por apenas R$ 99 ⚡"
        fase2_copy = (
            "Aproveite o lote promocional direto do laboratório: Caneta Azempika Original por apenas R$ 99,00! "
            "Embalagem térmica e entrega discreta rastreada pelos Correios em todo o Brasil. "
            "Estoque limitado com garantia do Marcão Personal!"
        )
        fase2_cta = "Comprar Caneta Azempika (R$ 99)"

    elif "Creatina" in nome or "CREATINA" in produto["sku"]:
        fase1_headline = "O mito que te impede de ter o glúteo e abdômen firmes: Creatina não incha mulher! 🏋️‍♀️"
        fase1_copy = (
            "Marcão Personal desmistifica: creatina não retém líquido debaixo da pele, ela hidrata a fibra "
            "muscular por dentro! O resultado? Muito mais força no treino, queima acelerada de calorias e músculos durinhos "
            "sem retenção hídrica. 100% de pureza com laudo."
        )
        fase1_cta = "Descobrir Como Tomar"

        fase2_headline = "Creatina Micronizada 100% Pura Nature's Prime (300g) — R$ 169,90 ⚡"
        fase2_copy = (
            "Pote de 300g rende 100 doses diárias. Zero açúcar, zero sódio e solubilidade instantânea. "
            "Compre agora a creatina com certificado máximo de pureza recomendado pelo Marcão com despacho imediato!"
        )
        fase2_cta = "Garantir Oferta da Creatina"

    elif "Colágeno" in nome or "COLAGENO" in produto["sku"]:
        fase1_headline = "Pós-25 anos você perde 1% de colágeno ao ano: por isso surgem as linhas de expressão ✨"
        fase1_copy = (
            "Não adianta tomar colágeno barato de farmácia com açúcar que não absorve! "
            "Para devolver a firmeza à pele e sustentabilidade facial, a molécula precisa ser Hidrolisada combinada com Ácido Hialurônico. "
            "Descubra a ciência por trás da firmeza dérmica."
        )
        fase1_cta = "Conhecer o Protocolo de Firmeza"

        fase2_headline = "Pele firme e hidratada sem gastar fortunas com estética facial ⚡"
        fase2_copy = (
            "Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime sabor Abacaxi com Hortelã. "
            "Apenas R$ 164,90 para 30 doses repletas de biopeptídeos. Entrega rastreada para todo o Brasil!"
        )
        fase2_cta = "Quero Pele Firme Agora"

    elif "Capilar" in nome or "IARMONIZE" in produto["sku"]:
        fase1_headline = "Xampu antiqueda não faz nascer cabelo porque não penetra no folículo ⚡"
        fase1_copy = (
            "Se você está vendo fios no ralo do banho ou as entradas aumentando, parar o processo exige nutrir "
            "a matriz celular de dentro para fora. O Protocolo IArmonize une 4 fases clínicas e fototerapia folicular. "
            "Veja os laudos e resultados."
        )
        fase1_cta = "Ver Como Salvar os Fios"

        fase2_headline = "KIT IArmonize Capilar Clínico: Tratamento Completo de 4 Fases ⚡"
        fase2_copy = (
            "Diga adeus à calvície sem dor e sem gastar R$ 20.000 em implantes. Tratamento completo IArmonize "
            "com atendimento de especialista 24h no WhatsApp. Em até 12x no cartão com frete grátis Correios!"
        )
        fase2_cta = "Falar no WhatsApp com Especialista"

    else:
        fase1_headline = f"Descubra o segredo do Marcão Personal para {produto['categoria']} ⚡"
        fase1_copy = f"Entenda por que o {nome} é o protocolo mais avançado do mercado para transformar sua saúde e performance."
        fase1_cta = "Saber Mais"

        fase2_headline = f"{nome} por apenas {preco} — Pronta Entrega ⚡"
        fase2_copy = f"Garanta seu {nome} com frete rápido para todo o Brasil e garantia total oficial Marcão Personal!"
        fase2_cta = "Garantir Meu Pedido"

    return {
        "produto": produto,
        "buscas_quentes_google": buscas_quentes,
        "publico_alvo": {
            "faixa_etaria": produto["faixa_etaria"],
            "genero": produto["genero"],
            "estados_chave": ["SP", "RJ", "MG", "PR", "SC", "RS", "DF", "GO", "BA"]
        },
        "fase_1_atencao": {
            "etapa": "Topo de Funil (Descoberta / Atenção)",
            "objetivo_meta": "OUTCOME_TRAFFIC (Gerar Visitantes Qualificados & Alimentar Pixel)",
            "headline": fase1_headline,
            "copy": fase1_copy,
            "cta": fase1_cta,
            "link": f"{link}?utm_source=meta_ads&utm_medium=cpc&utm_campaign=rui_fase1_atencao"
        },
        "fase_2_venda": {
            "etapa": "Fundo de Funil (Conversão / Venda Direta)",
            "objetivo_meta": "OUTCOME_TRAFFIC (Checkout Direto & WhatsApp Sofia)",
            "headline": fase2_headline,
            "copy": fase2_copy,
            "cta": fase2_cta,
            "link": f"{link}?utm_source=meta_ads&utm_medium=cpc&utm_campaign=rui_fase2_venda"
        }
    }


def gerar_relatorio_inteligencia_diario():
    """
    Compila o relatório com a análise de todos os produtos do Supabase e Google Trends.
    """
    produtos = obter_produtos_supabase()
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "total_produtos": len(produtos),
        "estados_prioritarios": ESTADOS_ALTA_DEMANDA_BR,
        "produtos_analisados": []
    }

    for p in produtos:
        intel = gerar_inteligencia_completa_produto(p)
        relatorio["produtos_analisados"].append(intel)

    return relatorio


if __name__ == "__main__":
    print("=== RUI INTELLIGENCE ENGINE (GOOGLE TRENDS & META 2026) ===")
    relatorio = gerar_relatorio_inteligencia_diario()
    print(f"Total de produtos mapeados no Supabase: {relatorio['total_produtos']}")
    for item in relatorio["produtos_analisados"]:
        prod = item["produto"]
        h1 = item['fase_1_atencao']['headline'].encode('ascii', errors='replace').decode('ascii')
        h2 = item['fase_2_venda']['headline'].encode('ascii', errors='replace').decode('ascii')
        print(f"\n-> {prod['nome']} ({prod['preco']})")
        print(f"   Publico: {item['publico_alvo']['genero']} | Idade: {item['publico_alvo']['faixa_etaria']}")
        print(f"   Buscas Google Brasil: {item['buscas_quentes_google']}")
        print(f"   Fase 1 (Atencao): {h1}")
        print(f"   Fase 2 (Venda): {h2}")
