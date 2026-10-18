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

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID', '187215')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET', 'b04505c55803754e0ad1cac759a0c0cf2a0999a5')
STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN', '530bc8243fa5b064a0949a99d5bc32a257a656ad')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN', '895147ad770fff878f08e365bc2c44a63c762a98')
STRAVA_VERIFY_TOKEN = os.getenv('STRAVA_VERIFY_TOKEN', 'marcao_strava_2026')
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


if __name__ == '__main__':
    print('[STRAVA SERVICE] Testando renovação de token...')
    res = renovar_token_strava()
    print('Resultado renovação:', res)
    link = gerar_link_oauth_aluno('5547999998888')
    print('Link de autorização de exemplo para aluno:')
    print(link)
