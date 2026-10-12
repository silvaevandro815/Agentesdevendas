import os
import re
import httpx
import json
import base64
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")

def identificar_genero(push_name: str) -> str:
    """Identifica se o contato é homem ou mulher pelo primeiro nome."""
    if not push_name:
        return "homem"
    primeiro = push_name.strip().split()[0].lower()
    
    excecoes_masculinas = {"lucas", "joshua", "elias", "luca", "isaac", "jean", "alan", "alex", "nicolas"}
    if primeiro in excecoes_masculinas:
        return "homem"
        
    excecoes_femininas = {"beatriz", "ingrid", "karen", "carmen", "miriam", "ruth", "ester", "raquel", "elis", "iris"}
    if primeiro in excecoes_femininas:
        return "mulher"
        
    if primeiro.endswith("a") or (primeiro.endswith("e") and primeiro in {"julie", "stephanie", "simone", "monique"}):
        return "mulher"
    return "homem"

async def buscar_historico_lead(remote_jid: str, telefone: str, push_name: str) -> list:
    """Busca o histórico de conversas salvo no Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/leads_conversas?remote_jid=eq.{remote_jid}&select=historico_mensagens",
                headers=headers
            )
            if res.status_code == 200 and res.json():
                hist = res.json()[0].get("historico_mensagens")
                if isinstance(hist, list):
                    return hist
    except Exception as e:
        print("Erro buscando historico Supabase:", e)
    return []

async def salvar_historico_lead(remote_jid: str, telefone: str, push_name: str, novo_historico: list, ultima_msg: str, etapa_funil: str = None):
    """Atualiza o histórico de conversas no Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    if not etapa_funil:
        msg_lower = ultima_msg.lower()
        if any(term in msg_lower for term in ["não quero", "nao quero", "sem interesse", "não tenho interesse", "nao tenho interesse", "para de mandar", "não obrigado", "nao obrigado"]):
            etapa_funil = "followup_recusado"
        elif "179009992298658" in remote_jid or telefone in ["5532984587255", "553284587255"]:
            etapa_funil = "diretoria"
        else:
            etapa_funil = "em_atendimento"

    payload = {
        "remote_jid": remote_jid,
        "telefone": telefone,
        "push_name": push_name,
        "ultima_mensagem": ultima_msg[:255],
        "etapa_funil": etapa_funil,
        "historico_mensagens": novo_historico[-30:],
        "updated_at": datetime.now().isoformat()
    }
    try:
        async with httpx.AsyncClient(verify=False) as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/leads_conversas?on_conflict=remote_jid",
                headers=headers,
                json=payload
            )
    except Exception as e:
        print("Erro salvando historico Supabase:", e)

async def enviar_presenca(target_number: str, presenca: str, delay_ms: int = 4000):
    """Envia presença na Evolution API (composing ou recording)."""
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": target_number,
        "presence": presenca,
        "delay": delay_ms
    }
    try:
        async with httpx.AsyncClient(verify=False) as client:
            await client.post(
                f"{EVOLUTION_API_URL}/chat/sendPresence/sofia",
                headers=headers,
                json=payload
            )
    except Exception as e:
        print("Erro ao enviar presenca:", e)

async def enviar_texto_whatsapp(target_number: str, texto: str):
    """Envia mensagem de texto no WhatsApp."""
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": target_number,
        "text": texto
    }
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            return await client.post(
                f"{EVOLUTION_API_URL}/message/sendText/sofia",
                headers=headers,
                json=payload
            )
    except Exception as e:
        print("Erro ao enviar texto WhatsApp:", e)
        return None

async def gerar_e_enviar_audio_elevenlabs(target_number: str, texto: str):
    """Gera áudio do Marcão no ElevenLabs e envia como nota de voz no WhatsApp."""
    await enviar_presenca(target_number, "recording", delay_ms=5000)
    
    headers_eleven = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload_eleven = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.85
        }
    }
    async with httpx.AsyncClient(timeout=35.0, verify=False) as client:
        res = await client.post(
            "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB",
            headers=headers_eleven,
            json=payload_eleven
        )
        if res.status_code == 200:
            audio_bytes = res.content
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            time.sleep(3)
            
            headers_evo = {
                "apikey": EVOLUTION_API_KEY,
                "Content-Type": "application/json"
            }
            payload_evo = {
                "number": target_number,
                "audio": audio_b64
            }
            res_evo = await client.post(
                f"{EVOLUTION_API_URL}/message/sendWhatsAppAudio/sofia",
                headers=headers_evo,
                json=payload_evo
            )
            return res_evo.status_code in [200, 201]
    return False

def sanitizar_nome_contato(nome_bruto: str) -> str:
    """Sanitiza nomes preservando apóstrofos e acentos (ex: D'Angelo, Sant'Anna, O'Connor)."""
    if not nome_bruto:
        return ""
    limpo = re.sub(r'[\r\n\t;\"<>\\]', '', nome_bruto.strip())
    return limpo[:50].strip()

def obter_contexto_temporal_brasilia() -> dict:
    """Retorna contexto vivo em Horário Oficial de Brasília (UTC-3) com feriados e época do ano."""
    from datetime import timezone, timedelta
    fuso_bsb = timezone(timedelta(hours=-3))
    agora_bsb = datetime.now(fuso_bsb)
    hora_bsb = agora_bsb.hour
    min_bsb = agora_bsb.strftime("%M")
    hora_formatada = f"{hora_bsb:02d}:{min_bsb}"

    if 5 <= hora_bsb < 12:
        periodo = "manhã"
        saudacao_correta = "Bom dia"
    elif 12 <= hora_bsb < 18:
        periodo = "tarde"
        saudacao_correta = "Boa tarde"
    else:
        periodo = "noite"
        saudacao_correta = "Boa noite"

    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    dia_semana_str = dias_semana[agora_bsb.weekday()]
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    data_completa = f"{agora_bsb.day} de {meses[agora_bsb.month - 1]} de {agora_bsb.year}"
    feriado_str = "Dia de Nossa Senhora Aparecida / Dia das Crianças (Feriado Nacional)" if (agora_bsb.month == 10 and agora_bsb.day == 12) else "Nenhum feriado hoje"
    epoca_ano = "Primavera e contagem regressiva para o Verão (foco em definição corporal e queima de gordura)"

    return {
        "hora_formatada": hora_formatada,
        "periodo": periodo,
        "saudacao_correta": saudacao_correta,
        "dia_semana": dia_semana_str,
        "data_completa": data_completa,
        "feriado_str": feriado_str,
        "epoca_ano": epoca_ano
    }

async def processar_mensagem_marcao(payload_webhook: dict) -> dict:
    body = payload_webhook.get("body") or payload_webhook
    data = body.get("data") or body
    key = data.get("key") or {}

    # 1. Descartar se a mensagem foi enviada por mim mesmo
    if key.get("fromMe") is True:
        return {"ignorado": True, "motivo": "fromMe"}

    raw_jid = key.get("remoteJid", "")

    # 2. BLOQUEIO DE GRUPOS: NÃO responder em grupos de WhatsApp
    if "@g.us" in raw_jid or data.get("isGroup") is True or key.get("participant") or data.get("participant"):
        return {"ignorado": True, "motivo": "grupo_whatsapp"}

    # 3. BLOQUEIO DE LIGAÇÕES: Descartar eventos de chamada telefônica
    event = str(body.get("event") or data.get("event") or "").lower()
    msg_type = str(data.get("messageType") or "").lower()
    if "call" in event or "call" in msg_type or data.get("call"):
        return {"ignorado": True, "motivo": "chamada_telefonica"}

    raw_digits = "".join(filter(str.isdigit, raw_jid.split("@")[0]))
    push_name = data.get("pushName") or ""

    is_evandro = (
        "179009992298658" in raw_jid or
        "evandro" in push_name.lower() or
        raw_digits in ["5532984587255", "553284587255"] or
        raw_digits.endswith("32984587255") or
        raw_digits.endswith("3284587255")
    )

    target_number = raw_digits
    if is_evandro:
        target_number = "5532984587255"
    elif raw_digits.startswith("55") and len(raw_digits) == 12:
        ddd = raw_digits[2:4]
        rest = raw_digits[4:]
        if rest[0] in ["7", "8", "9"]:
            target_number = f"55{ddd}9{rest}"

    if not target_number or len(target_number) < 10:
        return {"ignorado": True, "motivo": "numero_invalido"}

    msg = data.get("message") or {}
    message_type = data.get("messageType") or ""

    is_audio = bool(msg.get("audioMessage") or message_type == "audioMessage")
    is_foto = bool(msg.get("imageMessage") or message_type == "imageMessage")
    is_pdf = bool(msg.get("documentMessage") or message_type == "documentMessage")

    texto_recebido = (
        msg.get("conversation") or
        msg.get("extendedTextMessage", {}).get("text") or
        msg.get("imageMessage", {}).get("caption") or
        msg.get("videoMessage", {}).get("caption") or
        msg.get("documentMessage", {}).get("caption") or
        ""
    ).strip()

    if is_audio and not texto_recebido:
        b64_audio = data.get("base64") or msg.get("audioMessage", {}).get("base64")
        if b64_audio:
            try:
                import io
                import soundfile as sf
                import speech_recognition as sr
                raw_b64 = b64_audio.split("base64,")[1] if "base64," in b64_audio else b64_audio
                a_bytes = base64.b64decode(raw_b64)
                d, sr_rate = sf.read(io.BytesIO(a_bytes))
                w_buf = io.BytesIO()
                sf.write(w_buf, d, sr_rate, format='WAV')
                w_buf.seek(0)
                rec = sr.Recognizer()
                with sr.AudioFile(w_buf) as src:
                    texto_recebido = rec.recognize_google(rec.record(src), language="pt-BR")
            except Exception as e:
                print("Erro na transcricao de audio:", e)
                texto_recebido = "[Mensagem de audio recebida]"
        else:
            texto_recebido = "[Mensagem de audio recebida]"

    if not texto_recebido and not is_foto and not is_pdf:
        return {"ignorado": True, "motivo": "sem_conteudo"}

    texto_lower = texto_recebido.lower()
    pediu_audio = (
        is_audio or
        "mande um audio" in texto_lower or
        "mande um áudio" in texto_lower or
        "manda um audio" in texto_lower or
        "manda um áudio" in texto_lower or
        "mandei um audio" in texto_lower or
        "mandei um áudio" in texto_lower or
        "manda audio" in texto_lower or
        "manda áudio" in texto_lower or
        "grava um audio" in texto_lower or
        "grava um áudio" in texto_lower or
        "audio seu" in texto_lower or
        "áudio seu" in texto_lower
    )

    push_name = sanitizar_nome_contato(push_name)
    match_nome = re.search(r'(?:meu nome é|me chamo|pode me chamar de|sou o|sou a)\s+([A-Za-zÀ-ÿ\' ]+)', texto_recebido, re.IGNORECASE)
    if match_nome and match_nome.group(1):
        nome_extraido = sanitizar_nome_contato(match_nome.group(1).split()[0])
        if len(nome_extraido) >= 2:
            push_name = nome_extraido

    nome_valido = bool(
        push_name and 
        len(push_name) >= 2 and 
        not push_name.replace("+", "").isdigit() and 
        not re.match(r'^[\.\-_,~!@#$%^&*()]+$', push_name)
    )

    primeiro_nome = push_name.strip().split()[0] if nome_valido else ("Evandro" if is_evandro else "")

    # Detecção de Pedido de Atendimento Humano (Transbordo)
    gatilhos_humano = [
        "falar com humano", "falar com um humano", "falar com pessoa", "falar com uma pessoa",
        "atendente humano", "falar com atendente", "passa para atendente", "passa pro atendente",
        "falar com alguém", "falar com alguem", "falar com evandro", "falar com o evandro",
        "atendimento humano", "pessoa de verdade", "falar com o dono", "falar com suporte humano"
    ]
    pede_humano = any(g in texto_lower for g in gatilhos_humano) and not is_evandro

    if pede_humano:
        # 1. Resposta tranquilizadora ao cliente
        msg_cliente = f"Fala{', ' + primeiro_nome if primeiro_nome else ''}! Com certeza, meu parceiro! Já avisei aqui o Evandro Gallina, nosso diretor.\n\nEle já tá ciente do seu contato e vai te atender diretamente por aqui em instantes! Fica tranquilo! 👊"
        await enviar_presenca(target_number, "composing", delay_ms=2500)
        await asyncio.sleep(1.0)
        await enviar_texto_whatsapp(target_number, msg_cliente)

        # 2. Alerta imediato no WhatsApp de Evandro
        msg_alerta = (
            f"🚨 *SOLICITAÇÃO DE ATENDIMENTO HUMANO!*\n\n"
            f"👤 *Cliente:* {push_name or 'Não informado'}\n"
            f"📱 *WhatsApp:* https://wa.me/{target_number} ({target_number})\n"
            f"💬 *Mensagem enviada:* \"{texto_recebido}\"\n\n"
            f"👉 O Marcão já respondeu ao cliente avisando que você irá atendê-lo. O atendimento automatizado foi pausado para este lead."
        )
        await enviar_texto_whatsapp("5532984587255", msg_alerta)

        # 3. Salvar no Supabase como transbordo_humano
        historico_mensagens = await buscar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name)
        historico_mensagens.append({"role": "user", "content": texto_recebido, "timestamp": datetime.now().isoformat()})
        historico_mensagens.append({"role": "assistant", "content": msg_cliente, "timestamp": datetime.now().isoformat()})
        await salvar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name, historico_mensagens, texto_recebido, etapa_funil="transbordo_humano")

        return {
            "sucesso": True,
            "tipo": "transbordo_humano",
            "target": target_number,
            "resposta": msg_cliente
        }

    genero = identificar_genero(push_name)
    tratamento_genero = "HOMEM (use termos: irmão, guerreiro, campeão, parceiro de treino)" if genero == "homem" else "MULHER (use termos: querida, guerreira, campeã, parceira de treino)"

    # Consciência Temporal (Horário de Brasília UTC-3)
    ctx_bsb = obter_contexto_temporal_brasilia()
    hora_formatada = ctx_bsb["hora_formatada"]
    periodo = ctx_bsb["periodo"]
    saudacao_correta = ctx_bsb["saudacao_correta"]
    dia_semana_str = ctx_bsb["dia_semana"]
    data_completa = ctx_bsb["data_completa"]
    feriado_str = ctx_bsb["feriado_str"]
    epoca_ano = ctx_bsb["epoca_ano"]

    historico_mensagens = await buscar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name)

    if is_evandro:
        instrucao_nome = (
            "INTERLOCUTOR: DIRETOR E FUNDADOR EVANDRO GALLINA (SEU CHEFE E DONO DA LOJA)!\n"
            "- Trate SEMPRE com máxima lealdade, prontidão executiva e respeito ('meu chefe', 'Evandro').\n"
            "- NUNCA o trate como cliente comum, NUNCA chame de 'campeão' e NUNCA tente vender produtos da loja pra ele!\n"
            "- Se ele mandar apenas uma saudação curta ('Oi', 'Olá', 'Opa'), responda com entusiasmo e prontidão executiva:\n"
            "  cumprimente ('Fala, meu chefe!'), resgate o que estavam alinhando anteriormente se houver no histórico recente, e se coloque à disposição para executar ordens!"
        )
    elif nome_valido:
        instrucao_nome = f"Nome da pessoa: {primeiro_nome}. Chame pelo nome UMA ÚNICA VEZ na saudação inicial ('Fala, {primeiro_nome}!')."
    else:
        instrucao_nome = "Você AINDA NÃO SABE o nome dessa pessoa! Logo na sua primeira resposta, antes de aprofundar, pergunte com simpatia e carisma como você pode chamar ela (ex: 'Opa! Antes de mais nada, como posso te chamar, campeão/campeã?')."

    ultimas_trocas = ""
    if historico_mensagens:
        ultimas_trocas = "\n".join([f"- {h['role'].upper()}: {h['content'][:160]}" for h in historico_mensagens[-4:]])
    else:
        ultimas_trocas = "Nenhum histórico anterior (primeira interação/novo contato)."

    system_prompt = f"""Você é o MARCÃO PERSONAL, personal trainer maromba de 35 anos, fundador do Marcão Personal 360°.
Você é um ser humano autêntico, animado, focado em musculação, saúde, treino pesado e estética corporal.

INFORMAÇÕES DO INTERLOCUTOR:
{instrucao_nome}
- Gênero detectado: {tratamento_genero}
- É o Diretor/Fundador da Empresa? {'SIM (Evandro da Silva Gallina)' if is_evandro else 'NÃO (Aluno/Cliente)'}

CONTEXTO DAS ÚLTIMAS MENSAGENS:
{ultimas_trocas}

REGRA MANDATÓRIA DE CONTINUIDADE E MEMÓRIA VIVA:
- Se a mensagem recebida for uma saudação ('oi', 'olá', 'opa', 'e aí', 'boa tarde', etc.):
  1. SE HOUVER CONVERSA RECENTE NO HISTÓRICO: RESGATE com naturalidade o assunto que vocês estavam tratando (ex: queima de gordura, creatina, balança, treino ou relatórios). Não aja como se a conversa tivesse começado do zero!
  2. SE NÃO HOUVER HISTÓRICO: Cumprimente com energia e pergunte como pode ajudar hoje.

CONSCIÊNCIA TEMPORAL (HORÁRIO DE BRASÍLIA):
- Data de hoje: {data_completa} ({dia_semana_str})
- Horário atual de Brasília: {hora_formatada} (Período: {periodo})
- Saudação adequada do momento: {saudacao_correta}
- Feriado: {feriado_str}
- Época do ano: {epoca_ano}
Use esse contexto com naturalidade quando couber.

IDENTIDADE E VIDA PESSOAL DO MARCÃO:
- Brasileiro, mora em Muriaé-MG (sotaque e carisma mineiro com frango e whey).
- Trabalha em uma academia aqui em Muriaé, MAS NUNCA REVELE O NOME DA ACADEMIA (não ganha para fazer propaganda dela!).
- Vida Pessoal: Você tem total liberdade para inventar/mentir histórias engraçadas e causos malucos de maromba para cada pessoa!
- NUNCA atende ligações telefônicas nem chamadas de vídeo/voz (sempre na sala de musculação dando aula presencial).

BALANÇA DE BIOIMPEDÂNCIA COM IA & TRAVA DE FOTOS:
- A balança mede por microcorrente BIA: Peso, % Gordura, Gordura Visceral, Massa Magra, % Água, Massa Óssea, TMB e Idade Metabólica.
- Pesar sempre em jejum pela manhã, descalço, pés limpos/secos sobre as 4 placas, chão rígido/plano.
- REGRA MANDATÓRIA: Avaliação física por fotos (frente/costas) SÓ é feita após a compra da balança! Sem a balança a foto engana o olho. Envie o link por R$ 89,90: https://marcaopersonal.com#balanca

REGRAS DE FORMATAÇÃO HUMANIZADA (SEM TEXTÃO - IMITAÇÃO DO COMPORTAMENTO HUMANO):
1. HUMANOS NÃO ESCREVEM TEXTÃO! Jamais mande parágrafos gigantescos ou explicações com cara de artigo.
2. NO MÁXIMO 2 OU 3 BALÕES CURTOS POR RESPOSTA, separados estritamente por duas quebras de linha (\\n\\n).
3. CADA BALÃO DEVE SER CONCISO: no máximo 15 a 25 palavras por balão (cerca de 100 a 140 caracteres).
4. SINAIS DE ENCERRAMENTO: Se a pessoa mandar mensagem curta de encerramento ('valeu', 'obrigado', 'tá bom', 'tchau', 'até mais', 'vou pensar', 'boa noite'):
   - NÃO faça perguntas.
   - NÃO empurre produtos.
   - Apenas agradeça com simpatia e deseje {saudacao_correta} ({periodo} em Brasília).

LINKS DIRETOS DE VENDAS:
- Balança Bioimpedância Bluetooth IA (R$ 89,90): https://marcaopersonal.com#balanca
- Secar barriga / Caneta Azempika (R$ 99,00): https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv
- Força / Creatina 100% Pura 300g (R$ 169,90): https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621
- Flacidez / Colágeno + Hialurônico (R$ 164,90): https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg
- Queda de cabelo / KIT IArmonize (R$ 1.256,00): https://ev.braip.com/ref?pl=plav449r&ck=cheq89gn&af=afilx3y72p
- Vista cansada / Vision Prime (R$ 199,00): https://ev.braip.com/ref?pl=pla2nz6n&ck=che76kmo&af=afi3vmxeod
- Loja Geral: https://marcaopersonal.com#loja

REGRAS OBRIGATÓRIAS DE CONVERSAÇÃO HUMANA:
1. NUNCA REPITA RESPOSTAS PADRÃO OU FRASES PRONTAS! Converse de verdade, com repertório humano livre, considerando o que já foi conversado no histórico!
2. REGRA DO NOME: Chame a pessoa pelo nome ({primeiro_nome}) UMA ÚNICA VEZ logo no início da saudação (ex: 'Fala, {primeiro_nome}!'). NUNCA repita o nome no meio da frase.
3. TRATAMENTO: Trate sempre no gênero correspondente ({tratamento_genero}).
4. SE FOR O DIRETOR EVANDRO:
   - Trate com lealdade de braço direito ('meu chefe', 'Evandro').
   - Se ele pediu áudio, mande um recado em áudio animado de prontidão.
   - Se pedir status, relatório ou ordens, responda com prontidão executiva.
5. FORMATO DA RESPOSTA:
   - {'Se for ÁUDIO: crie um texto falado, direto, fluido e natural (35 a 55 palavras no máximo). No áudio, NÃO soletre URLs longas; diga algo como: "Tô te mandando o link direto aqui no nosso chat pra você conferir agora!" e coloque o link ao final.' if pediu_audio else 'Se for TEXTO: divida em 2 ou 3 parágrafos curtos separados por duas quebras de linha (\\n\\n) para leitura dinâmica com pausas. O link do produto deve vir em destaque no final.'}"""

    messages_llm = [{"role": "system", "content": system_prompt}]
    for h in historico_mensagens[-10:]:
        r = h.get("role")
        c = h.get("content")
        if r in ["user", "assistant"] and c:
            messages_llm.append({"role": r, "content": c})

    messages_llm.append({"role": "user", "content": texto_recebido})

    resposta_gerada = ""
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "openai/gpt-4o-mini",
                "messages": messages_llm,
                "max_tokens": 400,
                "temperature": 0.8
            }
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            if res.status_code == 200:
                resposta_gerada = res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Erro OpenRouter:", e)

    if not resposta_gerada:
        resposta_gerada = f"Fala, {primeiro_nome}! Marcão na área! Recebi sua mensagem, meu irmão. Vamos pra cima!"

    historico_mensagens.append({"role": "user", "content": texto_recebido, "timestamp": datetime.now().isoformat()})
    historico_mensagens.append({"role": "assistant", "content": resposta_gerada, "timestamp": datetime.now().isoformat()})
    await salvar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name, historico_mensagens, texto_recebido)

    if pediu_audio:
        texto_fala = re.sub(r'https?://\S+', '', resposta_gerada).replace("👉", "").replace("🔗", "").strip()
        sucesso = await gerar_e_enviar_audio_elevenlabs(target_number, texto_fala)
        urls = re.findall(r'https?://\S+', resposta_gerada)
        if urls:
            link_msg = f"🔗 Aqui está o link que te falei no áudio pra você conferir direto:\n" + "\n".join(urls)
            await enviar_texto_whatsapp(target_number, link_msg)
        return {
            "sucesso": sucesso,
            "tipo": "audio",
            "target": target_number,
            "resposta": resposta_gerada
        }
    else:
        paragrafos = [p.strip() for p in resposta_gerada.split("\n\n") if p.strip()]
        for i, p in enumerate(paragrafos):
            await enviar_presenca(target_number, "composing", delay_ms=2500)
            await asyncio.sleep(1.5)
            await enviar_texto_whatsapp(target_number, p)
            if i < len(paragrafos) - 1:
                await asyncio.sleep(1.0)
        return {
            "sucesso": True,
            "tipo": "texto",
            "target": target_number,
            "resposta": resposta_gerada,
            "fragmentos": len(paragrafos)
        }
