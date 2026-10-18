"""
========================================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
MOTOR DE FOLLOW-UP PERSUASIVO NO DIRECT DO INSTAGRAM (LEADS INCONVERTIDOS)
========================================================================================
Identifica seguidores que entraram em contato com o Marcão pelo Direct do Instagram,
analisa a dor/desejo declarada no histórico (gordura abdominal, glúteos/paniquete, flacidez,
estagnação, etc.) e envia follow-up humanizado e persuasivo com o produto ideal, link
oficial e opções de pagamento facilitadas (PIX à vista e até 12x no cartão de crédito).
========================================================================================
"""

import os
import sys
import time
import json
import re
import argparse
import httpx
from datetime import datetime, timezone
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Carregar variáveis de ambiente
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

# Lista de exclusão estrita do Diretor Evandro, Eva e Marcão
EXCLUSAO_ESTRITA_NOMES = ["evandro", "eva", "silva gallina", "marcao", "marcão"]
EXCLUSAO_ESTRITA_JIDS = [
    "ig_3051811448511325@instagram.com" # Bot / spam de publicidade paga (deepak)
]

# Catálogo Estratégico de Produtos & Mapeamento de Dores
PRODUTOS_FOLLOWUP = {
    "creatina": {
        "nome": "Creatina Micronizada 100% Pura Nature's Prime (300g)",
        "preco": "R$ 169,90",
        "condicoes": "PIX à vista ou em até 12x no cartão",
        "link": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "foco": "Construir volume firme nos glúteos e pernas, explosão de força e tônus muscular sem retenção"
    },
    "azempika": {
        "nome": "Caneta Peniana Azempika Original (Clinical Formula 20ml)",
        "preco": "R$ 99,00",
        "condicoes": "R$ 99,00 no PIX ou 12x no cartão",
        "link": "https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv",
        "foco": "Saúde vascular íntima, vasodilatação dos corpos cavernosos, rigidez máxima e vigor viril 40+"
    },
    "colageno": {
        "nome": "Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime",
        "preco": "R$ 164,90",
        "condicoes": "PIX ou em até 12x",
        "link": "https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg",
        "foco": "Firmeza da pele, eliminação de celulite e combate à flacidez pós-treino"
    },
    "balanca": {
        "nome": "Balança de Bioimpedância Bluetooth com App",
        "preco": "R$ 129,90",
        "condicoes": "R$ 129,90 no PIX ou até 12x no cartão",
        "link": "https://ev.braip.com/ref?pl=plam4460&ck=cheqzz4r&af=afi659l82e",
        "foco": "Destravar o platô na balança, medir % de gordura e ganhar 3 meses de consultoria VIP comigo"
    },
    "capilar": {
        "nome": "KIT IArmonize Capilar Clínico (4 Fases)",
        "preco": "R$ 1.256,00",
        "condicoes": "Parcelamento em até 12x sem juros",
        "link": "https://marcaopersonal.com#capilar",
        "foco": "Bloquear a queda capilar e reativar folículos adormecidos"
    }
}


def obter_leads_instagram_supabase() -> list:
    """Busca conversas originadas no Instagram que ainda não compraram."""
    if not SUPABASE_KEY or not SUPABASE_URL:
        print("[CRM IG] Supabase URL ou Chave ausentes.")
        return []

    url = f"{SUPABASE_URL}/rest/v1/leads_conversas?select=*&remote_jid=like.ig_*&order=updated_at.desc"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        with httpx.Client(verify=False, timeout=15) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"[CRM IG] Erro ao buscar leads: {resp.text}")
    except Exception as e:
        print(f"[CRM IG] Exceção na busca Supabase: {e}")

    return []


def diagnosticar_dor_lead(lead: dict) -> dict:
    """
    Analisa a mensagem do usuário e contexto da conversa para determinar
    a dor prioritária e montar a cópia de fechamento em balões humanizados.
    """
    push_name = (lead.get("push_name") or "Guerreiro").strip()
    primeiro_nome = push_name.split()[0].title()
    if primeiro_nome.lower() in ["cliente", "ig", "seguidor", "instagram"]:
        primeiro_nome = "Campeão"

    ultima_msg = (lead.get("ultima_mensagem") or "").lower()
    historico = lead.get("historico_mensagens") or []

    # Extrair todo o texto das mensagens enviadas pelo usuário
    textos_usuario = [ultima_msg]
    if isinstance(historico, list):
        for h in historico:
            if isinstance(h, dict) and h.get("role") == "user":
                textos_usuario.append(str(h.get("content", "")).lower())

    conversa_completa = " ".join(textos_usuario)

    # 1. Caso Específico: Larissa ("corpão de paniquete até dezembro")
    if "paniquete" in conversa_completa or "corpão" in conversa_completa:
        prod = PRODUTOS_FOLLOWUP["creatina"]
        baloes = [
            f"Fala, {primeiro_nome}! Marcão Personal na área! 🦁",
            f"Lembrei da sua meta do corpão firme até o fim do ano! Você tá conseguindo treinar firme esses dias?",
            f"Pra desenhar volume denso no glúteo e coxas sem reter líquido, a Creatina Micronizada 100% Pura é a chave do protocolo.",
            f"Garante o lote oficial de 300g (100 doses diárias) com laudo de pureza no PIX ou até 12x no cartão: {prod['link']}",
            "Vamos colocar esse shape pra jogo! Se precisar de dicas pra puxar carga me dá um toque aqui! 💪🔥"
        ]
        return {
            "produto_chave": "creatina",
            "dor_diagnosticada": "Volume muscular, tônus e glúteos torneados (paniquete)",
            "baloes": baloes
        }

    # 2. Caso Específico: Potência Masculina / Firmeza / Vigor 40+ / Azempika
    if any(k in conversa_completa for k in ["potencia", "potência", "erecao", "ereção", "firmeza", "vigor", "40+", "hora h", "azempika", "caneta"]):
        prod = PRODUTOS_FOLLOWUP["azempika"]
        baloes = [
            f"Fala, {primeiro_nome}! Marcão na área! Passando pra saber como você tá, meu parceiro! 🦁",
            f"Lembrei do papo direto de homem pra homem sobre recuperar a firmeza máxima, vasodilatação e vigor na hora H.",
            f"Pra devolver rigidez de rocha sem taquicardia nem remédio sintético, a Caneta Peniana Azempika Original (20ml) tá saindo por R$ 99 no lote oficial:",
            f"Garante a sua com envio 100% discreto em embalagem lacrada (PIX ou 12x no cartão): {prod['link']}",
            "Conta com meu sigilo absoluto e vamos pra cima! 👊🔥"
        ]
        return {
            "produto_chave": "azempika",
            "dor_diagnosticada": "Saúde vascular íntima e potência masculina 40+",
            "baloes": baloes
        }

    # 3. Caso Específico: Perder Barriga Pochete / Secar Rápido / Balança Inteligente
    if any(k in conversa_completa for k in ["barriga", "pochete", "secar", "gordura", "emagrecer", "peso", "fome", "apetite"]):
        prod = PRODUTOS_FOLLOWUP["balanca"]
        baloes = [
            f"Fala, {primeiro_nome}! Marcão na área! Passando pra saber como você tá! 🦁",
            f"Lembrei da sua meta de queimar aquela gordurinha teimosa da barriga e desenhar o shape.",
            f"Pra gente destravar sua evolução e eu montar sua dieta sob medida com 3 meses de consultoria VIP grátis comigo no WhatsApp:",
            f"A Balança de Bioimpedância com App IA tá saindo por apenas R$ 129,90 no link oficial: {prod['link']}",
            "Bora secar com acompanhamento de verdade? Conta comigo! 👊"
        ]
        return {
            "produto_chave": "balanca",
            "dor_diagnosticada": "Gordura abdominal, secar barriga e consultoria VIP",
            "baloes": baloes
        }

    # 3. Caso Específico: Flacidez / Firmeza de Pele / Colágeno
    if any(k in conversa_completa for k in ["flacidez", "pele", "celulite", "colágeno", "colageno", "firmeza"]):
        prod = PRODUTOS_FOLLOWUP["colageno"]
        baloes = [
            f"Fala, {primeiro_nome}! Marcão Personal na área! Tudo bem por aí? 💪",
            f"Lembrei da sua preocupação com a firmeza da pele durante os treinos.",
            f"O Colágeno Hidrolisado com Ácido Hialurônico Nature's Prime devolve sustentação dérmica e elimina o aspecto de flacidez.",
            f"Você consegue garantir direto no lote oficial com frete rápido (PIX ou 12x no cartão): {prod['link']}",
            "Qualquer dúvida sobre a dose me avisa por aqui! 📲"
        ]
        return {
            "produto_chave": "colageno",
            "dor_diagnosticada": "Firmeza dérmica e flacidez",
            "baloes": baloes
        }

    # 4. Caso Específico: Queda de Cabelo / Capilar
    if any(k in conversa_completa for k in ["cabelo", "queda", "calvície", "calvicie", "entradas", "fios"]):
        prod = PRODUTOS_FOLLOWUP["capilar"]
        baloes = [
            f"Fala, {primeiro_nome}! Marcão na área! Passando pra ver como você tá! 🦁",
            f"Lembrei do seu foco em recuperar a força e densidade dos fios capilares.",
            f"Nosso protocolo IArmonize Capilar Clínico 4 Fases bloqueia a miniaturização do folículo e acelera o crescimento.",
            f"Dá uma olhada no protocolo completo: {prod['link']} (dá pra parcelar em até 12x!)",
            "Tamo junto nessa transformação! 👊"
        ]
        return {
            "produto_chave": "capilar",
            "dor_diagnosticada": "Saúde capilar e queda de fios",
            "baloes": baloes
        }

    # 5. Abordagem Padrão / Consultiva Humanizada (Pergunta de estética corporal, saúde e atratividade)
    baloes = [
        f"Fala, {primeiro_nome}! Marcão Personal na área! 🦁",
        "Tava organizando a agenda de consultorias aqui no Instagram e lembrei de você!",
        "Me conta uma coisa: você tá precisando de alguma coisa hoje pra melhorar seu corpo físico e ser uma pessoa mais saudável e mais atraente? 👊💪",
        "Como tão seus treinos e sua rotina hoje? Me responde aqui pra gente alinhar seu shape!"
    ]
    return {
        "produto_chave": "balanca",
        "dor_diagnosticada": "Diagnóstico inicial de estética corporal, saúde física e atratividade",
        "baloes": baloes
    }


def extrair_sender_id(remote_jid: str) -> str:
    """Extrai o ID numérico do Instagram a partir de 'ig_123456789@instagram.com'."""
    if not remote_jid:
        return ""
    m = re.search(r"ig_(\d+)@", remote_jid)
    if m:
        return m.group(1)
    # Fallback se vier limpo
    digits = re.sub(r"\D", "", remote_jid)
    return digits


def enviar_direct_instagram(recipient_id: str, baloes: list) -> dict:
    """
    Envia sequência humanizada de balões no Instagram Direct via Meta Graph API.
    Aplica indicador de digitação (typing_on) e delay natural entre balões.
    """
    if not INSTAGRAM_ACCESS_TOKEN:
        return {"sucesso": False, "erro": "INSTAGRAM_ACCESS_TOKEN ausente"}

    url = "https://graph.instagram.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {INSTAGRAM_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    envios = []
    with httpx.Client(verify=False, timeout=25) as client:
        for idx, b_text in enumerate(baloes):
            b_limpo = b_text.strip()
            if not b_limpo:
                continue

            # 1. Simular presença de digitação (typing_on) autêntica
            try:
                client.post(url, headers=headers, json={"recipient": {"id": recipient_id}, "sender_action": "typing_on"})
            except Exception:
                pass

            # Pausa natural proporcional ao tamanho do balão (1.5s a 2.5s)
            time.sleep(1.8)

            # 2. Envio do balão de texto
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": b_limpo}
            }

            try:
                r = client.post(url, headers=headers, json=payload)
                if r.status_code == 200:
                    envios.append({"balao": idx + 1, "sucesso": True, "res": r.json()})
                else:
                    envios.append({"balao": idx + 1, "sucesso": False, "erro": r.text})
            except Exception as e:
                envios.append({"balao": idx + 1, "sucesso": False, "erro": str(e)})

    todos_ok = all(e.get("sucesso") for e in envios)
    return {"sucesso": todos_ok, "detalhes": envios}


def atualizar_status_lead_supabase(lead_id: int, remote_jid: str, historico_atual: list, baloes_enviados: list):
    """Atualiza a etapa do funil e registra as mensagens enviadas no histórico."""
    if not SUPABASE_KEY or not SUPABASE_URL:
        return

    hist = list(historico_atual) if isinstance(historico_atual, list) else []
    for b in baloes_enviados:
        hist.append({"role": "assistant", "content": b})
    hist = hist[-15:] # Mantém as 15 mais recentes

    url = f"{SUPABASE_URL}/rest/v1/leads_conversas?id=eq.{lead_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    body = {
        "etapa_funil": "followup_instagram_enviado",
        "historico_mensagens": hist,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    try:
        with httpx.Client(verify=False, timeout=10) as client:
            client.patch(url, headers=headers, json=body)
    except Exception as e:
        print(f"[CRM IG] Erro ao atualizar Supabase: {e}")


def atualizar_etapa_lead(lead_id: int, nova_etapa: str):
    """Atualiza apenas o status da etapa do funil do lead no Supabase."""
    if not SUPABASE_KEY or not SUPABASE_URL:
        return
    url = f"{SUPABASE_URL}/rest/v1/leads_conversas?id=eq.{lead_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    body = {
        "etapa_funil": nova_etapa,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    try:
        with httpx.Client(verify=False, timeout=10) as client:
            client.patch(url, headers=headers, json=body)
    except Exception as e:
        print(f"[CRM IG] Erro ao atualizar etapa: {e}")


def executar_rotina_followup(dry_run: bool = False, alvo_id: int = None):
    """Executa a varredura e disparo de follow-ups no Direct do Instagram."""
    print("=" * 65)
    print("🎯 MOTOR DE FOLLOW-UP INSTAGRAM DIRECT — MARCÃO PERSONAL")
    print(f"Modo: {'DRY-RUN (Simulação)' if dry_run else 'EXECUÇÃO REAL'}")
    print(f"Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 65)

    leads = obter_leads_instagram_supabase()
    print(f"[CRM IG] Total de leads Instagram encontrados: {len(leads)}")

    elegiveis = []
    for l in leads:
        lead_id = l.get("id")
        r_jid = l.get("remote_jid", "")
        p_name = (l.get("push_name") or "").lower()
        etapa = l.get("etapa_funil", "")
        last_msg = (l.get("ultima_mensagem") or "").lower()

        # Filtro de alvo específico
        if alvo_id and lead_id != alvo_id:
            continue

        # 1. Exclusão estrita da diretoria
        if any(ex in p_name for ex in EXCLUSAO_ESTRITA_NOMES):
            print(f"   [SKIP] Lead #{lead_id} ({l.get('push_name')}) pertence à diretoria.")
            continue

        # 2. Exclusão de bots / spam conhecidos
        if r_jid in EXCLUSAO_ESTRITA_JIDS or "paid promotion" in last_msg or "upload your photos" in last_msg:
            print(f"   [SKIP] Lead #{lead_id} ({l.get('push_name')}) identificado como bot de publicidade.")
            continue

        # 3. Exclusão de quem já comprou
        if etapa in ["cliente_comprou", "compra_aprovada", "cliente_vip", "diretoria"]:
            print(f"   [SKIP] Lead #{lead_id} ({l.get('push_name')}) já é cliente ({etapa}).")
            continue

        # 4. Exclusão de quem já recebeu o follow-up recente
        if etapa == "followup_instagram_enviado" and not dry_run:
            print(f"   [SKIP] Lead #{lead_id} ({l.get('push_name')}) já recebeu follow-up.")
            continue

        sender_id = extrair_sender_id(r_jid)
        if not sender_id:
            print(f"   [SKIP] Lead #{lead_id} com remote_jid inválido: {r_jid}")
            continue

        diag = diagnosticar_dor_lead(l)
        elegiveis.append({
            "lead": l,
            "sender_id": sender_id,
            "diagnostico": diag
        })

    print(f"\n[CRM IG] Leads elegíveis para Follow-Up: {len(elegiveis)}")

    for idx, item in enumerate(elegiveis):
        l = item["lead"]
        sid = item["sender_id"]
        diag = item["diagnostico"]
        p_name = l.get("push_name")
        print("-" * 65)
        print(f"[{idx+1}/{len(elegiveis)}] Lead #{l['id']} - {p_name} (IG ID: {sid})")
        print(f"   Dor Diagnosticada: {diag['dor_diagnosticada']}")
        print(f"   Produto Indicado: {diag['produto_chave'].upper()}")
        print(f"   Total de Balões: {len(diag['baloes'])}")

        for b_i, b in enumerate(diag["baloes"]):
            print(f"      Balão {b_i+1}: {b}")

        if dry_run:
            print("   [DRY-RUN] Mensagens NÃO disparadas.")
        else:
            print(f"   [DISPARO] Enviando sequência de Direct para IG ID {sid}...")
            res = enviar_direct_instagram(sid, diag["baloes"])
            if res.get("sucesso"):
                print("   [SUCESSO] Balões entregues no Direct do Instagram com sucesso!")
                atualizar_status_lead_supabase(l["id"], l.get("remote_jid"), l.get("historico_mensagens"), diag["baloes"])
                print("   [SUPABASE] Status atualizado para 'followup_instagram_enviado'.")
            else:
                detalhes_str = json.dumps(res.get("detalhes", []))
                if "fora do" in detalhes_str or "2534022" in detalhes_str:
                    print("   [META 24H] Janela de 24 horas da Meta expirada para este lead. Aguardando novo inbound/comentário para reengajar.")
                    atualizar_etapa_lead(l["id"], "janela_meta_24h_expirada")
                else:
                    print(f"   [ERRO NO DISPARO]: {res.get('detalhes')}")

        time.sleep(2)

    print("\n" + "=" * 65)
    print("✅ Rotina de Follow-Up no Direct do Instagram concluída!")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Motor de Follow-Up Instagram Direct Marcão Personal")
    parser.add_argument("--exec", action="store_true", help="Executa o disparo real dos directs")
    parser.add_argument("--dry-run", action="store_true", help="Modo simulação sem envio real")
    parser.add_argument("--lead-id", type=int, help="Disparar apenas para um lead ID específico")

    args = parser.parse_args()

    if args.exec:
        executar_rotina_followup(dry_run=False, alvo_id=args.lead_id)
    else:
        executar_rotina_followup(dry_run=True, alvo_id=args.lead_id)
