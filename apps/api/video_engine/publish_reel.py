import os
import sys
import time
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")

ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
BASE_DIR = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"

sys.path.append(BASE_DIR)
from daily_reel_generator import produzir_reel_diario, publicar_instagram_direto, carregar_historico


def publicar_reel_dinamico(forcar_tema=None, postar_stories=True):
    print("==========================================================")
    print("🚀 PUBLICADOR INTELIGENTE DE REELS COM ROTAÇÃO ANTI-REPETIÇÃO")
    print("==========================================================")
    
    # Produz o próximo reel da esteira HD com rosto de Evandro e publica diretamente
    res = produzir_reel_diario(tema_id=forcar_tema, publicar_agora=True)
    return res


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Publicar Reels e Stories com IA Marcão Personal")
    parser.add_argument("--exec", action="store_true", help="Executa a geração e publicação real no Instagram")
    parser.add_argument("--tema", type=str, default=None, help="ID do tema específico (opcional)")
    args = parser.parse_args()

    if args.exec:
        publicar_reel_dinamico(forcar_tema=args.tema)
    else:
        print("[AVISO] Para executar a produção e publicação completa no Instagram, use a flag: --exec")
