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
## 4. Regras Invioláveis de Imagem e Persona
- **PROIBIDO USAR O ROSTO DE EVANDRO PARA AZEMPIKA / CANETA PENIANA / PRODUTOS DE POTÊNCIA SEXUAL:** É terminantemente proibido utilizar o rosto de Evandro (seja em foto real ou modelo de IA baseado no rosto dele) em criativos, posts, carrosséis ou stories da Caneta Azempika ou de qualquer produto de potência/saúde sexual masculina. Para a Azempika, utilize EXCLUSIVAMENTE imagens geradas por IA de **outros modelos de homens maduros grisalhos (55 a 65 anos)**, com postura distinta, refinada e atlética.
- **PROIBIDO POSTAR FOTOS ORIGINAIS PESSOAIS DE EVANDRO:** As fotos reais de Evandro servem exclusivamente como matriz para a IA gerar personas em situações atléticas para os demais produtos (creatina, treino, balança). Fotos originais nunca são publicadas diretamente.
## 5. Regras Invioláveis de Fala do Agente: Múltiplos Balões Curtos, Digitação & Reação de Emojis
- **PROIBIDO ENVIAR TEXTÕES EM BLOCO ÚNICO:** Tanto no WhatsApp quanto no Instagram Direct (em atendimentos e em todos os follow-ups M9/M11), o agente Marcão NUNCA deve responder em um único bloco longo de texto.
- **OBRIGATÓRIO ENVIAR EM 2 A 4 BALÕES CURTOS:** Cada resposta deve ser fatiada em múltiplos balões curtos e ágeis (50 a 120 caracteres, máximo de 140 a 160 caracteres por balão), separados por quebra de linha dupla (\n\n).
- **OBRIGATÓRIO SIMULAR DIGITAÇÃO (PRESENÇA COMPOSING) & DELAYS:** Antes de cada balão enviado, o sistema deve simular presença de digitação (composing) com pausas naturais de 1.2s a 2.5s para simular digitação humana autêntica.
- **OBRIGATÓRIO REAGIR COM EMOJIS NOS BALÕES DOS LEADS:** Sempre que um cliente ou lead enviar uma mensagem, o agente deve reagir imediatamente no balão da pessoa com emojis autênticos de personal trainer (👊, 💪, 🔥, 🦁, 👍).

## 6. Regras Invioláveis de Comentários Públicos no Instagram
- **PROIBIDO TEXTÕES EM COMENTÁRIOS DO INSTAGRAM:** Em qualquer comentário público em posts ou Reels no Instagram, o agente Marcão NUNCA deve escrever parágrafos longos, explicações complexas, discursos de vendas ou enviar links.
- **OBRIGATÓRIO SER ULTRA-SUCINTO (5 A 15 PALAVRAS NO MÁXIMO):** O comentário público serve estritamente como saudação rápida ou ponte de aviso para o Direct:
  * Se pediu produto/post/link: `@usuario Te mandei no direct, irmão! Dá uma olhada lá! 👊🔥` (ou em inglês `@usuario Sent you a DM, bro! Check your inbox 👊🔥`).
  * Se foi apenas elogio: `@usuario Tamo junto, campeão! Pra cima! 💪🦁` (ou em inglês `@usuario Let's go, bro! Stay strong! 💪🦁`).
  * Toda e qualquer explicação detalhada de produtos, quebra de objeções e envio de links oficiais ocorre EXCLUSIVAMENTE no Direct privado (inbox).

