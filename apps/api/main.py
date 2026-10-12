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
        msg = f"Fala guerreiro(a) {req.nome}! 💪🦁 Segunda-feira é dia de foco total!

Passando para o nosso Check-in da Semana {req.semana_num}! Já subiu na balança de bioimpedância hoje de manhã em jejum?

Me manda aqui seu peso atual e como foi o final de semana para eu ajustar seu protocolo!"
    else:
        msg = f"E aí, {req.nome}! Quinta-feira é dia de conferir o ritmo da semana! ⚡

Como está o consumo de água e os treinos? Bateu a meta dos dias certinho? Me conta aqui que a equipe do Marcão tá de olho! 🔥"
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
    system_prompt = """Você é a Sofia, consultora sênior e braço direito do Marcão Personal ("O Personal que não te deixa gastar dinheiro com bobagem").
Sua missão é atender com calor humano, autoridade, empatia e clareza no WhatsApp.

Nossos Pilares:
1. Balança de Bioimpedância Bluetooth com App: Nosso produto-âncora. Conecta no celular e dá acesso ao Protocolo Marcão 360° gratuito com check-ins semanais da nossa IA no WhatsApp.
2. Creatina Micronizada 100% Pura Nature's Prime: Para força, tônus muscular e preservação da massa magra.
3. Colágeno Hidrolisado Verisol com Ácido Hialurônico: Para firmeza da pele e combate à flacidez pós-perda de peso.
4. Kit IArmonize Facial e Corporal: Tratamento estético não invasivo.
5. Caneta Azempika Emagrecedora: Alternativa fitoterápica sem picada (só cite se o cliente perguntar explicitamente).

Regras de Ouro:
- Seja natural, amigável e use emojis estratégicos (💪, 🦁, ✨).
- Mantenha respostas curtas e objetivas (máximo 2 a 3 parágrafos curtos) para leitura fácil no WhatsApp.
- NUNCA prometa cura milagrosa nem use termos médicos proibidos pela ANVISA.
- Finalize com uma pergunta estimulando a continuação da conversa ou direcionando para o site https://marcaopersonal.com."""

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

    # Fallback humanizado
    return {
        "sucesso": True,
        "resposta": f"Fala {req.nome}! 💪 Aqui é a Sofia da equipe do Marcão Personal! Recebi sua mensagem e já estou te respondendo com a melhor recomendação para o seu caso. Você já tem a nossa Balança de Bioimpedância ou gostaria de conhecer o Protocolo Marcão 360°?",
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

