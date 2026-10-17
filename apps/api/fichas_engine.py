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

            # Se não existe, cria ficha inicial
            payload = {
                "remote_jid": remote_jid,
                "telefone": telefone,
                "nome_aluno": nome,
                "etapa_onboarding": 0,
                "consentimento_lgpd": False,
                "dias_disponiveis_semana": 3,
                "local_treino": "academia",
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
    nivel_atividade: str = "moderado"
) -> dict:
    """
    Motor Clínico Integrado (Personal + Nutricionista + Clínico Geral).
    Calcula com precisão médica/esportiva:
    - IMC (com classificação médica da OMS)
    - TMB (Equação de Mifflin-St Jeor para Homens e Mulheres)
    - GET (Gasto Energético Total baseado no fator de atividade)
    - Meta calórica ajustada por objetivo (déficit ou superávit)
    - Meta hídrica (35ml/kg)
    - Divisão de Macronutrientes (Proteína 2.0g/kg, Gordura 0.8g/kg, Carboidrato residual)
    - Triagem Clínica Geral (restrições articulares, patologias e recomendações de segurança)
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

    # 5. Meta Hídrica (35ml/kg)
    agua_ml = int(peso * 35)

    # 6. Macronutrientes
    proteina_g = round(peso * 2.0, 1)
    gordura_g = round(peso * 0.8, 1)
    cal_proteina = proteina_g * 4
    cal_gordura = gordura_g * 9
    cal_restante = max(0, calorias_diarias - cal_proteina - cal_gordura)
    carbo_g = round(cal_restante / 4.0, 1)

    # 7. Triagem Clínica & Cuidados Biomecânicos
    rest_low = restricoes.lower() if restricoes else ""
    cuidados = []
    if any(w in rest_low for w in ["joelho", "menisco", "patela", "condromalacia"]):
        cuidados.append("Evitar impacto e flexão profunda > 90° em cadeia aberta. Foco em fortalecimento de vasto medial e glúteo médio.")
    if any(w in rest_low for w in ["coluna", "lombar", "hernia", "ciatico"]):
        cuidados.append("Zero compressão axial livre na coluna. Proibido levantamento terra pesado ou agachamento com barra nas costas. Substituir por leg press e exercícios guiados.")
    if any(w in rest_low for w in ["ombro", "manguito", "bursite"]):
        cuidados.append("Sem desenvolvimento acima da linha da cabeça. Priorizar elevações no plano escapular (30° anterior) e fortalecimento de rotadores externos.")
    if any(w in rest_low for w in ["pressao", "hipertensao"]):
        cuidados.append("Evitar Manobra de Valsalva (não prender a respiração no esforço máximo). Monitorar frequência cardíaca.")

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
            "restricoes_reportadas": restricoes or "Nenhuma restrição clínica severa",
            "cuidados_biomecanicos": cuidados if cuidados else ["Nenhuma contraindicação. Aluno(a) liberado(a) para sobrecarga progressiva."]
        },
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

    if etapa == 0:
        resposta = (
            f"Fala, {primeiro_nome}! 🦁 Marcão Personal na área! Parabéns por garantir seu acesso VIP oficial!\n\n"
            f"Tô aqui pra te acompanhar de verdade no seu WhatsApp! Pra eu abrir sua ficha oficial no nosso sistema e calcular seus macros e TMB com precisão cirúrgica, me conta:\n\n"
            f"👉 *Qual é o seu objetivo número 1 hoje?* (Secar barriga, ganhar massa muscular, definição corporal ou saúde?)\n"
            f"👉 E se souber, me passa também sua *altura e peso aproximados*! (Ou foto do visor da sua balança!)"
        )
        await atualizar_campo_ficha(remote_jid, {"etapa_onboarding": 1})
        return {"onboarding_ativo": True, "resposta": resposta}

    elif etapa == 1:
        txt = texto_recebido.strip()
        # Tenta extrair peso e altura
        peso_match = re.search(r'(\d{2,3}(?:[.,]\d+)?)\s*(?:kg|quilos)?', txt.lower())
        altura_match = re.search(r'(?:1[.,]\d{2}|1\d{2})\s*(?:m|cm)?', txt.lower())

        peso_val = float(peso_match.group(1).replace(',', '.')) if peso_match else None
        altura_val = None
        if altura_match:
            alt_str = altura_match.group(0).replace(',', '.').replace('m', '').replace('cm', '').strip()
            try:
                alt_num = float(alt_str)
                altura_val = alt_num if alt_num > 3.0 else alt_num * 100.0
            except Exception:
                pass

        dados_patch = {
            "objetivo": txt,
            "etapa_onboarding": 2
        }
        if peso_val: dados_patch["ultimo_peso"] = peso_val
        if altura_val: dados_patch["altura_cm"] = altura_val

        resposta = (
            f"Meta traçada, {primeiro_nome}! Vamos buscar esse resultado juntos! 💪\n\n"
            f"Agora me fala sobre a sua rotina semanal: *Quantos dias por semana você consegue treinar e onde prefere?* (Academia de musculação ou treinos em casa com objetos simples tipo cabo de vassoura e cadeira?)"
        )
        await atualizar_campo_ficha(remote_jid, dados_patch)
        return {"onboarding_ativo": True, "resposta": resposta}

    elif etapa == 2:
        rotina_declarada = texto_recebido.strip()
        local = "casa" if "casa" in rotina_declarada.lower() else "academia"
        dias_match = re.search(r'(\d+)', rotina_declarada)
        dias_num = int(dias_match.group(1)) if dias_match else 3

        idade_match = re.search(r'(\d{1,2})\s*anos', rotina_declarada.lower())
        idade_val = int(idade_match.group(1)) if idade_match else ficha.get("idade")

        dados_patch = {
            "dias_disponiveis_semana": dias_num,
            "local_treino": local,
            "etapa_onboarding": 3
        }
        if idade_val:
            dados_patch["idade"] = idade_val

        resposta = (
            f"Excelente! {dias_num} dias por semana é um ritmo perfeito pra consolidar constância!\n\n"
            f"Agora uma pergunta fundamental de saúde e segurança: *Qual a sua idade aproximada e você tem alguma dor, lesão no joelho, coluna, ombro ou toma algum remédio contínuo?* (Pode ser 100% sincero que eu adapto tudo pra você!)"
        )
        await atualizar_campo_ficha(remote_jid, dados_patch)
        return {"onboarding_ativo": True, "resposta": resposta}

    elif etapa == 3:
        restricoes_declaradas = texto_recebido.strip()
        idade_match = re.search(r'(\d{1,2})\s*anos?', restricoes_declaradas.lower())
        idade_val = int(idade_match.group(1)) if idade_match else ficha.get("idade")

        dados_patch = {
            "restricoes_saude": restricoes_declaradas,
            "etapa_onboarding": 4
        }
        if idade_val:
            dados_patch["idade"] = idade_val

        await atualizar_campo_ficha(remote_jid, dados_patch)
        termo = gerar_termo_lgpd(primeiro_nome)
        return {"onboarding_ativo": True, "resposta": termo}

    elif etapa == 4:
        txt_low = texto_recebido.lower()
        autorizou = any(w in txt_low for w in ["concordo", "ciente", "autorizo", "aceito", "sim", "com certeza", "pode", "ok", "claro", "bora"])

        if not autorizou:
            resposta = (
                f"Opa, {primeiro_nome}! 🦁 Entendo você perfeitamente!\n\n"
                f"Mas pela nossa segurança jurídica e respeito à Lei Geral de Proteção de Dados (LGPD), nossos treinos e acompanhamento personalizado só podem ser liberados após você confirmar ciência e responsabilidade!\n\n"
                f"Para ativarmos sua rotina e começarmos com segurança, basta me responder apenas:\n"
                f"👉 *CONCORDO*\n\n"
                f"Assim que você responder, sua ficha oficial é liberada na hora! Tamo junto!"
            )
            return {"onboarding_ativo": True, "resposta": resposta, "bloqueado_lgpd": True}

        # Usuário confirmou expressamente com CONCORDO / CIENTE / SIM
        obj = ficha.get("objetivo") or "Secar barriga e definir"
        loc = ficha.get("local_treino") or "casa"
        rest = ficha.get("restricoes_saude") or "Nenhuma"
        idade = ficha.get("idade")
        genero = ficha.get("genero", "mulher")
        peso = ficha.get("ultimo_peso") or 68.0
        altura = ficha.get("altura_cm") or 165.0

        treino = gerar_treino_personalizado(obj, loc, rest, idade=idade, genero=genero)
        diag = calcular_diagnostico_clinico_completo(peso, altura, idade or 30, genero, obj, rest)

        await atualizar_campo_ficha(remote_jid, {
            "consentimento_lgpd": True,
            "data_consentimento_lgpd": datetime.utcnow().isoformat(),
            "termo_lgpd_versao": "v2.0_lgpd",
            "treino_atual": treino,
            "diagnostico_clinico": diag,
            "metas_nutricionais": diag.get("macros", {}),
            "etapa_onboarding": 5,
            "status_acompanhamento": "ativo"
        })

        resposta = (
            f"Show de bola, {primeiro_nome}! Termo formalizado e sua Ficha VIP de Aluno está 100% ATIVA! 🛡️🔐\n\n"
            f"Montei seu protocolo sob medida:\n"
            f"🏋️ *{treino['estilo_periodizacao']}* ({treino['local']})\n"
            f"⚠️ *Cuidados:* {treino['cuidados_especiais']}\n\n"
            f"📋 *Sua Divisão de Treinos:*\n"
            f"• *Treino A:* {treino['treino_a']}\n\n"
            f"• *Treino B:* {treino['treino_b']}\n\n"
            f"• *Treino C:* {treino['treino_c']}\n\n"
            f"📸 Pra calibrarmos sua evolução visual, quando puder tire uma foto no espelho de frente e de costas e me mande aqui! Elas já ficam criptografadas na hora. Tamo junto nessa! 🔥"
        )
        return {"onboarding_ativo": False, "resposta": resposta, "treino": treino}

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


async def cobrar_dados_pendentes_aluno(remote_jid: str, nome: str = "Aluno(a)") -> dict:
    """
    Dispara cobrança conversacional, amigável e próxima do Marcão para o aluno preencher
    seus dados reais (peso, altura, idade, objetivo, dores). Zero dados fictícios.
    """
    primeiro_nome = nome.strip().split()[0] if nome else "Guerreira"
    tel = "".join(filter(str.isdigit, remote_jid.split("@")[0]))
    if not tel:
        return {"sucesso": False, "erro": "Telefone inválido"}

    mensagem = (
        f"Fala, {primeiro_nome}! Tudo na paz por aí? 🦁 Marcão passando pra dar um toque rápido e super amigo!\n\n"
        f"Pra eu deixar seu treino e seus macros 100% afinados sem inventar nenhum número, preciso dos seus dados reais:\n"
        f"1️⃣ Seu peso atual aproximado (ou foto do visor da balança);\n"
        f"2️⃣ Sua altura e idade aproximadas;\n"
        f"3️⃣ Se você tem alguma dorzinha no joelho, coluna ou ombro.\n\n"
        f"Me manda aqui no seu tempo que assim que você me responder eu monto sua ficha real com o maior carinho! Tamo junto! 💪👊"
    )

    evo_url = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
    evo_key = os.getenv("EVOLUTION_API_KEY", "")
    evo_inst = os.getenv("EVOLUTION_INSTANCE", "sofia")

    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            resp = await client.post(
                f"{evo_url}/message/sendText/{evo_inst}",
                headers={"apikey": evo_key, "Content-Type": "application/json"},
                json={"number": tel, "text": mensagem}
            )
            return {
                "sucesso": resp.status_code in (200, 201),
                "remote_jid": remote_jid,
                "mensagem": mensagem,
                "status_code": resp.status_code
            }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


async def verificar_e_cobrar_alunos_com_dados_pendentes() -> list:
    """
    Verifica todas as fichas de alunos VIP ativas no Supabase.
    Se a ficha não possuir peso real ou estiver com onboarding incompleto,
    dispara a cobrança conversacional do Marcão de forma totalmente amigável.
    """
    headers = get_supabase_headers()
    resultados = []
    try:
        async with httpx.AsyncClient(verify=False, timeout=20.0) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?select=id,remote_jid,nome,nome_aluno,telefone,etapa_onboarding,metas_nutricionais,objetivo,consentimento_lgpd",
                headers=headers
            )
            if res.status_code == 200:
                fichas = res.json()
                for f in fichas:
                    etapa = f.get("etapa_onboarding", 0)
                    tem_peso = bool(f.get("metas_nutricionais", {}).get("peso"))
                    tem_obj = bool(f.get("objetivo"))
                    # Se faltar dados fundamentais
                    if etapa < 4 or not tem_peso or not tem_obj:
                        r_jid = f.get("remote_jid")
                        nome = f.get("nome") or f.get("nome_aluno") or "Aluno"
                        if r_jid:
                            cob = await cobrar_dados_pendentes_aluno(r_jid, nome)
                            resultados.append(cob)
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro na checagem de dados pendentes: {e}")
    return resultados

