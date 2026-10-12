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
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrb3BnZnRmcmZmdG95bmRoaGZqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MTgwMTU4MywiZXhwIjoyMTA3Mzc3NTgzfQ.S_RRdnI6SZTVR1UH7jryDVHf316YmnMOVEBuoedyKv8")

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
