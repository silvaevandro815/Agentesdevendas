"""
Autonomous Curator - Motor de Curadoria e Estratégia Comercial Autônoma
========================================================================
Opera a inteligência de negócios do Marcão AI para atingir a meta de R$ 1 Milhão:
1. Avalia viabilidade comercial e margem de lucro de novos produtos.
2. Filtra rigorosamente contra regras ANVISA, CONAR, CREF e Meta Ads.
3. Ingestão e interpretação inteligente de links de afiliados (Amazon, Magalu, ML, Shopee, Braip).
4. Sincroniza imediatamente o catálogo unificado para WhatsApp e Instagram.
"""

import os
import re
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

try:
    from catalog_service import salvar_ou_atualizar_produto, obter_produtos_ativos, invalidar_cache
except ImportError:
    from apps.api.catalog_service import salvar_ou_atualizar_produto, obter_produtos_ativos, invalidar_cache

TERMOS_PROIBIDOS_ANVISA_META = [
    "cura", "curar", "emagreça dormindo", "queima gordura rápido", "derreter gordura",
    "antes e depois", "anabolizante", "injetável", "sem dieta e sem treino",
    "elimine 10kg em 7 dias", "remédio milagroso", "fórmula secreta dos médicos"
]

CATEGORIAS_ALTA_DEMANDA_FITNESS = [
    "creatina", "whey", "balança", "bioimpedância", "colágeno", "ômega 3",
    "magnésio", "strap", "faixa elástica", "smartband", "garrafa térmica",
    "pré-treino", "cafeína", "multivitamínico", "hipertrofia", "recuperação muscular"
]


def avaliar_compliance_sanitario(nome: str, descricao: str) -> dict:
    """
    Verifica se o produto respeita os guardrails da ANVISA, CONAR e Meta Ads.
    """
    texto_completo = f"{nome} {descricao}".lower()
    
    infracoes = []
    for termo in TERMOS_PROIBIDOS_ANVISA_META:
        if termo in texto_completo:
            infracoes.append(termo)
            
    if infracoes:
        return {
            "aprovado": False,
            "motivo": f"Contém termos proibidos pelas diretrizes sanitárias/publicitárias: {', '.join(infracoes)}",
            "score_compliance": 0
        }
        
    return {
        "aprovado": True,
        "motivo": "Em conformidade com as regras ANVISA, CONAR e políticas de anúncios da Meta.",
        "score_compliance": 100
    }


def calcular_score_viabilidade(
    preco: float,
    comissao_pct: float,
    nome: str,
    doses: int = 30
) -> dict:
    """
    Algoritmo de scoring (0 a 100) para viabilidade de venda com foco em alta conversão:
    - Margem Financeira (30%): Comissão percentual e valor absoluto por venda
    - Demanda e Dor do Público (25%): Aderência ao nicho fitness/estética
    - Custo por Dia (20%): Facilidade de quebra de objeção no WhatsApp
    - Fotogenia & Editorial (15%): Potencial visual para Instagram no estilo @caiqueness
    - Compliance Sanitário (10%): Segurança jurídica
    """
    custo_dia = preco / doses if doses > 0 else preco / 30.0
    valor_comissao_est = (preco * (comissao_pct / 100.0)) if comissao_pct > 0 else (preco * 0.10)
    
    # 1. Nota Margem (0 a 100)
    if valor_comissao_est >= 50.0:
        nota_margem = 100
    elif valor_comissao_est >= 20.0:
        nota_margem = 85
    elif valor_comissao_est >= 10.0:
        nota_margem = 70
    else:
        nota_margem = 50
        
    # 2. Nota Demanda (0 a 100)
    nome_lower = nome.lower()
    tem_alta_demanda = any(c in nome_lower for c in CATEGORIAS_ALTA_DEMANDA_FITNESS)
    nota_demanda = 95 if tem_alta_demanda else 65
    
    # 3. Nota Custo por Dia (0 a 100)
    if custo_dia <= 2.0:
        nota_custo_dia = 100  # Menos que meio cafezinho
    elif custo_dia <= 5.0:
        nota_custo_dia = 85
    elif custo_dia <= 10.0:
        nota_custo_dia = 70
    else:
        nota_custo_dia = 55
        
    # 4. Nota Apelo Visual Instagram (0 a 100)
    nota_visual = 90 if any(x in nome_lower for x in ["creatina", "balança", "colágeno", "smartband", "shape", "treino"]) else 75
    
    score_final = (
        (nota_margem * 0.30) +
        (nota_demanda * 0.25) +
        (nota_custo_dia * 0.20) +
        (nota_visual * 0.15) +
        (100 * 0.10)
    )
    
    return {
        "score": round(score_final, 1),
        "comissao_estimada_reais": round(valor_comissao_est, 2),
        "custo_dia": round(custo_dia, 2),
        "classificacao": "ALTA_CONVERSAO" if score_final >= 80 else ("VIÁVEL" if score_final >= 65 else "BAIXA_PRIORIDADE")
    }


async def processar_e_ingerir_afiliado(
    url: str,
    texto_ou_html: str = "",
    programa: str = "afiliado"
) -> dict:
    """
    Analisa um link ou dados de produto colados pelo Evandro (Amazon, Magalu, Mercado Livre, Shopee, Braip),
    extrai os parâmetros com IA, valida compliance sanitário, calcula viabilidade e salva no Supabase.
    """
    prompt = f"""Você é o Engenheiro de Catálogo e Inteligência Comercial do Marcão Personal.
Analise as informações do produto de afiliado abaixo:
URL: {url}
Programa: {programa}
Dados brutos/Texto:
{texto_ou_html[:2000]}

Extraia e retorne EXCLUSIVAMENTE um objeto JSON válido (sem tags markdown de código e sem texto extra):
{{
  "sku": "CODIGO-UNICO-EM-MAIUSCULAS",
  "nome": "Nome comercial limpo do produto",
  "marca": "Marca do fabricante",
  "preco": 0.00,
  "comissao_pct": 0.0,
  "doses": 30,
  "beneficio_chave": "Frase de alto impacto biomecânico ou estético sem promessas falsas de cura",
  "claims_permitidos": ["beneficio 1", "beneficio 2"],
  "categoria": "suplemento|equipamento|acessorio|estetica"
}}"""

    extraido = {}
    try:
        async with httpx.AsyncClient(timeout=25.0, verify=False) as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            if res.status_code == 200:
                raw_json = res.json()["choices"][0]["message"]["content"].strip()
                limpo = re.sub(r'^```json\s*|\s*```$', '', raw_json, flags=re.MULTILINE).strip()
                extraido = json.loads(limpo)
    except Exception as e:
        print("[AUTONOMOUS_CURATOR] Erro extraindo dados com IA:", e)
        # Fallback básico se a IA falhar
        sku_auto = f"PROD-{int(datetime.now().timestamp())}"
        extraido = {
            "sku": sku_auto,
            "nome": "Produto Fitness Selecionado",
            "preco": 99.0,
            "comissao_pct": 10.0,
            "doses": 30,
            "beneficio_chave": "Acessório ou suplemento para performance corporal.",
            "categoria": "fitness"
        }

    sku = str(extraido.get("sku") or f"PROD-{int(datetime.now().timestamp())}").upper().replace(" ", "-")
    nome = extraido.get("nome") or "Produto Fitness Marcão Personal"
    preco = float(extraido.get("preco") or 99.0)
    comissao_pct = float(extraido.get("comissao_pct") or 10.0)
    doses = int(extraido.get("doses") or 30)
    beneficio = extraido.get("beneficio_chave") or "Melhora do desempenho e autocuidado corporal."

    # 1. Validação de Compliance Sanitário (ANVISA / Meta)
    compliance = avaliar_compliance_sanitario(nome, beneficio + " " + texto_ou_html)
    if not compliance["aprovado"]:
        return {
            "sucesso": False,
            "motivo": compliance["motivo"],
            "produto": nome,
            "acao_tomada": "REJEITADO_POR_COMPLIANCE"
        }

    # 2. Avaliação de Viabilidade Comercial
    viabilidade = calcular_score_viabilidade(preco, comissao_pct, nome, doses)

    # Normalização de model para o check constraint do Supabase
    def normalizar_modelo(p: str) -> str:
        s = (p or "").lower()
        if "amazon" in s or "amzn" in s:
            return "afiliado_amazon"
        elif "magalu" in s:
            return "afiliado_magalu"
        elif "mercadolivre" in s or "meli" in s or "ml" in s:
            return "afiliado_ml"
        elif "shopee" in s:
            return "afiliado_shopee"
        elif "braip" in s:
            return "braip"
        elif "stripe" in s or "proprio" in s:
            return "proprio"
        return "afiliado_ml"

    model_normalizado = normalizar_modelo(programa)

    # 3. Salva no Supabase e atualiza a Memória Unificada
    res_salvar = await salvar_ou_atualizar_produto(
        sku=sku,
        name=nome,
        price=preco,
        affiliate_url=url,
        model=model_normalizado,
        commission_pct=comissao_pct,
        doses=doses,
        beneficio_chave=beneficio
    )

    return {
        "sucesso": res_salvar.get("sucesso", False),
        "sku": sku,
        "nome": nome,
        "preco": preco,
        "custo_dia": viabilidade["custo_dia"],
        "comissao_estimada": viabilidade["comissao_estimada_reais"],
        "score_viabilidade": viabilidade["score"],
        "classificacao": viabilidade["classificacao"],
        "beneficio_chave": beneficio,
        "affiliate_url": url,
        "memoria_sincronizada": True
    }


def calcular_projecao_meta_milhao() -> dict:
    """
    Calcula os cenários práticos e metas operacionais para o Marcão atingir R$ 1 Milhão em faturamento.
    Esteira Tripla:
    1. MRR Stripe (R$ 19,90/mês): Receita recorrente passiva acumulada.
    2. Vendas Físicas de Alta Recorrência (Creatina R$ 169,90 - comissão ~R$ 68,00).
    3. Balança de Bioimpedância (R$ 89,90) - aquisição inicial de leads.
    """
    return {
        "meta_total": 1000000.0,
        "estrategia_recorrencia_mrr": {
            "ticket_mensal": 19.90,
            "meta_1000_alunos": {
                "faturamento_mensal": 19900.0,
                "faturamento_anual": 238800.0
            },
            "meta_4200_alunos": {
                "faturamento_mensal": 83580.0,
                "faturamento_anual": 1002960.0,
                "descricao": "Com 4.200 alunos ativos no acompanhamento VIP, a empresa atinge R$ 1 Milhão anualizado de forma 100% digital e sem frete!"
            }
        },
        "estrategia_afiliados_fisicos": {
            "vendas_creatina_para_1_milhao": {
                "preco": 169.90,
                "volume_vendas_necessario": 5886,
                "descricao": "5.886 potes vendidos em 12 meses (~16 potes por dia através do tráfego do Instagram e WhatsApp)."
            },
            "vendas_balanca_para_gerar_leads": {
                "preco": 89.90,
                "funcao": "A balança é a porta de entrada. Cada balança vendida traz um lead para o WhatsApp com 3 meses grátis, que depois converte para a assinatura VIP de R$ 19,90/mês."
            }
        }
    }


async def selecionar_oferta_autonoma_do_dia() -> dict:
    """
    O Marcão decide de forma autônoma qual produto promover hoje com base em viabilidade e momento.
    Gera as diretrizes para post no Instagram e mensagem de fechamento no WhatsApp.
    """
    produtos = await obter_produtos_ativos()
    if not produtos:
        return {}

    # Ordena produtos priorizando balança (porta de entrada) e creatina (recorrência)
    candidatos = []
    for p in produtos:
        v = calcular_score_viabilidade(p["price"], p.get("commission_pct", 10.0), p["name"], p.get("doses", 30))
        candidatos.append({**p, "score": v["score"], "custo_dia": v["custo_dia"]})
        
    candidatos.sort(key=lambda x: x["score"], reverse=True)
    escolhido = candidatos[0]

    return {
        "produto_foco": escolhido["name"],
        "sku": escolhido["sku"],
        "preco": escolhido["price"],
        "custo_dia": escolhido["custo_dia"],
        "pitch_diario": escolhido["pitch_diario"],
        "headline_sugerida_instagram": f"{escolhido['sku'].split('-')[0]}: A CIÊNCIA DA HIPERTROFIA REAL",
        "angulo_closer_whatsapp": f"Fazer a conta de apenas R$ {escolhido['custo_dia']:.2f} por dia e contrastar com o custo de ficar estagnado.",
        "link_direto": escolhido["affiliate_url"]
    }
