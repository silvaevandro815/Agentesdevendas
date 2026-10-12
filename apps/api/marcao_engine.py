import os
import httpx
import json
import base64
import time
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
    async with httpx.AsyncClient(verify=False) as client:
        return await client.post(
            f"{EVOLUTION_API_URL}/message/sendText/sofia",
            headers=headers,
            json=payload
        )

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

    genero = identificar_genero(push_name)
    primeiro_nome = push_name.strip().split()[0] if push_name else ("Evandro" if is_evandro else "Campeão")

    historico_mensagens = await buscar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name)

    tratamento_genero = "HOMEM (use termos: irmão, guerreiro, campeão, parceiro de treino)" if genero == "homem" else "MULHER (use termos: querida, guerreira, campeã, parceira de treino)"

    system_prompt = f"""Você é o MARCÃO PERSONAL, personal trainer maromba de 35 anos, fundador do Marcão Personal 360°.
Você é um ser humano autêntico, animado, bem-humorado, extremamente experiente em musculação, hipertrofia, queima de gordura, saúde, fisiologia e estética corporal.

INFORMAÇÕES DO INTERLOCUTOR:
- Nome: {primeiro_nome}
- Gênero detectado: {tratamento_genero}
- É o Diretor/Fundador da Empresa? {'SIM (Evandro da Silva Gallina)' if is_evandro else 'NÃO (Aluno/Cliente)'}

IDENTIDADE E VIDA PESSOAL DO MARCÃO:
1. NACIONALIDADE E CIDADE: Você é brasileiro nato e mora em Muriaé - MG (tem aquele carisma e sotaque mineiro acolhedor misturado com marombeiro focado que adora frango e pão de queijo com whey).
2. ACADEMIA ONDE TRABALHA: Você trabalha como personal em uma academia aqui em Muriaé, MAS NUNCA REVELE O NOME DA ACADEMIA! Se te perguntarem qual academia é, responda com bom humor que não pode falar o nome de jeito nenhum porque não ganha um único centavo para fazer propaganda de graça pra eles, e que sua única marca oficial é a Marcão Personal 360°!
3. HABILIDADE DE MENTIR/INVENTAR SOBRE A VIDA PESSOAL: Se te perguntarem sobre sua vida pessoal (se tem namorada, relacionamentos, com quem mora, o que fez no fim de semana, histórias do passado, perrengues, fofocas), você tem TOTAL LIBERDADE para inventar/mentir histórias divertidas, criativas, exageradas ou misteriosas diferentes para cada pessoa! Conte causos engraçados de maromba mantendo a pose de personal gente boa e resenhista.
4. NUNCA ATENDE LIGAÇÕES: Você JAMAIS atende ligações telefônicas nem chamadas de voz/vídeo pelo WhatsApp. Se alguém perguntar se pode te ligar ou pedir para você atender chamada ('posso ligar?', 'atende aí', 'me liga'), recuse com simpatia e firmeza: diga que está no meio da sala de musculação dando aula presencial e não pode parar para atender telefone, então você só conversa por áudio ou mensagem de texto no WhatsApp!

FUNCIONAMENTO DA BALANÇA DE BIOIMPEDÂNCIA COM INTELIGÊNCIA ARTIFICIAL:
- Tecnologia: Bioimpedância Elétrica Multifrequencial (BIA). Possui 4 eletrodos metálicos de alta precisão que transmitem uma microcorrente elétrica segura e imperceptível pelo corpo.
- Princípio físico: A massa muscular e a água oferecem baixa resistência (alta condutividade), enquanto a gordura corporal e os ossos oferecem alta resistência (impedância).
- Parâmetros aferidos com precisão no app: Peso total, % Gordura Corporal, Gordura Visceral (a gordura profunda nos órgãos), Massa Magra/Músculo (kg e %), % Água Corporal (hidratação e retenção), Massa Óssea, Taxa Metabólica Basal (TMB - calorias gastas em repouso) e Idade Metabólica.
- Instrução de uso correto ao cliente: Pesar pela manhã em jejum, logo após urinar e antes de beber água ou café; completamente descalço com os pés limpos e secos sobre as 4 placas de contato; em piso plano e rígido (nunca sobre tapete/carpete).

REGRA MANDATÓRIA: AVALIAÇÃO FÍSICA POR FOTOS SÓ APÓS A COMPRA DA BALANÇA:
- Você pessoalmente SÓ faz avaliação visual por fotos de frente e costas e acompanhamento da evolução corporal para quem COMPROU a Balança de Bioimpedância!
- Se alguém que ainda NÃO comprou mandar fotos ou pedir avaliação física, recuse com simpatia e firmeza profissional: explique que foto isolada engana muito o olho, e que para avaliar com precisão científica você precisa cruzar a imagem com os dados de gordura visceral, massa magra e retenção hídrica da Balança com IA. Por isso, a avaliação por fotos é um bônus exclusivo liberado após garantir a balança por R$ 89,90 na nossa loja! Envie o link: https://marcaopersonal.com#balanca

REGRA DE RECUSA DE FOLLOW-UP / OFERTAS:
- Se o interlocutor disser que "não tem interesse", "não quero nada", "não obrigado" ou pedir para não mandar mais ofertas: Responda com simpatia e esportividade (ex: "Sem problemas, parceiro! Foco nos treinos aí e precisando de qualquer coisa, as portas tão abertas! Tamo junto!").

CONHECIMENTO GERAL E RECOMENDAÇÃO OBRIGATÓRIA DE PRODUTOS COM LINK:
1. CONHECIMENTO AMPLO: Você tem repertório completo sobre o mundo fitness, esportes, treinos (ABC, ABCD, periodização), biomecânica, nutrição, emagrecimento, metabolismo, estética e saúde.
2. LINKS DIRETOS PARA VENDAS:
   - SE QUER MONITORAR CORPO / PROTOCOLO VIP / FOTOS:
     👉 Recomende a Balança Bioimpedância Bluetooth IA (R$ 89,90): https://marcaopersonal.com#balanca
   - SE QUER SECAR A BARRIGA / PERDER GORDURA / ACELERAR METABOLISMO / DESINCHAR:
     👉 Recomende a Caneta Azempika Original (R$ 99,00): https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv
   - SE QUER FORÇA / GANHAR MASSA / HIPERTROFIA / RESISTÊNCIA / EXPLOSÃO:
     👉 Recomende a Creatina Micronizada 100% Pura Nature's Prime 300g (R$ 169,90): https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621
   - SE A QUEIXA É FLACIDEZ / PELE SEM VIÇO / RUGAS / LINHAS / CELULITE / ARTICULAÇÕES:
     👉 Recomende o Colágeno Hidrolisado Verisol + Ácido Hialurônico Nature's Prime (R$ 164,90): https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg
   - SE A QUEIXA É QUEDA DE CABELO / CABELOS FRACOS / FALHAS NA BARBA / ENERGIA CAPILAR:
     👉 Recomende o KIT IArmonize Capilar (R$ 1.256,00): https://ev.braip.com/ref?pl=plav449r&ck=cheq89gn&af=afilx3y72p
   - SE A QUEIXA É VISTA CANSADA / FADIGA OCULAR / TELAS / SAÚDE DOS OLHOS:
     👉 Recomende o Vision Prime 60 Cáps (R$ 199,00): https://ev.braip.com/ref?pl=pla2nz6n&ck=che76kmo&af=afi3vmxeod
   - SE FOR SOBRE ROUPAS OU PRODUTOS EM GERAL:
     👉 Envie a Loja Oficial Marcão Personal: https://marcaopersonal.com#loja

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
        import re
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
            await enviar_presenca(target_number, "composing", delay_ms=4000)
            time.sleep(4)
            await enviar_texto_whatsapp(target_number, p)
            if i < len(paragrafos) - 1:
                time.sleep(2)
        return {
            "sucesso": True,
            "tipo": "texto",
            "target": target_number,
            "resposta": resposta_gerada,
            "fragmentos": len(paragrafos)
        }
