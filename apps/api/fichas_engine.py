import os
import re
import json
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

from encryption_service import criptografar_foto, gerar_termo_lgpd

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
            return res.status_code in (200, 204)
    except Exception as e:
        print(f"[FICHAS_ENGINE] Erro ao atualizar ficha: {e}")
        return False

def gerar_treino_personalizado(objetivo: str, local: str, restricoes: str) -> dict:
    restricoes_lower = restricoes.lower() if restricoes else ""
    tem_dor_joelho = any(w in restricoes_lower for w in ["joelho", "menisco", "patela", "condromalacia"])
    tem_dor_ombro = any(w in restricoes_lower for w in ["ombro", "manguito", "clavicula", "bursite"])
    tem_dor_coluna = any(w in restricoes_lower for w in ["coluna", "lombar", "hernia", "ciatico", "dor nas costas"])

    estilo = "Foco em Hipertrofia & Força" if "massa" in objetivo.lower() or "hipertrofia" in objetivo.lower() else "Queima Acelerada & Definição Metabólica"

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

    return {
        "estilo_periodizacao": estilo,
        "local": "Academia de Musculação" if "academia" in local.lower() else "Treino Adaptado em Casa",
        "cuidados_especiais": f"Treino blindado contra dores: {restricoes}",
        "treino_a": f"Peitoral, Ombro & Tríceps: {peito_treino} + {ombro_treino}",
        "treino_b": f"Dorsal, Trapézio & Bíceps: {costas_treino}",
        "treino_c": f"Membros Inferiores & Core: {pernas_treino} + Prancha isométrica segura"
    }

async def processar_etapa_onboarding(remote_jid: str, telefone: str, nome: str, texto_recebido: str, ficha: dict) -> dict:
    etapa = ficha.get("etapa_onboarding", 0)
    primeiro_nome = nome.strip().split()[0] if nome else "Guerreiro(a)"

    if etapa == 0:
        resposta = (
            f"Fala, {primeiro_nome}! 🦁 Marcão Personal na área! Parabéns por garantir sua Balança de Bioimpedância oficial!\n\n"
            f"Tô aqui pra te acompanhar de verdade nesses 3 meses gratuitos direto no seu WhatsApp! Pra eu montar sua rotina de treino personalizada e calcular seus macros na ponta do lápis, me conta:\n\n"
            f"👉 *Qual é o seu objetivo principal hoje?* Secar a barriga, ganhar massa muscular com força ou definir o corpo todo?"
        )
        await atualizar_campo_ficha(remote_jid, {"etapa_onboarding": 1})
        return {"onboarding_ativo": True, "resposta": resposta}

    elif etapa == 1:
        objetivo_declarado = texto_recebido.strip()
        resposta = (
            f"Meta traçada, {primeiro_nome}! Vamos buscar esse resultado juntos! 💪\n\n"
            f"Agora me fala sobre a sua rotina semanal: *Quantos dias por semana você consegue treinar e onde prefere?* (Academia de musculação ou treinos em casa?)"
        )
        await atualizar_campo_ficha(remote_jid, {
            "objetivo": objetivo_declarado,
            "etapa_onboarding": 2
        })
        return {"onboarding_ativo": True, "resposta": resposta}

    elif etapa == 2:
        rotina_declarada = texto_recebido.strip()
        local = "academia" if "academia" in rotina_declarada.lower() else "casa"
        dias_match = re.search(r'(\d+)', rotina_declarada)
        dias_num = int(dias_match.group(1)) if dias_match else 3

        resposta = (
            f"Excelente! {dias_num} dias é um ritmo excelente pra gente consolidar consistência sem sobrecarregar!\n\n"
            f"Agora uma pergunta fundamental de saúde e segurança: *Você tem alguma dor, lesão antiga no joelho, coluna, ombro, hérnia ou qualquer restrição médica?* (Pode ser 100% sincero que eu adapto tudo pra você!)"
        )
        await atualizar_campo_ficha(remote_jid, {
            "dias_disponiveis_semana": dias_num,
            "local_treino": local,
            "etapa_onboarding": 3
        })
        return {"onboarding_ativo": True, "resposta": resposta}

    elif etapa == 3:
        restricoes_declaradas = texto_recebido.strip()
        termo = gerar_termo_lgpd(primeiro_nome)
        await atualizar_campo_ficha(remote_jid, {
            "restricoes_saude": restricoes_declaradas,
            "etapa_onboarding": 4
        })
        return {"onboarding_ativo": True, "resposta": termo}

    elif etapa == 4:
        txt_low = texto_recebido.lower()
        autorizou = any(w in txt_low for w in ["sim", "autorizo", "com certeza", "pode", "ok", "claro", "aceito", "bora"])

        if autorizou:
            obj = ficha.get("objetivo") or "Secar barriga e definir"
            loc = ficha.get("local_treino") or "academia"
            rest = ficha.get("restricoes_saude") or "Nenhuma"
            treino = gerar_treino_personalizado(obj, loc, rest)

            await atualizar_campo_ficha(remote_jid, {
                "consentimento_lgpd": True,
                "data_consentimento_lgpd": datetime.utcnow().isoformat(),
                "treino_atual": treino,
                "etapa_onboarding": 5,
                "status_acompanhamento": "ativo"
            })

            resposta = (
                f"Show de bola, {primeiro_nome}! Seu termo foi formalizado e sua Ficha VIP de Aluno está 100% ATIVA! 🛡️🔐\n\n"
                f"Já montei a estrutura do seu protocolo sob medida:\n"
                f"🏋️ *{treino['estilo_periodizacao']}* ({treino['local']})\n"
                f"⚠️ *Cuidados:* {treino['cuidados_especiais']}\n\n"
                f"📋 *Divisão Inicial:*\n"
                f"• *Treino A:* {treino['treino_a']}\n"
                f"• *Treino B:* {treino['treino_b']}\n"
                f"• *Treino C:* {treino['treino_c']}\n\n"
                f"📸 Pra calibrarmos seu ponto de partida com precisão visual, me manda uma foto de frente e de costas no espelho! Pode ficar 100% em paz: elas já serão criptografadas na hora com chave militar privada. Tamo junto!"
            )
            return {"onboarding_ativo": False, "resposta": resposta, "treino": treino}
        else:
            resposta = (
                f"Sem problemas, {primeiro_nome}! Respeito total à sua privacidade. "
                f"Vamos seguir com o acompanhamento 100% focado no peso da Balança, nas metas de água e nos treinos semanais, sem necessidade de fotos corporais! Bora pra cima! 💪"
            )
            await atualizar_campo_ficha(remote_jid, {
                "consentimento_lgpd": False,
                "etapa_onboarding": 5,
                "status_acompanhamento": "ativo"
            })
            return {"onboarding_ativo": False, "resposta": resposta}

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
    """Dispara mensagem de texto direta no WhatsApp via Evolution API."""
    if not EVOLUTION_API_KEY or not target_number:
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
