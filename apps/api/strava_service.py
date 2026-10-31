"""
========================================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
SERVIÇO DE INTEGRAÇÃO STRAVA & SMARTWATCH (APPLE / ANDROID / GARMIN)
========================================================================================
Conecta a conta oficial e os alunos ao Strava para monitoramento de treinos de corrida,
ciclismo e cardio, avaliando frequência cardíaca (Zonas 1 a 5), ritmo (pace) e
classificando o treino entre 'Treino de Monstro' vs 'Treino Fofo'.
Exclusivo para clientes que possuem a Balança de Bioimpedância VIP (3 meses grátis -> R$ 19,90).
========================================================================================
"""

import os
import json
import ssl
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID', '')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET', '')
STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN', '')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN', '')
STRAVA_VERIFY_TOKEN = os.getenv('STRAVA_VERIFY_TOKEN', '')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qkopgftfrfftoyndhhfj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'https://api.marcaopersonal.com')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', '')


def renovar_token_strava(refresh_token: str = None) -> dict:
    """
    Renova o token de acesso do Strava usando o refresh_token.
    Retorna o dicionário com novo access_token, expires_at e refresh_token.
    """
    r_token = refresh_token or STRAVA_REFRESH_TOKEN
    url = 'https://www.strava.com/oauth/token'
    data = urllib.parse.urlencode({
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': r_token
    }).encode('utf-8')

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, data=data, method='POST')

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print('[STRAVA] Token renovado com sucesso! Expira em:', res_data.get('expires_at'))
            return {
                'success': True,
                'access_token': res_data.get('access_token'),
                'refresh_token': res_data.get('refresh_token'),
                'expires_at': res_data.get('expires_at')
            }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f'[STRAVA] Erro ao renovar token ({e.code}):', err_body)
        return {'success': False, 'status': e.code, 'error': err_body}
    except Exception as e:
        print('[STRAVA] Erro inesperado ao renovar token:', str(e))
        return {'success': False, 'error': str(e)}


def gerar_link_oauth_aluno(telefone: str, redirect_uri: str = 'https://api.marcaopersonal.com/api/integracoes/strava/callback') -> str:
    """
    Gera o link de autorização em 1 clique para o aluno conectar o Strava no WhatsApp.
    O telefone do aluno é enviado no parâmetro 'state' para vincular a conta automaticamente.
    """
    tel_limpo = ''.join([c for c in telefone if c.isdigit()])
    params = {
        'client_id': STRAVA_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'approval_prompt': 'auto',
        'scope': 'read,activity:read_all',
        'state': tel_limpo
    }
    return f'https://www.strava.com/oauth/authorize?{urllib.parse.urlencode(params)}'


def trocar_codigo_por_token(code: str) -> dict:
    """
    Troca o authorization_code enviado pelo Strava após autorização do aluno por tokens definitivos.
    """
    url = 'https://www.strava.com/oauth/token'
    data = urllib.parse.urlencode({
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code
    }).encode('utf-8')

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, data=data, method='POST')

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return {'success': True, 'data': res_data}
    except urllib.error.HTTPError as e:
        return {'success': False, 'status': e.code, 'error': e.read().decode('utf-8')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def obter_detalhes_atividade(activity_id: int, access_token: str) -> dict:
    """
    Busca os detalhes completos de um treino no Strava (distância, tempo, FC média, FC máxima, pace).
    """
    url = f'https://www.strava.com/api/v3/activities/{activity_id}'
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return {'success': True, 'data': json.loads(response.read().decode('utf-8'))}
    except urllib.error.HTTPError as e:
        err_txt = e.read().decode('utf-8')
        return {'success': False, 'status': e.code, 'error': err_txt}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def diagnosticar_treino_fisiologico(atividade: dict, nome_aluno: str = 'Guerreiro') -> list:
    """
    Analisa os dados brutos da atividade do Strava e gera o feedback humanizado do Marcão
    em 2 a 3 balões curtos para o WhatsApp, classificando FC e esforço.
    """
    tipo = atividade.get('type', 'Corrida')
    dist_m = atividade.get('distance', 0)
    dist_km = round(dist_m / 1000.0, 2)
    moving_time_s = atividade.get('moving_time', 0)
    duracao_min = round(moving_time_s / 60.0)
    fc_media = atividade.get('average_heartrate')
    fc_max = atividade.get('max_heartrate')
    calorias = atividade.get('calories') or round(duracao_min * 8.5)
    
    # Calcular Pace (min/km)
    pace_str = ''
    if dist_km > 0 and moving_time_s > 0:
        sec_per_km = moving_time_s / dist_km
        pace_min = int(sec_per_km // 60)
        pace_sec = int(sec_per_km % 60)
        pace_str = f'{pace_min}\'{pace_sec:02d}"/km'

    primeiro_nome = nome_aluno.split()[0]
    eh_fofo = False
    diagnostico = ''

    if fc_media:
        fc_med = int(round(fc_media))
        fc_topo = int(round(fc_max)) if fc_max else fc_med + 15

        if fc_med >= 168:
            diagnostico = f'Olhei seu Strava: você correu {dist_km}km em {duracao_min}min com FC média de {fc_med} bpm (Zona 4/5)! Ritmo agressivo! Se era rodagem leve, você puxou demais o coração, guerreiro! Segura na Zona 2 na próxima!'
        elif fc_med <= 125 and duracao_min < 25:
            eh_fofo = True
            diagnostico = f'Olhei seus batimentos no Strava: {dist_km}km com FC média de só {fc_med} bpm em {duracao_min}min! Foi um trote bem leve, hoje o treino foi meio fofo, hein? Hahaha! Bora apertar o passo no próximo! 😄'
        else:
            diagnostico = f'Corrida de respeito registrada: {dist_km}km em {duracao_min}min (pace {pace_str}) com FC média cravada em {fc_med} bpm! Excelente controle aeróbico e queima de gordura!'
    else:
        # Sem medidor de batimentos (sem monitor cardíaco no treino)
        diagnostico = f'Treino de {tipo} no Strava registrado: {dist_km}km em {duracao_min}min com pace médio de {pace_str}! Ritmo muito constante!'

    baloes = [
        f'Fala, {primeiro_nome}! 🦁 Treinador Marcão na área! Vi seu treino de {tipo.lower()} no Strava agora! 🏃‍♂️💨',
        diagnostico,
        'Bebe água agora, toma sua dose de Creatina pra recuperar as fibras e parabéns pela disciplina! Tamo junto! 👊🔥' if not eh_fofo else 'Sem desculpas no próximo treino! Bebe água agora e bora pra cima! 👊💪'
    ]

    return baloes




def buscar_atividades_aluno_strava(access_token: str, start_epoch: int = None) -> list:
    """
    Busca as atividades registradas no Strava a partir de um timestamp epoch (ex: início do dia).
    """
    if not access_token:
        return []
    url = "https://www.strava.com/api/v3/athlete/activities?per_page=10"
    if start_epoch:
        url += f"&after={start_epoch}"

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("[STRAVA] Erro ao buscar atividades do aluno:", e)
        return []


def gerar_bronca_treino_faltoso(nome_aluno: str, dia_semana: str) -> list:
    """
    Gera a bronca construtiva e motivadora de Personal Trainer quando o aluno
    deveria ter treinado hoje mas NÃO registrou treino no Strava.
    SOMENTE NOS DIAS DE TREINO DO ALUNO.
    """
    primeiro_nome = (nome_aluno or "Guerreiro").strip().split()[0]
    return [
        f"Fala, {primeiro_nome}! 🦁 Marcão aqui na ronda das 22h conferindo as planilhas!",
        f"Passei o olho aqui no seu Strava e cadê o treino de hoje? Hoje é {dia_semana}, dia oficial de treino na sua planilha!",
        "Não me mata o treino não, guerreiro(a)! Disciplina é o que separa quem tem resultado de quem fica na promessa. Amanhã quero foco total! 👊🦁"
    ]


async def executar_auditoria_strava_noturna_22h(forcar_dia: str = None) -> dict:
    """
    Auditoria Noturna às 22h dos Treinos do Strava:
    - SOMENTE NOS DIAS DE TREINO DO ALUNO!
    - Se o aluno treinou: analisa frequência cardíaca, pace, intensidade e dá conselhos de personal trainer.
    - Se o aluno faltou (não registrou treino no dia agendado): DÁ A BRONCA DE PERSONAL!
    - Se não conectou o Strava e faz academia/esporte: envia lembrete para conectar o relógio ou garantir o smartwatch.
    """
    import httpx
    import asyncio
    from datetime import datetime, time as dtime

    dias_map = {0: "segunda", 1: "terça", 2: "quarta", 3: "quinta", 4: "sexta", 5: "sábado", 6: "domingo"}
    agora = datetime.now()
    dia_hoje = (forcar_dia or dias_map[agora.weekday()]).lower()

    # Normalizador para conferência robusta (sem acentos)
    def normalizar_dia(d):
        return str(d).lower().replace("terça", "terca").replace("sábado", "sabado").strip()

    dia_hoje_norm = normalizar_dia(dia_hoje)

    # Início do dia atual em epoch para filtrar treinos de hoje
    hoje_inicio_epoch = int(datetime.combine(agora.date(), dtime.min).timestamp())

    evo_url = os.getenv("EVOLUTION_API_URL", "https://evolution.marcaopersonal.com")
    evo_key = os.getenv("EVOLUTION_API_KEY", "")
    evo_inst = os.getenv("EVOLUTION_INSTANCE", "sofia")

    headers_sb = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    relatorio_execucao = {
        "data_execucao": agora.isoformat(),
        "dia_semana": dia_hoje,
        "alunos_auditados": [],
        "treinos_elogiados": 0,
        "broncas_aplicadas": 0,
        "lembretes_conexao": 0,
        "alunos_em_descanso_ignorados": 0
    }

    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            res = await client.get(f"{SUPABASE_URL}/rest/v1/fichas_alunos", headers=headers_sb)
            if res.status_code != 200:
                return {"sucesso": False, "erro": f"Erro Supabase: {res.status_code}"}
            alunos = res.json()
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

    for ficha in alunos:
        nome = (ficha.get("nome") or ficha.get("nome_aluno") or "Aluno").strip()
        primeiro_nome = nome.split()[0]
        tel = ficha.get("telefone") or "".join(filter(str.isdigit, ficha.get("remote_jid", "").split("@")[0]))
        if not tel:
            continue

        dias_treino_cadastrados = [normalizar_dia(d) for d in (ficha.get("dias_treino") or [])]
        dias_disp = ficha.get("dias_disponiveis_semana") or 0
        local_treino = ficha.get("local_treino") or ""

        # REGRA MANDATÓRIA: SOMENTE NOS DIAS DE TREINO DO ALUNO!
        # Se os dias específicos estiverem cadastrados, checa se hoje é dia de treino dele
        eh_dia_de_treino = dia_hoje_norm in dias_treino_cadastrados

        # Se não tiver dias específicos fixados na lista, mas o aluno treina 3+ dias na semana e treina hoje:
        if not dias_treino_cadastrados and dias_disp >= 3:
            # Padrão clássico: Segunda, Quarta, Sexta (ou Sexta, Sábado, Domingo)
            dias_padrao = ["segunda", "quarta", "sexta"] if dias_disp == 3 else ["segunda", "terca", "quarta", "quinta", "sexta"]
            eh_dia_de_treino = dia_hoje_norm in dias_padrao

        if not eh_dia_de_treino:
            # Descanso do aluno: Marcão NÃO incomoda!
            relatorio_execucao["alunos_em_descanso_ignorados"] += 1
            relatorio_execucao["alunos_auditados"].append({
                "aluno": nome,
                "status": "dia_de_descanso",
                "detalhes": f"Hoje ({dia_hoje}) não é dia de treino programado para {nome}. Descanso respeitado!"
            })
            continue

        # Hoje É DIA DE TREINO DO ALUNO! Realizar auditoria às 22h
        metas = ficha.get("metas_nutricionais") or {}
        strava_token = metas.get("strava_access_token") or os.getenv("STRAVA_ACCESS_TOKEN", "")
        strava_connected = metas.get("strava_connected", False)

        baloes_disparo = []
        tipo_acao = ""

        if strava_connected and strava_token:
            # Busca treinos de hoje no Strava
            atividades_hoje = buscar_atividades_aluno_strava(strava_token, hoje_inicio_epoch)
            if atividades_hoje and len(atividades_hoje) > 0:
                # Treinou! Diagnostica batimentos e esforço
                atividade_principal = atividades_hoje[0]
                baloes_disparo = diagnosticar_treino_fisiologico(atividade_principal, primeiro_nome)
                tipo_acao = "treino_elogiado_com_conselhos"
                relatorio_execucao["treinos_elogiados"] += 1
            else:
                # Não treinou no dia agendado! BRONCA DE PERSONAL!
                baloes_disparo = gerar_bronca_treino_faltoso(primeiro_nome, dia_semana=dia_hoje)
                tipo_acao = "bronca_treino_faltoso"
                relatorio_execucao["broncas_aplicadas"] += 1
        elif local_treino == "academia" or any(s in str(ficha.get("objetivo", "")).lower() for s in ["corrida", "atleta", "cardio", "esporte"]):
            # Aluno de academia ou esporte que ainda não conectou Strava
            link_strava = f"https://api.marcaopersonal.com/api/integracoes/strava/oauth?tel={tel}"
            baloes_disparo = [
                f"Fala, {primeiro_nome}! 🦁 Marcão aqui nas 22h conferindo a planilha!",
                f"Hoje foi dia de treino na academia, né? Como foi a pegada e a carga?",
                f"Aliás, conecta seu relógio no meu Strava pra eu analisar sua frequência cardíaca e intensidade direto: {link_strava}! Tamo junto! 👊🔥"
            ]
            tipo_acao = "lembrete_conexao_strava"
            relatorio_execucao["lembretes_conexao"] += 1
        else:
            # Aluno sem Strava que treina em casa
            baloes_disparo = [
                f"Fala, {primeiro_nome}! 🦁 Marcão aqui na ronda das 22h!",
                f"Hoje é dia de treino na sua rotina em casa! Treino tá pago com foco total?",
                "Toma água, garante a proteína e descanso anabólico de qualidade hoje! Tamo junto! 👊🔥"
            ]
            tipo_acao = "checkin_treino_casa"

        # Dispara os balões via Evolution API com composing
        if baloes_disparo:
            try:
                async with httpx.AsyncClient(verify=False, timeout=20.0) as client:
                    for i, balao in enumerate(baloes_disparo):
                        await client.post(
                            f"{evo_url}/message/sendText/{evo_inst}",
                            headers={"apikey": evo_key, "Content-Type": "application/json"},
                            json={"number": tel, "text": balao}
                        )
                        if i < len(baloes_disparo) - 1:
                            await asyncio.sleep(1.2)
            except Exception as e_send:
                print(f"[STRAVA AUDIT] Erro ao enviar mensagem para {tel}: {e_send}")

        relatorio_execucao["alunos_auditados"].append({
            "aluno": nome,
            "telefone": tel,
            "acao": tipo_acao,
            "baloes": baloes_disparo
        })

    return relatorio_execucao


if __name__ == '__main__':
    print('[STRAVA SERVICE] Testando renovação de token...')
    res = renovar_token_strava()
    print('Resultado renovação:', res)
    link = gerar_link_oauth_aluno('5547999998888')
    print('Link de autorização de exemplo para aluno:')
    print(link)
