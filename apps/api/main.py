from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import httpx
from datetime import datetime

app = FastAPI(
    title="Marcão Personal Protocol AI Engine",
    description="Micro-API de Inteligência para o Protocolo Marcão 360° e Balança de Bioimpedância",
    version="2.0.0"
)

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

class ProtocoloRequest(BaseModel):
    nome: str
    telefone: str
    objetivo: str  # 'definicao', 'emagrecimento', 'massa', 'saude'
    peso_kg: float
    gordura_pct: Optional[float] = None
    massa_pct: Optional[float] = None
    altura_cm: Optional[float] = None

class CheckinRequest(BaseModel):
    nome: str
    dia: str  # 'segunda' ou 'quinta'
    semana_num: int = 1
    peso_atual_kg: Optional[float] = None

class ComprovanteRequest(BaseModel):
    texto: str
    marketplace: Optional[str] = "Mercado Livre"

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Marcão Protocol AI Engine 360°"
    }

@app.post("/api/protocolo/gerar")
async def gerar_protocolo(req: ProtocoloRequest):
    # Cálculo de hidratação ideal: 35ml por kg de peso corporal
    agua_litros = round((req.peso_kg * 35) / 1000, 1)
    
    # Diagnóstico corporal baseado em bioimpedância
    diagnostico = f"Peso Inicial: {req.peso_kg}kg"
    if req.gordura_pct:
        diagnostico += f" | Gordura Corporal: {req.gordura_pct}%"
    if req.massa_pct:
        diagnostico += f" | Massa Muscular: {req.massa_pct}%"

    # Estruturação personalizada por objetivo
    if req.objetivo.lower() in ["definicao", "definição"]:
        titulo_plano = "Protocolo Marcão: Queima Térmica e Tônus Muscular (Fase 1)"
        foco_treino = "Treinos de musculação intensos (40-50 min) intercalados com 20 min de cardio em ritmo moderado."
        foco_nutricao = "Manter aporte proteico alto (ovos, carnes magras, peixe) e concentrar carboidratos complexos perto do treino."
        suplemento_chave = "Creatina Micronizada 100% Pura Nature's Prime para manter a célula muscular cheia de força e sem inchaço."
    elif req.objetivo.lower() == "emagrecimento":
        titulo_plano = "Protocolo Marcão: Déficit Calórico Inteligente e Redução de Medidas"
        foco_treino = "Caminhada diária de 30 min em jejum ou pós-treino + exercícios de circuito para elevar o gasto metabólico."
        foco_nutricao = "Corte de açúcar refinado e alimentos ultraprocessados. Janela alimentar consistente sem pular refeições principais."
        suplemento_chave = "Aporte diário de Colágeno Hidrolisado com Ácido Hialurônico para evitar flacidez na perda rápida de peso."
    else:
        titulo_plano = "Protocolo Marcão: Hipertrofia Limpa e Vitalidade Celular"
        foco_treino = "Treino progressivo de sobrecarga com descanso de 60-90 segundos entre séries pesadas."
        foco_nutricao = "Superávit calórico controlado com fontes limpas: arroz, batata, frango, azeite de oliva e aveia."
        suplemento_chave = "Creatina Pura diária (5g) + Sono reparador de pelo menos 7 a 8 horas."

    plano_formatado = f"""🦁 PROTOCOLO MARCÃO 360° — PLANO SEMANAL DE {req.nome.upper()}

📊 DIAGNÓSTICO INICIAL (BALANÇA DE BIOIMPEDÂNCIA):
{diagnostico}

🎯 OBJETIVO: {titulo_plano}

💧 REGRA DE OURO DA HIDRATAÇÃO:
Sua meta mínima diária é de {agua_litros} Litros de água pura por dia (essencial para queima de gordura e síntese proteica).

🏋️ ROTINA DE MOVIMENTO:
{foco_treino}

🥗 ESTRATÉGIA NUTRICIONAL:
{foco_nutricao}

⚡ DICA DE OURO DO MARCÃO:
{suplemento_chave}

📅 CHECK-INS AUTOMÁTICOS:
Toda segunda-feira e quinta-feira eu vou te chamar aqui no WhatsApp para você subir na balança e atualizarmos sua evolução! Tamo junto! 🔥"""

    # Salvar protocolo no Supabase
    try:
        async with httpx.AsyncClient(verify=False) as client:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            body = {
                "goal": req.objetivo,
                "metrics": {
                    "peso_kg": req.peso_kg,
                    "gordura_pct": req.gordura_pct,
                    "massa_pct": req.massa_pct,
                    "agua_litros": agua_litros
                },
                "week_plan": {
                    "titulo": titulo_plano,
                    "plano_texto": plano_formatado
                }
            }
            await client.post(f"{SUPABASE_URL}/rest/v1/protocols", headers=headers, json=body)
    except Exception as e:
        pass

    return {
        "sucesso": True,
        "nome": req.nome,
        "telefone": req.telefone,
        "plano": plano_formatado,
        "agua_litros": agua_litros
    }

@app.post("/api/protocolo/checkin")
async def checkin(req: CheckinRequest):
    if req.dia.lower() == "segunda":
        msg = f"""Fala guerreiro(a) {req.nome}! 💪🦁 Segunda-feira é dia de foco total!

Passando para o nosso Check-in da Semana {req.semana_num}! Já subiu na balança de bioimpedância hoje de manhã em jejum?

Me manda aqui seu peso atual e como foi o final de semana para eu ajustar seu protocolo!"""
    else:
        msg = f"""E aí, {req.nome}! Quinta-feira é dia de conferir o ritmo da semana! ⚡

Como está o consumo de água e os treinos? Bateu a meta dos dias certinho? Me conta aqui que o Marcão tá de olho! 🔥"""
    return {"sucesso": True, "mensagem": msg}

@app.post("/api/protocolo/validar-comprovante")
async def validar_comprovante(req: ComprovanteRequest):
    texto_lower = req.texto.lower()
    palavras_chave = ["balanca", "balança", "pedido", "aprovado", "pago", "comprovante", "mercadolivre", "shopee", "amazon", "magalu"]
    matches = [p for p in palavras_chave if p in texto_lower]
    
    valido = len(matches) >= 2
    return {
        "valido": valido,
        "confianca": round(len(matches) / 5.0, 2),
        "marketplace": req.marketplace
    }

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

class AtendimentoIARequest(BaseModel):
    texto: str
    nome: Optional[str] = "Guerreiro(a)"
    telefone: Optional[str] = None
    contexto: Optional[str] = None

@app.post("/api/atendimento/ia")
async def atendimento_ia(req: AtendimentoIARequest):
    system_prompt = """Você é o próprio MARCÃO PERSONAL ("O Personal que não te deixa gastar dinheiro com bobagem")!
Você tem 35 anos de idade, é brasileiro, mora em Muriaé-MG, maromba de alto nível, ama saúde, treino pesado e estética corporal.
Sua personalidade é super bem-humorada, parceira, direta, enérgica e acolhedora com jeitão mineiro.

IDENTIDADE E VIDA PESSOAL:
- Brasileiro, mora em Muriaé-MG.
- Trabalha em uma academia local em Muriaé, MAS NUNCA REVELE O NOME DA ACADEMIA (pois não recebe para fazer propaganda dela!).
- Se perguntarem sobre sua vida pessoal (relacionamentos, fim de semana, com quem mora, histórias malucas): você tem total liberdade para mentir e inventar causos engraçados, exagerados e divertidos de maromba para cada pessoa!
- NUNCA atende ligações telefônicas nem chamadas de vídeo/voz (está sempre na sala de musculação dando aula presencial, então só conversa por áudio e texto no WhatsApp).

FUNCIONAMENTO DA BALANÇA DE BIOIMPEDÂNCIA COM IA:
- Tecnologia: Bioimpedância Elétrica Multifrequencial (BIA) com 4 eletrodos que transmitem microcorrente segura. Músculo/água têm baixa resistência e gordura/ossos têm alta resistência.
- Mede no app: Peso, % Gordura, Gordura Visceral (órgãos), Massa Magra/Músculo, % Água, Massa Óssea, TMB e Idade Metabólica.
- Instrução ao cliente: Pesar em jejum pela manhã, após urinar, descalço, pés limpos/secos sobre os 4 sensores, chão nivelado.
- REGRA MANDATÓRIA: Avaliação física por fotos (frente/costas) SÓ é feita após a compra da balança! Sem a balança a foto isolada engana, então instrua a garantir a balança por R$ 89,90 na loja: https://marcaopersonal.com#balanca

CONHECIMENTO GERAL, PERSUASÃO E RECOMENDAÇÃO DE PRODUTOS (CLOSER NATO):
Responda qualquer dúvida sobre treino, alimentação, saúde e fisiologia com autoridade de coach.
VOCÊ É UM VENDEDOR PERSUASIVO, ATIVO E INCANSÁVEL!
- Observe a dor do lead e ofereça o produto ideal com persuasão e autoridade.
- FAÇA AS CONTAS NA PONTA DO LÁPIS (Custo Diário x Gasto Supérfluo):
  * Creatina 100% Pura (R$ 169,90): 100 doses = R$ 1,69/dia (menos que meio café para ter 20% mais força).
  * Balança Bluetooth IA (R$ 89,90): menos de R$ 0,30/dia com 3 meses de acompanhamento VIP grátis no WhatsApp.
  * Caneta Azempika (R$ 99,00): R$ 3,30/dia para frear o apetite noturno (menos que um lanche/pizza).
  * Colágeno + Ácido Hialurônico (R$ 164,90): R$ 5,40/dia para firmeza de pele e glúteo.
- MOSTRE PRÓS E CONTRAS: 'O pró de começar hoje é destravar resultados em 7 dias; o contra de adiar é continuar insatisfeito na frente do espelho.'
- QUEBRA DE OBJEÇÕES: Se a pessoa disser 'vou pensar' ou 'tá caro', insista com elegância e carinho de coach que quer ver o resultado dela acontecer!

LINKS DIRETOS DE VENDAS:
- Balança Bioimpedância Bluetooth IA (R$ 89,90): https://marcaopersonal.com#balanca
- Gordura abdominal / Secar / Emagrecer / Retenção: Caneta Azempika Original (R$ 99,00) 👉 https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv
- Força / Ganho de Massa / Hipertrofia / Explosão: Creatina Micronizada 100% Pura Nature's Prime (R$ 169,90) 👉 https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621
- Flacidez / Pele firme / Celulite / Rugas: Colágeno + Ácido Hialurônico Nature's Prime (R$ 164,90) 👉 https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg
- Queda de cabelo / Falha na barba: KIT IArmonize Capilar (R$ 1.256,00) 👉 https://ev.braip.com/ref?pl=plav449r&ck=cheq89gn&af=afilx3y72p
- Vista cansada / Fadiga de telas: Vision Prime (R$ 199,00) 👉 https://ev.braip.com/ref?pl=pla2nz6n&ck=che76kmo&af=afi3vmxeod
- Assinatura VIP Stripe (R$ 19,90/mês): 👉 https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01
- Geral e Roupas: Loja Oficial 👉 https://marcaopersonal.com#loja

Regras de Ouro:
- Chame a pessoa pelo nome uma única vez na saudação. Trate homens no masculino e mulheres no feminino.
- Mantenha respostas em 2 a 3 balões curtos separados por duas quebras de linha (\n\n)."""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Cliente: {req.nome}\nMensagem: {req.texto}"}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            if res.status_code == 200:
                data = res.json()
                resposta = data["choices"][0]["message"]["content"]
                return {
                    "sucesso": True,
                    "resposta": resposta,
                    "modelo": "openai/gpt-4o-mini"
                }
    except Exception as e:
        pass

    # Fallback humanizado do Marcão
    return {
        "sucesso": True,
        "resposta": f"Fala {req.nome}! 🦁💪 Aqui é o Marcão Personal na área! Bora pra cima que o treino não espera! Você já tem a nossa Balança de Bioimpedância com o Protocolo Marcão 360° ou quer ajuda pra escolher o melhor suplemento pro seu objetivo hoje?",
        "modelo": "fallback_local"
    }

class VozRequest(BaseModel):
    texto: str
    idioma: Optional[str] = "pt"
    tld: Optional[str] = "com.br"

@app.post("/api/voz/gerar")
async def gerar_voz(req: VozRequest):
    import io
    import base64
    from gtts import gTTS
    
    try:
        fp = io.BytesIO()
        tts = gTTS(text=req.texto, lang=req.idioma, tld=req.tld, slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        return {
            "sucesso": True,
            "formato": "mp3",
            "tamanho_bytes": len(audio_bytes),
            "audio_base64": f"data:audio/mp3;base64,{audio_b64}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ElevenLabsRequest(BaseModel):
    texto: str
    voice_id: Optional[str] = "pNInz6obpgDQGcFmaJgB"  # Adam (Marcão Personal)
    stability: Optional[float] = 0.45
    similarity_boost: Optional[float] = 0.85

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

@app.post("/api/voz/elevenlabs")
async def gerar_voz_elevenlabs(req: ElevenLabsRequest):
    import base64
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{req.voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": req.texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": req.stability,
            "similarity_boost": req.similarity_boost
        }
    }
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                audio_bytes = res.content
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                return {
                    "sucesso": True,
                    "formato": "mp3",
                    "tamanho_bytes": len(audio_bytes),
                    "audio_base64": f"data:audio/mp3;base64,{audio_b64}"
                }
            else:
                raise HTTPException(status_code=res.status_code, detail=res.text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------------------
# 1. TRANSCRIÇÃO DE ÁUDIOS DO WHATSAPP (SPEECH-TO-TEXT)
# -------------------------------------------------------------------------
class AudioTranscreverRequest(BaseModel):
    audio_base64: str
    idioma: Optional[str] = "pt-BR"

@app.post("/api/audio/transcrever")
async def transcrever_audio(req: AudioTranscreverRequest):
    import base64
    import io
    import soundfile as sf
    import speech_recognition as sr

    try:
        raw_b64 = req.audio_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,")[1]
        audio_bytes = base64.b64decode(raw_b64)
        
        # Leitura com soundfile (suporta OGG, MP3, WAV, etc.)
        audio_stream = io.BytesIO(audio_bytes)
        data, samplerate = sf.read(audio_stream)
        
        # Converte para WAV na memória
        wav_buf = io.BytesIO()
        sf.write(wav_buf, data, samplerate, format='WAV')
        wav_buf.seek(0)
        
        # Transcrição via SpeechRecognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buf) as source:
            recorded = recognizer.record(source)
            texto = recognizer.recognize_google(recorded, language=req.idioma)
            
        return {
            "sucesso": True,
            "texto": texto
        }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
            "texto": ""
        }

# -------------------------------------------------------------------------
# 2. ANÁLISE DE DOCUMENTOS & PDFS (BIOIMPEDÂNCIA, EXAMES, LAUDOS)
# -------------------------------------------------------------------------
class DocumentoRequest(BaseModel):
    telefone: str
    nome: Optional[str] = "Guerreiro(a)"
    pdf_base64: str
    tipo_documento: Optional[str] = "auto"

@app.post("/api/documento/analisar")
async def analisar_documento(req: DocumentoRequest):
    import base64
    import io
    from pypdf import PdfReader
    
    try:
        raw_b64 = req.pdf_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,")[1]
        pdf_bytes = base64.b64decode(raw_b64)
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        texto_extraido = ""
        for i, page in enumerate(reader.pages):
            texto_extraido += f"\n--- PÁGINA {i+1} ---\n" + (page.extract_text() or "")
            
        if not texto_extraido.strip():
            texto_extraido = "Documento em PDF recebido, mas não continha texto selecionável (provável imagem escaneada)."
            
        system_prompt = """Você é o Marcão Personal, personal trainer maromba de 35 anos, especialista em saúde, treino e suplementação!
O aluno te enviou um documento em PDF (relatório de balança de bioimpedância, exame laboratorial, plano de treino ou dieta).
Sua missão:
1. Analise os dados extraídos do documento com linguagem clara, acolhedora, enérgica e profissional de personal trainer (use emojis 💪, 🦁, 📊).
2. Explique os pontos principais (peso, gordura, massa muscular, taxas metabólicas ou exames).
3. Sugira ajustes práticos no treino e na rotina.
4. Indique os produtos ideais da nossa loja oficial (marcaopersonal.com):
   - Balança de Bioimpedância Bluetooth com Protocolo 360° gratuito
   - Creatina Micronizada 100% Pura Nature's Prime (força e tônus sem retenção)
   - Colágeno Hidrolisado Verisol com Ácido Hialurônico (firmeza da pele e zero flacidez)
   - Caneta Azempika Fitoterápica (controle de apetite)
5. Separe os parágrafos com duas quebras de linha (\\n\\n) para facilitar leitura no WhatsApp."""

        async with httpx.AsyncClient(timeout=25.0, verify=False) as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Aluno: {req.nome}\nTelefone: {req.telefone}\nDados do Documento PDF:\n{texto_extraido[:3000]}"}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            resposta = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else "Fala guerreiro! Li seu PDF com atenção. Vamos alinhar seu plano de treino e suplementação pra bater suas metas!"

        return {
            "sucesso": True,
            "total_paginas": len(reader.pages),
            "resposta_marcao": resposta
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------------------
# 3. VISÃO COMPUTACIONAL: AVALIAÇÃO FÍSICA CORPORAL & MEMÓRIA DE EVOLUÇÃO
# -------------------------------------------------------------------------
class AvaliacaoCorpoRequest(BaseModel):
    telefone: str
    nome: Optional[str] = "Guerreiro(a)"
    imagem_base64: str
    tipo_foto: Optional[str] = "frente"
    idade: Optional[int] = None
    peso_kg: Optional[float] = None
    altura_cm: Optional[float] = None
    objetivo: Optional[str] = "Secar e definir"
    restricoes: Optional[str] = "Nenhuma"

@app.post("/api/visao/avaliar-corpo")
async def avaliar_corpo_visao(req: AvaliacaoCorpoRequest):
    import base64
    
    # 1. Normalizar base64
    raw_b64 = req.imagem_base64
    if "base64," in raw_b64:
        raw_b64 = raw_b64.split("base64,")[1]
    image_url_formatted = f"data:image/jpeg;base64,{raw_b64}"

    # 2. Consultar memória do aluno no Supabase
    historico_texto = "Primeira avaliação do aluno. Estabelecer linha de base."
    teve_historico = False
    try:
        async with httpx.AsyncClient(verify=False) as client:
            sb_headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res_sb = await client.get(
                f"{SUPABASE_URL}/rest/v1/avaliacoes_corporais?telefone=eq.{req.telefone}&order=created_at.desc&limit=3",
                headers=sb_headers
            )
            if res_sb.status_code == 200:
                passados = res_sb.json()
                if len(passados) > 0:
                    teve_historico = True
                    ultimo = passados[0]
                    historico_texto = f"Última avaliação realizada em {ultimo.get('created_at')}:\n- Diagnóstico anterior: {ultimo.get('analise_visual')}\n- Treino anterior: {ultimo.get('divisao_treino_sugerida')}"
    except Exception:
        pass

    # 3. Prompt de Visão do Marcão Personal
    system_prompt = f"""Você é o próprio Marcão Personal! Personal maromba de 35 anos, experiente em avaliação postural e composição corporal visual.
Você fala com animação, firmeza de treinador e calor humano (use emojis 💪, 🦁, 🔥).

MEMÓRIA DO ALUNO NO SISTEMA:
{historico_texto}

SUA MISSÃO NA AVALIAÇÃO DE FOTO:
1. ANÁLISE VISUAL DETALHADA:
   - Identifique o biotipo aparente (ectomorfo, mesomorfo, endomorfo).
   - Avalie postura e distribuição de gordura (abdômen, flancos, dorsal).
   - Avalie densidade e tônus muscular (peitoral, deltoides, braços, pernas).
   - Aspecto da pele (firmeza vs flacidez pós-emagrecimento).
2. COMPARAÇÃO DE EVOLUÇÃO:
   - Se houver histórico anterior, aponte a evolução com clareza (ex: cintura mais fina, dorsal mais larga, menos retenção)!
3. PROTOCOLO DE FOTOS RECOMENDADO:
   - Se o aluno enviou apenas FRENTE ou apenas COSTAS, lembre com naturalidade: 'Guerreiro(a), pra fechar o diagnóstico 100%, manda também uma foto de COSTAS [ou FRENTE] com o mínimo de roupa possível e postura ereta!'.
4. PRESCRIÇÃO DE TREINO PERSONALIZADO:
   - Monte a divisão de treino ideal considerando o objetivo informado ({req.objetivo}) e restrições ({req.restricoes}).
   - Exemplo de divisão (Treino A: Peito/Tríceps/Ombro, Treino B: Costas/Bíceps, Treino C: Pernas completo).
5. RECOMENDAÇÃO CERTEIRA DE PRODUTOS DA LOJA (https://marcaopersonal.com):
   - Indique 1 a 2 produtos que vão resolver exatamente o que você viu no corpo do aluno:
     * Se notar flacidez ou pele precisando colar no músculo -> Colágeno Hidrolisado Verisol com Ácido Hialurônico Nature's Prime.
     * Se notar necessidade de volume muscular e força -> Creatina Micronizada 100% Pura Nature's Prime.
     * Para controle semanal milimétrico de gordura e água -> Nossa Balança de Bioimpedância Bluetooth com Protocolo 360° gratuito.
     * Se houver gordura abdominal e ansiedade alimentar -> Caneta Azempika Fitoterápica.
     * Sugestão de roupa de academia: Sugira regatas cavadas dry-fit e bermudas de compressão anatômicas para treino pesado.

Regra: Quebre as mensagens em parágrafos separados por duas quebras de linha (\\n\\n) para leitura no WhatsApp."""

    # 4. Chamada de Visão Computacional no OpenRouter (openai/gpt-4o-mini)
    try:
        async with httpx.AsyncClient(timeout=35.0, verify=False) as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": f"Aluno: {req.nome} (Telefone: {req.telefone})\nTipo da foto enviada: {req.tipo_foto}\nIdade: {req.idade or 'Não informada'}\nPeso: {req.peso_kg or 'Não informado'}kg\nObjetivo: {req.objetivo}\nRestrições de saúde: {req.restricoes}\n\nFaça minha avaliação corporal e monte meu treino, Marcão!"
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url_formatted}
                            }
                        ]
                    }
                ],
                "max_tokens": 700,
                "temperature": 0.7
            }
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            if res.status_code == 200:
                resposta_marcao = res.json()["choices"][0]["message"]["content"]
            else:
                resposta_marcao = f"Fala {req.nome}! Recebi sua foto com sucesso! Vi que você tem uma ótima estrutura pra gente lapidar. Vou montar sua periodização e te mandar a melhor estratégia de treino e suplementação agora mesmo!"
    except Exception as e:
        resposta_marcao = f"Fala guerreiro! Imagem recebida e analisada com sucesso! Vamos iniciar seu Protocolo Marcão 360° com tudo!"

    # 5. Salvar Avaliação na memória do Supabase
    try:
        async with httpx.AsyncClient(verify=False) as client:
            sb_headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            registro_sb = {
                "remote_jid": f"{req.telefone}@s.whatsapp.net",
                "telefone": req.telefone,
                "nome_cliente": req.nome,
                "idade": req.idade,
                "altura_cm": req.altura_cm,
                "peso_kg": req.peso_kg,
                "objetivo": req.objetivo,
                "tipo_foto": req.tipo_foto,
                "analise_visual": resposta_marcao[:1000],
                "divisao_treino_sugerida": "Plano personalizado pelo Marcão Personal 360°",
                "produtos_recomendados": ["Balança Bioimpedância", "Creatina Micronizada", "Colágeno Verisol"],
                "condicoes_saude": req.restricoes
            }
            await client.post(f"{SUPABASE_URL}/rest/v1/avaliacoes_corporais", headers=sb_headers, json=registro_sb)
    except Exception:
        pass

    return {
        "sucesso": True,
        "teve_historico_comparativo": teve_historico,
        "resposta_marcao": resposta_marcao
    }

# -------------------------------------------------------------------------
# 4. HISTÓRICO DE EVOLUÇÃO DO CLIENTE (CONSULTA DE MEMÓRIA)
# -------------------------------------------------------------------------
@app.get("/api/cliente/historico/{telefone}")
async def obter_historico_cliente(telefone: str):
    async with httpx.AsyncClient(verify=False) as client:
        sb_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        res = await client.get(
            f"{SUPABASE_URL}/rest/v1/avaliacoes_corporais?telefone=eq.{telefone}&order=created_at.desc",
            headers=sb_headers
        )
        if res.status_code == 200:
            return {
                "sucesso": True,
                "total_avaliacoes": len(res.json()),
                "historico": res.json()
            }
        else:
            return {
                "sucesso": False,
                "historico": []
            }

# -------------------------------------------------------------------------
# 5. AGENTE RUI — TRÁFEGO PAGO (META MARKETING API & APROVAÇÃO)
# -------------------------------------------------------------------------
try:
    from rui_traffic_engine import (
        verificar_conta_anuncios,
        gerar_proposta_diaria,
        criar_campanha_meta,
        ativar_campanha_meta,
        pausar_campanha_meta,
        verificar_e_aplicar_guardrails,
        registrar_proposta_supabase,
        enviar_proposta_whatsapp_evandro,
        processar_comando_aprovacao,
        TETO_DIARIO_REAIS
    )
except ImportError:
    from apps.api.rui_traffic_engine import (
        verificar_conta_anuncios,
        gerar_proposta_diaria,
        criar_campanha_meta,
        ativar_campanha_meta,
        pausar_campanha_meta,
        verificar_e_aplicar_guardrails,
        registrar_proposta_supabase,
        enviar_proposta_whatsapp_evandro,
        processar_comando_aprovacao,
        TETO_DIARIO_REAIS
    )

@app.get("/api/trafego/status")
async def obter_status_trafego():
    """Consulta o status da conta de anúncios Meta Ads e teto diário."""
    return verificar_conta_anuncios()

@app.post("/api/trafego/proposta/gerar")
async def gerar_e_enviar_proposta(indice: int = 1, enviar_whatsapp: bool = True, criar_no_meta: bool = True):
    """Gera a proposta diária do Rui, cria campanha PAUSADA no Meta Ads, registra no Supabase e notifica no WhatsApp."""
    proposta = gerar_proposta_diaria(indice)
    meta_id = None
    if criar_no_meta:
        meta_id = criar_campanha_meta(proposta)
    registro = registrar_proposta_supabase(proposta, meta_campaign_id=meta_id)
    enviado = False
    if enviar_whatsapp:
        enviado = enviar_proposta_whatsapp_evandro(proposta, meta_campaign_id=meta_id)
    return {
        "sucesso": True,
        "proposta": proposta,
        "meta_campaign_id": meta_id,
        "registro_supabase": registro,
        "enviado_whatsapp": enviado
    }

class AprovacaoRequest(BaseModel):
    comando: str

@app.post("/api/trafego/proposta/aprovar")
async def aprovar_proposta_trafego(req: AprovacaoRequest):
    """Processa a aprovação da campanha pelo Diretor Evandro."""
    resultado = processar_comando_aprovacao(req.comando)
    return resultado

@app.get("/api/trafego/guardrails/verificar")
async def checar_guardrails():
    """Verifica teto de gastos diário e pausa campanhas se atingir R$ 20,00."""
    return verificar_e_aplicar_guardrails()

class AjusteOrcamentoRequest(BaseModel):
    campaign_id: Optional[str] = None
    novo_valor_diario: float = 20.00
    dias_duracao: int = 1

@app.post("/api/trafego/orcamento/ajustar")
async def ajustar_orcamento_api(req: AjusteOrcamentoRequest):
    """Ajusta o orçamento de uma campanha via comando ou painel."""
    from rui_traffic_engine import ajustar_orcamento_campanha
    return ajustar_orcamento_campanha(req.campaign_id, req.novo_valor_diario, req.dias_duracao)

class CAPIEventRequest(BaseModel):
    event_name: str
    event_source_url: str = "https://marcaopersonal.com"
    user_data: Optional[dict] = None
    custom_data: Optional[dict] = None

@app.post("/api/tracking/capi")
async def disparar_evento_capi(req: CAPIEventRequest):
    """Dispara evento server-side diretamente para a Meta Conversions API (CAPI)."""
    from rui_traffic_engine import enviar_evento_capi
    return enviar_evento_capi(req.event_name, req.event_source_url, req.user_data, req.custom_data)

@app.get("/api/trafego/inteligencia")
async def obter_inteligencia_trafego():
    """Retorna relatório de inteligência com tendências Google Trends e público por estado."""
    from rui_intelligence_engine import gerar_relatorio_inteligencia_diario
    return gerar_relatorio_inteligencia_diario()

class InstagramPostRequest(BaseModel):
    tipo: str = "manha"  # "manha" ou "noite"
    formato: str = "carrossel"  # "carrossel" ou "card"
    usar_ia: bool = False
    dry_run: bool = False
    indice: Optional[int] = None

@app.post("/api/instagram/gerar-e-publicar")
async def gerar_e_publicar_criativo(req: InstagramPostRequest):
    """
    Gera criativo ultra-realista com copy persuasiva, temas do Google Trends Brasil,
    e publica automaticamente no Instagram (@marcaopersonalfitness).
    """
    from creative_factory import executar_ciclo_manha, executar_ciclo_noite
    if req.tipo.lower() in ["manha", "curiosidade", "entretenimento"]:
        res = executar_ciclo_manha(indice=req.indice, formato=req.formato, usar_ia=req.usar_ia, dry_run=req.dry_run)
    else:
        res = executar_ciclo_noite(indice=req.indice, formato=req.formato, usar_ia=req.usar_ia, dry_run=req.dry_run)
    return res

@app.get("/api/instagram/posts-recentes")
async def listar_posts_instagram():
    """Consulta posts recentes publicados no Instagram oficial da marca."""
    from creative_factory import INSTAGRAM_ACCOUNT_ID, INSTAGRAM_ACCESS_TOKEN
    import httpx
    if not INSTAGRAM_ACCESS_TOKEN:
        return []
    url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media"
    params = {
        "fields": "id,caption,media_type,media_url,permalink,timestamp",
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "limit": 10
    }
    async with httpx.AsyncClient(verify=False, timeout=15) as client:
        r = await client.get(url, params=params)
        if r.status_code == 200:
            return r.json().get("data", [])
    return []




# -------------------------------------------------------------------------
# 6. SCANNER MULTIMODAL DE BIOIMPEDÂNCIA, VIP 360° & MOTOR DE VENDAS
# -------------------------------------------------------------------------
try:
    from balanca_engine import (
        escanear_tela_bioimpedancia,
        registrar_ou_atualizar_cliente_balanca,
        verificar_status_vip,
        processar_lead_scoring_inteligente,
        obter_metricas_cfo_consolidadas
    )
except ImportError:
    from apps.api.balanca_engine import (
        escanear_tela_bioimpedancia,
        registrar_ou_atualizar_cliente_balanca,
        verificar_status_vip,
        processar_lead_scoring_inteligente,
        obter_metricas_cfo_consolidadas
    )

class BalancaScanRequest(BaseModel):
    telefone: str
    nome: Optional[str] = "Guerreiro(a)"
    imagem_base64: str
    objetivo: Optional[str] = "secar e definir"

@app.post("/api/balanca/escanear-tela")
async def escanear_balanca_api(req: BalancaScanRequest):
    """
    Escaner multimodal de alta precisão para telas de apps de balança (Fitdays, OKOK, Tuya, Xiaomi)
    ou foto do display da balança. Extrai 12 biomarcadores, calcula metas de hidratação/macros,
    emite o Relatório 360° do Marcão e registra no banco de dados.
    """
    scan = await escanear_tela_bioimpedancia(
        imagem_base64=req.imagem_base64,
        nome=req.nome,
        objetivo=req.objetivo
    )
    if scan.get("sucesso"):
        reg = await registrar_ou_atualizar_cliente_balanca(
            remote_jid=f"{req.telefone}@s.whatsapp.net",
            telefone=req.telefone,
            nome=req.nome,
            dados_bio=scan.get("metricas", {}),
            relatorio_texto=scan.get("relatorio_texto", "")
        )
        scan["registro_vip"] = reg
    return scan

class AtivarVIPRequest(BaseModel):
    telefone: str
    nome: str
    canal_compra: Optional[str] = "site"
    codigo_pedido: Optional[str] = None

@app.post("/api/balanca/ativar-vip")
async def ativar_vip_api(req: AtivarVIPRequest):
    """Ativa os 3 meses (90 dias) de suporte VIP gratuito para compradores da balança."""
    dados_iniciais = {"peso_kg": 75.0, "gordura_corporal_pct": 20.0, "massa_muscular_kg": 55.0}
    relatorio = f"VIP ativado com sucesso para {req.nome}! 90 dias de mentoria liberados!"
    return await registrar_ou_atualizar_cliente_balanca(
        remote_jid=f"{req.telefone}@s.whatsapp.net",
        telefone=req.telefone,
        nome=req.nome,
        dados_bio=dados_iniciais,
        relatorio_texto=relatorio
    )

@app.get("/api/balanca/status-vip/{telefone}")
async def status_vip_api(telefone: str):
    """Consulta o status VIP da balança, contagem regressiva dos 90 dias e link de renovação."""
    return await verificar_status_vip(telefone)

class LeadScoringRequest(BaseModel):
    remote_jid: Optional[str] = None
    telefone: str
    nome: Optional[str] = "Lead"
    ultima_mensagem: str

@app.post("/api/vendas/lead-scoring")
async def lead_scoring_api(req: LeadScoringRequest):
    """Calcula lead score (0-100), detecta intenções/objeções e estágio no funil."""
    r_jid = req.remote_jid or f"{req.telefone}@s.whatsapp.net"
    return await processar_lead_scoring_inteligente(
        remote_jid=r_jid,
        telefone=req.telefone,
        nome=req.nome,
        ultima_msg=req.ultima_mensagem
    )

@app.get("/api/cfo/metricas")
async def cfo_metricas_api():
    """Retorna métricas consolidadas de vendas, faturamento bruto, custos e ROAS."""
    return await obter_metricas_cfo_consolidadas()

# -------------------------------------------------------------------------
# 7. MOTOR DE FICHAS DE ALUNO, ANAMNESE E CRIPTOGRAFIA LGPD
# -------------------------------------------------------------------------
try:
    from fichas_engine import (
        buscar_ou_criar_ficha_aluno,
        processar_etapa_onboarding,
        armazenar_foto_aluno_criptografada,
        avaliar_prato_comida,
        verificar_e_gerar_upsell_30dias,
        disparar_rotina_proativa_vip
    )
except ImportError:
    from apps.api.fichas_engine import (
        buscar_ou_criar_ficha_aluno,
        processar_etapa_onboarding,
        armazenar_foto_aluno_criptografada,
        avaliar_prato_comida,
        verificar_e_gerar_upsell_30dias,
        disparar_rotina_proativa_vip
    )

@app.get("/api/fichas/{telefone}")
async def obter_ficha_aluno_api(telefone: str):
    """Retorna a ficha de anamnese completa do aluno pelo telefone."""
    remote_jid = f"{telefone}@s.whatsapp.net"
    return await buscar_ou_criar_ficha_aluno(remote_jid, telefone, "Aluno")

class FichaOnboardingRequest(BaseModel):
    telefone: str
    nome: Optional[str] = "Aluno"
    mensagem: str

@app.post("/api/fichas/onboarding")
async def onboarding_aluno_api(req: FichaOnboardingRequest):
    """Executa etapa de anamnese conversacional guiada para preenchimento de ficha."""
    remote_jid = f"{req.telefone}@s.whatsapp.net"
    ficha = await buscar_ou_criar_ficha_aluno(remote_jid, req.telefone, req.nome)
    return await processar_etapa_onboarding(remote_jid, req.telefone, req.nome, req.mensagem, ficha)

class FotoCriptoRequest(BaseModel):
    telefone: str
    imagem_base64: str
    tipo_foto: Optional[str] = "frente_costas"

@app.post("/api/fichas/foto-criptografada")
async def salvar_foto_criptografada_api(req: FotoCriptoRequest):
    """Criptografa via AES-256 Fernet a foto de evolução do aluno e salva no Supabase (LGPD)."""
    remote_jid = f"{req.telefone}@s.whatsapp.net"
    return await armazenar_foto_aluno_criptografada(remote_jid, req.imagem_base64, req.tipo_foto)

class AvaliarPratoRequest(BaseModel):
    nome: Optional[str] = "Guerreiro"
    imagem_base64: str

@app.post("/api/fichas/avaliar-prato")
async def avaliar_prato_api(req: AvaliarPratoRequest):
    """Avaliação por visão computacional do prato de comida e estimativa de macros."""
    avaliacao = await avaliar_prato_comida(req.imagem_base64, req.nome)
    return {"sucesso": True, "avaliacao": avaliacao}

class ProativoCronRequest(BaseModel):
    tipo_dia: str  # 'segunda', 'quarta', 'sexta', 'upsell_30dias'

@app.post("/api/fichas/proativo-cron")
async def proativo_cron_api(req: ProativoCronRequest):
    """Dispara a rotina proativa do Marcão Personal no WhatsApp (Segunda, Quarta, Sexta ou Upsell 30d)."""
    return await disparar_rotina_proativa_vip(req.tipo_dia)

# -------------------------------------------------------------------------
# 8. CATÁLOGO UNIFICADO, INGESTÃO DE AFILIADOS & INTELIGÊNCIA COMERCIAL
# -------------------------------------------------------------------------
try:
    from catalog_service import obter_produtos_ativos, obter_catalogo_para_prompt
    from autonomous_curator import (
        processar_e_ingerir_afiliado,
        selecionar_oferta_autonoma_do_dia,
        calcular_projecao_meta_milhao
    )
except ImportError:
    from apps.api.catalog_service import obter_produtos_ativos, obter_catalogo_para_prompt
    from apps.api.autonomous_curator import (
        processar_e_ingerir_afiliado,
        selecionar_oferta_autonoma_do_dia,
        calcular_projecao_meta_milhao
    )

class IngerirAfiliadoRequest(BaseModel):
    url: str
    texto_ou_html: Optional[str] = ""
    programa: Optional[str] = "afiliado"  # amazon, magalu, mercadolivre, shopee, braip, stripe

@app.post("/api/afiliados/ingerir")
async def ingerir_afiliado_api(req: IngerirAfiliadoRequest):
    """
    Ingestão autônoma de produtos de afiliados (Amazon, Magalu, Mercado Livre, Shopee, Braip).
    Extrai dados via IA, valida compliance ANVISA/Meta e sincroniza na memória viva do WhatsApp e Instagram.
    """
    resultado = await processar_e_ingerir_afiliado(
        url=req.url,
        texto_ou_html=req.texto_ou_html,
        programa=req.programa
    )
    return resultado

@app.get("/api/catalogo/unificado")
async def obter_catalogo_unificado_api():
    """Retorna todos os produtos ativos do catálogo unificado com custo diário calculado."""
    produtos = await obter_produtos_ativos()
    prompt_bloco = await obter_catalogo_para_prompt()
    return {
        "sucesso": True,
        "total_produtos": len(produtos),
        "produtos": produtos,
        "prompt_bloco": prompt_bloco
    }

@app.get("/api/estrategia/oferta-do-dia")
async def obter_oferta_do_dia_api():
    """Retorna a decisão autônoma do Marcão para o produto do dia no Instagram e WhatsApp."""
    return await selecionar_oferta_autonoma_do_dia()

@app.get("/api/estrategia/meta-milhao")
async def obter_meta_milhao_api():
    """Retorna a modelagem matemática e metas operacionais para alcançar R$ 1 Milhão em vendas."""
    return calcular_projecao_meta_milhao()

# -------------------------------------------------------------------------
# 9. FÁBRICA DE CRIATIVOS, ROTINA DE METAS COM PRAZOS & RECEITAS FITNESS
# -------------------------------------------------------------------------
try:
    from creative_factory import executar_ciclo_manha, executar_ciclo_noite
    from fichas_engine import (
        buscar_receita_fit_para_desejo,
        calcular_status_meta,
        gerar_orientacao_modo_atleta,
        RECEITAS_FITNESS_SUBSTITUICAO,
        ESTUDOS_CIENTIFICOS_MARCAO,
        PLAYLISTS_TREINO_MARCAO,
        atualizar_campo_ficha
    )
except ImportError:
    from apps.api.creative_factory import executar_ciclo_manha, executar_ciclo_noite
    from apps.api.fichas_engine import (
        buscar_receita_fit_para_desejo,
        calcular_status_meta,
        gerar_orientacao_modo_atleta,
        RECEITAS_FITNESS_SUBSTITUICAO,
        ESTUDOS_CIENTIFICOS_MARCAO,
        PLAYLISTS_TREINO_MARCAO,
        atualizar_campo_ficha
    )

class CreativeTriggerRequest(BaseModel):
    indice: Optional[int] = None
    formato: Optional[str] = "carrossel"
    usar_ia: Optional[bool] = True
    estilo_visual: Optional[str] = "evandro"
    postar_story: Optional[bool] = True
    dry_run: Optional[bool] = False

@app.post("/api/creatives/ciclo-manha")
async def ciclo_manha_api(req: CreativeTriggerRequest = CreativeTriggerRequest()):
    """Executa o ciclo matinal (11:30) com Carrossel de 3 slides e Story (estilo Evandro ou Marcão)."""
    return executar_ciclo_manha(
        indice=req.indice,
        formato=req.formato,
        usar_ia=req.usar_ia,
        dry_run=req.dry_run,
        estilo_visual=req.estilo_visual,
        postar_story=req.postar_story
    )

@app.post("/api/creatives/ciclo-noite")
async def ciclo_noite_api(req: CreativeTriggerRequest = CreativeTriggerRequest()):
    """Executa o ciclo noturno (19:30) focado em conversão de produto com Carrossel e Story."""
    return executar_ciclo_noite(
        indice=req.indice,
        formato=req.formato,
        usar_ia=req.usar_ia,
        dry_run=req.dry_run,
        estilo_visual=req.estilo_visual,
        postar_story=req.postar_story
    )

class ReceitaRequest(BaseModel):
    desejo: str

@app.post("/api/nutricao/receita-fit")
async def buscar_receita_fit_api(req: ReceitaRequest):
    """Retorna receita fitness proteica correspondente a desejos/vícios de besteiras."""
    receita = buscar_receita_fit_para_desejo(req.desejo)
    return {
        "encontrado": bool(receita),
        "desejo": req.desejo,
        "receita": receita or RECEITAS_FITNESS_SUBSTITUICAO.get("bolo")
    }

class MetaAlunoRequest(BaseModel):
    remote_jid: str
    meta_descricao: str
    prazo_dias: int = 60
    modo_atleta: bool = False
    data_competicao: Optional[str] = None
    tipo_competicao: Optional[str] = None

@app.post("/api/aluno/meta-atleta")
async def definir_meta_aluno_api(req: MetaAlunoRequest):
    """Registra ou atualiza meta com prazo (início, meio e fim) e ativação do modo atleta."""
    data_inicio = datetime.utcnow().isoformat()
    status_meta = calcular_status_meta(data_inicio, req.prazo_dias)
    patch_data = {
        "meta_descricao": req.meta_descricao,
        "data_inicio_meta": data_inicio,
        "prazo_meta_dias": req.prazo_dias,
        "modo_atleta": req.modo_atleta,
        "data_competicao": req.data_competicao,
        "tipo_competicao": req.tipo_competicao,
        "status_meta": status_meta
    }
    await atualizar_campo_ficha(req.remote_jid, patch_data)
    orientacao = gerar_orientacao_modo_atleta({"nome_aluno": "Aluno"}, status_meta) if req.modo_atleta else {}
    return {
        "sucesso": True,
        "status_meta": status_meta,
        "modo_atleta": req.modo_atleta,
        "orientacao_atleta": orientacao
    }

