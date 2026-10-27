"""
Shopee Affiliate Open API Engine — Marcão Personal
==================================================
Autonomia total de busca, recomendação e conversão de afiliados na Shopee.
Permite ao Marcão Personal:
1. Buscar produtos em tempo real na Shopee com base nas dores, queixas e objetivos dos alunos.
2. Gerar links curtos de afiliado (s.shopee.com.br) automaticamente com rastreio por sub_id.
3. Obter produtos com melhores avaliações, maiores comissões e melhores preços.
4. Mapear dores fisiológicas e biomecânicas para os acessórios ideais.
5. Monitorar relatórios de conversão e comissões da Shopee.
"""

import os
import json
import time
import hashlib
import re
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

APP_ID = os.getenv("SHOPEE_APP_ID", "18302091279").strip()
SECRET = os.getenv("SHOPEE_SECRET", "4KLNIQLXFE7TNE7UTNZHE44BBRIIHDOS").strip()
GRAPHQL_URL = os.getenv("SHOPEE_GRAPHQL_URL", "https://open-api.affiliate.shopee.com.br/graphql").strip()

# Cache local de buscas para respostas instantâneas (< 1 segundo)
_CACHE_BUSCA = {}
_CACHE_TTL = 300  # 5 minutos


def normalizar_texto(texto: str) -> str:
    """Remove acentos e padroniza o texto para casamento de palavras-chave."""
    substituicoes = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u',
        'ç': 'c'
    }
    t = (texto or "").lower()
    for k, v in substituicoes.items():
        t = t.replace(k, v)
    return t


def _gerar_headers_shopee(payload_string: str) -> Dict[str, str]:
    """Gera a assinatura criptográfica SHA256 exigida pela Shopee Open API."""
    timestamp = int(time.time())
    factor = f"{APP_ID}{timestamp}{payload_string}{SECRET}"
    signature = hashlib.sha256(factor.encode("utf-8")).hexdigest()
    
    return {
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={signature}"
    }


async def executar_graphql_shopee(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Executa uma chamada GraphQL autenticada na Shopee Affiliate Open API."""
    payload_dict = {"query": query}
    if variables:
        payload_dict["variables"] = variables
        
    payload_string = json.dumps(payload_dict, separators=(",", ":"))
    headers = _gerar_headers_shopee(payload_string)
    
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        res = await client.post(GRAPHQL_URL, content=payload_string, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"[SHOPEE API] Erro HTTP {res.status_code}: {res.text[:300]}")
            return {"error": f"HTTP {res.status_code}", "detail": res.text}


async def _executar_query_ofertas(keyword: str, limit: int = 3, sort_type: int = 1) -> List[Dict[str, Any]]:
    """Helper interno de execução GraphQL para productOfferV2."""
    query = """
    query SearchOffers($keyword: String, $limit: Int, $sortType: Int) {
      productOfferV2(keyword: $keyword, listType: 0, sortType: $sortType, page: 1, limit: $limit) {
        nodes {
          itemId
          productName
          price
          ratingStar
          sales
          commissionRate
          commission
          imageUrl
          shopName
          productLink
          offerLink
        }
      }
    }
    """
    variables = {
        "keyword": keyword,
        "limit": limit,
        "sortType": sort_type
    }
    data = await executar_graphql_shopee(query, variables)
    nodes = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])
    
    produtos = []
    for n in nodes:
        preco_float = float(n.get("price", 0.0))
        comissao_float = float(n.get("commission", 0.0))
        taxa_float = float(n.get("commissionRate", 0.0)) * 100
        
        # Cálculo de custo por dia diluído em 30 ou 60 dias
        dias_estimados = 30 if preco_float < 80 else 60
        custo_dia = preco_float / dias_estimados
        
        produtos.append({
            "item_id": n.get("itemId"),
            "titulo": n.get("productName"),
            "preco": preco_float,
            "preco_formatado": f"R$ {preco_float:.2f}".replace(".", ","),
            "custo_dia_formatado": f"R$ {custo_dia:.2f}".replace(".", ","),
            "avaliacao": float(n.get("ratingStar", 5.0)),
            "vendas": int(n.get("sales", 0)),
            "comissao_reais": comissao_float,
            "comissao_taxa": f"{taxa_float:.1f}%",
            "imagem_url": n.get("imageUrl"),
            "loja": n.get("shopName"),
            "link_produto": n.get("productLink"),
            "link_afiliado": n.get("offerLink")
        })
    return produtos


async def buscar_produtos_shopee(keyword: str, limit: int = 3, sort_type: int = 1) -> List[Dict[str, Any]]:
    """
    Busca produtos por palavra-chave na Shopee retornando dados enriquecidos e links de afiliado.
    Possui fallback automático para termos mais concisos caso a busca longa retorne vazia.
    sort_type: 1 = Relevância / Mais Vendidos, 2 = Maior Comissão, 5 = Menor Preço
    """
    termo_limpo = normalizar_texto(keyword).strip()
    cache_key = f"{termo_limpo}_{limit}_{sort_type}"
    now = time.time()
    
    if cache_key in _CACHE_BUSCA:
        cached_data, timestamp = _CACHE_BUSCA[cache_key]
        if now - timestamp < _CACHE_TTL:
            return cached_data

    try:
        # Tentativa 1: termo completo
        produtos = await _executar_query_ofertas(termo_limpo, limit, sort_type)
        
        # Tentativa 2 (Fallback): se vazio e tiver mais de 2 palavras, reduz para as 2 primeiras
        if not produtos and len(termo_limpo.split()) > 2:
            palavras = termo_limpo.split()
            termo_reduzido = f"{palavras[0]} {palavras[1]}"
            produtos = await _executar_query_ofertas(termo_reduzido, limit, sort_type)
            
        _CACHE_BUSCA[cache_key] = (produtos, now)
        return produtos
    except Exception as e:
        print(f"[SHOPEE API] Erro ao buscar produtos para '{keyword}': {e}")
        return []


async def gerar_link_afiliado_shopee(url_original: str, sub_id: Optional[str] = "marcao") -> Optional[str]:
    """
    Converte qualquer URL de produto da Shopee em um short link de afiliado oficial.
    Ex: https://shopee.com.br/... -> https://s.shopee.com.br/XYZ
    """
    sub_id_limpo = "".join(c for c in (sub_id or "marcao") if c.isalnum())[:20]
    
    mutation = """
    mutation GenerateLink($originUrl: String!, $subIds: [String]) {
      generateShortLink(input: {
        originUrl: $originUrl,
        subIds: $subIds
      }) {
        shortLink
      }
    }
    """
    
    variables = {
        "originUrl": url_original,
        "subIds": [sub_id_limpo] if sub_id_limpo else ["marcao"]
    }
    
    try:
        data = await executar_graphql_shopee(mutation, variables)
        short_link = data.get("data", {}).get("generateShortLink", {}).get("shortLink")
        if short_link:
            return short_link
    except Exception as e:
        print(f"[SHOPEE API] Erro ao gerar link de afiliado: {e}")
        
    return None


# -----------------------------------------------------------------------------
# MAPEAMENTO DINÂMICO DE DORES E NECESSIDADES PARA PRODUTOS SHOPEE
# -----------------------------------------------------------------------------
MAPA_DORES_SHOPEE = {
    # 1. Biomecânica & Articulações
    "joelho": {
        "aliases": ["joelho", "patela", "estalando o joelho", "dor no joelho", "menisco"],
        "termo_busca": "joelheira compressao crossfit",
        "motivo": "estabilizar a patela, aquecer a articulação e eliminar o atrito nos agachamentos",
        "estudo": "a compressão térmica e elástica reduz a sobrecarga tendínea em até 35%"
    },
    "lombar": {
        "aliases": ["lombar", "dor na lombar", "coluna", "pinçando a lombar"],
        "termo_busca": "cinto musculacao lombar",
        "motivo": "aumentar a pressão intra-abdominal e blindar a coluna contra hérnias em cargas pesadas",
        "estudo": "o cinturão reduz em até 40% a compressão dos discos vertebrais no levantamento terra"
    },
    "costas": {
        "aliases": ["costas", "dorsal", "escapula"],
        "termo_busca": "cinto musculacao agachamento",
        "motivo": "suporte de sustentação e estabilidade central nos treinos de força",
        "estudo": "estabilidade postural máxima"
    },
    "ombro": {
        "aliases": ["ombro", "manguito", "dor no ombro", "supino doendo"],
        "termo_busca": "faixa elastica manguito",
        "motivo": "fortalecimento e aquecimento do manguito rotador antes do supino",
        "estudo": "ativação preventiva reduz em 80% o risco de impacto subacromial"
    },
    "punho": {
        "aliases": ["punho", "pulso", "dor no punho", "aberto o punho"],
        "termo_busca": "munhequeira elastica musculacao",
        "motivo": "evitar a hiperextensão do punho no supino reto e desenvolvimento militar",
        "estudo": "estabilidade articular e transmissão direta de força para a barra"
    },
    "cotovelo": {
        "aliases": ["cotovelo", "epicondilite", "triceps doendo"],
        "termo_busca": "cotoveleira compressao musculacao",
        "motivo": "prevenção de epicondilite nos treinos pesados de tríceps e peito",
        "estudo": "compressão térmica melhora a circulação local e absorve o impacto"
    },
    "pegada": {
        "aliases": ["pegada", "mao abrindo", "antebraço", "antepraco", "falha na pegada", "strap"],
        "termo_busca": "strap musculacao peso",
        "motivo": "eliminar a falha do antebraço para esmagar as dorsais com carga máxima",
        "estudo": "permite realizar 3 a 5 repetições extras sem abrir a mão"
    },
    "calos": {
        "aliases": ["calo", "calos", "mao doendo", "mao machucada", "luva", "caleira"],
        "termo_busca": "luva musculacao academia",
        "motivo": "proteger as palmas das mãos contra calos e melhorar a aderência na barra",
        "estudo": "antiderrapante com proteção na palma"
    },

    # 2. Treino em Casa, Viagens e Aeróbico
    "elastico": {
        "aliases": ["elastico", "extensor", "mini band", "treinar em casa", "treino em casa", "viajar", "viagem"],
        "termo_busca": "kit elastico extensor musculacao",
        "motivo": "permitir treino com tensão contínua progressiva em qualquer lugar sem depender de academia",
        "estudo": "a tensão elástica gera hipertrofia mecânica equivalente aos pesos livres"
    },
    "corda": {
        "aliases": ["corda", "pular corda", "cardio em casa", "aerobico rapido"],
        "termo_busca": "corda pular crossfit",
        "motivo": "manter o condicionamento aeróbico e gasto calórico em qualquer hotel ou parque",
        "estudo": "15 minutos de corda equivalem a 30 minutos de corrida moderada"
    },

    # 3. Performance, Hidratação, Visão e Acessórios
    "garrafa": {
        "aliases": ["garrafa", "agua", "hidratacao", "sede", "garrafao"],
        "termo_busca": "garrafa termica academia",
        "motivo": "bater a meta hídrica de 35ml a 40ml por kg com água gelada o treino inteiro",
        "estudo": "desidratação de apenas 2% derruba a força muscular em mais de 15%"
    },
    "celular": {
        "aliases": ["celular", "suporte", "gravar treino", "filmar execucao", "tripe"],
        "termo_busca": "suporte celular ima academia",
        "motivo": "gravar a execução dos exercícios para eu analisar a sua biomecânica e corrigir a postura",
        "estudo": "o feedback visual acelera o aprendizado motor e previne lesões"
    },
    "roupa_termica": {
        "aliases": ["suor", "assadura", "segunda pele", "roupa de treino", "termica"],
        "termo_busca": "camiseta termica compressao dry fit",
        "motivo": "absorção rápida do suor, conforto térmico e suporte muscular sem assaduras",
        "estudo": "melhora a oxigenação muscular e a dissipação de calor"
    },
    "bermuda": {
        "aliases": ["bermuda", "coxa assando", "short compressao"],
        "termo_busca": "bermuda compressao academia",
        "motivo": "evitar o atrito interno das coxas e dar sustentação ao quadríceps",
        "estudo": "zero fricção na pele e suporte venoso"
    },
    "tenis": {
        "aliases": ["tenis", "calcado", "sapato", "agachamento reto", "pe descalco"],
        "termo_busca": "tenis sola reta academia",
        "motivo": "base estável de apoio com sola reta para transmitir força nos agachamentos",
        "estudo": "sola plana aumenta o torque nos calcanhares em até 22%"
    },
    "mochila": {
        "aliases": ["mochila", "bolsa de treino", "levar marmita", "mala academia"],
        "termo_busca": "mochila academia impermeavel",
        "motivo": "organizar marmitas, straps, garrafa e roupa de treino no dia a dia",
        "estudo": "organização diária elimina faltas nos treinos"
    },

    # 4. Monitoramento & Balança
    "balanca": {
        "aliases": ["balanca", "bioimpedancia", "pesar", "gordura corporal", "balanca inteligente"],
        "termo_busca": "balanca bioimpedancia bluetooth",
        "motivo": "medir 13 biomarcadores clínicos (gordura visceral, massa muscular, água) e ativar a mentoria VIP",
        "estudo": "o peso isolado mente; o que importa é a composição de gordura visceral e massa magra"
    }
}


async def prescrever_produto_autonomo(mensagem_aluno: str, sub_id: str = "aluno") -> Optional[Dict[str, Any]]:
    """
    Analisa a mensagem do aluno e prescreve o produto ideal da Shopee com link de afiliado,
    pitch personalizado de treinador e decomposição do custo por dia.
    """
    texto_norm = normalizar_texto(mensagem_aluno)
    
    # 1. Procurar nas categorias do mapa de dores
    dor_detectada = None
    dados_dor = None
    
    for chave, config in MAPA_DORES_SHOPEE.items():
        for alias in config["aliases"]:
            if alias in texto_norm:
                dor_detectada = chave
                dados_dor = config
                break
        if dor_detectada:
            break
            
    termo = dados_dor["termo_busca"] if dados_dor else None
    
    # 2. Se não caiu nas regras fixas, verificar se pediu recomendação explícita
    if not termo:
        gatilhos_compra = [
            "onde compro", "qual comprar", "recomenda", "indica", "qual voce usa",
            "qual você usa", "preciso de", "quero comprar", "link da", "link do",
            "tem na shopee", "acha na shopee", "me manda o link", "qual suporte"
        ]
        for g in gatilhos_compra:
            g_norm = normalizar_texto(g)
            if g_norm in texto_norm:
                partes = texto_norm.split(g_norm, 1)
                if len(partes) > 1 and len(partes[1].strip()) > 2:
                    termo_candidato = partes[1].strip().replace("?", "").replace(".", "")[:30]
                    termo_candidato = re.sub(r'^(um|uma|o|a|os|as|de|para|pra)\s+', '', termo_candidato)
                    if len(termo_candidato) >= 3:
                        termo = termo_candidato
                        break
                        
    if not termo:
        return None
        
    # 3. Buscar produto mais bem avaliado na Shopee
    produtos = await buscar_produtos_shopee(termo, limit=2, sort_type=1)
    if not produtos:
        return None
        
    campeao = produtos[0]
    
    # 4. Montar a resposta persuasiva do Marcão em 2 a 3 balões curtos
    motivo_tecnico = dados_dor["motivo"] if dados_dor else f"garantir a máxima performance no seu treino de {termo}"
    
    pitch = (
        f"Irmão, pra resolver essa questão e {motivo_tecnico}, eu recomendo exatamente este modelo da Shopee!\n\n"
        f"Faz a conta comigo: sai por apenas {campeao['custo_dia_formatado']} por dia! Menos que uma moeda de troco pra você treinar com segurança e sem dor.\n\n"
        f"⭐ Avaliação {campeao['avaliacao']} estrelas de quem comprou. Garante o seu direto com frete oficial aqui: {campeao['link_afiliado']}"
    )
    
    return {
        "termo_buscado": termo,
        "produto": campeao,
        "pitch_pronto": pitch,
        "dor_detectada": dor_detectada
    }


async def obter_relatorio_vendas_shopee(dias: int = 7) -> Dict[str, Any]:
    """
    Consulta o relatório de pedidos e comissões dos últimos N dias na Shopee Affiliate API.
    """
    now = datetime.now()
    inicio = int((now - timedelta(days=dias)).timestamp())
    fim = int(now.timestamp())
    
    query = """
    query GetPartnerReport($start: Int!, $end: Int!, $limit: Int) {
      partnerOrderReport(purchaseTimeStart: $start, purchaseTimeEnd: $end, limit: $limit) {
        nodes {
          orderId
          orderStatus
          purchaseTime
          completeTime
          totalCommission
          items {
            itemId
            itemName
            itemPrice
            qty
            actualCommission
          }
        }
        totalCount
      }
    }
    """
    
    variables = {
        "start": inicio,
        "end": fim,
        "limit": 50
    }
    
    try:
        data = await executar_graphql_shopee(query, variables)
        report = data.get("data", {}).get("partnerOrderReport", {})
        return {
            "total_pedidos": report.get("totalCount", 0),
            "pedidos": report.get("nodes", []),
            "periodo_dias": dias
        }
    except Exception as e:
        print(f"[SHOPEE API] Erro ao obter relatório de vendas: {e}")
        return {"total_pedidos": 0, "pedidos": [], "erro": str(e)}
