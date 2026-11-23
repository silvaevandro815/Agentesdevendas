"""
=============================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
MOTOR UNIFICADO DO CARRO-CHEFE Nº 1: KIT RESET 5 DIAS (PARCERIA KAMILA VITÓRIA)
=============================================================================
Centraliza toda a inteligência comercial, memória de 40 dias, ativação de alunos,
transição para assinatura Stripe R$ 19,90/mês, follow-up semanal e geração/publicação
diária de posts do Kit Reset 5 Dias no Instagram (Feed 4:5 + Story 9:16).
=============================================================================
"""

import os
import re
import json
import time
import asyncio
import httpx
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image, ImageDraw, ImageFont, ImageOps
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_BASE_DIR, "..", ".."))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "sofia")

FUSO_BR = timezone(timedelta(hours=-3))

KAMILA_NOME = "Kamila Vitória"
KAMILA_TELEFONE_E164 = "5532999120912"
KAMILA_TELEFONE_FMT = "(32) 99912-0912"
KAMILA_WHATSAPP_LINK = (
    "https://wa.me/5532999120912?text=Ol%C3%A1%20Kamila!%20Vim%20por%20indica%C3%A7%C3%A3o%20"
    "do%20Treinador%20Marc%C3%A3o%20e%20quero%20garantir%20meu%20Kit%20Reset%205%20Dias!"
)
SITE_RESET_URL = "https://marcaopersonal.com/#reset"
STRIPE_VIP_LINK = "https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01"
RESET_CONSULTORIA_DIAS = 40
RESET_CICLO_RECOMPRA_DIAS = 40

RESET_DIR = Path(PROJECT_ROOT) / "kamila.RESET"
RESET_JSON_PATH = RESET_DIR / "BASE_CONHECIMENTO_RESET.json"
RESET_IMAGENS_DIR = RESET_DIR / "imagens"
SITE_RESET_IMAGENS_DIR = Path(PROJECT_ROOT) / "apps" / "site" / "public" / "images" / "reset"
FONTS_DIR = Path(PROJECT_ROOT) / "assets" / "fonts"


def _sb_headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def carregar_base_reset() -> dict:
    """Carrega a base estruturada JSON do Reset 5 Dias."""
    if RESET_JSON_PATH.exists():
        try:
            return json.loads(RESET_JSON_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[RESET_ENGINE] Erro lendo BASE_CONHECIMENTO_RESET.json: {e}")
    return {}


def obter_prompt_conhecimento_reset(eh_aluno: bool = False, metas_aluno: Optional[dict] = None) -> str:
    """
    Retorna o bloco de conhecimento profundo e instruções comerciais do Carro-Chefe Nº 1 (Kit Reset 5 Dias)
    para injeção unificada no WhatsApp, Instagram Direct e Comentários do Instagram.
    """
    metas = metas_aluno or {}
    reset_status = str(metas.get("reset_status") or "")
    proxima_oferta = str(metas.get("reset_proxima_oferta_em") or "")
    hoje_str = datetime.now(FUSO_BR).strftime("%Y-%m-%d")

    em_cooldown_40d = bool(
        reset_status in ("ja_tomou", "ativo_40d")
        and proxima_oferta
        and hoje_str < proxima_oferta
    )

    nota_status_aluno = ""
    if em_cooldown_40d:
        nota_status_aluno = (
            f"- STATUS DESTE ALUNO COM O RESET: Já conhece e já tomou! Cooldown ativo até {proxima_oferta}. "
            f"NÃO fique oferecendo compra de novo kit antes de {proxima_oferta} (a menos que o próprio aluno peça!).\n"
        )
    elif reset_status in ("ja_tomou", "ativo_40d") and proxima_oferta and hoje_str >= proxima_oferta:
        nota_status_aluno = (
            f"- STATUS DESTE ALUNO COM O RESET: Já se passaram mais de 40 dias desde o último ciclo ({proxima_oferta})! "
            f"É o momento ideal para lembrar com entusiasmo de fazer um novo ciclo do Kit Reset 5 Dias para manter o desinchaço e os resultados!\n"
        )

    return f"""
===============================================================================
CARRO-CHEFE Nº 1 DO MARCÃO PERSONAL: KIT RESET 5 DIAS (PARCERIA KAMILA VITÓRIA)
===============================================================================
{nota_status_aluno}- O QUE É O RESET 5 DIAS (EDUQUE SEMPRE — LEADS E ALUNOS COMUNS NÃO SABEM O QUE É!):
  * É um protocolo prático de 5 garrafinhas prontas de 500ml de chá funcional 100% natural, sem conservantes e sem açúcar adicionado, com sabor refrescante de frutas e blend de ervas selecionadas (1 garrafa por dia durante 5 dias).
  * Base nutricional consolidada há mais de 40 anos no mercado mundial (presente em mais de 90 países, incluindo EUA), validada por médicos, cientistas e nutricionistas.
- OS DOIS KITS OFICIAIS E SEUS COMPOSTOS:
  1) RESET TRADICIONAL — R$ 45,00 (apenas R$ 9,00/dia! 5 garrafinhas de 500ml):
     * Composição: Blend 100% natural de Cavalinha (drenagem potente contra retenção), Hibisco (diurético e antioxidante contra gordura visceral), Chá Preto/Verde + Cafeína Natural (termogênese, foco e energia limpa), Malva (acalma estômago e reduz gases) e Cardamomo (digestivo termogênico).
     * Benefícios: Desincha a barriga, elimina retenção de líquido, dá vitalidade, disposição, leveza e inicia a desinflamação em 5 dias.
  2) RESET TURBO — R$ 75,00 (apenas R$ 15,00/dia! 5 garrafinhas de 500ml — O MAIS COMPLETO E RECOMENDADO!):
     * Composição: TODO o blend de ervas do Tradicional + Fibra Solúvel Prebiótica Concentrada!
     * Benefícios Extras: Alimenta as bactérias boas do intestino (efeito prebiótico), destrava e regula o trânsito intestinal, dá altíssima saciedade, corta a vontade de doce e compulsão de beliscar besteiras, e potencializa a redução de medidas e gordura abdominal!
- COMO TOMAR & DICA DO TREINADOR MARCÃO:
  * 1 garrafinha gelada (500ml) por dia, durante 5 dias, bebida aos poucos pela manhã ou início da tarde (evitar após 18h por causa da cafeína natural).
  * Obrigatório manter boa ingestão de água pura ao longo do dia para potencializar a drenagem e a ação das fibras!
  * Responsabilidade: Fórmula 100% natural sem conservantes e sem açúcar; gestantes, lactantes, crianças ou hipertensos sensíveis à cafeína devem validar com seu médico.
- BÔNUS IRRESISTÍVEL DO CARRO-CHEFE (SUBSTITUI A REGRA ANTIGA DA BALANÇA):
  * Quem compra o Kit Reset 5 Dias (Tradicional R$ 45 ou Turbo R$ 75) ganha **40 DIAS DE CONSULTORIA VIP GRATUITA COM O TREINADOR MARCÃO** (treino sob medida, análise de pratos por foto no WhatsApp, metas calculadas, portal individual e cobrança diária)!
  * Como ativa: A Kamila envia o nome e WhatsApp do comprador para o Marcão recepcionar e liberar na hora os 40 dias de Consultoria VIP!
  * Após os 40 dias: O aluno pode continuar o acompanhamento VIP pela assinatura de apenas **R$ 19,90/mês no Stripe (sem multa de cancelamento)**!
- FLUXO OBRIGATÓRIO QUANDO O LEAD/ALUNO DEMONSTRAR INTERESSE OU PERGUNTAR SOBRE O RESET:
  1. Explique com entusiasmo e clareza o que é o Reset, recomendando o Turbo (R$ 75) para quem quer secar barriga, travar doce e regular intestino, ou Tradicional (R$ 45) para começar a desinflamar — sempre quebrando em custo por dia (R$ 9/dia ou R$ 15/dia) + os 40 DIAS DE CONSULTORIA VIP COM O MARCÃO!
  2. Envie o link do nosso site com todos os detalhes do produto: {SITE_RESET_URL}
  3. Envie IMEDIATAMENTE o contato WhatsApp personalizado da nossa parceira Kamila Vitória (quem faz a venda final e entrega do Kit):
     WhatsApp da Kamila: {KAMILA_TELEFONE_FMT} | Link direto: {KAMILA_WHATSAPP_LINK}
  4. PEDIDO DE OURO OBRIGATÓRIO: Peça com carinho e entusiasmo para a pessoa **dizer à Kamila que foi indicação do Treinador Marcão**! Diga que o Marcão fica muito feliz quando ela sabe que veio por indicação dele, e que assim a Kamila já passa o contato para o Marcão liberar os **40 dias de Consultoria VIP**!
- SE O ALUNO DISSER QUE JÁ CONHECE E JÁ TOMOU O RESET:
  * Parabenize e elogie a escolha (o sistema grava automaticamente na memória e pausa novas ofertas por 40 dias, voltando a oferecer apenas após 40 dias para renovação do ciclo!).
- OUTROS PRODUTOS (BALANÇA SHOPEE R$ 34,90, CREATINA, COLÁGENO, WHEY, VITAMINAS E ACESSÓRIOS SHOPEE):
  * Continuam 100% disponíveis no nosso catálogo e suporte sempre que surgir queixa ou necessidade específica do aluno, com nossos links oficiais de comissão!
"""


def detectar_ja_tomou_reset(texto: str, contexto_recente: str = "") -> bool:
    """
    Detecta se o aluno afirmou que já conhece e já tomou / toma o Kit Reset 5 Dias.
    """
    t = (texto or "").lower()
    ctx = (contexto_recente or "").lower()
    menciona_reset = ("reset" in t) or ("reset" in ctx)
    if not menciona_reset:
        return False

    sinais_ja_tomou = [
        "ja tomei", "já tomei", "ja tomo", "já tomo",
        "estou tomando", "to tomando", "tô tomando",
        "ja usei", "já usei", "ja comprei", "já comprei",
        "ja fiz o reset", "já fiz o reset", "conheco e ja tomei",
        "conheço e já tomei", "sim ja tomei", "sim, já tomei",
        "ja conheco e tomo", "já conheço e tomo",
    ]
    return any(s in t for s in sinais_ja_tomou)


async def registrar_aluno_ja_tomou_reset(telefone: str, origem: str = "conversa_whatsapp") -> dict:
    """
    Grava na memória permanente do aluno (Supabase `fichas_alunos.metas_nutricionais`)
    que ele já tomou o Reset 5 Dias, travando novas ofertas por 40 dias.
    """
    tel_limpo = "".join(filter(str.isdigit, str(telefone or "")))
    last8 = tel_limpo[-8:] if len(tel_limpo) >= 8 else tel_limpo
    if not last8:
        return {"sucesso": False, "erro": "Telefone inválido"}

    agora = datetime.now(FUSO_BR)
    hoje_str = agora.strftime("%Y-%m-%d")
    proxima_oferta_str = (agora + timedelta(days=RESET_CICLO_RECOMPRA_DIAS)).strftime("%Y-%m-%d")
    headers = _sb_headers()

    try:
        async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
            q = f"{SUPABASE_URL}/rest/v1/fichas_alunos?or=(telefone.ilike.*{last8}*,remote_jid.ilike.*{last8}*)&select=id,nome,metas_nutricionais"
            r = await client.get(q, headers=headers)
            if r.status_code != 200 or not r.json():
                return {"sucesso": False, "erro": "Aluno não localizado"}

            row = r.json()[0]
            metas = row.get("metas_nutricionais") or {}
            if not isinstance(metas, dict):
                metas = {}

            metas["reset_status"] = "ja_tomou"
            metas["reset_ultimo_uso_data"] = hoje_str
            metas["reset_proxima_oferta_em"] = proxima_oferta_str
            metas["reset_registro_origem"] = origem

            p = await client.patch(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.{row['id']}",
                headers=headers,
                json={"metas_nutricionais": metas},
            )
            if p.status_code in (200, 204):
                print(f"[RESET_ENGINE] Memória gravada: {row.get('nome')} já tomou Reset. Próxima oferta somente em {proxima_oferta_str} (+40d).")
                return {
                    "sucesso": True,
                    "aluno": row.get("nome"),
                    "reset_status": "ja_tomou",
                    "proxima_oferta_em": proxima_oferta_str,
                }
    except Exception as e:
        print(f"[RESET_ENGINE] Erro registrando reset_status: {e}")
    return {"sucesso": False}


async def _enviar_baloes_whatsapp(telefone: str, baloes: List[str]) -> bool:
    """Envia múltiplos balões curtos no WhatsApp com presença 'composing' (Regra 5)."""
    tel_limpo = "".join(filter(str.isdigit, str(telefone or "")))
    if not tel_limpo:
        return False
    headers = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            for idx, texto in enumerate(baloes):
                if not texto.strip():
                    continue
                try:
                    await client.post(
                        f"{EVOLUTION_API_URL}/chat/sendPresence/{EVOLUTION_INSTANCE}",
                        headers=headers,
                        json={"number": tel_limpo, "delay": 1500, "presence": "composing"},
                    )
                except Exception:
                    pass
                await asyncio.sleep(1.4 if idx == 0 else 1.8)
                await client.post(
                    f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}",
                    headers=headers,
                    json={"number": tel_limpo, "text": texto.strip()},
                )
        return True
    except Exception as e:
        print(f"[RESET_ENGINE] Erro enviando WhatsApp para {tel_limpo}: {e}")
        return False


async def ativar_consultoria_40_dias_reset(
    nome: str,
    telefone: str,
    kit_tipo: str = "Reset Turbo",
    enviar_boas_vindas: bool = True,
) -> dict:
    """
    Ativa imediatamente os 40 DIAS DE CONSULTORIA VIP GRATUITA para um novo aluno
    que comprou o Kit Reset 5 Dias com a Kamila Vitória.
    Cria/atualiza `fichas_alunos` e `clientes_balanca` (controle VIP),
    e envia a recepção personalizada do Treinador Marcão no WhatsApp!
    """
    tel_limpo = "".join(filter(str.isdigit, str(telefone or "")))
    if not tel_limpo:
        return {"sucesso": False, "erro": "Telefone obrigatório"}
    if not tel_limpo.startswith("55") and len(tel_limpo) in (10, 11):
        tel_limpo = "55" + tel_limpo
    last8 = tel_limpo[-8:]
    remote_jid = f"{tel_limpo}@s.whatsapp.net"

    agora = datetime.now(FUSO_BR)
    hoje_str = agora.strftime("%Y-%m-%d")
    expiracao_dt = agora + timedelta(days=RESET_CONSULTORIA_DIAS)
    expiracao_str = expiracao_dt.strftime("%Y-%m-%d")
    headers = _sb_headers()

    async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
        # 1. Atualiza ou cria ficha em `fichas_alunos`
        q = f"{SUPABASE_URL}/rest/v1/fichas_alunos?or=(telefone.ilike.*{last8}*,remote_jid.ilike.*{last8}*)&select=*"
        r = await client.get(q, headers=headers)
        if r.status_code == 200 and r.json():
            row = r.json()[0]
            metas = row.get("metas_nutricionais") or {}
            if not isinstance(metas, dict):
                metas = {}
            metas.update({
                "origem_vip": "kit_reset_kamila",
                "reset_status": "ativo_40d",
                "reset_kit_comprado": kit_tipo,
                "reset_ultimo_uso_data": hoje_str,
                "reset_consultoria_inicio": hoje_str,
                "reset_consultoria_fim": expiracao_str,
                "reset_proxima_oferta_em": expiracao_str,
                "stripe_oferta_enviada": False,
            })
            compras = metas.get("produtos_comprados") or []
            if not isinstance(compras, list):
                compras = []
            compras.append({"produto": f"Kit {kit_tipo} (5 Dias)", "origem": "Kamila Reset", "data": hoje_str})
            metas["produtos_comprados"] = compras

            await client.patch(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.{row['id']}",
                headers=headers,
                json={"status_acompanhamento": "ativo", "metas_nutricionais": metas},
            )
        else:
            nova_ficha = {
                "nome": nome.strip(),
                "telefone": tel_limpo,
                "remote_jid": remote_jid,
                "status_acompanhamento": "ativo",
                "objetivo": "Desinchar, secar gordura abdominal e definir",
                "local_treino": "academia",
                "metas_nutricionais": {
                    "origem_vip": "kit_reset_kamila",
                    "reset_status": "ativo_40d",
                    "reset_kit_comprado": kit_tipo,
                    "reset_ultimo_uso_data": hoje_str,
                    "reset_consultoria_inicio": hoje_str,
                    "reset_consultoria_fim": expiracao_str,
                    "reset_proxima_oferta_em": expiracao_str,
                    "stripe_oferta_enviada": False,
                    "produtos_comprados": [
                        {"produto": f"Kit {kit_tipo} (5 Dias)", "origem": "Kamila Reset", "data": hoje_str}
                    ],
                },
            }
            await client.post(f"{SUPABASE_URL}/rest/v1/fichas_alunos", headers=headers, json=nova_ficha)

        # 2. Registra/atualiza em `clientes_balanca` (tabela de controle VIP unificado)
        q_vip = f"{SUPABASE_URL}/rest/v1/clientes_balanca?or=(telefone.ilike.*{last8}*,remote_jid.ilike.*{last8}*)&select=id"
        r_vip = await client.get(q_vip, headers=headers)
        vip_payload = {
            "remote_jid": remote_jid,
            "telefone": tel_limpo,
            "nome_cliente": nome.strip(),
            "data_compra": agora.isoformat(),
            "data_expiracao_vip": expiracao_dt.isoformat(),
            "status_vip": "ativo_reset_40d",
        }
        if r_vip.status_code == 200 and r_vip.json():
            vip_id = r_vip.json()[0]["id"]
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/clientes_balanca?id=eq.{vip_id}",
                headers=headers,
                json=vip_payload,
            )
        else:
            await client.post(f"{SUPABASE_URL}/rest/v1/clientes_balanca", headers=headers, json=vip_payload)

    # 3. Recepção calorosa do Marcão no WhatsApp (3 balões curtos)
    primeiro_nome = nome.strip().split()[0] if nome else "campeão(ã)"
    link_portal = f"https://marcaopersonal.com/aluno?id={tel_limpo}"
    enviado = False
    if enviar_boas_vindas:
        baloes = [
            f"Fala, {primeiro_nome}! 🦁🔥 Aqui é o Treinador Marcão! A Kamila acabou de me avisar que você garantiu seu Kit Reset 5 Dias!",
            f"Seja super bem-vindo(a)! Seus 40 DIAS DE CONSULTORIA VIP comigo estão 100% liberados até {expiracao_dt.strftime('%d/%m/%Y')}! 💪",
            f"Me conta aqui agora: qual é seu peso atual, sua altura e se você treina em casa ou na academia? Já vou montar sua ficha no seu portal: {link_portal}",
        ]
        enviado = await _enviar_baloes_whatsapp(tel_limpo, baloes)

    return {
        "sucesso": True,
        "aluno": nome.strip(),
        "telefone": tel_limpo,
        "kit": kit_tipo,
        "dias_vip": RESET_CONSULTORIA_DIAS,
        "expira_em": expiracao_str,
        "portal_url": link_portal,
        "boas_vindas_enviadas": enviado,
    }


async def executar_followup_semanal_reset(forcar: bool = False) -> dict:
    """
    Follow-up Semanal Automático sobre o Kit Reset 5 Dias:
    - Pergunta a todos os alunos ativos se eles já conhecem o Reset 5 Dias.
    - Se o aluno já conhece e já tomou: pula durante 40 dias!
    - Após 40 dias: volta a oferecer um novo Kit Reset para continuar o tratamento!
    - Nunca envia para Evandro (diretor) nem para a própria Kamila (vendedora parceira).
    """
    agora = datetime.now(FUSO_BR)
    hoje_str = agora.strftime("%Y-%m-%d")
    headers = _sb_headers()

    relatorio = {"data": hoje_str, "perguntados": [], "recompras_40d": [], "pulados_cooldown": []}

    async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=*", headers=headers)
        alunos = r.json() if r.status_code == 200 else []

        for a in alunos:
            tel = "".join(filter(str.isdigit, str(a.get("telefone") or "")))
            nome = (a.get("nome") or "Guerreiro(a)").strip()
            primeiro_nome = nome.split()[0]

            # Nunca dispara para Diretor Evandro nem para Kamila (parceira)
            if not tel or "84587255" in tel or "99120912" in tel:
                continue

            metas = a.get("metas_nutricionais") or {}
            if not isinstance(metas, dict):
                metas = {}

            # Se estiver em Modo Cuidado (doente/gripado), respeita o repouso
            if metas.get("modo_cuidado"):
                continue

            reset_status = str(metas.get("reset_status") or "")
            proxima_oferta = str(metas.get("reset_proxima_oferta_em") or "")
            ultimo_fup = str(metas.get("reset_ultimo_followup_semanal") or "")

            # Trava semanal: não enviar 2x em menos de 6 dias
            if not forcar and ultimo_fup:
                try:
                    dt_ult = datetime.strptime(ultimo_fup[:10], "%Y-%m-%d").replace(tzinfo=FUSO_BR)
                    if (agora - dt_ult).days < 6:
                        continue
                except Exception:
                    pass

            # Regra dos 40 dias: se já tomou e ainda não venceram os 40 dias -> PULAR!
            if reset_status in ("ja_tomou", "ativo_40d") and proxima_oferta and hoje_str < proxima_oferta:
                relatorio["pulados_cooldown"].append({"aluno": nome, "liberado_em": proxima_oferta})
                continue

            # Caso A: Já tomou antes e JÁ PASSARAM OS 40 DIAS -> Oferta de continuidade/recompra!
            if reset_status in ("ja_tomou", "ativo_40d") and proxima_oferta and hoje_str >= proxima_oferta:
                baloes = [
                    f"Fala, {primeiro_nome}! 🦁 Tudo bem? Já fecharam 40 dias desde o seu último Kit Reset 5 Dias!",
                    "Esse é o momento perfeito pra fazer um novo ciclo do Reset, manter o corpo desinflamado, o intestino regulado e acelerar ainda mais seus resultados! 🔥",
                    f"Confere os detalhes aqui ({SITE_RESET_URL}) e chama a Kamila no WhatsApp ({KAMILA_WHATSAPP_LINK}) dizendo que foi indicação do Marcão! Fico muito feliz quando você avisa ela! 👊💪",
                ]
                ok = await _enviar_baloes_whatsapp(tel, baloes)
                if ok:
                    metas["reset_ultimo_followup_semanal"] = hoje_str
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.{a['id']}",
                        headers=headers,
                        json={"metas_nutricionais": metas},
                    )
                    relatorio["recompras_40d"].append(nome)
            else:
                # Caso B: Ainda não sabemos se conhece o Reset -> Pergunta semanal de abertura!
                baloes = [
                    f"Fala, {primeiro_nome}! 🦁 Tudo certo no foco hoje? Me tira uma dúvida rápida aqui:",
                    "Você já conhece o Kit Reset 5 Dias? São umas garrafinhas de chá natural com ervas e sabor de frutas que ajudam demais a desinchar a barriga, secar retenção e controlar a vontade de doce! 💧🔥",
                    "Me conta aqui se você já conhece ou já tomou alguma vez! 👇",
                ]
                ok = await _enviar_baloes_whatsapp(tel, baloes)
                if ok:
                    metas["reset_ultimo_followup_semanal"] = hoje_str
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.{a['id']}",
                        headers=headers,
                        json={"metas_nutricionais": metas},
                    )
                    relatorio["perguntados"].append(nome)

    return relatorio


async def verificar_transicao_stripe_40_dias() -> dict:
    """
    Audita diariamente alunos que entraram via Kit Reset 5 Dias (40 dias de consultoria gratuita).
    Quando os 40 dias terminam, oferece a continuidade da consultoria VIP pelo Stripe R$ 19,90/mês
    (sem multa de cancelamento) + opção de renovar o Kit Reset com a Kamila!
    """
    agora = datetime.now(FUSO_BR)
    hoje_str = agora.strftime("%Y-%m-%d")
    headers = _sb_headers()
    ofertas_enviadas = []

    async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=*", headers=headers)
        alunos = r.json() if r.status_code == 200 else []

        for a in alunos:
            metas = a.get("metas_nutricionais") or {}
            if not isinstance(metas, dict):
                continue
            if metas.get("origem_vip") != "kit_reset_kamila":
                continue
            if metas.get("stripe_oferta_enviada"):
                continue

            fim_vip = str(metas.get("reset_consultoria_fim") or "")
            if not fim_vip or hoje_str < fim_vip:
                continue

            tel = "".join(filter(str.isdigit, str(a.get("telefone") or "")))
            nome = (a.get("nome") or "Guerreiro(a)").strip()
            primeiro_nome = nome.split()[0]

            baloes = [
                f"Fala, {primeiro_nome}! 🦁🔥 Parabéns demais pelos seus 40 dias de Consultoria VIP comigo após o Kit Reset!",
                "Pra gente não perder esse ritmo e continuar evoluindo seus treinos, sua dieta e suas fotos todo mês, você pode continuar no meu Acompanhamento VIP por apenas R$ 19,90/mês (menos de R$ 0,66 por dia e SEM multa de cancelamento)!",
                f"É só ativar sua assinatura oficial aqui no Stripe pra continuar comigo no WhatsApp: {STRIPE_VIP_LINK} 💪👊",
            ]
            ok = await _enviar_baloes_whatsapp(tel, baloes)
            if ok:
                metas["stripe_oferta_enviada"] = True
                metas["stripe_oferta_data"] = hoje_str
                await client.patch(
                    f"{SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.{a['id']}",
                    headers=headers,
                    json={"metas_nutricionais": metas},
                )
                ofertas_enviadas.append(nome)

    return {"data": hoje_str, "ofertas_stripe_enviadas": ofertas_enviadas}


def _carregar_fonte(nome_ttf: str, tamanho: int):
    for candidato in [
        FONTS_DIR / nome_ttf,
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]:
        if candidato.exists():
            try:
                return ImageFont.truetype(str(candidato), tamanho)
            except Exception:
                pass
    return ImageFont.load_default()


def _quebrar_texto(draw: ImageDraw.ImageDraw, texto: str, fonte, max_w: int) -> List[str]:
    palavras = texto.split()
    linhas = []
    atual = ""
    for p in palavras:
        teste = f"{atual} {p}".strip()
        bbox = draw.textbbox((0, 0), teste, font=fonte)
        if bbox[2] - bbox[0] <= max_w:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def gerar_card_diario_reset(dia_indice: Optional[int] = None) -> dict:
    """
    Gera o card diário exclusivo do Kit Reset 5 Dias (1080x1350 Feed 4:5)
    utilizando as imagens reais das garrafinhas da pasta `kamila.RESET/imagens/`
    e rotacionando diariamente o ângulo persuasivo para nunca repetir posts!
    """
    base = carregar_base_reset()
    angulos = base.get("angulos_posts_diarios") or []
    if not angulos:
        return {"sucesso": False, "erro": "Sem ângulos configurados em BASE_CONHECIMENTO_RESET.json"}

    agora = datetime.now(FUSO_BR)
    idx = dia_indice if dia_indice is not None else agora.timetuple().tm_yday
    angulo = angulos[idx % len(angulos)]

    # Lista imagens reais válidas (prioriza pasta kamila.RESET/imagens e fallback apps/site/public/images/reset)
    imgs_disponiveis = []
    for pasta in [RESET_IMAGENS_DIR, SITE_RESET_IMAGENS_DIR]:
        if pasta.exists():
            achadas = sorted([
                p for p in pasta.glob("*.jpg")
                if p.name in (
                    "reset_oficial_kits_comparativo.jpg",
                    "reset_real_07.jpg",
                    "reset_real_08.jpg",
                    "reset_real_01.jpg",
                    "reset_real_05.jpg",
                    "reset_real_06.jpg",
                    "reset_real_03.jpg",
                )
            ])
            if achadas:
                imgs_disponiveis = achadas
                break

    if not imgs_disponiveis:
        return {"sucesso": False, "erro": "Nenhuma imagem do Kit Reset encontrada"}

    foto_escolhida = imgs_disponiveis[idx % len(imgs_disponiveis)]

    # Se a foto sorteada já é a arte oficial comparativa dos kits (com preços e textos),
    # fazemos enquadramento limpo 4:5 com cabeçalho/rodapé CTA do Marcão;
    # nas demais fotos reais de garrafinhas, montamos o layout editorial 4:5 de alto impacto!
    W, H = 1080, 1350
    card = Image.new("RGBA", (W, H), (10, 14, 18, 255))
    draw = ImageDraw.Draw(card)

    f_tag = _carregar_fonte("Montserrat-Bold.ttf", 22)
    f_h1 = _carregar_fonte("Montserrat-Black.ttf", 54)
    f_sub = _carregar_fonte("Montserrat-Bold.ttf", 26)
    f_bullet = _carregar_fonte("Montserrat-Bold.ttf", 24)
    f_dest_num = _carregar_fonte("Montserrat-Black.ttf", 46)
    f_dest_sub = _carregar_fonte("Montserrat-Bold.ttf", 22)
    f_cta = _carregar_fonte("Montserrat-Black.ttf", 25)
    f_footer = _carregar_fonte("Montserrat-Bold.ttf", 20)

    if foto_escolhida.name == "reset_oficial_kits_comparativo.jpg":
        # Enquadramento nobre preservando 100% da arte oficial + barra CTA do Marcão no rodapé
        im_art = Image.open(foto_escolhida).convert("RGBA")
        # Cabeçalho escuro + arte central + CTA inferior
        target_h = 1130
        ratio = target_h / im_art.height
        new_w = min(W, int(im_art.width * ratio))
        im_resized = im_art.resize((new_w, target_h), Image.Resampling.LANCZOS)
        # Fundo desfocado / escuro suave
        bg_fill = ImageOps.fit(im_art, (W, H), method=Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", (W, H), (8, 12, 16, 215))
        card = Image.alpha_composite(bg_fill, overlay)
        card.paste(im_resized, ((W - new_w) // 2, 70), im_resized)
        draw = ImageDraw.Draw(card)

        # Topo
        draw.rounded_rectangle([140, 14, 940, 58], radius=22, fill=(16, 185, 129, 240))
        top_txt = "TREINADOR MARCÃO  •  CARRO-CHEFE + 40 DIAS VIP GRÁTIS"
        tb = draw.textbbox((0, 0), top_txt, font=f_footer)
        draw.text(((W - (tb[2] - tb[0])) // 2, 24), top_txt, fill=(6, 13, 24), font=f_footer)

        # Rodapé CTA
        draw.rounded_rectangle([40, 1215, 1040, 1322], radius=24, fill=(249, 115, 22, 255), outline=(254, 215, 170), width=3)
        cta1 = "MANDE 'RESET' NO DIRECT OU WHATSAPP DO MARCÃO!"
        cta2 = "Garanta seu Kit + 40 DIAS de Consultoria VIP Grátis!"
        b1 = draw.textbbox((0, 0), cta1, font=f_cta)
        b2 = draw.textbbox((0, 0), cta2, font=f_footer)
        draw.text(((W - (b1[2] - b1[0])) // 2, 1233), cta1, fill=(10, 14, 20), font=f_cta)
        draw.text(((W - (b2[2] - b2[0])) // 2, 1276), cta2, fill=(255, 255, 255), font=f_footer)
    else:
        # Layout Editorial Split Superior (Foto Real) + Inferior Dark Glassmorphism
        im_foto = Image.open(foto_escolhida).convert("RGBA")
        foto_h = 620
        im_top = ImageOps.fit(im_foto, (W, foto_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.22))
        card.paste(im_top, (0, 0))

        # Gradiente alfa real de transição suave entre foto e fundo escuro
        grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(grad)
        for y in range(470, foto_h):
            alpha = int(((y - 470) / (foto_h - 470)) * 255)
            gdraw.line([(0, y), (W, y)], fill=(10, 14, 18, alpha))
        card = Image.alpha_composite(card, grad)
        draw = ImageDraw.Draw(card)

        # Badge superior
        draw.rounded_rectangle([190, 22, 890, 68], radius=23, fill=(10, 15, 22, 235), outline=(16, 185, 129, 255), width=2)
        tag_txt = "TREINADOR MARCÃO  •  KIT RESET 5 DIAS"
        tb = draw.textbbox((0, 0), tag_txt, font=f_tag)
        draw.text(((W - (tb[2] - tb[0])) // 2, 33), tag_txt, fill=(52, 211, 153), font=f_tag)

        # Painel de conteúdo inferior (y: 575 até 1320)
        draw.rounded_rectangle([40, 575, 1040, 1320], radius=30, fill=(14, 21, 31, 255), outline=(249, 115, 22, 230), width=3)

        # Headline
        y_cursor = 602
        for linha in _quebrar_texto(draw, angulo["headline"], f_h1, 920)[:2]:
            draw.text((80, y_cursor), linha, fill=(255, 255, 255), font=f_h1)
            y_cursor += 60

        # Subheadline
        y_cursor += 6
        for linha in _quebrar_texto(draw, angulo["subheadline"], f_sub, 920)[:2]:
            draw.text((80, y_cursor), linha, fill=(251, 146, 60), font=f_sub)
            y_cursor += 34

        # Linha divisória
        y_cursor += 8
        draw.line([(80, y_cursor), (1000, y_cursor)], fill=(249, 115, 22, 180), width=2)
        y_cursor += 20

        # 3 Bullets com barra verde esmeralda
        for b_txt in angulo.get("bullets", [])[:3]:
            draw.rounded_rectangle([80, y_cursor + 4, 90, y_cursor + 50], radius=4, fill=(16, 185, 129, 255))
            linhas_b = _quebrar_texto(draw, b_txt, f_bullet, 880)[:2]
            ly = y_cursor
            for lb in linhas_b:
                draw.text((108, ly), lb, fill=(241, 245, 249), font=f_bullet)
                ly += 30
            y_cursor += max(62, len(linhas_b) * 30 + 12)

        # Caixa de Destaque de Alto Contraste (Verde Escuro Profundo + Número Neon + Subtítulo Branco)
        y_dest = max(y_cursor + 8, 1020)
        draw.rounded_rectangle([80, y_dest, 1000, y_dest + 104], radius=18, fill=(8, 42, 34, 255), outline=(16, 185, 129, 255), width=3)
        draw.text((110, y_dest + 12), angulo["destaque_numero"], fill=(52, 211, 153), font=f_dest_num)
        draw.text((110, y_dest + 68), angulo["destaque_sub"], fill=(255, 255, 255), font=f_dest_sub)

        # Botão CTA Final (Direct ou WhatsApp do Marcão)
        y_cta = 1155
        draw.rounded_rectangle([80, y_cta, 1000, y_cta + 125], radius=22, fill=(249, 115, 22, 255))
        cta_top = "CHAME O MARCÃO NO DIRECT OU WHATSAPP!"
        cta_bot = "Mande 'RESET' e garanta seu Kit + 40 DIAS VIP Grátis!"
        ct1 = draw.textbbox((0, 0), cta_top, font=f_cta)
        ct2 = draw.textbbox((0, 0), cta_bot, font=f_footer)
        draw.text(((W - (ct1[2] - ct1[0])) // 2, y_cta + 24), cta_top, fill=(10, 14, 20), font=f_cta)
        draw.text(((W - (ct2[2] - ct2[0])) // 2, y_cta + 72), cta_bot, fill=(255, 255, 255), font=f_footer)

    out_dir = Path(PROJECT_ROOT) / "scratch"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"reset_post_diario_{agora.strftime('%Y%m%d')}_{angulo['id']}.png"
    card.convert("RGB").save(out_path, quality=96)

    # Legenda persuasiva calibrada (Regra 12: gancho nos primeiros 125 caracteres + 4 hashtags)
    legenda = (
        f"{angulo['headline']} 💧🔥\n\n"
        f"{angulo['subheadline']}.\n\n"
        f"A maioria das pessoas começa a dieta e trava na primeira semana por causa de inchaço, intestino lento e vontade de doce.\n\n"
        f"O Kit Reset 5 Dias resolve isso com 5 garrafinhas prontas 100% naturais e sem conservantes:\n"
        f"🌿 Reset Tradicional (R$ 45): Cavalinha, Hibisco, Chá Preto, Malva e Cardamomo para drenar líquido e dar energia.\n"
        f"🔥 Reset Turbo (R$ 75): Todo o blend de ervas + Fibras Prebióticas que destravam o intestino e cortam a compulsão por doces!\n\n"
        f"🦁 BÔNUS EXCLUSIVO: Garantindo seu Kit Reset você ganha 40 DIAS DE CONSULTORIA VIP comigo no WhatsApp (treino, dieta e avaliação de pratos)!\n\n"
        f"👇 Quer garantir o seu? Mande 'RESET' agora aqui no Direct ou no WhatsApp do Marcão (ou clique no link da Bio)!\n\n"
        f"#reset5dias #desinchar #emagrecimentosaudavel #treinadormarcao"
    )

    return {
        "sucesso": True,
        "angulo_id": angulo["id"],
        "headline": angulo["headline"],
        "imagem_origem": str(foto_escolhida),
        "card_path": str(out_path),
        "legenda": legenda,
    }


async def gerar_e_publicar_post_diario_reset(dia_indice: Optional[int] = None) -> dict:
    """
    Gera o card único do dia do Kit Reset 5 Dias e publica oficialmente no Instagram
    (Feed 4:5 + Story 9:16) via `canva_publisher_service` (ZERO vídeos/Reels).
    """
    arte = gerar_card_diario_reset(dia_indice=dia_indice)
    if not arte.get("sucesso"):
        return arte

    try:
        try:
            from canva_publisher_service import publicar_arte_canva_no_instagram
        except ImportError:
            from apps.api.canva_publisher_service import publicar_arte_canva_no_instagram

        pub = publicar_arte_canva_no_instagram(
            caminho_imagem_canva=arte["card_path"],
            legenda=arte["legenda"],
            titulo_story="KIT RESET 5 DIAS + 40 DIAS VIP",
        )
        return {**arte, "publicacao": pub}
    except Exception as e:
        return {**arte, "publicacao": {"sucesso": False, "erro": str(e)}}


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    res = gerar_card_diario_reset()
    print(json.dumps(res, indent=2, ensure_ascii=False))
