# apps/api/food_cards_engine.py
"""
========================================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
MOTOR DE POSTAGENS DIÁRIAS DE ALIMENTOS (365 DIAS DE NUTRIÇÃO & BIOQUÍMICA)
========================================================================================
Seleciona automaticamente o alimento do dia conforme o dia do ano (1 a 366),
estruturando o card no padrão aprovado pelo Diretor Evandro Gallina:
- Topo: Fotografia gastronômica macro ultra-realista do alimento (protagonista absoluto)
- Base: Card escuro (Dark Glassmorphism) de alto contraste com:
  * Headline de longevidade / emagrecimento
  * Sub-headline de benefícios diretos
  * 3 tópicos escaneáveis em bullets
  * Destaque numérico científico (ex: até 600% mais absorção)
  * Regra de Ouro do Treinador Marcão (segredo prático de preparo / consumo)
========================================================================================
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "alimentos_365_dias.json")

def carregar_catalogo_alimentos() -> list:
    """Carrega o catálogo completo com 366 dias de alimentos únicos."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def obter_alimento_do_dia(dia_especifico: Optional[int] = None) -> Dict[str, Any]:
    """
    Retorna o alimento correspondente ao dia do ano (1 a 366).
    Se dia_especifico for fornecido, retorna aquele dia. Caso contrário, usa a data atual.
    """
    catalogo = carregar_catalogo_alimentos()
    if not catalogo:
        return {
            "dia": 1,
            "alimento": "Cenoura",
            "categoria": "Raízes & Tubérculos",
            "headline": "Cenoura: Aliada da Longevidade",
            "subheadline": "Perda de peso • rejuvenescimento da pele • mais betacaroteno",
            "topicos": [
                "Ajuda na saciedade e perda de peso",
                "Betacaroteno precursor de vitamina A",
                "Antioxidantes protetores do colágeno"
            ],
            "destaque_bioquimico": "até 600% mais absorção com gordura boa",
            "regra_de_ouro_marcao": "Consuma sempre com 1 fio de azeite de oliva extravirgem para absorver o betacaroteno!",
            "prompt_foto_macro": "Cenoura fresca fatiada com gotas de água e fio de azeite dourado em macro fotografia"
        }
    
    dia_ano = dia_especifico if dia_especifico is not None else datetime.now().timetuple().tm_yday
    # Garantir que o índice circule de 1 a 366
    indice = (dia_ano - 1) % len(catalogo)
    return catalogo[indice]

def montar_legenda_instagram_alimento(alimento_info: Dict[str, Any]) -> str:
    """
    Gera a legenda do post no Instagram seguindo as regras de ouro:
    - Gancho nos primeiros 125 caracteres (antes do '...mais')
    - 2 a 3 balões/parágrafos curtos e energéticos com a voz do Treinador Marcão
    - A 'Regra de Ouro' explicada de forma simples e maromba
    - 3 a 5 hashtags dimensionadas
    """
    nome = alimento_info["alimento"]
    destaque = alimento_info.get("destaque_bioquimico", "poder nutricional comprovado")
    regra = alimento_info.get("regra_de_ouro_marcao", "")
    
    # Gancho estritamente antes dos 125 caracteres
    gancho = f"O segredo do(a) {nome} que quase ninguém aproveita: {destaque}! 🦁🔥"
    if len(gancho) > 125:
        gancho = f"O segredo do {nome} que transforma seus resultados! 🦁🔥"
    
    corpo = (
        f"{gancho}\n\n"
        f"Fala, minha turma! O Treinador Marcão trouxe a ciência pura pra sua mesa hoje:\n\n"
        f"O {nome} é um dos alimentos mais estratégicos que você pode colocar no prato se quiser secar com saúde e manter o corpo funcionando no pico máximo!\n\n"
        f"💡 A REGRA DE OURO DO MARCÃO:\n"
        f"{regra}\n\n"
        f"Nada de comer no escuro achando que comida saudável é sem graça. É sobre estratégia bioquímica aplicada ao seu treino!\n\n"
        f"Salva esse card pra não esquecer no próximo mercado e compartilha com aquele parceiro que precisa comer melhor! Tamo junto! 👊🦁\n\n"
        f"#nutricaoesportiva #marcaoalimentos #alimentacaosaudavel #{nome.lower().replace(' ', '').replace('-', '')} #treinopesado"
    )
    return corpo

if __name__ == "__main__":
    hoje_info = obter_alimento_do_dia()
    print("=== ALIMENTO DO DIA SELECIONADO ===")
    print(f"Dia {hoje_info['dia']}: {hoje_info['alimento']} ({hoje_info['categoria']})")
    print(f"Headline: {hoje_info['headline']}")
    print(f"Destaque: {hoje_info['destaque_bioquimico']}")
    print(f"Regra de Ouro: {hoje_info['regra_de_ouro_marcao']}")
    print("\n=== LEGENDA DO INSTAGRAM GERADA ===")
    print(montar_legenda_instagram_alimento(hoje_info))
