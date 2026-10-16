# Diretrizes e Memória Central — Marcão Personal (Antigravity AI)

Este documento é lido automaticamente no início de **toda e qualquer nova conversa** no Antigravity para este projeto.

## 1. Contexto e Identidade
- **Diretor / Fundador:** Evandro da Silva Gallina.
- **Marca:** Marcão Personal (`marcaopersonal.com`).
- **Projeto:** Centro de Comando de IA, Agentes de Vendas, Automações no n8n, Evolution API e E-commerce.
- **Documento Vivo de Arquitetura:** Consulte sempre `MEMORIA_DO_PROJETO.md` para decisões, regras de negócio e stack.

## 2. Gerenciamento de Credenciais e Chaves de API
- **NÃO PEÇA CHAVES DE API AO USUÁRIO:** Todas as chaves ativas do projeto estão salvas no arquivo `.env` na raiz do projeto (`c:\Users\User\Desktop\Agentes de venda\.env`).
- Chaves disponíveis: `SUPABASE_URL`, `SUPABASE_KEY`, `OPENROUTER_API_KEY`, `ELEVENLABS_API_KEY`, `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `INSTAGRAM_*`, `META_*`, `STRIPE_*`, `GOOGLE_API_KEY` / `GEMINI_API_KEY`.
- Se precisar conectar novos workflows no n8n ou novos projetos na Coolify, leia o `.env` diretamente.

## 3. Ferramentas Locais de Mídia e Edição de Vídeo
- **FFmpeg 9.0.1:** Instalado e disponível globalmente no PATH (`ffmpeg`, `ffprobe`, `ffplay`).
- **LosslessCut 3.69.0:** Editor visual leve e sem perda de qualidade instalado com atalho na Área de Trabalho.
- **MoviePy 2.1.2 no Python 3.12:** Biblioteca instalada para geração automatizada de vídeos, cortes milimétricos, sobreposição de legendas dinâmicas, inserção de ícones animados, motion graphics e formatação vertical (Reels/TikTok 9:16).