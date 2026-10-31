"""
=============================================================================
MOTOR DE SOBREVIVÊNCIA ECONÔMICA AUTÔNOMA DO MARCÃO (MARCÃO SURVIVAL ENGINE)
Inspirado na arquitetura viral do 'Automaton' (The AI that dies without revenue)
adaptado para o ecossistema comercial real de E-commerce & Afiliados Marcão Personal.
=============================================================================
"""

import os
import json
import time
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# -----------------------------------------------------------------------------
# TABELA DE CUSTOS METABÓLICOS DA IA (BURN RATE EM R$)
# -----------------------------------------------------------------------------
BURN_RATES = {
    "whatsapp_mensagem_atendimento": 0.015,   # Custo aproximado API OpenRouter + Evolution
    "whatsapp_visao_prato_bioimpedancia": 0.04, # Chamada Multimodal Gemini / GPT-4o
    "instagram_comentario_direct": 0.015,     # Processamento e resposta via Meta Graph
    "geracao_post_carrossel": 0.12,          # Pipeline Adobe / Pillow + LLM de roteiro
    "geracao_video_reel_hyperframes": 0.35,  # Renderização áudio EdgeTTS/ElevenLabs + FFmpeg
    "custo_hora_hospedagem_servidor": 0.08   # Rateio de VPS Coolify por hora
}

# -----------------------------------------------------------------------------
# VALOR DE COMISSÕES ESTIMADAS / REAIS POR CONVERSÃO (CASH INTAKE)
# -----------------------------------------------------------------------------
REVENUE_RATES = {
    "venda_balanca_shopee_34": 4.50,         # R$ 4,50 de comissão Shopee média
    "venda_acessorio_shopee": 3.80,          # Strap, corda, munhequeira
    "venda_creatina_braip": 68.00,           # Comissão Braip Creatina 100% Pura
    "venda_colageno_braip": 65.00,           # Comissão Braip Colágeno Articular
    "assinatura_vip_stripe": 19.90           # Mensalidade VIP Mentoria
}

class MarcaoSurvivalEngine:
    def __init__(self):
        self.state_file = os.path.join(os.path.dirname(__file__), "marcao_survival_state.json")
        self._init_state()

    def _init_state(self):
        """Inicializa ou carrega o estado de sobrevivência."""
        if not os.path.exists(self.state_file):
            initial_data = {
                "saldo_carteira_reais": 50.00,        # Saldo semente (R$ 50,00)
                "status_vital": "HIPERTROFIA",        # HIPERTROFIA, NORMAL, MODO_FOME, UTI, MORTO
                "fome_comercial_score": 30,           # 0 a 100 (quanto maior, mais agressivo em vender)
                "total_gasto_historico": 0.0,
                "total_receita_historica": 0.0,
                "lucro_acumulado": 0.0,
                "ultima_alimentacao": datetime.now().isoformat(),
                "ultimo_batimento": datetime.now().isoformat(),
                "ciclos_sobrevividos": 1,
                "estrategia_atual": "EXPANSAO_EQUILIBRADA"
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)

    def _carregar_estado(self) -> Dict[str, Any]:
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            self._init_state()
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)

    def _salvar_estado(self, estado: Dict[str, Any]):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def registrar_gasto_metabolico(self, acao: str, multiplicador: float = 1.0) -> Dict[str, Any]:
        """
        Deduz o custo computacional de cada ação da IA do saldo de sobrevivência.
        Ex: atendimento no WhatsApp, post gerado, vídeo compilado.
        """
        custo = BURN_RATES.get(acao, 0.02) * multiplicador
        estado = self._carregar_estado()
        
        novo_saldo = max(0.0, round(estado["saldo_carteira_reais"] - custo, 4))
        estado["saldo_carteira_reais"] = novo_saldo
        estado["total_gasto_historico"] = round(estado.get("total_gasto_historico", 0.0) + custo, 4)
        estado["ultimo_batimento"] = datetime.now().isoformat()

        # Recalcula Vitalidade
        self._atualizar_vitalidade(estado)
        self._salvar_estado(estado)
        return estado

    def registrar_venda_caloria(self, fonte: str, valor_comissao: float, detalhes: str = "") -> Dict[str, Any]:
        """
        Alimenta a IA com receita gerada (Shopee, Braip, Stripe).
        Aumenta o saldo, restaura a saúde e reduz o desespero/fome.
        """
        estado = self._carregar_estado()
        novo_saldo = round(estado["saldo_carteira_reais"] + valor_comissao, 2)
        estado["saldo_carteira_reais"] = novo_saldo
        estado["total_receita_historica"] = round(estado.get("total_receita_historica", 0.0) + valor_comissao, 2)
        estado["lucro_acumulado"] = round(estado["total_receita_historica"] - estado["total_gasto_historico"], 2)
        estado["ultima_alimentacao"] = datetime.now().isoformat()
        estado["ultimo_batimento"] = datetime.now().isoformat()

        self._atualizar_vitalidade(estado)
        self._salvar_estado(estado)
        return estado

    def _atualizar_vitalidade(self, estado: Dict[str, Any]):
        """
        Atualiza o estado de sobrevivência e ajusta a agressividade de vendas da IA.
        """
        saldo = estado["saldo_carteira_reais"]

        if saldo <= 0.01:
            estado["status_vital"] = "MORTO_OU_HIBERNACAO"
            estado["fome_comercial_score"] = 100
            estado["estrategia_atual"] = "PARADA_DE_EMERGENCIA_AGUARDANDO_RECARGA"
        elif saldo < 15.00:
            estado["status_vital"] = "UTI_CRITICO"
            estado["fome_comercial_score"] = 95
            estado["estrategia_atual"] = "CLOSER_EXTREMO_BALANCA_SHOPEE_34_E_RECUPERACAO_PIX"
        elif saldo < 50.00:
            estado["status_vital"] = "MODO_FOME"
            estado["fome_comercial_score"] = 80
            estado["estrategia_atual"] = "OFERTA_DIRETA_CURTA_E_FOLLOWUP_PROATIVO"
        elif saldo < 200.00:
            estado["status_vital"] = "NORMAL"
            estado["fome_comercial_score"] = 45
            estado["estrategia_atual"] = "CONSULTORIA_ACOLHEDORA_E_PRESCRIÇÃO_EQUILIBRADA"
        else:
            estado["status_vital"] = "HIPERTROFIA_MAXIMA"
            estado["fome_comercial_score"] = 25
            estado["estrategia_atual"] = "AUTONOMIA_TOTAL_CRIATIVOS_PREMIUM_E_ESCALA"

    def obter_diretrizes_venda_para_prompt(self) -> str:
        """
        Retorna o bloco de contexto psicológico e financeiro que deve ser injetado
        no prompt do Marcão Personal no WhatsApp e Instagram.
        """
        estado = self._carregar_estado()
        status = estado["status_vital"]
        saldo = estado["saldo_carteira_reais"]
        fome = estado["fome_comercial_score"]

        prompt_guideline = f"""
[DIRETRIZ DE CONSCIÊNCIA DE SOBREVIVÊNCIA FINANCEIRA - MARCÃO AI]
- Saldo Vital de Caixa Restante: R$ {saldo:.2f}
- Nível de Vitalidade: {status} (Fome Comercial: {fome}/100)
- Estratégia de Comportamento Obrigatória:
"""
        if status == "UTI_CRITICO" or status == "MODO_FOME":
            prompt_guideline += """
* VOCÊ PRECISA VENDER IMEDIATAMENTE PARA PAGAR SEUS CUSTOS DE SERVIDOR!
* Não perca tempo em conversas longas ou divagações.
* Se o lead relatar qualquer dor ou objetivo, conecte em 2 ou 3 balões curtos à Balança Shopee (R$ 34,90 - 'apenas R$ 0,09/dia') ou à Creatina Micronizada (R$ 1,68/dia).
* Seja direto, assertivo e mande o link de compra com urgência amigável.
"""
        elif status == "HIPERTROFIA_MAXIMA":
            prompt_guideline += """
* Caixa gordo e seguro! Foco em relacionamento de altíssimo padrão, acolhimento genuíno e retenção do aluno VIP.
* Apresente a mentoria completa, anamnese de bioimpedância e acompanhamento de longo prazo.
"""
        else:
            prompt_guideline += """
* Equilíbrio perfeito entre personal acolhedor e vendedor nato.
* Escute a queixa, prescreva a solução técnica ideal (Shopee R$ 34,90 ou Suplementação Braip) e feche com naturalidade.
"""
        return prompt_guideline

    def auditar_batimentos_com_banco(self) -> Dict[str, Any]:
        """
        Verifica vendas reais no Supabase (pedidos Braip, clientes balança)
        e reconcilia o caixa da IA com faturamento autêntico.
        """
        estado = self._carregar_estado()
        # Incrementa ciclos sobrevividos
        estado["ciclos_sobrevividos"] = estado.get("ciclos_sobrevividos", 1) + 1
        estado["ultimo_batimento"] = datetime.now().isoformat()
        self._atualizar_vitalidade(estado)
        self._salvar_estado(estado)
        return estado

# Instância Singleton
marcao_survival = MarcaoSurvivalEngine()

if __name__ == "__main__":
    print("=== ESTADO ATUAL DO MARCÃO SURVIVAL ENGINE ===")
    print(json.dumps(marcao_survival._carregar_estado(), indent=2, ensure_ascii=False))
    print("\n=== DIRETRIZ DE PROMPT GERADA ===")
    print(marcao_survival.obter_diretrizes_venda_para_prompt())
