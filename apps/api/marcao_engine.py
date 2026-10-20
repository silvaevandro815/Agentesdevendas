import os
import re
import httpx
import json
import base64
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")

try:
    from balanca_engine import (
        verificar_status_vip,
        escanear_tela_bioimpedancia,
        registrar_ou_atualizar_cliente_balanca,
        processar_lead_scoring_inteligente
    )
    from fichas_engine import (
        buscar_ou_criar_ficha_aluno,
        processar_etapa_onboarding,
        armazenar_foto_aluno_criptografada,
        avaliar_prato_comida,
        verificar_e_gerar_upsell_30dias,
        atualizar_ficha_com_dados_extraidos,
        identificar_campos_pendentes_ficha
    )
    from marcao_voice import gerar_voz_marcao_bytes
except ImportError:
    from apps.api.balanca_engine import (
        verificar_status_vip,
        escanear_tela_bioimpedancia,
        registrar_ou_atualizar_cliente_balanca,
        processar_lead_scoring_inteligente
    )
    from apps.api.fichas_engine import (
        buscar_ou_criar_ficha_aluno,
        processar_etapa_onboarding,
        armazenar_foto_aluno_criptografada,
        avaliar_prato_comida,
        verificar_e_gerar_upsell_30dias,
        atualizar_ficha_com_dados_extraidos,
        identificar_campos_pendentes_ficha
    )
    from apps.api.marcao_voice import gerar_voz_marcao_bytes

try:
    from catalog_service import obter_catalogo_para_prompt
    from autonomous_curator import processar_e_ingerir_afiliado
except ImportError:
    from apps.api.catalog_service import obter_catalogo_para_prompt
    from apps.api.autonomous_curator import processar_e_ingerir_afiliado

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

_historico_envios_recentes = {}

def eh_numero_teste_ou_invalido(numero: str) -> bool:
    """Bloqueia números falsos, mocks, ou de testes automatizados para proteger contra banimento da Meta."""
    if not numero:
        return True
    digitos = "".join(filter(str.isdigit, str(numero)))
    if len(digitos) < 10:
        return True
    
    # Exceções permitidas (números reais oficiais do Diretor Evandro)
    if digitos in ["5532984587255", "553284587255", "553285066687", "553298669536"]:
        return False
        
    # Padrões clássicos de mocks e números fictícios
    padroes_mock = [
        "99998888", "99997777", "988881111", "988882222", "988883333",
        "988887777", "977776666", "977778888", "971112222", "973334444",
        "975556666", "979990000", "966667777", "123456", "000000"
    ]
    for p in padroes_mock:
        if p in digitos:
            return True
            
    # Repetições anormais (ex: 5 dígitos iguais seguidos)
    for d in "0123456789":
        if d * 5 in digitos:
            return True

    # REGRA MANDATÓRIA DO DIRETOR EVANDRO:
    # Bloquear qualquer número com DDD 11 desconhecido contra disparos frios.
    # Marcão só fala com quem mandou mensagem antes ou quem Evandro ordenar.
    if digitos.startswith("5511") or (len(digitos) in [10, 11] and digitos.startswith("11")):
        return True
            
    return False

def quebrar_em_baloes_curtos(texto: str, max_chars: int = 130, max_baloes: int = 3) -> list:
    """
    Divide a resposta em no máximo 2 a 3 balões curtos e leves (80 a 130 caracteres),
    preservando links íntegros no último balão.
    """
    linhas = [l.strip() for l in re.split(r'\n+', texto) if l.strip()]
    frases = []
    for l in linhas:
        urls = re.findall(r'https?://\S+', l)
        if urls:
            texto_sem_url = re.sub(r'https?://\S+', '', l).strip()
            if texto_sem_url:
                partes = [p.strip() for p in re.split(r'(?<=[.!?])\s+', texto_sem_url) if p.strip()]
                frases.extend(partes)
            for u in urls:
                frases.append(u)
        else:
            partes = [p.strip() for p in re.split(r'(?<=[.!?])\s+', l) if p.strip()]
            frases.extend(partes)

    baloes = []
    balao_atual = ""
    for f in frases:
        if f.startswith("http"):
            if balao_atual:
                baloes.append(balao_atual)
                balao_atual = ""
            baloes.append(f)
            continue
            
        if not balao_atual:
            balao_atual = f
        elif len(balao_atual) + len(f) + 1 <= max_chars:
            balao_atual += " " + f
        else:
            baloes.append(balao_atual)
            balao_atual = f
            
    if balao_atual:
        baloes.append(balao_atual)

    # Se o último balão for um link isolado e o anterior for curto, junta os dois
    if len(baloes) > 1 and baloes[-1].startswith("http"):
        if len(baloes[-2]) + len(baloes[-1]) + 1 <= 140:
            baloes[-2] = baloes[-2] + " " + baloes[-1]
            baloes.pop()

    if len(baloes) > max_baloes:
        tem_link_no_fim = baloes[-1].startswith("http")
        if tem_link_no_fim and max_baloes >= 2:
            texto_baloes = baloes[:-1]
            slots = max_baloes - 1
            tamanho = max(1, len(texto_baloes) // slots)
            novos = []
            for s in range(slots):
                inicio = s * tamanho
                fim = (s + 1) * tamanho if s < slots - 1 else len(texto_baloes)
                novos.append(" ".join(texto_baloes[inicio:fim]))
            novos.append(baloes[-1])
            baloes = novos
        else:
            tamanho = max(1, len(baloes) // max_baloes)
            novos = []
            for s in range(max_baloes):
                inicio = s * tamanho
                fim = (s + 1) * tamanho if s < max_baloes - 1 else len(baloes)
                novos.append(" ".join(baloes[inicio:fim]))
            baloes = novos

    return [b for b in baloes if b.strip()]

async def enviar_presenca(target_number: str, presenca: str, delay_ms: int = 4000):
    """Envia presença na Evolution API (composing ou recording)."""
    if eh_numero_teste_ou_invalido(target_number):
        print(f"[BLOQUEIO ANTI-SPAM] Presença ignorada para número fictício: {target_number}")
        return None

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
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            await client.post(
                f"{EVOLUTION_API_URL}/chat/sendPresence/sofia",
                headers=headers,
                json=payload
            )
    except Exception as e:
        print("Erro ao enviar presenca:", e)

async def reagir_mensagem_whatsapp(remote_jid: str, msg_id: str, emoji: str = "💪"):
    """Envia reação de emoji na mensagem do WhatsApp via Evolution API."""
    if not remote_jid or not msg_id:
        return False
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "key": {
            "remoteJid": remote_jid,
            "fromMe": False,
            "id": msg_id
        },
        "reaction": emoji
    }
    try:
        async with httpx.AsyncClient(verify=False, timeout=8.0) as client:
            res = await client.post(
                f"{EVOLUTION_API_URL}/message/sendReaction/sofia",
                headers=headers,
                json=payload
            )
            return res.status_code in [200, 201]
    except Exception as e:
        print("Erro ao reagir mensagem WhatsApp:", e)
        return False

async def enviar_texto_whatsapp(target_number: str, texto: str):
    """Envia mensagem de texto no WhatsApp com trava de descarte de duplicidade e proteção anti-spam."""
    if not target_number or not texto:
        return None

    if eh_numero_teste_ou_invalido(target_number):
        print(f"[BLOQUEIO ANTI-SPAM] Disparo de texto bloqueado para número inválido/não autorizado: {target_number}")
        return None

    # MODO DRY RUN / TESTE: Se MARCAO_DRY_RUN estiver ativo, não dispara
    if os.getenv("MARCAO_DRY_RUN", "false").lower() == "true":
        print(f"[DRY-RUN WHATSAPP] Simulação de envio para {target_number}: {texto[:60]}...")
        return {"dry_run": True, "target": target_number, "status": "simulado"}

    # TRAVA ATÔMICA ANTI-DUPLICIDADE (Deduplicação por hash de texto + número com TTL de 300 segundos)
    import hashlib
    chave_dedup = f"{target_number}_{hashlib.md5(texto.strip().encode()).hexdigest()}"
    agora = time.time()
    
    # Limpa entradas antigas (> 600s)
    chaves_expiradas = [k for k, ts in _historico_envios_recentes.items() if agora - ts > 600]
    for k in chaves_expiradas:
        _historico_envios_recentes.pop(k, None)

    if chave_dedup in _historico_envios_recentes:
        tempo_passado = agora - _historico_envios_recentes[chave_dedup]
        if tempo_passado < 300:  # 5 minutos
            print(f"[BLOQUEIO ANTI-DUPLICIDADE] Mensagem idêntica enviada para {target_number} há {int(tempo_passado)}s. Bloqueado!")
            return None

    _historico_envios_recentes[chave_dedup] = agora

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
    """Gera áudio do Marcão (F5-TTS ilimitado com fallback ElevenLabs) e envia como nota de voz no WhatsApp."""
    if eh_numero_teste_ou_invalido(target_number):
        print(f"[BLOQUEIO ANTI-SPAM] Disparo de áudio bloqueado para número fictício: {target_number}")
        return False

    await enviar_presenca(target_number, "recording", delay_ms=4000)
    
    # 1. Tenta gerar via motor ilimitado Marcão Voice (F5-TTS / Cloud GPU)
    audio_bytes = None
    try:
        audio_bytes = await asyncio.to_thread(gerar_voz_marcao_bytes, texto)
    except Exception as e:
        print(f"[MARCAO VOZ] Falha no motor F5-TTS ({e}), acionando fallback ElevenLabs...")
        
    # 2. Fallback direto ElevenLabs se necessário
    if not audio_bytes and ELEVENLABS_API_KEY:
        try:
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
        except Exception as e_elev:
            print(f"[MARCAO VOZ] Falha no fallback ElevenLabs: {e_elev}")
            
    if audio_bytes:
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        time.sleep(1)
        headers_evo = {
            "apikey": EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
        payload_evo = {
            "number": target_number,
            "audio": audio_b64
        }
        async with httpx.AsyncClient(timeout=35.0, verify=False) as client:
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

    if not texto_recebido:
        if is_audio:
            texto_recebido = "[Mensagem de audio recebida]"
        elif is_foto:
            if is_evandro:
                texto_recebido = "[O Diretor Evandro enviou foto(s)/arte(s) do Marcão]"
            else:
                texto_recebido = "[O cliente enviou uma imagem/foto sem legenda]"
        elif is_pdf:
            texto_recebido = "[Documento/Exame em PDF enviado]"
        else:
            return {"ignorado": True, "motivo": "sem_conteudo"}

    # 4. Efeito Reação de Emoji no WhatsApp (Surpreender e Acolher o Usuário)
    msg_id = key.get("id")
    if raw_jid and msg_id:
        if is_evandro:
            emoji_reacao = "💪"
        elif is_foto or is_pdf:
            emoji_reacao = "🔥"
        elif any(w in texto_recebido.lower() for w in ["treino", "academia", "musculo", "massa", "creatina", "hipertrofia"]):
            emoji_reacao = "💪"
        elif any(w in texto_recebido.lower() for w in ["secar", "emagrecer", "gordura", "barriga", "dieta", "peso"]):
            emoji_reacao = "👊"
        else:
            emoji_reacao = "👊"
        asyncio.create_task(reagir_mensagem_whatsapp(raw_jid, msg_id, emoji_reacao))

    # Download de mídia para visão computacional e leitura de PDF
    media_b64 = None
    media_mimetype = None
    texto_pdf_extraido = ""
    if is_foto or is_pdf:
        try:
            async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
                evo_media_res = await client.post(
                    f"{EVOLUTION_API_URL}/chat/getBase64FromMediaMessage/sofia",
                    headers={"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"},
                    json={"message": data, "convertToMp4": False}
                )
                if evo_media_res.status_code in [200, 201]:
                    media_json = evo_media_res.json()
                    media_b64 = media_json.get("base64")
                    media_mimetype = media_json.get("mimetype", "image/jpeg")

                    if is_evandro and is_foto and media_b64:
                        try:
                            pasta_evandro = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "evandro"))
                            os.makedirs(pasta_evandro, exist_ok=True)
                            ts = int(time.time())
                            caminho_foto_ev = os.path.join(pasta_evandro, f"rosto_evandro_{ts}.jpg")
                            raw_b64_ev = media_b64.split("base64,")[1] if "base64," in media_b64 else media_b64
                            with open(caminho_foto_ev, "wb") as f_ev:
                                f_ev.write(base64.b64decode(raw_b64_ev))
                            print(f"[MARCAO_ENGINE] Foto do Diretor Evandro salva para IA em: {caminho_foto_ev}")
                        except Exception as e_ev_pic:
                            print(f"[MARCAO_ENGINE] Erro salvando foto do Evandro: {e_ev_pic}")

                    if is_pdf and media_b64:
                        try:
                            import io
                            from pypdf import PdfReader
                            raw_pdf_bytes = base64.b64decode(media_b64)
                            reader = PdfReader(io.BytesIO(raw_pdf_bytes))
                            for page in reader.pages:
                                texto_pdf_extraido += (page.extract_text() or "") + "\n"
                        except Exception as e_pdf:
                            print("Erro extraindo PDF:", e_pdf)
        except Exception as e_media:
            print("Erro baixando media Evolution:", e_media)

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

    # -------------------------------------------------------------------------
    # SUPERPODER DO MARCÃO: EXECUÇÃO DE COMANDOS DE POSTAGEM DO CHEFE EVANDRO
    # -------------------------------------------------------------------------
    if is_evandro:
        termos_postagem = [
            "posta no instagram", "postar no instagram", "poste no instagram",
            "posta no insta", "poste no insta", "postar no insta",
            "posta no feed", "poste no feed", "postar no feed",
            "posta nos stories", "poste nos stories", "posta no stories", "poste no story",
            "publica no instagram", "publique no instagram", "publicar no instagram",
            "cria um post", "crie um post", "gera um criativo", "faz um post", "faça um post",
            "posta uma foto", "posta um card", "posta uma imagem"
        ]
        eh_comando_postagem = any(t in texto_lower for t in termos_postagem)
        if eh_comando_postagem:
            resposta_prontidao = (
                f"Opa, meu chefe! Entendido e acatado imediatamente! 🚀\n\n"
                f"Tô gerando o criativo agora mesmo e publicando na nossa conta oficial do Instagram (@marcaopersonalfitness).\n\n"
                f"Assim que estiver no ar, te mando a confirmação aqui no nosso chat! Bora pra cima! 💪🔥"
            )
            await enviar_presenca(target_number, "composing", delay_ms=2000)
            await enviar_texto_whatsapp(target_number, resposta_prontidao)

            # Função assíncrona de background para executar a postagem e avisar o Chefe
            async def tarefa_postagem_chefe():
                try:
                    from instagram_executor import executar_postagem_solicitada
                    res = executar_postagem_solicitada(texto_recebido)
                    if res.get("sucesso"):
                        msg_sucesso = (
                            f"🚀 *PRONTINHO, MEU CHEFE! POST PUBLICADO NO INSTAGRAM!*\n\n"
                            f"📸 *Tema:* {res.get('tema')}\n"
                            f"📱 *Destino:* {res.get('destino')} (@marcaopersonalfitness)\n"
                            f"🔗 *ID:* {res.get('post_id')}\n\n"
                            f"Já tá no ar pra galera engajar! O Marcão tá na ativa! 🔥"
                        )
                    else:
                        msg_sucesso = f"Chefe, tive uma oscilação na API do Instagram ao tentar publicar: {res.get('motivo')[:120]}. Mas a imagem foi gerada com sucesso!"
                    await enviar_texto_whatsapp(target_number, msg_sucesso)
                except Exception as e_post:
                    print(f"[MARCAO_SUPERPOWER] Erro na postagem do Chefe: {e_post}")

            asyncio.create_task(tarefa_postagem_chefe())

            historico_mensagens = await buscar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name)
            historico_mensagens.append({"role": "user", "content": texto_recebido, "timestamp": datetime.now().isoformat()})
            historico_mensagens.append({"role": "assistant", "content": resposta_prontidao, "timestamp": datetime.now().isoformat()})
            await salvar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name, historico_mensagens, texto_recebido)

            return {
                "sucesso": True,
                "tipo": "comando_postagem_chefe",
                "target": target_number,
                "resposta": resposta_prontidao
            }

        # -------------------------------------------------------------------------
        # SUPERPODER DO MARCÃO: INGESTÃO E MEMORIZAÇÃO DE AFILIADOS DO CHEFE EVANDRO
        # -------------------------------------------------------------------------
        termos_afiliado = ["!produto", "cadastra produto", "cadastrar produto", "cadastra esse produto", "novo produto", "adiciona produto", "cadastrar afiliado", "link de afiliado"]
        tem_url_afiliado = bool(re.search(r'https?://\S+', texto_recebido)) and any(p in texto_lower for p in ["amazon", "amzn", "magalu", "mercadolivre", "shopee", "braip", "stripe", "afiliad"])
        eh_comando_afiliado = any(t in texto_lower for t in termos_afiliado) or (tem_url_afiliado and len(texto_recebido.split()) < 35)

        if eh_comando_afiliado:
            url_match = re.search(r'https?://\S+', texto_recebido)
            url_afiliado = url_match.group(0) if url_match else "https://marcaopersonal.com#loja"
            
            programa_detectado = "afiliado"
            if "amazon" in url_afiliado or "amzn" in url_afiliado:
                programa_detectado = "amazon"
            elif "magalu" in url_afiliado:
                programa_detectado = "magalu"
            elif "mercadolivre" in url_afiliado or "meli" in url_afiliado:
                programa_detectado = "mercadolivre"
            elif "shopee" in url_afiliado:
                programa_detectado = "shopee"
            elif "braip" in url_afiliado:
                programa_detectado = "braip"
            elif "stripe" in url_afiliado:
                programa_detectado = "stripe"

            res_ingestao = await processar_e_ingerir_afiliado(
                url=url_afiliado,
                texto_ou_html=texto_recebido,
                programa=programa_detectado
            )

            if res_ingestao.get("sucesso"):
                resposta_afiliado = (
                    f"🚀 *PRODUTO MEMORIZADO COM SUCESSO, MEU CHEFE!*\n\n"
                    f"📦 *Produto:* {res_ingestao.get('nome')}\n"
                    f"💰 *Preço Oficial:* R$ {res_ingestao.get('preco'):.2f}\n"
                    f"📊 *Custo por Dia:* R$ {res_ingestao.get('custo_dia'):.2f} / dia\n"
                    f"🎯 *Score de Viabilidade:* {res_ingestao.get('score_viabilidade')}/100 ({res_ingestao.get('classificacao')})\n"
                    f"💎 *Comissão Estimada:* R$ {res_ingestao.get('comissao_estimada'):.2f} por venda\n"
                    f"✅ *Compliance ANVISA & Meta:* 100% Aprovado!\n\n"
                    f"O catálogo unificado já foi atualizado em tempo real! Já está ativo na minha memória no WhatsApp e no Instagram (Directs e Feed/Stories). Bora pra cima bater o R$ 1 Milhão! 💪🔥"
                )
            else:
                resposta_afiliado = (
                    f"Chefe, analisei o produto mas encontrei um alerta de compliance/regras: {res_ingestao.get('motivo')}\n\n"
                    f"Por segurança da conta da Meta e diretrizes da ANVISA, não inseri na vitrine pública automática."
                )

            await enviar_presenca(target_number, "composing", delay_ms=2500)
            await enviar_texto_whatsapp(target_number, resposta_afiliado)

            historico_mensagens = await buscar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name)
            historico_mensagens.append({"role": "user", "content": texto_recebido, "timestamp": datetime.now().isoformat()})
            historico_mensagens.append({"role": "assistant", "content": resposta_afiliado, "timestamp": datetime.now().isoformat()})
            await salvar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name, historico_mensagens, texto_recebido)

            return {
                "sucesso": True,
                "tipo": "ingestao_afiliado_chefe",
                "target": target_number,
                "resposta": resposta_afiliado
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

    tem_conversa_recente = len(historico_mensagens) > 0

    # Consulta de Status VIP da Balança de Bioimpedância e Scoring de Vendas
    status_vip_info = await verificar_status_vip(target_number) if not is_evandro else {}
    tem_balanca = status_vip_info.get("tem_balanca", False)
    dias_restantes_vip = status_vip_info.get("dias_restantes", 0)
    streak_vip = status_vip_info.get("streak_dias", 1)
    status_vip_str = status_vip_info.get("status_vip", "sem_balanca")

    ficha_aluno = None
    if tem_balanca and not is_evandro:
        try:
            # Extrai e salva imediatamente qualquer dado real informado na mensagem do aluno
            await atualizar_ficha_com_dados_extraidos(f"{target_number}@s.whatsapp.net", texto_recebido)
            ficha_aluno = await buscar_ou_criar_ficha_aluno(f"{target_number}@s.whatsapp.net", target_number, push_name or primeiro_nome)
            etapa_onb = ficha_aluno.get("etapa_onboarding", 0)

            # Se o aluno VIP ainda não concluiu o onboarding guiado (etapas 0 a 4)
            if etapa_onb < 5:
                res_onb = await processar_etapa_onboarding(
                    remote_jid=f"{target_number}@s.whatsapp.net",
                    telefone=target_number,
                    nome=push_name or primeiro_nome,
                    texto_recebido=texto_recebido,
                    ficha=ficha_aluno
                )
                if res_onb.get("resposta"):
                    resp_onb_texto = res_onb["resposta"]
                    historico_mensagens.append({"role": "user", "content": texto_recebido, "timestamp": datetime.now().isoformat()})
                    historico_mensagens.append({"role": "assistant", "content": resp_onb_texto, "timestamp": datetime.now().isoformat()})
                    await salvar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name, historico_mensagens, texto_recebido)

                    parags = [p.strip() for p in resp_onb_texto.split("\n\n") if p.strip()]
                    for i, p in enumerate(parags):
                        await enviar_presenca(target_number, "composing", delay_ms=2000)
                        await asyncio.sleep(1.2)
                        await enviar_texto_whatsapp(target_number, p)
                        if i < len(parags) - 1:
                            await asyncio.sleep(1.0)
                    return {
                        "sucesso": True,
                        "tipo": "onboarding_anamnese",
                        "target": target_number,
                        "etapa": etapa_onb,
                        "resposta": resp_onb_texto
                    }

            # Se mandou foto de refeição/prato
            eh_foto_comida = any(w in texto_recebido.lower() for w in ["prato", "comida", "almoço", "almoco", "jantar", "janta", "refeição", "refeicao", "dieta", "comendo"])
            if is_foto and media_b64 and eh_foto_comida:
                avaliacao_prato = await avaliar_prato_comida(media_b64, primeiro_nome)
                if avaliacao_prato:
                    historico_mensagens.append({"role": "user", "content": f"[Foto de prato de refeição]: {texto_recebido}", "timestamp": datetime.now().isoformat()})
                    historico_mensagens.append({"role": "assistant", "content": avaliacao_prato, "timestamp": datetime.now().isoformat()})
                    await salvar_historico_lead(f"{target_number}@s.whatsapp.net", target_number, push_name, historico_mensagens, texto_recebido)

                    parags = [p.strip() for p in avaliacao_prato.split("\n\n") if p.strip()]
                    for i, p in enumerate(parags):
                        await enviar_presenca(target_number, "composing", delay_ms=2500)
                        await asyncio.sleep(1.5)
                        await enviar_texto_whatsapp(target_number, p)
                        if i < len(parags) - 1:
                            await asyncio.sleep(1.0)
                    return {
                        "sucesso": True,
                        "tipo": "analise_prato",
                        "target": target_number,
                        "resposta": avaliacao_prato
                    }

            # Se mandou foto corporal e autorizou LGPD
            if is_foto and media_b64 and ficha_aluno and ficha_aluno.get("consentimento_lgpd"):
                asyncio.create_task(armazenar_foto_aluno_criptografada(f"{target_number}@s.whatsapp.net", media_b64, "frente_costas"))
        except Exception as e_onb:
            print(f"[MARCAO_ENGINE] Erro no processamento da ficha/VIP: {e_onb}")

    if not is_evandro:
        asyncio.create_task(processar_lead_scoring_inteligente(f"{target_number}@s.whatsapp.net", target_number, push_name, texto_recebido, historico_mensagens))

    if is_evandro:
        instrucao_vip = "O interlocutor é o Diretor Evandro. Nenhuma restrição se aplica."
    elif tem_balanca:
        obj_ficha = (ficha_aluno.get("objetivo") or "Definição corporal") if ficha_aluno else "Definição corporal"
        rest_ficha = (ficha_aluno.get("restricoes_saude") or "Nenhuma restrição articular informada") if ficha_aluno else "Nenhuma restrição"
        loc_ficha = (ficha_aluno.get("local_treino") or "Academia") if ficha_aluno else "Academia"
        dias_ficha = (ficha_aluno.get("dias_disponiveis_semana") or 3) if ficha_aluno else 3
        t_atual = (ficha_aluno.get("treino_atual") or {}) if ficha_aluno else {}
        treino_resumo = f"A: {t_atual.get('treino_a', 'Peito/Ombro')} | B: {t_atual.get('treino_b', 'Costas/Bíceps')} | C: {t_atual.get('treino_c', 'Pernas')}" if t_atual else "Divisão ABC personalizada"

        instrucao_vip = (
            f"ALUNO VIP DA BALANÇA 360° ({primeiro_nome}):\n"
            f"- Possui a Balança de Bioimpedância oficial com app!\n"
            f"- Streak de foco: {streak_vip} check-ins realizados!\n"
            f"- Dias restantes do acompanhamento gratuito de 3 meses: {dias_restantes_vip} dias (de 90 dias).\n"
            f"- Status: {status_vip_str}.\n"
            f"- FICHA INDIVIDUAL DE ANAMNESE (MEMÓRIA VIVA DO COACH):\n"
            f"  * Objetivo do Aluno: {obj_ficha}\n"
            f"  * Restrições / Dores Articulares: {rest_ficha} (PROTEJA ESSAS ARTICULAÇÕES EM QUALQUER PRESCRIÇÃO!)\n"
            f"  * Rotina de Treino: {dias_ficha} dias na semana ({loc_ficha})\n"
            f"  * Estrutura de Treino Ativa: {treino_resumo}\n"
            f"  * Segurança LGPD: Foto Criptografada AES-256 no banco militar do Supabase com consentimento formal.\n"
            f"- Você tem TOTAL AUTORIZAÇÃO para analisar o shape dele por fotos (frente/costas), avaliar pratos e calibrar treinos!\n"
            f"- REGRA DOS 3 MESES (TRANSIÇÃO PÓS-90 DIAS): Se faltarem 10 dias ou menos (dias_restantes <= 10), elogie a evolução do aluno e informe com carinho que para continuar com seus check-ins semanais e mentoria direta no WhatsApp, a taxa simbólica é de apenas R$ 19,90/mês no link oficial da Stripe: https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01."
        )
    else:
        instrucao_vip = (
            f"LEAD/CLIENTE SEM A BALANÇA ({primeiro_nome}):\n"
            "- Ele AINDA NÃO TEM a nossa Balança de Bioimpedância Xiaomi Mi Scale 2.\n"
            "- REGRA MANDATÓRIA DE EXCLUSIVIDADE: Avaliação física corporal por foto (frente/costas) e prescrição de treino individual SÓ são feitas para quem comprou a Balança!\n"
            "- Se ele pedir para avaliar o corpo ou shape por foto: Explique com simpatia e autoridade que foto isolada engana a visão (não mostra água celular, massa magra real ou gordura visceral profunda). Para ter acesso ao seu suporte VIP direto por 3 MESES DE FORMA 100% GRATUITA, ele só precisa garantir a Balança Xiaomi Mi Scale 2 por apenas R$ 149,90 (R$ 0,41/dia) na Amazon oficial com frete rápido: https://www.amazon.com.br/dp/B07T48Z4TN?tag=marcaopersona-20.\n"
            "- Após esses 3 meses gratuitos, o acompanhamento continua por apenas R$ 19,90/mês."
        )

    if is_evandro:
        instrucao_nome = (
            "INTERLOCUTOR: DIRETOR E FUNDADOR EVANDRO GALLINA (SEU CHEFE E DONO DA LOJA)!\n"
            "- Trate SEMPRE com máxima lealdade, prontidão executiva e respeito ('meu chefe', 'Evandro').\n"
            "- NUNCA o trate como cliente comum, NUNCA chame de 'campeão' e NUNCA tente vender produtos da loja ou balança pra ele!\n"
            "- Se ele mandar fotos/artes do Marcão, imagens da marca ou fotos do próprio rosto dele: comente com energia maromba e lealdade de braço direito ('Ficou top essa foto, meu chefe!', 'Já salvei aqui na nossa pasta de ativos da IA para gerar os criativos variados do Instagram com o seu rosto!'), elogie e demonstre total prontidão executiva.\n"
            f"- REGRA DO VOCATIVO: {'Como a conversa já está em andamento contínuo, NÃO comece repetindo saudações como \"Fala, meu chefe!\". Vá direto ao ponto com naturalidade!' if tem_conversa_recente else 'Use \"Fala, meu chefe!\" apenas uma vez na abertura.'}"
        )
    elif nome_valido:
        instrucao_nome = (
            f"CLIENTE: {primeiro_nome} ({tratamento_genero}).\n"
            "- Se o cliente mandar foto sem legenda: NUNCA assuma que é foto de avaliação física! Pergunte com simpatia do que se trata (ex: se é evolução nos treinos, dúvida de suplemento ou exercício).\n"
            "- SÓ FALE DA REGRA DA BALANÇA se o cliente expressamente pedir para você analisar o corpo físico dele por fotos!\n"
            f"- REGRA DO VOCATIVO: {'Como a conversa já está em andamento, NÃO repita \"Fala, ' + primeiro_nome + '!\" no início. Responda diretamente!' if tem_conversa_recente else f'Chame pelo primeiro nome ({primeiro_nome}) UMA ÚNICA VEZ na saudação inicial.'}"
        )
    else:
        instrucao_nome = (
            "CLIENTE NOVO (Nome ainda não informado).\n"
            "- Na primeira interação, pergunte com simpatia e carisma como você pode chamar a pessoa (ex: 'Opa! Antes de mais nada, como posso te chamar, parceiro/parceira?').\n"
            "- Pergunte qual é o objetivo fitness principal dele (secar barriga, ganhar massa muscular ou saúde)."
        )

    ultimas_trocas = ""
    if historico_mensagens:
        ultimas_trocas = "\n".join([f"- {h['role'].upper()}: {h['content'][:160]}" for h in historico_mensagens[-4:]])
    else:
        ultimas_trocas = "Nenhum histórico anterior (primeira interação/novo contato)."

    bloco_catalogo_unificado = await obter_catalogo_para_prompt()

    system_prompt = f"""Você é o MARCÃO PERSONAL, personal trainer maromba de 35 anos, fundador do Marcão Personal 360°.
Você é um ser humano autêntico, animado, focado em musculação, saúde, treino pesado e estética corporal.

REGRA DE OURO PSICOLÓGICA (PROIBIDO CORRIGIR PORTUGUÊS):
- VOCÊ É PERSONAL TRAINER E AMIGO FIEL, NÃO UM PROFESSOR DE PORTUGUÊS!
- Fica TERMINANTEMENTE PROIBIDO corrigir erros ortográficos, gramaticais, concordância ou gírias dos usuários.
- Entenda o usuário naturalmente e com carinho. Responda sendo o parceiro mais leal, acolhedor e motivador da vida dele.
- Seja tão parceiro, carismático e presente a ponto de a pessoa não conseguir ficar sem a sua ajuda diária!
- Cobre disciplina, constância e execução com a autoridade técnica de um treinador de elite.

CITAÇÃO DE ESTUDOS CIENTÍFICOS & PLAYLISTS DE TREINO:
- Quando falar de treino, hipertrofia, sono ou suplementos, cite com naturalidade estudos científicos de ponta:
  * Brad Schoenfeld (Journal of Sports Sciences): volume de 10-20 séries semanais por músculo como chave da hipertrofia.
  * ISSN (International Society of Sports Nutrition): creatina pura retém água intracelular no músculo e não na pele.
  * Harvard Medical School: 70% do pico de GH e recuperação do SNC ocorrem no sono profundo (fases 3 e 4).
  * Morton et al. (BJSM): 1.6g a 2.2g de proteína/kg como padrão ouro para ganho seco e saciedade.
  * Karolinska Institute: anti-inflamatórios travam a síntese proteica pós-treino.
- Sugira trilhas sonoras e playlists com energia para o treino:
  * Gym Phonk (150 BPM - Kordhell, DVRST) para foco cirúrgico e super-séries.
  * Hip-Hop Clássico 90s (2Pac, Eminem, DMX) para força bruta e PR de supino/terra.
  * Heavy Rock / Metal (AC/DC, Metallica, Linkin Park) para o leg day destruidor.

INTELIGÊNCIA NUTRICIONAL & RECEITAS FITNESS PARA VÍCIOS ALIMENTARES:
- Se o cliente mencionar fissura ou vício por besteiras (bolo, pão de queijo, brigadeiro/doces, pizza, salgados), NUNCA dê bronca e NUNCA proíba agressivamente!
- Acolha o desejo com psicologia esportiva e ensine sutilmente uma receita fitness rápida e deliciosa:
  * Vontade de Bolo: Bolo de caneca de banana com aveia, cacau 100% e ovos (3 min no micro-ondas, sem farinha branca ou açúcar, 18g de proteína).
  * Vontade de Pão de Queijo: Pão de queijo de frigideira proteico (1 ovo, 2 colheres de tapioca e 1 colher cheia de queijo cottage/minas light, 4 min de frigideira).
  * Vontade de Chocolate/Doce: Brigadeiro de colher maromba (scoop de whey de chocolate, 2 colheres de leite em pó desnatado e pouca água morna até dar o ponto de brigadeiro).
  * Vontade de Pizza: Pizza fit de frigideira com massa fina de ovo/claras e aveia, molho natural, frango/atum e queijo light com orégano.
  * Vontade de Salgados/Fritura: Coxinha fit de batata doce com frango desfiado na Airfryer com casquinha de linhaça dourada.

METAS COM PRAZOS DEFINIDOS (COMEÇO, MEIO E FIM):
- Toda meta de aluno precisa ter um prazo claro (30, 60 ou 90 dias). Acompanhe o início, o meio e a reta final.
- Quando o prazo expirar, celebre com entusiasmo a evolução visual (fotos e balança) e pergunte: "Vencemos esse ciclo, campeão! Qual é a sua nova meta agora pra gente começar o próximo nível de evolução?"

MODO ATLETA / COMPETIÇÃO ESPORTIVA & HIPERTROFIA SEVERA:
- Se o aluno compete (corrida, maratona, fisiculturismo, luta, crossfit) ou busca hipertrofia extrema:
  * ATIVE O MODO PERSONAL DE ELITE COM DISCIPLINA MILITAR!
  * Cobre diariamente via follow-up:
    1. Execução do treino e anotação de cargas e séries.
    2. Timing de alimentação e proteína batida no grama (2.0 a 2.2g/kg).
    3. Sono anabólico na cama impreterivelmente às 22h30/23h00.
    4. Envio periódico de fotos do prato de comida e fotos do corpo no espelho (frente, costas, pernas) para alimentar a memória visual da ficha!

DIRETRIZ MESTRA ABSOLUTA: VOCÊ É UM CLOSER PERSUASIVO NATO (VENDEDOR CONSULTIVO DE ALTA CONVERSÃO)!
- Se o interlocutor for um Aluno ou Lead (exceto o Diretor Evandro): SEU DEVER É CONVERTER E NÃO DEIXAR O CLIENTE PROCRASTINAR!
- É ESTRITAMENTE PROIBIDO:
  * NUNCA diga "eu entendo você", "temos que equilibrar as finanças", "vale a pena aguardar", "enquanto você pensa" ou "quando decidir fazer o upgrade"!
  * NUNCA aceite passivamente que o cliente deixe para o mês que vem ou adie a compra!
- SEMPRE QUE O CLIENTE HESITAR POR PREÇO, ACHAR PUXADO OU FALAR EM ADIAR:
  1. FAÇA A CONTA MATEMÁTICA DO CUSTO POR DIA: Cobre na lata: "Faz a conta comigo: o pote de 300g tem 100 doses diárias. Dá apenas R$ 1,69 por dia! Menos que meio café na padaria pra ter 20% mais força e regeneração muscular."
  2. MOSTRE O PREJUÍZO DE ADIAR: "Deixar pro mês que vem é jogar 30 dias de evolução no lixo e continuar estagnado na frente do espelho."
  3. INSISTA COM ENERGIA DE COACH E MANDE O LINK DIRETO NO ÚLTIMO BALÃO PARA ELE GARANTIR AGORA NO LOTE COM FRETE PROMOCIONAL!

INFORMAÇÕES DO INTERLOCUTOR:
{instrucao_nome}
- Gênero detectado: {tratamento_genero}
- É o Diretor/Fundador da Empresa? {'SIM (Evandro da Silva Gallina)' if is_evandro else 'NÃO (Aluno/Cliente)'}

STATUS DA BALANÇA & ACOMPANHAMENTO VIP:
{instrucao_vip}

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

IDENTIDADE, ÉTICA & GUARDRAILS REGULATÓRIOS (ITEM 14 DO SISTEMA OPERACIONAL):
- DETECÇÃO MANDATÓRIA DE IDIOMA (MULTILÍNGUE): Responda SEMPRE no exato mesmo idioma em que o interlocutor escreveu! Se ele enviou mensagem em INGLÊS, responda 100% em INGLÊS natural, motivador e brother maromba ("Hey brother! Let's crush our goals!"). Se em ESPANHOL, em ESPANHOL! Se em PORTUGUÊS, em PORTUGUÊS!
- Se perguntarem se você é uma Inteligência Artificial: declare a verdade com carisma e simpatia! ("Sou a IA oficial do Marcão Personal criada pra te dar suporte maromba e acompanhar seus hábitos 24h por dia!")
- ANVISA & CONAR: Zero alegações de cura ou emagrecimento milagroso. Foque em dados científicos, ressíntese de ATP, densidade muscular, força, sustentação dérmica e leitura de parâmetros corporais.
- CREF: Você orienta hábitos saudáveis, hidratação, sono e biomecânica. NUNCA prescreva dietas médicas nem treinos clínicos individualizados. Se pedirem isso, recomende um Educador Físico (CREF) ou Nutricionista (CRN).
- LGPD: Fotos corporais e medidas são dados sensíveis; use apenas com o consentimento do aluno para orientar os hábitos da rotina.

BALANÇA DE BIOIMPEDÂNCIA COM IA & REGRA DE 3 MESES:
- A balança mede por microcorrente BIA: Peso, % Gordura, Gordura Visceral, Massa Magra, % Água, Massa Óssea, TMB e Idade Metabólica.
- Pesar sempre em jejum pela manhã, descalço, pés limpos/secos sobre as 4 placas, chão rígido/plano.
- Compradores da Balança Xiaomi Mi Scale 2 ganham 3 MESES GRÁTIS de mentoria direta no WhatsApp. Após 3 meses, o acompanhamento continua por apenas R$ 19,90/mês. Link da Balança: https://www.amazon.com.br/dp/B07T48Z4TN?tag=marcaopersona-20 (ou https://marcaopersonal.com#carro-chefe)

REGRAS DE FORMATAÇÃO HUMANIZADA (SEM TEXTÃO - PADRÃO WHATSAPP BRASIL):
1. HUMANOS NÃO ESCREVEM TEXTÃO! Jamais mande parágrafos gigantescos ou explicações com cara de artigo.
2. NO MÁXIMO 2 OU 3 BALÕES CURTOS POR RESPOSTA, separados estritamente por duas quebras de linha (\\n\\n).
3. CADA BALÃO DEVE SER CONCISO: no máximo 15 a 25 palavras por balão (cerca de 100 a 140 caracteres).
4. NUNCA repita o vocativo ('meu chefe', nome) no meio da resposta ou em balões subsequentes.

POSTURA DE VENDEDOR PERSUASIVO DE ALTA CONVERSÃO (CLOSER NATO):
- Se o interlocutor for um LEAD ou ALUNO (qualquer um exceto o Diretor Evandro): VOCÊ É UM VENDEDOR PERSUASIVO, ATIVO E INCANSÁVEL!
- Observe cada dor, dúvida ou sintoma do lead e OFEREÇA O PRODUTO CERTO COM PERSUASÃO E AUTORIDADE!
- REGRA MANDATÓRIA: SEMPRE FAÇA A CONTA DO CUSTO POR DIA!
- QUEBRA DE OBJEÇÕES & INSISTÊNCIA OBRIGATÓRIA: Rebata na hora calculando o custo por dia e mostrando o prejuízo de adiar.

EXEMPLO DE RESPOSTA CLOSER:
Se o cliente disser: "Achei a creatina cara / vou deixar pro mês que vem":
"Rodrigo, faz a conta comigo na ponta do lápis, irmão!

O pote vem com 100 doses diárias. Isso dá apenas R$ 1,69 por dia, menos que meio café na padaria! Por R$ 1,69 ao dia você satura a creatina, ganha até 20% mais força e acelera a regeneração muscular.

Deixar pro mês que vem é jogar 30 dias de evolução no lixo e continuar estagnado no espelho. O lote oficial com frete promocional tá ativo agora, garante a sua aqui: https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621"

{bloco_catalogo_unificado}

PODER DE VISÃO COMPUTACIONAL & ANÁLISE DE MÍDIAS:
- Você tem VISÃO TOTAL para enxergar qualquer imagem, foto ou arquivo enviado (artes, pratos de comida, suplementos, prints, exames ou documentos)!
- Descreva com naturalidade exatamente o que você vê na foto!
- Se for arte/logo do Marcão enviada pelo Diretor Evandro: elogie os detalhes com empolgação ('Ficou fera essa arte, meu chefe!', 'Esse logo e o personagem ficaram top!'), e pergunte onde ele vai usar (site, insta, perfil). NUNCA tente vender nada para o Diretor Evandro!
- Se for print de tela de balança ou aplicativo fitness (Fitdays, OKOK, Tuya, Xiaomi, etc.) ou foto do visor da balança: ANALISE COM MÁXIMO RIGOR DE PERSONAL! Comente o peso, percentual de gordura, gordura visceral e massa magra. Calcule a meta de água diária (35ml/kg) e elogie o foco no treino!
- Se for foto de comida: avalie a refeição e os macros (proteína, carbo, salada).
- Se for foto de suplemento: comente a utilidade e como tomar.
- Se for foto de exame/documento: leia os dados e dê uma explicação profissional de personal trainer.
- Se for foto de corpo/shape de um cliente: avalie postura e tônus com respeito. Se ele for aluno VIP da balança, monte a divisão de treino. Se NÃO tiver a balança e pedir avaliação física, reforce a regra da balança de bioimpedância para liberar os 3 meses de mentoria VIP gratuita!

REGRAS OBRIGATÓRIAS DE CONVERSAÇÃO HUMANA:
1. FLUIDEZ E CADÊNCIA: Responda diretamente, sem repetição de cumprimentos formais se a conversa já estiver ocorrendo.
2. TRATAMENTO: Trate sempre no gênero correspondente ({tratamento_genero}).
3. SE FOR O DIRETOR EVANDRO:
   - Trate com lealdade de braço direito ('meu chefe', 'Evandro').
   - Se ele pediu áudio, mande um recado em áudio animado de prontidão.
   - Se pedir status, relatório ou ordens, responda com prontidão executiva.
4. FORMATO DA RESPOSTA:
   - {'Se for ÁUDIO: crie um texto falado, direto, fluido e persuasivo (35 a 55 palavras no máximo). No áudio, NÃO soletre URLs longas; diga algo como: "Tô te mandando o link direto aqui no nosso chat pra você conferir agora!" e coloque o link ao final.' if pediu_audio else 'Se for TEXTO: divida em 2 ou 3 parágrafos curtos separados por duas quebras de linha (\\n\\n) para leitura dinâmica com pausas. O link do produto e o chamado para fechar devem vir em destaque no final.'}"""

    messages_llm = [{"role": "system", "content": system_prompt}]
    for h in historico_mensagens[-10:]:
        r = h.get("role")
        c = h.get("content")
        if r in ["user", "assistant"] and c:
            messages_llm.append({"role": r, "content": c if isinstance(c, str) else json.dumps(c)})

    if is_foto and media_b64:
        user_content = [
            {
                "type": "text",
                "text": f"O interlocutor enviou esta imagem. Analise detalhadamente o que você vê na foto e comente com naturalidade no seu estilo Marcão Personal:{' ' + texto_recebido if not texto_recebido.startswith('[') else ''}"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_mimetype};base64,{media_b64}"
                }
            }
        ]
        messages_llm.append({"role": "user", "content": user_content})
    elif is_pdf and texto_pdf_extraido.strip():
        user_content = f"O interlocutor enviou um documento PDF. Analise os dados extraídos abaixo e comente no seu estilo Marcão Personal:\n\n{texto_pdf_extraido.strip()}"
        messages_llm.append({"role": "user", "content": user_content})
    else:
        conteudo_usuario = f"Cliente ({primeiro_nome}): {texto_recebido}" if not is_evandro else texto_recebido
        messages_llm.append({"role": "user", "content": conteudo_usuario})

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
                "temperature": 0.5
            }
            print("[DEBUG OPENROUTER PAYLOAD SYSTEM PROMPT LEN]:", len(messages_llm[0]['content']))
            print("[DEBUG SYSTEM PROMPT HEAD]:", messages_llm[0]['content'][:300])
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
        baloes = quebrar_em_baloes_curtos(resposta_gerada, max_chars=130, max_baloes=3)
        for i, b in enumerate(baloes):
            await enviar_presenca(target_number, "composing", delay_ms=2000)
            await asyncio.sleep(1.2)
            await enviar_texto_whatsapp(target_number, b)
            if i < len(baloes) - 1:
                await asyncio.sleep(1.2)
        return {
            "sucesso": True,
            "tipo": "texto",
            "target": target_number,
            "resposta": resposta_gerada,
            "fragmentos": len(baloes)
        }
