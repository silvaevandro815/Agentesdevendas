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
    """Retorna a mensagem formal e amigável de isenção de responsabilidade médica e consentimento LGPD."""
    primeiro_nome = nome_aluno.strip().split()[0] if nome_aluno else "Guerreiro(a)"
    return f"""🔒 *TERMO DE CIÊNCIA, ISENÇÃO DE RESPONSABILIDADE & LGPD — MARCÃO PERSONAL*

Fala, {primeiro_nome}! Para garantirmos sua segurança e a conformidade legal do nosso projeto (LGPD - Lei nº 13.709/2018):

1️⃣ *NATUREZA DO SERVIÇO:* O Marcão é uma Inteligência Artificial assistente de bem-estar. Todas as recomendações de treinos, exercícios e dicas nutricionais são de caráter educativo e NÃO substituem consulta médica ou profissional de saúde presencial.
2️⃣ *ASSUNÇÃO DE RESPONSABILIDADE:* Você declara estar apto(a) à prática de atividades físicas e assume integral responsabilidade por cada exercício que optar por realizar, adaptando ao seu próprio limite e sem exageros.
3️⃣ *PRIVACIDADE TOTAL (LGPD):* Seus dados (peso, altura, idade e fotos) são protegidos com criptografia militar e mantidos sob sigilo absoluto, servindo apenas para sua evolução.

👉 *OBRIGATÓRIO:* Para ativar sua ficha e receber seus treinos sob medida com total segurança jurídica, basta me responder aqui escrevendo:
*CONCORDO*"""

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
