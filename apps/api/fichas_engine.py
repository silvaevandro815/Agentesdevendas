import os
import re
import json
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    from encryption_service import criptografar_foto, gerar_termo_lgpd
except ImportError:
    from apps.api.encryption_service import criptografar_foto, gerar_termo_lgpd

_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"), override=True)
load_dotenv(os.path.join(_base_dir, "..", "..", ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

async def buscar_ou_criar_ficha_aluno(remote_jid: str, telefone: str, nome: str) -> dict:
    headers = get_supabase_headers()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.{remote_jid}",
                headers=headers
            )
            if res.status_code == 200:
                dados = res.json()
                if dados and len(dados) > 0:
                    return dados[0]

            # Se não existe, cria ficha inicial zerada (sem inventar nenhum dado!)
            payload = {
                "remote_jid": remote_jid,
                "telefone": telefone,
                "nome_aluno": nome,
                "etapa_onboarding": 0,
                "consentimento_lgpd": False,
                "idade": None,
                "dias_disponiveis_semana": None,
                "local_treino": None,
                "restricoes_saude": None,
                "metas_nutricionais": {},
                "fotos_criptografadas": []
            }
            create_res = await client.post(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos",
                json=payload,
                headers=headers
            )
            if create_res.status_code in (200, 201):
                res_data = create_res.json()
                return res_data[0] if res_data else payload
            return payload
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro ao buscar/criar ficha: {e}")
        return {
            "remote_jid": remote_jid,
            "telefone": telefone,
            "nome_aluno": nome,
            "etapa_onboarding": 0,
            "consentimento_lgpd": False
        }

async def sincronizar_com_clientes_balanca(remote_jid: str, dados_atualizacao: dict):
    """Garante que qualquer aluno de fichas_alunos também esteja sincronizado na tabela clientes_balanca do admin."""
    headers = get_supabase_headers()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            check_res = await client.get(
                f"{SUPABASE_URL}/rest/v1/clientes_balanca?remote_jid=eq.{remote_jid}",
                headers=headers
            )
            nome = dados_atualizacao.get("nome") or dados_atualizacao.get("nome_aluno")
            tel = dados_atualizacao.get("telefone")
            if not tel:
                tel = "".join(filter(str.isdigit, remote_jid.split("@")[0]))
            peso = dados_atualizacao.get("peso")

            if check_res.status_code == 200 and check_res.json():
                c_id = check_res.json()[0]["id"]
                patch_data = {"updated_at": datetime.utcnow().isoformat()}
                if nome: patch_data["nome_cliente"] = nome
                if peso: patch_data["ultimo_peso"] = float(peso)
                patch_data["status_vip"] = "ativo_gratis"
                await client.patch(
                    f"{SUPABASE_URL}/rest/v1/clientes_balanca?id=eq.{c_id}",
                    json=patch_data,
                    headers=headers
                )
            else:
                agora = datetime.utcnow()
                exp_90d = (agora + timedelta(days=90)).isoformat()
                novo_balanca = {
                    "remote_jid": remote_jid,
                    "telefone": tel,
                    "nome_cliente": nome or "Aluno VIP",
                    "data_compra": agora.isoformat(),
                    "data_expiracao_vip": exp_90d,
                    "status_vip": "ativo_gratis",
                    "streak_dias": 1,
                    "ultimo_peso": float(peso) if peso else None,
                    "link_renovacao": "https://marcaopersonal.com#renovacao-vip"
                }
                await client.post(
                    f"{SUPABASE_URL}/rest/v1/clientes_balanca",
                    json=novo_balanca,
                    headers=headers
                )
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro sincronizando com clientes_balanca: {e}")

async def atualizar_campo_ficha(remote_jid: str, dados_atualizacao: dict) -> bool:
    headers = get_supabase_headers()
    dados_atualizacao["atualizado_em"] = datetime.utcnow().isoformat()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.patch(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.{remote_jid}",
                json=dados_atualizacao,
                headers=headers
            )
            # Sincroniza automaticamente com o cadastro da balança para refletir no admin
            await sincronizar_com_clientes_balanca(remote_jid, dados_atualizacao)
            return res.status_code in (200, 204)
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro ao atualizar ficha: {e}")
        return False

def calcular_diagnostico_clinico_completo(
    peso: float,
    altura_cm: float,
    idade: int,
    genero: str = "mulher",
    objetivo: str = "emagrecimento",
    restricoes: str = "",
    nivel_atividade: str = "moderado",
    sono_horas: float = 7.0,
    sono_qualidade: str = "bom",
    agua_litros_habitual: float = 2.0,
    estresse_nivel: str = "moderado",
    trabalho_rotina: str = "misto",
    remedios_continuos: str = "nenhum",
    pressao_arterial: str = "normal",
    tempo_treino_min: int = 45
) -> dict:
    """
    Motor Clínico Integrado de Alta Performance (Personal Trainer + Nutricionista + Clínico Geral).
    Calcula com precisão médica/esportiva:
    - IMC (classificação oficial OMS)
    - TMB (Equação de Mifflin-St Jeor para Homens e Mulheres)
    - GET (Gasto Energético Total baseado no fator de atividade)
    - Meta calórica ajustada por objetivo (déficit controlado ou superávit limpo)
    - Meta hídrica ótima (35 a 40ml/kg)
    - Divisão de Macronutrientes (Proteína 2.0g/kg, Gordura 0.8g/kg, Carboidrato residual)
    - Triagem Clínica Geral & Biomecânica (segurança cardiovascular, articular e farmacológica)
    - Perfil Circadiano & Carga de Estresse (impacto do sono e cortisol na recuperação)
    """
    altura_m = altura_cm / 100.0 if altura_cm > 3.0 else altura_cm
    altura_cm_val = altura_cm if altura_cm > 3.0 else altura_cm * 100.0

    # 1. IMC
    imc = round(peso / (altura_m ** 2), 2)
    if imc < 18.5:
        classificacao_imc = "Abaixo do peso ideal"
    elif imc < 25.0:
        classificacao_imc = "Eutrofia (Peso saudável)"
    elif imc < 30.0:
        classificacao_imc = "Sobrepeso"
    elif imc < 35.0:
        classificacao_imc = "Obesidade Grau I"
    elif imc < 40.0:
        classificacao_imc = "Obesidade Grau II"
    else:
        classificacao_imc = "Obesidade Grau III (Mórbida)"

    # 2. TMB - Taxa Metabólica Basal (Mifflin-St Jeor)
    gen_low = genero.lower()
    eh_homem = any(h in gen_low for h in ["m", "homem", "masculino", "man"])
    if eh_homem:
        tmb = (10.0 * peso) + (6.25 * altura_cm_val) - (5.0 * idade) + 5.0
    else:
        tmb = (10.0 * peso) + (6.25 * altura_cm_val) - (5.0 * idade) - 161.0
    tmb = round(tmb, 1)

    # 3. Fator de Atividade e GET
    fatores = {
        "sedentario": 1.2,
        "leve": 1.375,
        "moderado": 1.55,
        "intenso": 1.725,
        "muito_intenso": 1.9
    }
    fator = fatores.get(nivel_atividade.lower(), 1.55)
    get_kcal = round(tmb * fator, 1)

    # 4. Meta Calórica Ajustada ao Objetivo
    obj_low = objetivo.lower() if objetivo else ""
    if any(k in obj_low for k in ["massa", "hipertrofia", "crescer", "força"]):
        calorias_diarias = round(get_kcal + 300)
        estrategia_nutricional = "Superávit Calórico Controlado (+300 kcal para ganho limpo)"
    elif any(k in obj_low for k in ["secar", "emagrecer", "emagrecimento", "perder gordura", "pochete", "barriga"]):
        calorias_diarias = round(get_kcal - 450)
        estrategia_nutricional = "Déficit Calórico Moderado (-450 kcal para queima acelerada sem perda de massa)"
    else:
        calorias_diarias = round(get_kcal)
        estrategia_nutricional = "Normocalórica para Recomposição Corporal e Tônus"

    # 5. Meta Hídrica (35 a 40ml/kg)
    agua_ml = int(peso * 35)

    # 6. Macronutrientes
    proteina_g = round(peso * 2.0, 1)
    gordura_g = round(peso * 0.8, 1)
    cal_proteina = proteina_g * 4
    cal_gordura = gordura_g * 9
    cal_restante = max(0, calorias_diarias - cal_proteina - cal_gordura)
    carbo_g = round(cal_restante / 4.0, 1)

    # 7. Triagem Clínica & Cuidados Biomecânicos
    rest_low = (restricoes or "").lower()
    rem_low = (remedios_continuos or "").lower()
    press_low = (pressao_arterial or "").lower()
    cuidados = []
    alertas_seguranca = []

    # Articular
    if any(w in rest_low for w in ["joelho", "menisco", "patela", "condromalacia"]):
        cuidados.append("Evitar impacto e flexão profunda > 90° em cadeia aberta. Foco em fortalecimento de vasto medial e glúteo médio.")
    if any(w in rest_low for w in ["coluna", "lombar", "hernia", "ciatico"]):
        cuidados.append("Zero compressão axial livre na coluna. Proibido agachamento livre pesado com barra nas costas. Substituir por leg press e exercícios guiados com apoio.")
    if any(w in rest_low for w in ["ombro", "manguito", "bursite"]):
        cuidados.append("Sem desenvolvimento acima da linha da cabeça. Priorizar elevações no plano escapular (30° anterior) e fortalecimento de rotadores externos.")
    if any(w in rest_low for w in ["quadril", "labrum", "bursite trocanterica"]):
        cuidados.append("Evitar adução excessiva e rotações extremas de quadril sob carga.")

    # Cardiovascular / Clínico
    if any(w in press_low or w in rest_low or w in rem_low for w in ["pressao", "pressão", "hipertens", "losartana", "enalapril", "atenolol", "anlodipino"]):
        alertas_seguranca.append("HIPERTENSÃO / CONTROLE DE PRESSÃO: Proibido prender o ar em esforço máximo (Manobra de Valsalva). Manter respiração ritmada (soltar ar na contração). Pausas ativas de 60 a 90 segundos.")
    if any(w in rem_low for w in ["ozempic", "wegovy", "saxenda", "mounjaro", "tirzepatida", "semaglutida"]):
        alertas_seguranca.append("AGONISTA GLP-1 / INJETÁVEL: Risco elevado de perda de massa magra. Aporte proteico rigoroso (2.0 a 2.2g/kg) e ingestão hídrica reforçada para prevenir náusea e constipação.")
    if any(w in rem_low for w in ["puran", "levotiroxina", "tireoide", "t4"]):
        alertas_seguranca.append("TIREOIDE: Tomar o remédio estritamente em jejum 30min antes de qualquer alimento para não interferir na absorção do hormônio.")

    # 8. Fisiologia do Sono & Recuperação Circadiana
    rec_circadiana = []
    if sono_horas < 6.5 or "ruim" in sono_qualidade.lower() or "cansado" in sono_qualidade.lower() or "insonia" in sono_qualidade.lower():
        rec_circadiana.append("Sono abaixo do ideal (<6.5h ou não-reparador). Cortisol basal provavelmente elevado. Recomenda-se higiene do sono: quarto a 20-22°C, escuridão total, cortar telas 40min antes e suplementar Magnésio Glicinato à noite.")
    else:
        rec_circadiana.append("Janela de sono anabólico preservada. Síntese proteica noturna e pico de GH favoráveis.")

    # 9. Sedentarismo de Escritório
    if "sentado" in trabalho_rotina.lower() or "escritorio" in trabalho_rotina.lower() or "computador" in trabalho_rotina.lower():
        cuidados.append("ROTINA SEDENTÁRIA 8H+: Encurtamento de flexores de quadril (iliopsoas) e inibição de glúteo. Necessário aquecimento com mobilidade de tornozelo/quadril e pontes de glúteo antes do treino.")

    return {
        "peso_kg": peso,
        "altura_cm": altura_cm_val,
        "idade": idade,
        "genero": "masculino" if eh_homem else "feminino",
        "imc": imc,
        "classificacao_imc": classificacao_imc,
        "tmb_kcal": tmb,
        "get_kcal": get_kcal,
        "calorias_diarias": calorias_diarias,
        "estrategia_nutricional": estrategia_nutricional,
        "agua_ml": agua_ml,
        "macros": {
            "proteina_g": proteina_g,
            "carboidrato_g": carbo_g,
            "gordura_g": gordura_g,
            "distribuicao": f"{proteina_g}g Proteína (2g/kg) | {carbo_g}g Carboidrato | {gordura_g}g Gordura boa"
        },
        "triagem_clinica": {
            "pressao_arterial": pressao_arterial,
            "remedios_continuos": remedios_continuos,
            "restricoes_reportadas": restricoes or "Nenhuma restrição articular reportada",
            "cuidados_biomecanicos": cuidados if cuidados else ["Nenhuma contraindicação. Aluno(a) liberado(a) para sobrecarga progressiva."],
            "alertas_seguranca": alertas_seguranca if alertas_seguranca else ["Sem riscos cardiovasculares agudos declarados."]
        },
        "fisiologia_circadiana": {
            "sono_horas": sono_horas,
            "sono_qualidade": sono_qualidade,
            "agua_litros_habitual": agua_litros_habitual,
            "estresse_nivel": estresse_nivel,
            "trabalho_rotina": trabalho_rotina,
            "recomendacoes": rec_circadiana
        },
        "tempo_treino_sugerido_min": tempo_treino_min,
        "data_calculo": datetime.utcnow().isoformat()
    }


def gerar_treino_personalizado(objetivo: str, local: str, restricoes: str, idade: int = None, genero: str = "mulher") -> dict:
    restricoes_lower = restricoes.lower() if restricoes else ""
    tem_dor_joelho = any(w in restricoes_lower for w in ["joelho", "menisco", "patela", "condromalacia"])
    tem_dor_ombro = any(w in restricoes_lower for w in ["ombro", "manguito", "clavicula", "bursite"])
    tem_dor_coluna = any(w in restricoes_lower for w in ["coluna", "lombar", "hernia", "ciatico", "dor nas costas"])

    eh_idoso = idade is not None and idade >= 60
    eh_casa = "casa" in (local or "").lower()

    if eh_casa:
        # TREINOS EM CASA COM ELEMENTOS SIMPLES (CABO DE VASSOURA, CADEIRA, DEGRAU, STEP-JACK)
        if eh_idoso:
            estilo = f"Mobilidade, Equilíbrio & Preservação Muscular 60+ ({idade} anos - Casa sem Impacto)"
            cuidados = (
                "⚠️ SEGURANÇA TOTAL 60+: Treino seguro sem impacto articular e sem sobrecarga na coluna. "
                "Mantenha sempre uma cadeira firme ou parede por perto para apoio de equilíbrio. "
                "Lembre-se: o Marcão é uma IA que sugere rotinas educativas; você é o único responsável pelo seu ritmo. "
                "Beba água aos poucos e, se sentir tontura ou dor, pare imediatamente e consulte seu médico."
            )
            treino_a = (
                "Pernas & Equilíbrio Funcional: "
                "1. Senta-e-levanta na cadeira firme com braços cruzados no peito (3x10 a 12); "
                "2. Panturrilha no chão ou degrau segurando firme na parede (3x15); "
                "3. Elevação pélvica/ponte suave no colchonete ou sofá (3x12); "
                "4. Polichinelo adaptado ('Step-Jack' pisando de lado sem salto, 3x30 segundos)."
            )
            treino_b = (
                "Superiores & Mobilidade com Cabo de Vassoura: "
                "1. Mobilidade torácica e escapular com cabo de vassoura acima da cabeça (3x12); "
                "2. 'Bom-Dia' leve com cabo de vassoura apoiado nas costas para postura e alongamento suave de isquiotibiais (3x10); "
                "3. Flexão inclinada com as mãos apoiadas na parede ou encosto alto do sofá (3x10); "
                "4. Remada suave com garrafa de água de 500ml ou 1L (3x12)."
            )
            treino_c = (
                "Core, Postura & Cardio Regenerativo: "
                "1. Prancha isométrica adaptada na parede (3x20 a 30s); "
                "2. Elevação de joelhos alternados segurando no encosto da cadeira (3x10 cada perna); "
                "3. Caminhada suave de 15 a 20 minutos pela casa/quintal com tênis macio."
            )
        else:
            estilo = "Calistenia & Treino Funcional Domiciliar (Objetos Simples & Peso Corporal)"
            cuidados = (
                "⚠️ Execução consciente em casa: use tapete ou colchonete. "
                "Ajuste a intensidade ao seu limite. Você é responsável por cada movimento proposto. O Marcão é uma IA assistente."
            )
            treino_a = (
                "Peitoral, Ombros & Tríceps em Casa: "
                "1. Flexão de braço no chão (ou joelhos apoiados/sofá) (4x8-12); "
                "2. Tríceps banco na cadeira firme ou sofá (3x12); "
                "3. Elevação lateral com garrafas de 1L ou 2L (4x15); "
                "4. Polichinelo dinâmico para queima calórica (3x45s)."
            )
            treino_b = (
                "Costas, Bíceps & Mobilidade em Casa: "
                "1. Remada curvada unilateral com mochila carregada com livros ou galão de água (4x12); "
                "2. Mobilidade articular e agachamento overhead com cabo de vassoura (3x15); "
                "3. Rosca bíceps com garrafas PET ou toalha sob tração isométrica (4x12); "
                "4. Superman no chão para fortalecimento lombar (3x15)."
            )
            treino_c = (
                "Pernas, Glúteos & Abdômen em Casa: "
                "1. Agachamento livre peso corporal com boa amplitude (4x15); "
                "2. Afundo alternado (3x10 cada perna); "
                "3. Elevação pélvica no chão com pausa de 2s no topo (4x15); "
                "4. Panturrilha no degrau da escada (4x20); "
                "5. Prancha isométrica (3x40s)."
            )
    else:
        # TREINOS EM ACADEMIA DE MUSCULAÇÃO
        if eh_idoso:
            estilo = f"Musculação Guiada & Saúde Articular 60+ ({idade} anos - Aparelhos Seguros)"
            cuidados = (
                "⚠️ Aparelhos guiados para máxima estabilidade e segurança biomecânica. "
                "Sem peso livre solto sobre a cabeça ou agachamentos livres com barra. Cargas moderadas e cadência controlada. "
                "O Marcão é uma IA assistente; consulte sempre seu médico para liberação física."
            )
            treino_a = (
                "Membros Inferiores Guiados: "
                "1. Leg Press 45° ou horizontal com amplitude segura sem fechar menos de 90° (3x12); "
                "2. Cadeira Extensora com carga moderada (3x12); "
                "3. Cadeira Flexora (3x12); "
                "4. Panturrilha sentado na máquina (3x15); "
                "5. 15 minutos de bike horizontal sem impacto."
            )
            treino_b = (
                "Superiores & Postura Guiada: "
                "1. Puxada frontal alta na polia aberta (3x12); "
                "2. Remada baixa máquina com apoio no peito (3x12); "
                "3. Supino máquina articulada guiada (3x10); "
                "4. Elevação lateral no cross polia baixa ou halteres leves (3x12)."
            )
            treino_c = (
                "Core & Mobilidade Ativa: "
                "1. Abdominal na máquina ou prancha na bola suíça (3x15); "
                "2. Rotação de tronco e mobilidade articular com bastão/vassoura (3x15); "
                "3. Caminhada ritmada na esteira plana sem inclinação (20 minutos)."
            )
        else:
            estilo = "Foco em Hipertrofia & Força" if "massa" in objetivo.lower() or "hipertrofia" in objetivo.lower() else "Queima Acelerada & Definição Metabólica"
            cuidados = f"Treino calibrado para academia: {restricoes if restricoes else 'Sem restrições reportadas'}. (Lembre-se: Marcão é uma IA assistente e a responsabilidade da execução é sua)."

            if tem_dor_joelho:
                pernas_treino = "Leg Press 45° com pés altos (sem passar de 90°), Cadeira Flexora unilateral, Elevação Pélvica com barra e Panturrilha sentado. (Zero impacto e zero agachamento livre profundo)."
            else:
                pernas_treino = "Agachamento Goblet/Livre (4x10), Leg Press 45° (4x12), Cadeira Extensora (3x15), Mesa Flexora (4x10) e Panturrilha em pé (4x15)."

            if tem_dor_ombro:
                ombro_treino = "Elevação Lateral na polia baixa (ângulo escapular seguro), Face Pull na corda e Manguito Rotador com elástico/polia. (Sem desenvolvimento militar acima da cabeça)."
                peito_treino = "Supino reto com halteres pegada neutra (4x10) e Peck Deck controlado (3x12)."
            else:
                ombro_treino = "Desenvolvimento militar com halteres (4x10), Elevação Lateral (4x12) e Crucifixo Invertido (3x12)."
                peito_treino = "Supino Reto barra ou halteres (4x10), Supino Inclinado (3x10) e Crossover polia média (3x12)."

            if tem_dor_coluna:
                costas_treino = "Puxada Frontal alta na polia, Remada Baixa sentado com apoio no peito (zero sobrecarga na lombar) e Bíceps Scott na máquina."
            else:
                costas_treino = "Puxada Alta (4x10), Remada Curvada com halteres (4x10), Remada Baixa triângulo (3x12) e Bíceps direto barra W (4x10)."

            treino_a = f"Peitoral, Ombro & Tríceps: {peito_treino} + {ombro_treino}"
            treino_b = f"Dorsal, Trapézio & Bíceps: {costas_treino}"
            treino_c = f"Membros Inferiores & Core: {pernas_treino} + Prancha isométrica segura"

    return {
        "estilo_periodizacao": estilo,
        "local": "Treino Adaptado em Casa" if eh_casa else "Academia de Musculação",
        "faixa_etaria": f"Sênior 60+ ({idade} anos)" if eh_idoso else "Adulto",
        "cuidados_especiais": cuidados,
        "treino_a": treino_a,
        "treino_b": treino_b,
        "treino_c": treino_c
    }

async def processar_etapa_onboarding(remote_jid: str, telefone: str, nome: str, texto_recebido: str, ficha: dict) -> dict:
    etapa = ficha.get("etapa_onboarding", 0)
    primeiro_nome = nome.strip().split()[0] if nome else "Guerreiro(a)"
    txt = texto_recebido.strip()
    txt_low = txt.lower()

    # =========================================================================
    # ETAPA 0: BOAS-VINDAS & BIOMETRIA INICIAL (Objetivo, Peso, Altura, Idade)
    # =========================================================================
    if etapa == 0:
        resposta = (
            f"Fala, {primeiro_nome}! 🦁 Marcão Personal na área! Parabéns por garantir seu acesso VIP oficial!\n\n"
            f"Tô aqui pra cuidar de você de verdade no seu WhatsApp! Pra eu abrir seu Prontuário Oficial e calibrar seus treinos e macros com precisão cirúrgica, me passa primeiro o seu ponto de partida:\n\n"
            f"1️⃣ *Qual é o seu objetivo número 1 hoje?* (Secar barriga, ganhar massa magra, definição ou saúde e disposição?)\n"
            f"2️⃣ *Sua idade, altura e peso aproximados?* (Ou me manda a foto do visor da sua balança!)"
        )
        await atualizar_campo_ficha(remote_jid, {"etapa_onboarding": 1})
        return {"onboarding_ativo": True, "resposta": resposta}

    # =========================================================================
    # ETAPA 1: TRIAGEM CLÍNICA GERAL & SEGURANÇA ORTOPÉDICA (Médico / Fisio)
    # =========================================================================
    elif etapa == 1:
        # Extrai peso, altura e idade da resposta
        peso_match = re.search(r'(\d{2,3}(?:[.,]\d+)?)\s*(?:kg|quilos)?', txt_low)
        altura_match = re.search(r'(?:1[.,]\d{2}|1\d{2})\s*(?:m|cm)?', txt_low)
        idade_match = re.search(r'\b(\d{1,2})\s*(?:anos|ano)?\b', txt_low)

        peso_val = float(peso_match.group(1).replace(',', '.')) if peso_match else None
        altura_val = None
        if altura_match:
            alt_str = altura_match.group(0).replace(',', '.').replace('m', '').replace('cm', '').strip()
            try:
                alt_num = float(alt_str)
                altura_val = alt_num if alt_num > 3.0 else alt_num * 100.0
            except Exception:
                pass
        idade_val = int(idade_match.group(1)) if idade_match and int(idade_match.group(1)) in range(12, 95) else None

        dados_patch = {
            "objetivo": txt,
            "etapa_onboarding": 2
        }
        if peso_val: dados_patch["ultimo_peso"] = peso_val
        if altura_val: dados_patch["altura_cm"] = altura_val
        if idade_val: dados_patch["idade"] = idade_val

        resposta = (
            f"Perfeito, {primeiro_nome}! Já guardei suas medidas no seu prontuário! 👊\n\n"
            f"Agora uma checagem fundamental de *saúde clínica e segurança física* (pra eu blindar seu corpo e não te passar nada perigoso):\n\n"
            f"👉 *Você tem pressão alta ou baixa? Toma algum remédio contínuo no dia a dia?*\n"
            f"👉 *Tem alguma dor ou lesão no joelho, coluna/lombar, ombro ou cirurgia prévia?*\n\n"
            f"Pode me mandar tudo sem vergonha que quanto mais eu souber, mais seguro e eficiente fica seu treino!"
        )
        await atualizar_campo_ficha(remote_jid, dados_patch)
        return {"onboarding_ativo": True, "resposta": resposta}

    # =========================================================================
    # ETAPA 2: FISIOLOGIA CIRCADIANA, SONO & CARGA DE ESTRESSE (Metabolismo)
    # =========================================================================
    elif etapa == 2:
        dados_patch = {
            "restricoes_saude": txt,
            "etapa_onboarding": 3
        }
        # Detecta idade se ainda não tiver
        idade_match = re.search(r'\b(\d{1,2})\s*(?:anos|ano)?\b', txt_low)
        if idade_match and not ficha.get("idade"):
            id_num = int(idade_match.group(1))
            if id_num in range(12, 95): dados_patch["idade"] = id_num

        resposta = (
            f"Entendido com clareza, {primeiro_nome}! Já registrei essas informações clínicas pra blindar suas articulações e seu coração! 🛡️\n\n"
            f"Agora duas perguntas que controlam seus hormônios anabólicos e queima de gordura:\n\n"
            f"🌙 *Quantas horas você costuma dormir por noite e você acorda descansado(a) ou parece que foi atropelado(a)?*\n"
            f"💧 *Quantos litros de água pura você bebe por dia na realidade?* (E me conta se você passa o dia sentado em escritório ou se trabalha em movimento)."
        )
        await atualizar_campo_ficha(remote_jid, dados_patch)
        return {"onboarding_ativo": True, "resposta": resposta}

    # =========================================================================
    # ETAPA 3: CAPACIDADE DE TREINO & NUTRIÇÃO COMPORTAMENTAL (Treinador)
    # =========================================================================
    elif etapa == 3:
        # Extrai horas de sono e água declaradas
        sono_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:horas|h)\b', txt_low)
        agua_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:litros|l|garrafas)\b', txt_low)

        dados_fisiologicos = {
            "declaracao_sono_estresse": txt,
            "sono_horas": float(sono_match.group(1).replace(',', '.')) if sono_match else 7.0,
            "agua_litros": float(agua_match.group(1).replace(',', '.')) if agua_match else 2.0
        }

        dados_patch = {
            "etapa_onboarding": 4,
            "metas_nutricionais": {
                **(ficha.get("metas_nutricionais") or {}),
                "anamnese_fisiologica": dados_fisiologicos
            }
        }

        resposta = (
            f"Show de bola! O sono e a água são 70% da sua recuperação e tônus muscular! 💧🛌\n\n"
            f"Pra eu fechar seu protocolo sob medida com chave de ouro:\n\n"
            f"🏋️ *Onde você vai treinar (academia completa ou em casa)?*\n"
            f"⏱️ *Quantos dias na semana e quanto tempo por sessão você REALMENTE consegue dedicar?* (Ex: 3x de 40 min, 4x de 1 hora... Seja sincero pra ser sustentável!)\n"
            f"🍫 *Você sente aquela fome louca por doce/carboidrato em algum horário específico (tipo final da tarde ou noite)?*"
        )
        await atualizar_campo_ficha(remote_jid, dados_patch)
        return {"onboarding_ativo": True, "resposta": resposta}

    # =========================================================================
    # ETAPA 4: TERMO DE CONSENTIMENTO LGPD & RESPONSABILIDADE
    # =========================================================================
    elif etapa == 4:
        local = "casa" if "casa" in txt_low else "academia"
        dias_match = re.search(r'(\d+)\s*(?:dias|x|vezes)', txt_low) or re.search(r'\b([2-6])\b', txt_low)
        dias_num = int(dias_match.group(1)) if dias_match else 3

        tempo_match = re.search(r'(\d+)\s*(?:min|minutos)', txt_low)
        tempo_min = int(tempo_match.group(1)) if tempo_match else 45

        dados_patch = {
            "local_treino": local,
            "dias_disponiveis_semana": dias_num,
            "etapa_onboarding": 5,
            "metas_nutricionais": {
                **(ficha.get("metas_nutricionais") or {}),
                "tempo_treino_min": tempo_min,
                "declaracao_habitos_treino": txt
            }
        }
        await atualizar_campo_ficha(remote_jid, dados_patch)

        termo = gerar_termo_lgpd(primeiro_nome)
        return {"onboarding_ativo": True, "resposta": termo}

    # =========================================================================
    # ETAPA 5: VALIDAÇÃO LGPD ("CONCORDO") & ENTREGA DA PRESCRIÇÃO HIPERPERSONALIZADA
    # =========================================================================
    elif etapa == 5:
        autorizou = any(w in txt_low for w in ["concordo", "ciente", "autorizo", "aceito", "sim", "com certeza", "pode", "ok", "claro", "bora", "fechado"])

        if not autorizou:
            resposta = (
                f"Opa, {primeiro_nome}! 🦁 Entendo você perfeitamente!\n\n"
                f"Mas pela nossa segurança jurídica e respeito à Lei Geral de Proteção de Dados (LGPD), nossos treinos e prontuário personalizado só podem ser liberados após você confirmar ciência e responsabilidade!\n\n"
                f"Para ativarmos sua rotina e começarmos com segurança, basta me responder apenas:\n"
                f"👉 *CONCORDO*\n\n"
                f"Assim que você responder, seu protocolo oficial sai do forno na hora! Tamo junto!"
            )
            return {"onboarding_ativo": True, "resposta": resposta, "bloqueado_lgpd": True}

        # Usuário confirmou expressamente com CONCORDO / CIENTE / SIM
        obj = ficha.get("objetivo") or "Secar barriga e definição"
        loc = ficha.get("local_treino")
        rest = ficha.get("restricoes_saude")
        idade = ficha.get("idade")
        genero = ficha.get("genero", "mulher")
        peso = ficha.get("ultimo_peso") or (ficha.get("metas_nutricionais") or {}).get("peso")
        altura = ficha.get("altura_cm") or (ficha.get("metas_nutricionais") or {}).get("altura_cm")

        # REGRA INVIOLÁVEL: NUNCA ADIVINHA OU INVENTA DADOS!
        # Se faltar idade, peso, altura ou local de treino, pergunta ao aluno antes de prescrever!
        faltas_criticas = []
        if idade is None or not isinstance(idade, (int, float)) or idade <= 0:
            faltas_criticas.append("sua idade real")
        if peso is None or not isinstance(peso, (int, float)) or peso <= 0:
            faltas_criticas.append("seu peso atual")
        if altura is None or not isinstance(altura, (int, float)) or altura <= 0:
            faltas_criticas.append("sua altura")
        if not loc:
            faltas_criticas.append("se você treina em casa ou na academia")

        if faltas_criticas:
            resposta = (
                f"Show, {primeiro_nome}! Termo LGPD formalizado com sucesso! 🛡️🔐\n\n"
                f"Pra eu calcular seus macros, calorias e treino com precisão médica sem adivinhar absolutamente nada sobre você, me passa só {', '.join(faltas_criticas)} rapidinho!\n\n"
                f"Assim que você mandar, seu protocolo sob medida sai do forno na hora! Tamo junto! 👊🔥"
            )
            return {"onboarding_ativo": True, "resposta": resposta}

        meta_info = ficha.get("metas_nutricionais") or {}
        fisio = meta_info.get("anamnese_fisiologica") or {}
        sono_h = fisio.get("sono_horas", 7.0)
        agua_l = fisio.get("agua_litros", 2.0)
        tempo_t = meta_info.get("tempo_treino_min", 45)

        treino = gerar_treino_personalizado(obj, loc, rest or "", idade=idade, genero=genero)
        diag = calcular_diagnostico_clinico_completo(
            peso=peso,
            altura_cm=altura,
            idade=idade,
            genero=genero,
            objetivo=obj,
            restricoes=rest or "",
            sono_horas=sono_h,
            agua_litros_habitual=agua_l,
            tempo_treino_min=tempo_t
        )

        await atualizar_campo_ficha(remote_jid, {
            "consentimento_lgpd": True,
            "data_consentimento_lgpd": datetime.utcnow().isoformat(),
            "termo_lgpd_versao": "v2.0_lgpd",
            "treino_atual": treino,
            "diagnostico_clinico": diag,
            "metas_nutricionais": {
                **meta_info,
                **diag.get("macros", {}),
                "calorias": diag.get("calorias_diarias"),
                "agua_ml": diag.get("agua_ml"),
                "score_completude": 100
            },
            "etapa_onboarding": 6,
            "status_acompanhamento": "ativo"
        })

        resposta = (
            f"Show de bola, {primeiro_nome}! Termo formalizado e seu Prontuário VIP de Aluno está 100% ATIVO! 🛡️🔐\n\n"
            f"Montei seu protocolo sob medida baseado na sua clínica e rotina:\n"
            f"🏋️ *{treino['estilo_periodizacao']}* ({treino['local']})\n"
            f"⏱️ *Sessões:* {tempo_t} min por treino | 💧 *Meta de Água:* {diag.get('agua_ml')}ml/dia\n"
            f"⚠️ *Cuidados Clínicos:* {treino['cuidados_especiais']}\n\n"
            f"📋 *Sua Divisão de Treinos:*\n"
            f"• *Treino A:* {treino['treino_a']}\n\n"
            f"• *Treino B:* {treino['treino_b']}\n\n"
            f"• *Treino C:* {treino['treino_c']}\n\n"
            f"📸 Pra calibrarmos sua evolução visual: não precisa de espelho! Você pode apoiar o celular numa estante ou mesa de frente pra luz de uma janela (sempre a favor da luz natural, nunca contra), colocar o timer de 10 segundos e tirar a foto de corpo inteiro de frente e de costas. Ou pedir pra alguém em casa tirar pra você! Vou guardar essas fotos com sigilo militar no seu prontuário pra daqui a alguns dias compararmos lado a lado os resultados! Tamo junto nessa jornada! 🔥"
        )
        return {"onboarding_ativo": False, "resposta": resposta, "treino": treino}

    return {"onboarding_ativo": False}

    return {"onboarding_ativo": False}

    return {"onboarding_ativo": False}

async def armazenar_foto_aluno_criptografada(remote_jid: str, base64_image: str, tipo_foto: str = "frente") -> dict:
    token_cripto = criptografar_foto(base64_image)
    if not token_cripto:
        return {"sucesso": False, "erro": "Falha na criptografia"}

    headers = get_supabase_headers()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.{remote_jid}",
                headers=headers
            )
            ficha = None
            if res.status_code == 200 and res.json():
                ficha = res.json()[0]
            else:
                tel_limpo = "".join(filter(str.isdigit, remote_jid.split("@")[0]))
                ficha = await buscar_ou_criar_ficha_aluno(remote_jid, tel_limpo, "Aluno VIP")

            if ficha:
                fotos_lista = ficha.get("fotos_criptografadas") or []
                if not isinstance(fotos_lista, list):
                    fotos_lista = []

                novo_registro = {
                    "data": datetime.utcnow().isoformat(),
                    "tipo": tipo_foto,
                    "token_criptografado": token_cripto,
                    "algoritmo": "AES-256-Fernet"
                }
                fotos_lista.append(novo_registro)

                patch_res = await client.patch(
                    f"{SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.{remote_jid}",
                    json={"fotos_criptografadas": fotos_lista, "atualizado_em": datetime.utcnow().isoformat()},
                    headers=headers
                )
                if patch_res.status_code in (200, 204):
                    return {"sucesso": True, "tipo": tipo_foto, "total_fotos": len(fotos_lista)}
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro ao armazenar foto criptografada: {e}")
    return {"sucesso": False}

async def avaliar_prato_comida(base64_image: str, nome_aluno: str) -> str:
    primeiro_nome = nome_aluno.strip().split()[0] if nome_aluno else "Guerreiro"

    if not OPENROUTER_API_KEY:
        return f"Boa refeição, {primeiro_nome}! Prato bem colorido e nutritivo! Mantenha o foco na hidratação e nas proteínas! 💪"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://marcaopersonal.com",
        "X-Title": "Marcao Personal Meal Scanner"
    }

    prompt = (
        "Você é o Marcão Personal Trainer avaliando a foto do prato de comida do seu aluno VIP no WhatsApp. "
        "Analise a imagem e identifique: os alimentos presentes, fonte principal de proteína, carboidrato e salada/legumes. "
        "Dê uma estimativa aproximada de calorias e macros (proteína, carbo, gordura). "
        "Responda no tom do Marcão: enérgico, direto, encorajador, como um verdadeiro treinador parceiro. "
        "Máximo de 3 parágrafos curtos com emojis de treino."
    )

    image_url_str = base64_image if base64_image.startswith("data:") else f"data:image/jpeg;base64,{base64_image}"

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url_str}}
                ]
            }
        ],
        "temperature": 0.4
    }

    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro na análise de prato: {e}")

    return f"Show de bola, {primeiro_nome}! Prato bonito e equilibrado. Capricha na água pós-refeição e bora pro treino mais tarde! 🦁"

def verificar_e_gerar_upsell_30dias(ficha: dict) -> dict:
    if not ficha or ficha.get("status_acompanhamento") != "ativo":
        return {"elegivel": False}

    criado_em_str = ficha.get("criado_em")
    if not criado_em_str:
        return {"elegivel": False}

    try:
        criado_em = datetime.fromisoformat(criado_em_str.replace("Z", "+00:00"))
        dias_ativos = (datetime.utcnow().replace(tzinfo=criado_em.tzinfo) - criado_em).days
    except Exception:
        dias_ativos = 0

    ultimo_upsell = ficha.get("ultimo_upsell_em")
    if ultimo_upsell:
        try:
            ultimo_upsell_dt = datetime.fromisoformat(ultimo_upsell.replace("Z", "+00:00"))
            dias_desde_ultimo = (datetime.utcnow().replace(tzinfo=ultimo_upsell_dt.tzinfo) - ultimo_upsell_dt).days
            if dias_desde_ultimo < 28:
                return {"elegivel": False}
        except Exception:
            pass

    if dias_ativos < 28:
        return {"elegivel": False}

    nome = ficha.get("nome_aluno", "Guerreiro").strip().split()[0]
    objetivo = (ficha.get("objetivo") or "").lower()
    restricoes = (ficha.get("restricoes_saude") or "").lower()

    if "dor" in restricoes or "joelho" in restricoes or "coluna" in restricoes:
        sugestao = {
            "produto": "Colágeno Tipo II com Cúrcuma & Magnésio",
            "link": "https://marcaopersonal.com#produtos",
            "mensagem": (
                f"Fala, {nome}! Fechando nosso ciclo de 30 dias de acompanhamento firme! 👊\n\n"
                f"Como você me falou daquela sensibilidade nas articulações, reparei que muitos alunos meus destravam 100% da amplitude e zeram o incômodo usando um Colágeno Tipo II de alta pureza junto com magnésio. "
                f"Dá uma olhada no catálogo da nossa loja oficial se quiser acelerar essa regeneração articular: https://marcaopersonal.com#produtos\n\n"
                f"Sem pressão nenhuma, é recomendação técnica de treinador pra proteger sua estrutura! Bora pro treino!"
            )
        }
    elif "massa" in objetivo or "hipertrofia" in objetivo or "força" in objetivo:
        sugestao = {
            "produto": "Creatina Creapure 100% Pura",
            "link": "https://marcaopersonal.com#produtos",
            "mensagem": (
                f"Fala, {nome}! Completamos 30 dias de treino consistente, parabéns pela dedicação! 🔥\n\n"
                f"Pra essa próxima fase de progressão de carga e ganho de volume muscular seco, a Creatina monohidratada pura é o suplemento número 1 do mundo com comprovação científica total. "
                f"Se quiser conferir a que nós usamos com laudo garantido no site oficial, tá aqui: https://marcaopersonal.com#produtos\n\n"
                f"Vai te dar aquela força extra na última repetição! Tamo junto!"
            )
        }
    else:
        sugestao = {
            "produto": "Caneta Azempika Natural / Termogênico Ativador",
            "link": "https://marcaopersonal.com#produtos",
            "mensagem": (
                f"Fala, {nome}! 30 dias de foco e evolução na balança! Orgulho demais da sua disciplina! 🦁\n\n"
                f"Normalmente a partir do primeiro mês o metabolismo tende a dar uma desacelerada natural pra defender as reservas de gordura. "
                f"Pra manter a queima acelerada e evitar aquele platô chato de estagnação de peso, o ativador Azempika do nosso site ajuda demais a controlar os picos de apetite sem dar taquicardia: https://marcaopersonal.com#produtos\n\n"
                f"Se fizer sentido pra sua rotina, dá um confere lá. O foco continua no plano diário!"
            )
        }

    return {"elegivel": True, "sugestao": sugestao}

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")

async def enviar_mensagem_whatsapp_fichas(target_number: str, texto: str):
    """Dispara mensagem de texto direta no WhatsApp via Evolution API com proteção estrita anti-spam."""
    if not EVOLUTION_API_KEY or not target_number or not texto:
        return None

    # MODO DRY RUN / TESTE
    if os.getenv("MARCAO_DRY_RUN", "false").lower() == "true":
        print(f"[DRY-RUN FICHAS] Simulação de envio para {target_number}: {texto[:60]}...")
        return {"dry_run": True, "target": target_number, "status": "simulado"}

    digitos = "".join(filter(str.isdigit, str(target_number)))
    if len(digitos) < 10:
        return None

    # Bloqueio estrito de DDD 11 desconhecido
    if digitos.startswith("5511") or (len(digitos) in [10, 11] and digitos.startswith("11")):
        print(f"[BLOQUEIO ANTI-SPAM] Fichas VIP bloqueado para DDD 11: {target_number}")
        return None

    # Padrões clássicos de mock
    if any(m in digitos for m in ["99998888", "988887777", "988881111", "988882222", "999990001"]):
        print(f"[BLOQUEIO ANTI-SPAM] Fichas VIP bloqueado para número teste: {target_number}")
        return None

    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": target_number,
        "text": texto
    }
    try:
        async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
            return await client.post(
                f"{EVOLUTION_API_URL}/message/sendText/sofia",
                headers=headers,
                json=payload
            )
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro enviando WhatsApp: {e}")
        return None

async def disparar_rotina_proativa_vip(tipo_dia: str) -> dict:
    """
    Executa a rotina proativa de acompanhamento do Marcão para todos os alunos VIP ativos:
    - 'segunda': 07:30 - Balança em jejum, meta de hidratação (35ml/kg) e Treino A
    - 'quarta': 18:00 - Cobrança de treino e pedido de foto do prato de jantar/almoço
    - 'sexta': 18:30 - Fechamento semanal e moderação de descanso no fim de semana
    - 'upsell_30dias': Recomendação técnica e não invasiva de produto da loja após 30 dias
    """
    headers = get_supabase_headers()
    alunos_alvo = []

    try:
        async with httpx.AsyncClient(verify=False) as client:
            # 1. Alunos da tabela de fichas
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?status_acompanhamento=eq.ativo",
                headers=headers
            )
            if res.status_code == 200 and res.json():
                alunos_alvo = res.json()

            # 2. Se não houver fichas ativas ainda, busca clientes_balanca ativos
            if not alunos_alvo:
                res_bal = await client.get(
                    f"{SUPABASE_URL}/rest/v1/clientes_balanca?status_vip=eq.ativo",
                    headers=headers
                )
                if res_bal.status_code == 200 and res_bal.json():
                    for cb in res_bal.json():
                        alunos_alvo.append({
                            "remote_jid": cb.get("remote_jid"),
                            "telefone": cb.get("telefone"),
                            "nome_aluno": cb.get("nome_cliente", "Guerreiro"),
                            "objetivo": "Definição corporal",
                            "restricoes_saude": "Nenhuma",
                            "treino_atual": {"treino_a": "Peito, Ombro e Tríceps"},
                            "status_acompanhamento": "ativo"
                        })
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro buscando alunos ativos: {e}")

    disparados = []

    for aluno in alunos_alvo:
        telefone = aluno.get("telefone")
        if not telefone or len(telefone) < 10:
            continue

        nome = (aluno.get("nome_aluno") or "Guerreiro").strip().split()[0]
        treino_info = aluno.get("treino_atual") or {}
        treino_a_desc = treino_info.get("treino_a", "Peitoral & Ombros")

        msg = ""
        if tipo_dia == "segunda":
            msg = (
                f"Fala, {nome}! 🦁 Marcão na área! Segunda-feira é dia sagrado de recomeço com foco total!\n\n"
                f"Primeira missão do dia em jejum: sobe na sua Balança de Bioimpedância e me manda o print ou peso aqui! "
                f"Sua meta hoje é água na garrafa (35ml por kg) e foco no Treino A ({treino_a_desc}).\n\n"
                f"Bora começar a semana vencendo! Tamo junto!"
            )
        elif tipo_dia == "quarta":
            msg = (
                f"E aí, {nome}! 👊 Quarta-feira, metade da semana vencida! Como tá a pegada dos treinos?\n\n"
                f"Passando pra checar se o treino de hoje já tá pago! Me manda uma foto do seu prato de almoço ou jantar aqui pra eu dar uma olhada nos seus macros e calibrar sua dieta!\n\n"
                f"Mantém o ritmo firme, guerreiro!"
            )
        elif tipo_dia == "sexta":
            msg = (
                f"Fala, {nome}! 🦁 Sextou com a sensação de dever cumprido!\n\n"
                f"Fechamos a meta semanal de treinos com chave de ouro! Agora no fim de semana, descanso com moderação e nada de jogar fora o esforço dos últimos 5 dias, combinado?\n\n"
                f"Segura a hidratação e excelente descanso!"
            )
        elif tipo_dia == "upsell_30dias":
            check_up = verificar_e_gerar_upsell_30dias(aluno)
            if check_up.get("elegivel"):
                msg = check_up["sugestao"]["mensagem"]
                # Atualizar ultimo_upsell_em
                await atualizar_campo_ficha(aluno.get("remote_jid"), {"ultimo_upsell_em": datetime.utcnow().isoformat()})

        if msg:
            res_envio = await enviar_mensagem_whatsapp_fichas(telefone, msg)
            disparados.append({
                "telefone": telefone,
                "nome": nome,
                "tipo_dia": tipo_dia,
                "enviado": bool(res_envio and res_envio.status_code in [200, 201])
            })

    return {
        "sucesso": True,
        "tipo_dia": tipo_dia,
        "total_alunos": len(alunos_alvo),
        "total_disparados": len(disparados),
        "disparados": disparados
    }


# =========================================================================
# 8. INTELIGÊNCIA NUTRICIONAL & SUBSTITUIÇÃO DE VÍCIOS ALIMENTARES
# =========================================================================
RECEITAS_FITNESS_SUBSTITUICAO = {
    "bolo": {
        "titulo": "Bolo de Caneca Maromba de Banana, Cacau e Aveia (Sem Açúcar & Sem Farinha Branca)",
        "tempo_preparo": "3 minutos no micro-ondas",
        "ingredientes": [
            "1 banana madura bem amassada (adoça naturalmente)",
            "1 ovo inteiro",
            "2 colheres de sopa de farelo ou farinha de aveia",
            "1 colher de sopa de cacau 100% puro em pó (ou 1 scoop de Whey de chocolate)",
            "1 colher de café de fermento em pó químico",
            "Pitada de canela a gosto"
        ],
        "modo_preparo": "Misture tudo na própria caneca até ficar bem homogêneo. Leve ao micro-ondas por 2 a 3 minutos. Fica fofinho, mata a fissura de doce e entrega 14 a 22g de proteína com fibras saciantes!",
        "calorias_aprox": "220 kcal (sem whey) / 290 kcal (com whey)",
        "proteinas": "15g a 24g"
    },
    "pao_de_queijo": {
        "titulo": "Pão de Queijo de Frigideira Proteico Fit (Pronto em 4 Minutos)",
        "tempo_preparo": "4 minutos na frigideira",
        "ingredientes": [
            "1 ovo inteiro",
            "2 colheres de sopa de goma de tapioca hidratada",
            "1 colher de sopa bem cheia de queijo cottage ou queijo minas light ralado",
            "1 colher de sopa de água ou leite desnatado",
            "1 pitada de sal marinho e orégano"
        ],
        "modo_preparo": "Bata bem o ovo com garfo, misture a tapioca, o queijo e o sal. Despeje numa frigideira antiaderente untada com fio de azeite em fogo baixo. Tampe por 2 minutos, vire para dourar o outro lado. Crocante por fora e puxa-puxa por dentro!",
        "calorias_aprox": "170 kcal",
        "proteinas": "14g"
    },
    "brigadeiro_doce": {
        "titulo": "Brigadeiro de Colher Maromba Ultra-Cremoso",
        "tempo_preparo": "1 minuto (sem fogo)",
        "ingredientes": [
            "1 scoop de Whey Protein de chocolate (ou 2 colheres de leite em pó desnatado + 1 colher de cacau 100%)",
            "1 colher de café de pasta de amendoim integral",
            "Pouquíssima água morna (cerca de 2 a 3 colheres de sopa, pingada aos poucos)"
        ],
        "modo_preparo": "Coloque o pó numa xícara e vá pingando a água morna bem devagar, mexendo com uma colher pequena sem parar até virar um creme brilhante e denso de brigadeiro de panela. Zero açúcar e 25g de proteína pura!",
        "calorias_aprox": "160 kcal",
        "proteinas": "24g"
    },
    "pizza": {
        "titulo": "Pizza Fit de Frigideira Proteica (Massa Fina Sem Glúten)",
        "tempo_preparo": "8 minutos",
        "ingredientes": [
            "1 ovo + 2 claras",
            "2 colheres de sopa de aveia em flocos finos",
            "2 colheres de sopa de molho de tomate 100% natural",
            "2 fatias de muçarela light ou queijo branco",
            "Frango desfiado temperado ou atum sólido",
            "Orégano e rodelas de tomate"
        ],
        "modo_preparo": "Misture o ovo, claras e aveia com uma pitada de sal. Espalhe na frigideira antiaderente como uma panqueca. Quando firmar, vire, passe o molho de tomate, o queijo, o recheio de frango/atum e orégano. Tampe até o queijo derreter completamente!",
        "calorias_aprox": "280 kcal",
        "proteinas": "32g"
    },
    "coxinha_salgado": {
        "titulo": "Coxinha Maromba Fit de Batata Doce na Airfryer",
        "tempo_preparo": "15 minutos na Airfryer",
        "ingredientes": [
            "100g de batata doce ou mandioca cozida e bem amassada",
            "100g de peito de frango cozido e desfiado temperado",
            "1 gema de ovo para pincelar",
            "Farinha de linhaça dourada para empanar"
        ],
        "modo_preparo": "Abra a massa de batata doce na palma da mão, coloque o frango desfiado, modele em formato de coxinha. Pincele a gema, passe na linhaça e asse a 200°C na Airfryer por 12 a 15 minutos até dourar. Fica crocante e sequinha!",
        "calorias_aprox": "240 kcal",
        "proteinas": "30g"
    }
}

def buscar_receita_fit_para_desejo(texto: str) -> dict:
    """Identifica sutilmente menções a vontades de besteiras e retorna a receita fitness ideal."""
    if not texto:
        return {}
    txt = texto.lower()
    if any(w in txt for w in ["bolo", "torta doce", "confeitaria", "pão de ló"]):
        return RECEITAS_FITNESS_SUBSTITUICAO["bolo"]
    elif any(w in txt for w in ["pão de queijo", "pao de queijo", "chipá", "biscoito de queijo"]):
        return RECEITAS_FITNESS_SUBSTITUICAO["pao_de_queijo"]
    elif any(w in txt for w in ["chocolate", "brigadeiro", "doce", "fissura por doce", "nutella", "sobremesa"]):
        return RECEITAS_FITNESS_SUBSTITUICAO["brigadeiro_doce"]
    elif any(w in txt for w in ["pizza", "pizzaria", "calzone"]):
        return RECEITAS_FITNESS_SUBSTITUICAO["pizza"]
    elif any(w in txt for w in ["coxinha", "pastel", "salgadinho", "empada", "esfiha"]):
        return RECEITAS_FITNESS_SUBSTITUICAO["coxinha_salgado"]
    return {}


# =========================================================================
# 9. BIBLIOTECA DE ESTUDOS CIENTÍFICOS & PLAYLISTS DE TREINO DO MARCÃO
# =========================================================================
ESTUDOS_CIENTIFICOS_MARCAO = [
    {
        "tema": "Hipertrofia e Volume Semanal",
        "fonte": "Schoenfeld et al. (Journal of Sports Sciences)",
        "resumo": "Demonstrou que acumular de 10 a 20 séries semanais por grupamento muscular próximo à falha é o principal gatilho biológico para hipertrofia máxima em homens e mulheres."
    },
    {
        "tema": "Creatina e Retenção Intracelular",
        "fonte": "International Society of Sports Nutrition (ISSN)",
        "resumo": "Comprovou que a creatina monohidratada não retém água na camada subcutânea (pele), mas sim 100% dentro do sarcoplasma muscular, aumentando a força em até 20% e preservando a hidratação celular."
    },
    {
        "tema": "Sono Profundo e Liberação de GH",
        "fonte": "Harvard Medical School (Division of Sleep Medicine)",
        "resumo": "Identificou que mais de 70% do pulso diário de hormônio do crescimento (GH) e reparação do sistema nervoso central ocorrem nas fases 3 e 4 do sono profundo não-REM."
    },
    {
        "tema": "Anti-inflamatórios e Trava Muscular",
        "fonte": "Karolinska Institute (Suécia)",
        "resumo": "Evidenciou que tomar ibuprofeno ou analgésicos comuns após o treino inibe a enzima COX-2 e paralisa a síntese proteica, reduzindo pela metade o ganho de massa muscular."
    },
    {
        "tema": "Aporte Proteico Ideal e Saciedade",
        "fonte": "Morton et al. (British Journal of Sports Medicine)",
        "resumo": "Meta-análise em mais de 1.800 atletas validando que 1.6g a 2.2g de proteína por kg corporal é a dosagem exata para construir músculo limpo e blindar contra catabolismo em déficit calórico."
    }
]

PLAYLISTS_TREINO_MARCAO = [
    {
        "estilo": "Gym Phonk & Cyberpunk High BPM (150-160 BPM)",
        "vibe": "Foco cirúrgico, vascularização no talo e ritmo acelerado",
        "artistas": "Kordhell, DVRST, Hensonn, Pharmacist",
        "indicacao": "Treinos de perna pesados, super-séries e cardio intenso."
    },
    {
        "estilo": "Hip-Hop Clássico 90s & Underground",
        "vibe": "Pura agressividade, ritmo marcante e sangue nos olhos",
        "artistas": "2Pac, The Notorious B.I.G., Eminem, 50 Cent, DMX",
        "indicacao": "Treinos de força máxima, supino pesado e levantamento terra."
    },
    {
        "estilo": "Hard Rock & Heavy Metal Pump",
        "vibe": "Adrenalina pura e explosão de força",
        "artistas": "AC/DC, Metallica, Guns N' Roses, Linkin Park, Slipknot",
        "indicacao": "Leg day destruidor e quebra de recordes pessoais (PR)."
    },
    {
        "estilo": "Trap & Funk Maromba Nacional",
        "vibe": "Motivação brasileira e batida energética",
        "artistas": "Toguro beats, Trap de academia, Jax, B-Dynamitze",
        "indicacao": "Treinos diários com alta energia e ritmo constante."
    }
]


# =========================================================================
# 10. GESTÃO DE METAS COM PRAZOS (INÍCIO, MEIO E FIM) & MODO ATLETA / COMPETIÇÃO
# =========================================================================
def calcular_status_meta(data_inicio_str: str, prazo_dias: int = 60) -> dict:
    """Calcula a fase atual da meta do aluno com começo, meio e fim rigorosos."""
    if not data_inicio_str:
        return {"fase": "inicio", "dias_passados": 0, "dias_restantes": prazo_dias, "progresso_pct": 0}

    try:
        inicio = datetime.fromisoformat(data_inicio_str.replace("Z", "+00:00"))
        agora = datetime.utcnow().replace(tzinfo=inicio.tzinfo)
        dias_passados = max(0, (agora - inicio).days)
        dias_restantes = max(0, prazo_dias - dias_passados)
        progresso_pct = min(100.0, round((dias_passados / float(prazo_dias)) * 100, 1))

        if dias_restantes == 0:
            fase = "concluida"
        elif progresso_pct <= 30.0:
            fase = "inicio"
        elif progresso_pct <= 70.0:
            fase = "meio"
        else:
            fase = "reta_final"

        return {
            "fase": fase,
            "dias_passados": dias_passados,
            "dias_restantes": dias_restantes,
            "prazo_total_dias": prazo_dias,
            "progresso_pct": progresso_pct,
            "data_inicio": data_inicio_str,
            "data_termino_prevista": (inicio + timedelta(days=prazo_dias)).strftime("%d/%m/%Y")
        }
    except Exception:
        return {"fase": "inicio", "dias_passados": 0, "dias_restantes": prazo_dias, "progresso_pct": 0}


def gerar_orientacao_modo_atleta(ficha: dict, meta_status: dict) -> dict:
    """
    Gera as diretrizes de cobrança diária rigorosa para alunos no Modo Atleta / Competição.
    Cobrança disciplinar de:
    1. Treino & Cargas
    2. Timing de Alimentação & Macros
    3. Sono Anabólico (dormir no horário certo)
    4. Fotos do Espelho & Refeições
    """
    nome = (ficha.get("nome_aluno") or "Atleta").strip().split()[0]
    dias_rest = meta_status.get("dias_restantes", 30)
    progresso = meta_status.get("progresso_pct", 0.0)

    cobranças = [
        f"🎯 CONTAGEM REGRESSIVA: Faltam exatamente {dias_rest} dias para o seu objetivo/competição! Zero espaço para deslizes!",
        "🏋️ TREINO DO DIA: Executar cada repetição com cadência perfeita (2s descida, 1s contração máxima). Carga anotada no papel!",
        "🥩 NUTRIÇÃO MILITAR: Bater 2.0g a 2.2g de proteína/kg rigorosamente. Refeição pré-treino 1h30 antes e pós-treino imediato.",
        "💤 SONO ANABÓLICO: Na cama impreterivelmente às 22h30/23h00! É no sono profundo que o GH faz o trabalho pesado de hipertrofia.",
        "📸 MONITORAMENTO VISUAL: Enviar foto do prato principal e foto no espelho semanalmente para calibrarmos a retenção e densidade muscular."
    ]

    return {
        "modo_atleta_ativo": True,
        "aluno": nome,
        "dias_restantes": dias_rest,
        "progresso_pct": progresso,
        "diretrizes_cobranca": cobranças,
        "mensagem_coach": (
            f"Fala, {nome}! 🦁 Modo Atleta de Elite ATIVADO! Faltam {dias_rest} dias pro nosso objetivo!\n\n"
            f"A partir de agora é disciplina militar: treino no horário, macros batidos na balança e sono anabólico às 22h30 sem desculpas!\n\n"
            f"Me manda a foto do seu prato de hoje e do treino cumprido mais tarde! Tamo junto até o pódio! 👊🔥"
        )
    }


async def enviar_presenca_fichas(target_number: str, presence: str = "composing", delay_ms: int = 1500):
    evo_url = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
    evo_key = os.getenv("EVOLUTION_API_KEY", "")
    evo_inst = os.getenv("EVOLUTION_INSTANCE", "sofia")
    try:
        async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
            await client.post(
                f"{evo_url}/chat/sendPresence/{evo_inst}",
                headers={"apikey": evo_key, "Content-Type": "application/json"},
                json={"number": target_number, "presence": presence, "delay": delay_ms}
            )
    except Exception:
        pass

def identificar_campos_pendentes_ficha(ficha: dict) -> dict:
    """
    Inspeciona com rigor cirúrgico a ficha do aluno no Supabase.
    Retorna a lista exata do que ainda falta para a ficha estar 100% preenchida com dados reais.
    REGRA INVIOLÁVEL: NENHUM DADO PODE SER ADIVINHADO OU INVENTADO!
    """
    if not ficha:
        return {"ficha_completa": False, "campos_faltantes": ["Ficha inexistente"], "score_completude": 0}

    nome = (ficha.get("nome") or ficha.get("nome_aluno") or "Aluno").strip().split()[0]
    metas = ficha.get("metas_nutricionais") or {}
    local_treino = ficha.get("local_treino")
    eh_casa = local_treino == "casa"

    # Checagens individuais com tolerância zero para dados inventados/zerados
    idade = ficha.get("idade")
    tem_idade = idade is not None and isinstance(idade, (int, float)) and idade > 0

    peso = ficha.get("ultimo_peso") or metas.get("peso")
    tem_peso = peso is not None and isinstance(peso, (int, float)) and peso > 0

    altura = ficha.get("altura_cm") or metas.get("altura_cm")
    tem_altura = altura is not None and isinstance(altura, (int, float)) and altura > 0

    tem_local = bool(local_treino)
    equipamentos = metas.get("equipamentos_casa")
    tem_equipamentos = bool(equipamentos and str(equipamentos).strip()) if eh_casa else True

    dias = ficha.get("dias_disponiveis_semana")
    tem_dias = dias is not None and isinstance(dias, int) and dias > 0

    tempo = metas.get("tempo_treino_min")
    tem_tempo = tempo is not None and isinstance(tempo, (int, float)) and tempo > 0

    restricoes = ficha.get("restricoes_saude")
    tem_restricoes = bool(restricoes and str(restricoes).strip())

    fotos = ficha.get("fotos_criptografadas") or []
    tem_fotos = isinstance(fotos, list) and len(fotos) > 0

    tem_bioimpedancia = bool(metas.get("dados_bioimpedancia"))

    campos_faltantes = []
    if not tem_idade: campos_faltantes.append("idade_real")
    if not tem_peso: campos_faltantes.append("peso_atual")
    if not tem_altura: campos_faltantes.append("altura")
    if not tem_local: campos_faltantes.append("local_treino")
    if eh_casa and not tem_equipamentos: campos_faltantes.append("equipamentos_em_casa")
    if not tem_dias: campos_faltantes.append("dias_semana")
    if not tem_tempo: campos_faltantes.append("tempo_por_treino")
    if not tem_restricoes: campos_faltantes.append("dores_restricoes_saude")
    if not tem_fotos: campos_faltantes.append("fotos_avaliacao_espelho")
    if not tem_bioimpedancia: campos_faltantes.append("balanca_bioimpedancia")

    total_campos = 10 if eh_casa else 9
    campos_preenchidos = total_campos - len(campos_faltantes)
    score_completude = max(0, min(100, int((campos_preenchidos / total_campos) * 100)))

    return {
        "aluno": nome,
        "score_completude": score_completude,
        "ficha_completa": len(campos_faltantes) == 0,
        "campos_faltantes": campos_faltantes,
        "eh_casa": eh_casa,
        "local_treino": local_treino,
        "tem_idade": tem_idade,
        "tem_peso": tem_peso,
        "tem_altura": tem_altura,
        "tem_local": tem_local,
        "tem_equipamentos": tem_equipamentos,
        "tem_dias": tem_dias,
        "tem_tempo": tem_tempo,
        "tem_restricoes": tem_restricoes,
        "tem_fotos": tem_fotos,
        "tem_bioimpedancia": tem_bioimpedancia
    }

async def extrair_dados_reais_anamnese(texto_aluno: str, ficha_atual: dict = None) -> dict:
    """
    Extrator de Alta Precisão (Personal Trainer & Nutrição):
    Analisa o texto do aluno e extrai APENAS dados que o aluno explicitamente declarou.
    REGRA INVIOLÁVEL: NUNCA INVENTA OU ADIVINHA NENHUM DADO.
    Campos não informados retornam estritamente None.
    """
    if not texto_aluno or not texto_aluno.strip():
        return {}

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    dados_extraidos = {}

    if api_key:
        prompt = (
            "Você é um extrator de prontuário esportivo e clínico de um Personal Trainer de elite. "
            "Analise a mensagem enviada pelo aluno e extraia estritamente os dados que o aluno informou. "
            "REGRA INVIOLÁVEL: NUNCA INVENTE OU ADIVINHE NENHUM DADO. Se o aluno não informou, coloque null.\n\n"
            f'Mensagem do aluno:\n"{texto_aluno}"\n\n'
            "Retorne ESTRITAMENTE um JSON válido (sem markdown, sem backticks):\n"
            "{\n"
            '  "idade": int ou null,\n'
            '  "peso": float ou null,\n'
            '  "altura_cm": float ou null,\n'
            '  "genero": "homem" ou "mulher" ou null,\n'
            '  "local_treino": "casa" ou "academia" ou "ar_livre" ou null,\n'
            '  "equipamentos_casa": string ou null,\n'
            '  "dias_disponiveis_semana": int ou null,\n'
            '  "tempo_treino_min": int ou null,\n'
            '  "restricoes_saude": string ou null,\n'
            '  "objetivo": string ou null\n'
            "}"
        )
        try:
            async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
                res = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://marcaopersonal.com",
                        "X-Title": "Marcao Anamnese Scanner"
                    },
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0
                    }
                )
                if res.status_code == 200:
                    raw = res.json()["choices"][0]["message"]["content"].strip()
                    if raw.startswith("```"):
                        raw = raw.split("```")[1]
                        if raw.startswith("json"):
                            raw = raw[4:].strip()
                    dados_extraidos = json.loads(raw)
        except Exception as e:
            print(f"[FICHAS_ENGINE] Erro no extrator LLM: {e}")

    # Fallback ou reforço via regex para máxima resiliência
    txt_low = texto_aluno.lower()

    # 1. Idade
    if dados_extraidos.get("idade") is None:
        idade_m = re.search(r'\b(\d{1,2})\s*(?:anos|ano|primaveras)\b', txt_low)
        if idade_m and int(idade_m.group(1)) in range(12, 95):
            dados_extraidos["idade"] = int(idade_m.group(1))

    # 2. Peso
    if dados_extraidos.get("peso") is None:
        peso_m = re.search(r'(\d{2,3}(?:[.,]\d+)?)\s*(?:kg|quilos|kilos)\b', txt_low)
        if peso_m:
            try:
                dados_extraidos["peso"] = float(peso_m.group(1).replace(",", "."))
            except Exception:
                pass

    # 3. Altura
    if dados_extraidos.get("altura_cm") is None:
        alt_m = re.search(r'\b(1[.,]\d{2}|1\d{2})\s*(?:m|cm|metro|metros)?\b', txt_low)
        if alt_m:
            try:
                val = float(alt_m.group(1).replace(",", "."))
                dados_extraidos["altura_cm"] = val if val > 3.0 else val * 100.0
            except Exception:
                pass

    # 4. Local de treino
    if dados_extraidos.get("local_treino") is None:
        if any(w in txt_low for w in ["em casa", "minha casa", "treino em casa", "malho em casa", "home"]):
            dados_extraidos["local_treino"] = "casa"
        elif any(w in txt_low for w in ["na academia", "academia", "gym", "smart fit", "musculação"]):
            dados_extraidos["local_treino"] = "academia"

    # 5. Dias na semana
    if dados_extraidos.get("dias_disponiveis_semana") is None:
        dias_m = re.search(r'(\d+)\s*(?:dias|x|vezes)\s*(?:na|por|semana)?', txt_low)
        if dias_m and int(dias_m.group(1)) in range(1, 8):
            dados_extraidos["dias_disponiveis_semana"] = int(dias_m.group(1))

    # 6. Tempo de treino
    if dados_extraidos.get("tempo_treino_min") is None:
        tempo_m = re.search(r'(\d+)\s*(?:min|minutos)\b', txt_low)
        if tempo_m and int(tempo_m.group(1)) in range(15, 180):
            dados_extraidos["tempo_treino_min"] = int(tempo_m.group(1))

    # 7. Restrições e dores articulares
    if dados_extraidos.get("restricoes_saude") is None:
        if any(w in txt_low for w in ["sem dor", "nenhuma dor", "sem lesao", "sem lesão", "tudo certo", "100%", "tudo bem", "saudavel", "saudável"]):
            dados_extraidos["restricoes_saude"] = "Nenhuma dor ou lesão reportada"
        elif any(w in txt_low for w in ["joelho", "coluna", "lombar", "ombro", "hernia", "hérnia", "tendinite", "bursite", "menisco"]):
            dados_extraidos["restricoes_saude"] = texto_aluno.strip()

    # 8. Equipamentos em casa
    if dados_extraidos.get("equipamentos_casa") is None and dados_extraidos.get("local_treino") == "casa":
        if any(w in txt_low for w in ["halter", "halteres", "elastico", "elástico", "caneleira", "colchonete", "peso do corpo", "peso corporal"]):
            dados_extraidos["equipamentos_casa"] = texto_aluno.strip()

    return dados_extraidos

async def atualizar_ficha_com_dados_extraidos(remote_jid: str, texto_aluno: str) -> dict:
    """
    Extrai dados reais da mensagem do aluno e atualiza o Supabase imediatamente.
    Nunca sobrescreve com dados nulos, apenas agrega dados reais confirmados.
    """
    headers = get_supabase_headers()
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.{remote_jid}",
                headers=headers
            )
            if res.status_code != 200 or not res.json():
                return {"sucesso": False, "erro": "Ficha não encontrada"}

            ficha = res.json()[0]
            extraidos = await extrair_dados_reais_anamnese(texto_aluno, ficha)

            patch_data = {}
            metas_patch = dict(ficha.get("metas_nutricionais") or {})

            if extraidos.get("idade"):
                patch_data["idade"] = extraidos["idade"]
            if extraidos.get("peso"):
                patch_data["ultimo_peso"] = extraidos["peso"]
                metas_patch["peso"] = extraidos["peso"]
            if extraidos.get("altura_cm"):
                patch_data["altura_cm"] = extraidos["altura_cm"]
                metas_patch["altura_cm"] = extraidos["altura_cm"]
            if extraidos.get("local_treino"):
                patch_data["local_treino"] = extraidos["local_treino"]
            if extraidos.get("equipamentos_casa"):
                metas_patch["equipamentos_casa"] = extraidos["equipamentos_casa"]
            if extraidos.get("dias_disponiveis_semana"):
                patch_data["dias_disponiveis_semana"] = extraidos["dias_disponiveis_semana"]
            if extraidos.get("tempo_treino_min"):
                metas_patch["tempo_treino_min"] = extraidos["tempo_treino_min"]
            if extraidos.get("restricoes_saude"):
                patch_data["restricoes_saude"] = extraidos["restricoes_saude"]
            if extraidos.get("objetivo") and not ficha.get("objetivo"):
                patch_data["objetivo"] = extraidos["objetivo"]

            if metas_patch != ficha.get("metas_nutricionais"):
                patch_data["metas_nutricionais"] = metas_patch

            if patch_data:
                await atualizar_campo_ficha(remote_jid, patch_data)
                ficha.update(patch_data)
                diag = identificar_campos_pendentes_ficha(ficha)
                return {
                    "sucesso": True,
                    "campos_atualizados": list(patch_data.keys()),
                    "dados_extraidos": extraidos,
                    "score_completude": diag["score_completude"],
                    "ficha_completa": diag["ficha_completa"],
                    "campos_faltantes": diag["campos_faltantes"]
                }
            return {"sucesso": True, "nenhum_dado_novo": True}
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro ao atualizar ficha com dados extraídos: {e}")
        return {"sucesso": False, "erro": str(e)}

async def cobrar_dados_pendentes_aluno(ficha: dict) -> dict:
    """
    Dispara acompanhamento amigável e personalizado do Marcão em múltiplos balões curtos
    (Regra 5: 2 a 4 balões, composing, delays naturais de 1.5s a 2.0s) para coletar exatamente
    os dados ou fotos que faltam na ficha do aluno. NUNCA ADIVINHA OU INVENTA DADOS!
    """
    import asyncio
    nome = (ficha.get("nome") or ficha.get("nome_aluno") or "Campeão(ã)").strip()
    primeiro_nome = nome.split()[0]
    remote_jid = ficha.get("remote_jid", "")
    tel = ficha.get("telefone") or "".join(filter(str.isdigit, remote_jid.split("@")[0]))
    if not tel:
        return {"sucesso": False, "erro": "Telefone inválido"}

    evo_url = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
    evo_key = os.getenv("EVOLUTION_API_KEY", "")
    evo_inst = os.getenv("EVOLUTION_INSTANCE", "sofia")

    diag = identificar_campos_pendentes_ficha(ficha)
    if diag["ficha_completa"]:
        return {"sucesso": True, "pendente": False, "mensagem": "Ficha 100% preenchida com dados reais!"}

    objetivo = ficha.get("objetivo") or ""
    eh_casa = diag["eh_casa"] or "casa" in (ficha.get("local_treino") or "").lower()

    baloes = []

    # Balão 1: Saudação amigável personalizada (Regra 5: 80-130 chars)
    if eh_casa:
        baloes.append(f"Fala, {primeiro_nome}! Tudo na paz? 🦁 Marcão aqui! Como você treina em casa, vou montar seu treino sob medida sem adivinhar nada.")
    elif diag["local_treino"] == "academia":
        baloes.append(f"Fala, {primeiro_nome}! Tudo na paz? 🦁 Marcão aqui! Tô montando sua planilha de academia sob medida pra sua rotina.")
    else:
        baloes.append(f"Fala, {primeiro_nome}! Tudo na paz? 🦁 Marcão aqui! Pra eu montar seu protocolo sob medida, me tira só umas dúvidas rápidas:")

    # Balão 2: Medidas corporais e rotina (Regra 5: 50-120 chars)
    perguntas_b2 = []
    faltas_corpo = []
    if not diag["tem_idade"]: faltas_corpo.append("sua idade real")
    if not diag["tem_peso"]: faltas_corpo.append("peso atual")
    if not diag["tem_altura"]: faltas_corpo.append("altura")
    if faltas_corpo:
        perguntas_b2.append(f"Qual {', '.join(faltas_corpo)}?")
    if not diag["tem_dias"]:
        perguntas_b2.append("Quantos dias na semana consegue treinar?")
    if perguntas_b2:
        baloes.append(" ".join(perguntas_b2))

    # Balão 3: Local/equipamentos em casa e dores (Regra 5: 50-130 chars)
    perguntas_b3 = []
    if not diag["local_treino"]:
        perguntas_b3.append("Você vai treinar em casa ou na academia?")
    elif eh_casa and not diag.get("tem_equipamentos"):
        perguntas_b3.append("Em casa você tem algum halter/elástico ou é só peso do corpo?")
    if not diag["tem_restricoes"]:
        perguntas_b3.append("Sente dor no joelho, coluna ou tem restrição médica?")
    if perguntas_b3:
        baloes.append(" ".join(perguntas_b3))

    # Balão 4: Fotos / Balança / Fechamento acolhedor (Regra 5: 80-120 chars)
    if not diag["tem_fotos"] or not diag["tem_bioimpedancia"]:
        baloes.append("Quando der, manda 1 foto no espelho e do visor da balança pro prontuário blindado! Tamo junto! 👊🔥")
    else:
        baloes.append("Me manda aqui no seu tempo que assim que responder eu fecho seu treino com todo o carinho! Tamo junto! 👊🔥")

    # Envio sequencial dos balões com simulação de presença (composing)
    resultados_envio = []
    try:
        async with httpx.AsyncClient(verify=False, timeout=20.0) as client:
            for i, balao in enumerate(baloes):
                # 1. Simula digitando
                await enviar_presenca_fichas(tel, "composing", delay_ms=1800)
                await asyncio.sleep(1.6)

                # 2. Envia balão
                resp = await client.post(
                    f"{evo_url}/message/sendText/{evo_inst}",
                    headers={"apikey": evo_key, "Content-Type": "application/json"},
                    json={"number": tel, "text": balao}
                )
                resultados_envio.append(resp.status_code in (200, 201))

                # 3. Pequeno delay entre balões
                if i < len(baloes) - 1:
                    await asyncio.sleep(1.2)

        # Atualiza timestamp de follow-up na ficha
        try:
            await atualizar_campo_ficha(remote_jid, {"ultimo_followup_pendencias_em": datetime.now().isoformat()})
        except Exception:
            pass

        return {
            "sucesso": all(resultados_envio),
            "remote_jid": remote_jid,
            "telefone": tel,
            "aluno": nome,
            "score_completude": diag["score_completude"],
            "campos_faltantes": diag["campos_faltantes"],
            "baloes_enviados": len(baloes)
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

async def verificar_e_cobrar_alunos_com_dados_pendentes(filtro_aluno: str = None) -> list:
    """
    Verifica todas as fichas de alunos VIP no Supabase.
    Identifica faltas de dados ou fotos e dispara contato amigável em múltiplos balões.
    Se filtro_aluno for informado (ex: 'eva'), foca no aluno específico.
    """
    headers = get_supabase_headers()
    resultados = []
    try:
        async with httpx.AsyncClient(verify=False, timeout=20.0) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=*",
                headers=headers
            )
            if res.status_code == 200:
                fichas = res.json()
                for f in fichas:
                    nome_f = (f.get("nome") or f.get("nome_aluno") or "").lower()
                    tel_f = (f.get("telefone") or "").lower()

                    # Se houver filtro e não bater, pula
                    if filtro_aluno:
                        filtro_low = filtro_aluno.strip().lower()
                        tokens_nome = [w.lower() for w in nome_f.split()]
                        bate_nome = any(filtro_low == t for t in tokens_nome) or (len(filtro_low) > 3 and filtro_low in nome_f)
                        bate_tel = filtro_low in tel_f
                        if not (bate_nome or bate_tel):
                            continue

                    # Não cobrar o próprio Evandro em ambiente de produção (a menos que explicitamente filtrado por 'evandro')
                    if "84587255" in tel_f and (not filtro_aluno or "evandro" not in filtro_aluno.lower()):
                        continue

                    r_jid = f.get("remote_jid")
                    if r_jid:
                        cob = await cobrar_dados_pendentes_aluno(f)
                        resultados.append(cob)
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro na checagem de dados pendentes: {e}")
    return resultados

