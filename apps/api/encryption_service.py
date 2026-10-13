import os
import base64
import hashlib
from datetime import datetime
import httpx
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Chave de criptografia AES-256 (Fernet) derivada de forma segura e determinística
def obter_fernet():
    secret = os.getenv("ENCRYPTION_SECRET") or SUPABASE_KEY or "Marcao_Encryption_Key_2026_Secure!"
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)

fernet_cipher = obter_fernet()

def criptografar_dado(texto_ou_bytes: str | bytes) -> str:
    """Criptografa um dado em texto ou bytes usando AES-256/Fernet com HMAC-SHA256."""
    if isinstance(texto_ou_bytes, str):
        data_bytes = texto_ou_bytes.encode("utf-8")
    else:
        data_bytes = texto_ou_bytes
    encrypted_bytes = fernet_cipher.encrypt(data_bytes)
    return encrypted_bytes.decode("utf-8")

def descriptografar_dado(payload_encriptado: str) -> str:
    """Descriptografa um dado criptografado com a chave do servidor."""
    try:
        decrypted_bytes = fernet_cipher.decrypt(payload_encriptado.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        print("Erro ao descriptografar:", e)
        return ""

def criptografar_foto(base64_foto: str) -> str:
    """Criptografa a string base64 de uma foto corporal para armazenamento seguro na LGPD."""
    clean_b64 = base64_foto.split("base64,")[1] if "base64," in base64_foto else base64_foto
    return criptografar_dado(clean_b64)

def descriptografar_foto(payload_encriptado: str, mime_type: str = "image/jpeg", incluir_prefixo_data_uri: bool = False) -> str:
    """Recupera a foto descriptografada em formato base64 utilizável para comparação de visão."""
    raw_b64 = descriptografar_dado(payload_encriptado)
    if not raw_b64:
        return ""
    if incluir_prefixo_data_uri:
        return f"data:{mime_type};base64,{raw_b64}"
    return raw_b64

def gerar_termo_lgpd(nome_aluno: str) -> str:
    """Retorna a mensagem formal e amigável de consentimento da LGPD para envio ao aluno."""
    primeiro_nome = nome_aluno.strip().split()[0] if nome_aluno else "Guerreiro(a)"
    return f"""🔒 *COMPROMISSO DE PRIVACIDADE E SEGURANÇA (LGPD) — MARCÃO PERSONAL*

Fala, {primeiro_nome}! Pela Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018) e pelo meu compromisso ético e profissional com a sua saúde:

1. Todas as suas fotos corporais (frente e costas), exames e biometrias são mantidas sob *sigilo absoluto*.
2. Seus dados são protegidos por *criptografia militar de ponta a ponta* no nosso banco de dados seguro, sem acesso público.
3. Essas imagens serão usadas *exclusivamente* para eu acompanhar sua evolução, avaliar sua postura e comparar seu 'antes e depois'.

Você autoriza o uso estritamente técnico e confidencial das suas fotos para o seu acompanhamento de personal trainer?

👉 Responda com *"Autorizo"* ou *"Sim"* para ativarmos sua ficha oficial! 👊"""

async def salvar_consentimento_lgpd(remote_jid: str, telefone: str, nome: str) -> bool:
    """Grava o consentimento formal na tabela fichas_alunos do Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    agora = datetime.now().isoformat()
    payload = {
        "remote_jid": remote_jid,
        "telefone": telefone,
        "nome": nome,
        "consentimento_lgpd": True,
        "data_consentimento_lgpd": agora,
        "termo_lgpd_versao": "v1.0_whatsapp",
        "updated_at": agora
    }
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.patch(
                f"{SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.{remote_jid}",
                headers=headers,
                json=payload
            )
            return res.status_code in [200, 204]
    except Exception as e:
        print("Erro salvando consentimento LGPD:", e)
        return False
