# -*- coding: utf-8 -*-
"""
Motor de Voz Central do Marcão Personal (Voz Nativa Brasileira pt-BR)
=====================================================================
- Provedor Primário: pt-BR-AntonioNeural (100% Português Brasileiro Nativo, Zero Sotaque Estrangeiro).
- Provedor Feminino: pt-BR-FranciscaNeural (100% Brasileira Nativa).
- Desempenho: 2 a 4 segundos por geração.
- Custo: R$ 0,00 (Totalmente Ilimitado para WhatsApp e Instagram).
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import time
import base64
import asyncio
import tempfile
import subprocess
import requests
import imageio_ffmpeg
import edge_tts
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('c:/Users/User/Desktop/Agentes de venda/.env')

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'https://evolution.marcaopersonal.com')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', '')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')

VOZ_MARCAO_DEFAULT = 'pt-BR-AntonioNeural'
VOZ_FEMININA_DEFAULT = 'pt-BR-FranciscaNeural'

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def _converter_mp3_otimizado(input_path: str, output_path: str) -> bool:
    try:
        cmd = [
            FFMPEG_EXE, '-y',
            '-i', input_path,
            '-codec:a', 'libmp3lame',
            '-b:a', '128k',
            output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f'[MARCAO VOZ] Erro conversao MP3: {e}')
        return False

async def _gerar_voz_edge_async(texto: str, out_file: str, voz: str = VOZ_MARCAO_DEFAULT, rate: str = "+6%", pitch: str = "-1Hz"):
    """Gera áudio em português brasileiro nativo usando Edge-TTS."""
    comm = edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch)
    await comm.save(out_file)

def gerar_voz_marcao(texto: str, out_file: str = None, modo: str = 'masculino') -> str:
    """
    Gera voz em Português Brasileiro Nativo (100% sem sotaque estrangeiro).
    modo: 'masculino' (Marcão) | 'feminino' (Atleta/Colágeno)
    """
    t0 = time.time()
    voz_escolhida = VOZ_MARCAO_DEFAULT if modo != 'feminino' else VOZ_FEMININA_DEFAULT
    pitch_ajustado = "-1Hz" if modo != 'feminino' else "+0Hz"
    rate_ajustado = "+6%" if modo != 'feminino' else "+4%"
    
    if not out_file:
        fd, out_file = tempfile.mkstemp(suffix='.mp3')
        os.close(fd)
        
    try:
        print(f"[MARCAO VOZ] Gerando fala 100% Brasileira Nativa ({voz_escolhida})...")
        asyncio.run(_gerar_voz_edge_async(texto, out_file, voz_escolhida, rate=rate_ajustado, pitch=pitch_ajustado))
        duracao = time.time() - t0
        print(f"[MARCAO VOZ] Voz brasileira gerada em {duracao:.2f}s! ({os.path.getsize(out_file)} bytes)")
        return out_file
    except Exception as e:
        print(f"[MARCAO VOZ] Erro na síntese nativa ({e}).")
        raise

def gerar_voz_marcao_bytes(texto: str, modo: str = 'masculino') -> bytes:
    """Retorna o binário MP3 da fala brasileira nativa."""
    caminho = gerar_voz_marcao(texto, modo=modo)
    with open(caminho, 'rb') as f:
        data = f.read()
    try:
        if 'tmp' in caminho.lower():
            os.remove(caminho)
    except Exception:
        pass
    return data

async def gerar_e_enviar_audio_whatsapp(target_number: str, texto: str, modo: str = 'masculino') -> bool:
    """Gera a voz brasileira nativa e envia como nota de voz (PTT) no WhatsApp via Evolution API."""
    import httpx
    
    headers_evo = {
        'apikey': EVOLUTION_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # 1. Simula gravação de áudio no WhatsApp
    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        try:
            await client.post(
                f'{EVOLUTION_API_URL}/chat/sendPresence/sofia',
                headers=headers_evo,
                json={'number': target_number, 'presence': 'recording', 'delay': 3000}
            )
        except Exception as e:
            print(f'[MARCAO VOZ] Presença recording ignorada: {e}')
            
    # 2. Gera o áudio brasileiro
    try:
        audio_bytes = await asyncio.to_thread(gerar_voz_marcao_bytes, texto, modo)
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    except Exception as e:
        print(f'❌ [MARCAO VOZ] Erro gerando áudio brasileiro: {e}')
        return False
        
    # 3. Dispara no WhatsApp como áudio gravado na hora (PTT)
    async with httpx.AsyncClient(timeout=40.0, verify=False) as client:
        payload_evo = {
            'number': target_number,
            'audio': audio_b64
        }
        res_evo = await client.post(
            f'{EVOLUTION_API_URL}/message/sendWhatsAppAudio/sofia',
            headers=headers_evo,
            json=payload_evo
        )
        if res_evo.status_code in [200, 201]:
            print(f'[MARCAO VOZ] Áudio brasileiro entregue com sucesso para {target_number}!')
            return True
        else:
            print(f'[MARCAO VOZ] Falha Evolution API ({res_evo.status_code}): {res_evo.text}')
            return False

if __name__ == '__main__':
    print('Testando módulo voz brasileira nativa...')
    txt = 'Fala meu parceiro! Aqui é o Marcão. Agora sim a voz é brasileira de verdade, sem sotaque de gringo!'
    f = gerar_voz_marcao(txt, 'test_output_marcao_br.mp3')
    print('Sucesso! Arquivo gerado:', f)
