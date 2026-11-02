# MEMÓRIA DO PROJETO — Centro de Comando de IA (E-commerce automatizado)

> Arquivo vivo. Ler SEMPRE no início de cada sessão e atualizar a cada decisão.

## Contexto
- Diretor/Empreendedor: Evandro da Silva Gallina (CNPJ MEI: 68.746.249/0001-84).
- IP da VPS Hostinger: Configurado via DNS (subdomínios protegidos)
- Domínio principal registrado: `marcaopersonal.com`
- Subdomínio Administrativo (Painel de Controle e Aprovações): `admin.marcaopersonal.com`
- Subdomínio Loja / Landing Page: `loja.marcaopersonal.com` ou raiz `marcaopersonal.com`
- Subdomínio n8n / Automações: `n8n.marcaopersonal.com`
- Stack Definido por Evandro:
  - **n8n**: Orquestração e fluxo de trabalho dos agentes
  - **Evolution API**: Conexão com WhatsApp para Sofia e Davi
  - **Supabase**: Banco de dados relacional + pgvector para memória do Cérebro
  - **Painel Admin**: Interface web para aprovações Human-in-the-Loop
- Nicho Escolhido: **Estética Corporal, Cabelo, Pele & Definição (Marcão Personal)**
  - Catálogo Validado Sem Estoque:
    1. **Escova de LED Capilar (Fototerapia Vermelha/Azul + Microvibração)**: Gadget de altíssima conversão para queda capilar masculina e feminina (via Dropshipping Nacional Dropi / Armazém SP).
    2. **Nutracêutico Capilar Antiqueda (Biotina + Silício Inteligente + Zinco)**: Cápsulas que fortalecem o bulbo capilar de dentro para fora (Afiliado Físico Braip/Monetizze com 50% a 70% de comissão).
    3. **Colágeno Verisol® + Ácido Hialurônico**: Firmeza da pele corporal, combate a flacidez e celulite.
    4. **Creatina Monohidratada 100% Pura + TermoFit Drenante**: Tônus muscular e queima de gordura sem retenção de líquidos.
  - Branding: **Mascote Marcão** ("O Personal que não te deixa gastar dinheiro com bobagem") estrela os criativos de vídeo, enquanto a equipe de agentes (Téo, Lia, Rui, Sofia, Otto) cuida do marketing, tráfego, vendas no WhatsApp e pós-venda.
- Modelo: Híbrido Sem Estoque (Dropshipping Nacional via Dropi para a Escova de LED + Afiliado Autorizado de Produtos Físicos na Braip/Monetizze para encapsulados com despacho em 24h pelos Correios).
- Repositório GitHub: https://github.com/silvaevandro815/Agentesdevendas
- Acesso Direto Coolify: Evandro gerou API Tokens ativos para automação total da VPS.
- **Supabase Oficial Conectado:**
  - Project Ref: `qkopgftfrfftoyndhhfj`
  - URL da API: `https://qkopgftfrfftoyndhhfj.supabase.co`
  - Região: `sa-east-1` (São Paulo / Brasil)
  - Banco: PostgreSQL 17 com extensão `vector` (pgvector ativo)
  - Tabelas Criadas: `cerebro_conhecimento` (7 artigos), `leads_conversas`, `pedidos_braip`, `fila_aprovacoes`
  - Credencial no n8n: ID `h8yD2TQTqUkaUCRh` ("Supabase - Marcao Personal")
  - Sofia integrada: grava cada novo lead automaticamente em `leads_conversas`

## Confirmação do Vídeo de Referência (Assistido e Transcrito)
- Sistema: "Sua Empresa 24h" (Central de comando de IA conectada a um Cérebro Central com objetivos do mês, ofertas, números e políticas).
- Agentes e Departamentos identificados exatamente na interface do vídeo:
  - Marketing & Conteúdo: Bela (SEO/Artigos), Lia (Copywriter), Téo (Criativos), Rui (Tráfego), Nina (Social Media).
  - Vendas & Atendimento: Sofia (Atendimento 24h via WhatsApp), Davi (Follow-up de vendas e recuperação).
  - Financeiro & Dados: Iago (Analista de Dados / Relatório Executivo), Marta (Analista Financeira / Fluxo de Caixa).
  - Operações, Gente & Jurídico: Alan (Jurídico / Contratos / Compliance), Otto (Processos / SOPs / Despacho), Paulo (RH / Onboarding e contratação de novos agentes).
  - Ações padrão dos agentes: `Buscar no Cérebro` e `Emitir artefato`.


## Análise Regulatória & Fiscal (Alerta Estratégico)
- O MEI atual tem CNAE `7319-0/02` (Promoção de vendas).
- Se trabalhar como **Afiliado Oficial** (Shopee Afiliados, TikTok Shop Afiliado, Mercado Livre Afiliado): o CNAE `7319-0/02` é 100% aderente, sem risco de estoque, nota emitida pela plataforma/fornecedor.
- Se for **Dropshipping / Revenda com checkout próprio** (o cliente paga a você e você repassa ao fornecedor): recomenda-se adicionar no MEI a atividade de *Comércio varejista de cosméticos* (CNAE 4772-5/00) pelo Portal do Empreendedor (gratuito e instantâneo).
- Conformidade ANVISA: o fornecedor/fabricante é o responsável técnico pelo registro na ANVISA. Nossos agentes de copy e marketing serão blindados contra "alegações terapêuticas ou cura de calvície", mantendo conformidade com RDC/ANVISA para cosméticos.

## Agentes planejados
- Marketing: Bela (SEO/Artigos), Lia (Copywriter persuasiva), Téo (Criativos para Reels/TikTok), Rui (Gestor de Tráfego - monta campanhas pausadas), Nina (Social Media & Calendário).
- Vendas: Sofia (Atendimento WhatsApp & Dúvidas sobre o produto com RAG), Davi (Recuperação de carrinho e follow-up).
- Dados/Finanças: Iago (Relatório diário de vendas e ROAS), Marta (Controle de custos e margem líquida).
- Operações: Otto (Integração de pedidos e rastreio), Alan (Jurídico, LGPD e compliance de claims ANVISA), João (Chefe de Gabinete / Orquestrador via Telegram).

## Guardrails
- Nenhuma campanha ou gasto é ativado sem aprovação explícita de Evandro (via bot Telegram ou painel).
- Teto diário de anúncio: travado no orçamento estabelecido (R$ 16,50/dia inicialmente).
- Nenhuma chave de API ou credencial real no repositório público (.gitignore + .env.example).
- Cópias sem promessas proibidas por ANVISA/CONAR.

## Status das Fases
- [x] Pré-alinhamento & Definição da Infraestrutura
- [x] P0 — Fundação Técnica (Monorepo, Docker Compose, Git connect, Setup Coolify)
- [x] P0.5 — Deploy no Servidor Hostinger via Coolify API Concluído!
  - `https://admin.marcaopersonal.com` ONLINE (Status 200) — Painel dos Agentes
  - `https://n8n.marcaopersonal.com` ONLINE (Status 200) — Motor de Automações com fluxos F1 e F3 ativos
  - `https://evolution.marcaopersonal.com` ONLINE (Status 200) — Evolution API v2 para WhatsApp
  - **WhatsApp da Sofia Conectado**: Instância `sofia` com status `open` (Pareado com WhatsApp `553285066687` de Evandro) e webhook ativo para o n8n.
- [x] P1 — Landing Page Oficial `https://marcaopersonal.com` no ar com Mascote Marcão e integração WhatsApp Sofia
  - Design neon dark mode com paleta oficial da logo (Cyan `#00e5ff`, Verde `#00ff88`, Laranja `#ff7a00`)
  - 3 Protocolos de Ouro estruturados (Capilar com Escova LED, Pele Firme Verisol, Definição & Tônus Muscular)
  - Botões interativos com mensagens personalizadas direcionando para o WhatsApp da Sofia (`553285066687`)
- [x] P2 — Máquina de Criativos e Conteúdo (Téo, Lia, Nina) Concluída!
  - 10 Roteiros de Vídeos Virais estrelando o Mascote Marcão (`brain/05-marketing/roteiros-virais-mascote-teo.md`)
  - 10 Anúncios de Alta Conversão para Meta Ads Feed/Stories (`brain/05-marketing/anuncios-meta-ads-lia.md`)
  - Calendário Editorial Estratégico de 30 Dias (`brain/05-marketing/calendario-editorial-30dias-nina.md`)
  - Fila de Aprovações no Painel Web (`apps/admin/server.js`) alimentada com os novos criativos e campanhas
- [x] P3 — Cérebro RAG & Memória da Sofia (Supabase / Postgres com pgvector + Playbook de Vendas no n8n) Concluída!
  - Schema SQL completo do Cérebro criado com tabelas de conhecimento RAG, leads e vendas (`brain/01-produto/schema_banco_cerebro.sql`)
  - Conhecimento completo dos 5 produtos injetado (bulas, dosagens, ANVISA, preços e links oficiais Braip)
  - Workflow `F3 - Atendimento WhatsApp 24h (Sofia)` atualizado no n8n com processador inteligente de mensagens conectado à Evolution API (`instance: sofia`)
  - Sofia respondendo dúvidas de forma acolhedora, tirando objeções e entregando links de checkout em tempo real no WhatsApp
- [x] P4 — Conexão Meta Ads & Instagram (Rui e Nina com aprovação Human-in-the-Loop) Concluída!
  - `T1`: Gestor de Tráfego Pago (Rui) com propostas cirúrgicas e guardrail travado em R$ 20,00/dia.
  - `T2`: Inteligência de Mercado com Google Trends Brasil sincronizado diariamente às 07:00.
  - `T3`: Monitor de Expiração de Tokens Meta com alerta proativo para Evandro às 09:00.
  - `I2`: Fábrica autônoma de criativos com publicação 2x/dia (11:30h e 19:30h) no `@marcaopersonalfitness` para Feed e Stories.
  - Painel Admin 360° integrado para aprovações e ajustes de orçamento sem consumo de tokens de WhatsApp.
- [x] P5 — Recuperação de Vendas & Follow-up (Davi no WhatsApp com carrinho abandonado Braip) Concluída!
  - `M8`: Recuperador de Vendas Braip ativo para Boletos e PIX com cadência inteligente (10h e 18h).
  - `M9`: CRM Follow-Up & Aquecimento de Leads Inativos ativo aos 7 e 30 dias com ofertas cirúrgicas.
  - Motor de Lead Scoring em tempo real (0 a 100) com detecção e quebra imediata de objeções (`leads_scoring`).
- [x] P6 — Painel Gerencial & Métricas (Iago + Marta com cálculo diário de lucro líquido) Concluída!
  - `M5`: CFO Marcão & Central Executiva do Diretor Evandro com relatório diário de lucratividade e ROAS.
  - Painel Admin com aba exclusiva de Finanças & CFO (`/api/cfo/overview`) e tabela `metricas_cfo` no Supabase.
- [x] P7 — Balança de Bioimpedância 360° & Retenção VIP (3 Meses Grátis -> R$ 19,90/mês) Concluída!
  - Scanner Multimodal de Bioimpedância (`balanca_engine.py`): extração de 12 biomarcadores de prints de apps (Fitdays, OKOK, Tuya, Xiaomi) e display da balança.
  - Emissão instantânea do "Relatório 360° do Marcão" com metas de hidratação (35ml/kg), calorias, divisão de macros e periodização de treino.
  - Regra de Exclusividade VIP: Avaliação física e mentoria direta no WhatsApp 100% exclusivas para donos da balança.
  - Esteira de Retenção: 90 dias de acompanhamento gratuito com contagem regressiva e gamificação (`streak_dias`), transacionando para a assinatura de R$ 19,90/mês através do workflow `M10` no n8n.
- [x] P8 — Modo Comando Supremo (SUPER_ADMIN) do Diretor Evandro no WhatsApp Concluída!
  - Reconhecimento automático de Evandro Gallina (`553284587255` / `5532984587255` / LID `179009992298658`) como `SUPER_ADMIN`.
  - Blindagem total: Leads comuns no WhatsApp (F3) e Instagram (I1) permanecem 100% intactos com fluxo de vendas e quebra de objeções humanizado.
  - Módulos Executivos no WhatsApp de Evandro:
    1. Finanças & Vendas (CFO em tempo real).
    2. Disparo de Criativos & Carrosséis no Instagram (I2 via Webhook).
    3. Disparo de Follow-up de Leads Inativos (M9 via Webhook).
    4. Consulta de Leads Recentes no Supabase.
    5. Monitoramento de Alunos VIP (Eva Maria, etc.).
    6. Despacho de Áudios de Voz clonados via ElevenLabs para contatos/amigos.
    7. Prescrição esportiva e nutricional para o shape do Diretor (76.5kg).
    8. Diagnóstico de saúde dos servidores e robôs 24h.
- [x] P9 — Sentinela & Auditoria Diária 24h em Camada Dupla (Antigravity + n8n Cloud) Concluída!
  - **Camada Cloud Hostinger 24/7 (Workflow M0 no n8n):** Dispara todos os dias às 08:00h da manhã (ou sob demanda via webhook). Audita 15 componentes essenciais: Sites, Painéis, Evolution API, Supabase, Meta Ads Token, OpenRouter e Workflows. Se houver qualquer falha, dispara alerta vermelho no WhatsApp de Evandro. Se tudo estiver 100%, envia o briefing matinal verde.
  - **Camada Antigravity Local (Cron Daemon `0 8 * * *`):** Agendador autônomo ativado no Antigravity para inspeção diária com diagnóstico de engenharia e plano de ação.
- [x] P10 — Reorientação Caneta Peniana Azempika (Saúde Vascular & Potência Masculina 40+) Concluída!
  - Correção cirúrgica de posicionamento: O produto é 100% voltado para saúde vascular peniana, rigidez máxima, firmeza e vigor na hora H para homens maduros (40+, 50+, 60+). Não é emagrecedor.
  - Treinamento da mente do Marcão no WhatsApp (Workflow F3) e Instagram Direct (Workflow I1): domínio completo da fisiologia dos corpos cavernosos, vasodilatação sem efeitos cardíacos, quebra de tabus com sigilo de homem pra homem.
  - Inserção do **Modo de Aplicação Passo a Passo**: girar dosador, aplicar na haste peniana 10-15 min antes da relação, massagear por 1-2 min até absorção total.
  - Atualização do Site Oficial (pps/site/public/index.html), tabela products no Supabase e link oficial Braip (https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv).
- [x] P11 — Adobe Creative Engine 2.5: Motor de Layout Inteligente & Tipografia Avançada Concluída!
  - **Eliminação de Vazio Preto (Smart Flexbox Vertical):** Cálculo dinâmico da altura remanescente (vailable_height = y_bottom_limit - top_content_y) com cartões dinâmicos (74px a 135px) e gaps flexíveis (22px a 55px). Distribuição homogênea que preenche 60-70% do slide sem zonas mortas.
  - **Safe Zone Anti-Colisão com o Selo:** Deslocamento do início dos títulos dos Slides 2 e 3 para =195$ (respiro seguro abaixo do selo a =173$) e barreira inteligente de corte (width - 250px) se a manchete iniciar acima de =190$. Zero colisão com o selo dourado.
  - **Smart Keyword & Entity Highlighter:** Parser léxico com detecção de markdown (**termo**), métricas/números (100%, 30%, R$ 99,00, 10 a 15 min, 20ml, 90 dias), termos clínicos (COX-2, óxido nítrico, corpos cavernosos, asodilatação) e labels de ação (1. GIRE O DOSADOR:), renderizados em ouro radiante #FDE047 com soft drop-shadow.
  - **Hero Mockup 3D Proporcional:** Mockup do produto no Slide 3 ampliado para 440x480px, centralizado na altura exata da coluna de cards, acompanhado de aura dourada radial e sombra de solo.
- [x] P12 — Blindagem de Persona: Proibição Estrita do Rosto de Evandro para Azempika & Modelos Grisalhos de IA Concluída!
  - **Diretriz Suprema do Diretor Evandro:** Proibição irrevogável de usar o rosto de Evandro (seja foto real ou persona de IA baseada nele) em criativos, posts ou carrosséis da Caneta Azempika ou de qualquer produto de potência/saúde sexual masculina.
  - **Modelos de IA Homens Grisalhos 55-65 anos:** A IA gera exclusivamente homens maduros distintos, com cabelos grisalhos e barba aparada, em ambientes sofisticados (lounge/penthouse), conectando diretamente com o público masculino maduro.
  - **Guardrails de Código:** Ativados em GEMINI.md, anti_repetition_guard.py (descarte automático da persona 'evandro' para Azempika), creative_factory.py (anulação de foto de referência e injeção de homem maduro grisalho) e seed_adobe_creatives.py.
  - **Sincronização:** Slide 1 e Story gerados com o novo modelo grisalho de IA e sincronizados no Supabase Storage e content_calendar.
- [x] P13 — Auditoria & Blindagem de Onboarding, Fichas Faltantes e Follow-ups (WhatsApp & Instagram Direct) Concluída!
  - **WhatsApp Atendimento (Workflow F3):** Ativo e respondendo em tempo real via Evolution API (instância 'sofia' aberta). Regra 'PERSISTÊNCIA SUAVE PARA PREENCHER A FICHA' ativa (solicitação de peso, altura, local de treino, restrições e consentimento LGPD).
  - **WhatsApp Proativo VIP & Cobrança de Fichas (Workflow M11):** Ativo com 7 gatilhos semanais. Checa alunos com 'dados_completos: false' e executa cobranças bem-humoradas com PRIORIDADE MÁXIMA (LGPD, peso/balança, local e restrições). Testado ao vivo com sucesso (Execução 6346: SUCCESS).
  - **Painel Admin Marcão (admin.marcaopersonal.com):** Botão '📲 Cobrar Dados' ativo e disparando mensagens personalizadas de cobrança via endpoint '/api/vip/:id/cobrar-dados'.
  - **CRM Follow-Up (Workflow M9):** Ativo com execução diária às 10h (100% de taxa de sucesso). Query modernizada para busca dinâmica (order=updated_at.desc). Segmentação refinada: 'secar/barriga' direciona para Balança Inteligente 360 e 'potência/40+' direciona para Caneta Peniana Azempika.
  - **Instagram Direct (Workflow I1 & followup_instagram.py):** Ativo respondendo directs e comentários com 100% de sucesso. Injetada a regra de 'PERSISTÊNCIA SUAVE PARA PREENCHER FICHA E ONBOARDING' nos nós de áudio e texto para captação direta de métricas e conversão para WhatsApp.
- [x] P14 — Blindagem Suprema: Múltiplos Balões Curtos (<140 chars), Presença Composing e Reações de Emojis em Todo o Ecossistema Concluída!
  - **Diretriz Absoluta:** Proibido o envio de textões em bloco único em qualquer canal (atendimentos e follow-ups).
  - **Fatiamento Dinâmico em 2 a 4 Balões Curtos:** Cada intervenção do Marcão é dividida em balões de 50 a 120 caracteres (máximo 140-160 chars), garantindo leitura leve e dinâmica no celular.
  - **Simulação de Digitação & Pausas Naturais:** Envio sequencial de cada balão precedido por 'composing' de 2000ms e delays de 1.2s a 1.8s entre as mensagens no WhatsApp e no Instagram Direct.
  - **Reações de Emojis nos Balões do Lead:** Configurada a reação imediata com emojis autênticos (👊, 💪, 🔥, 🦁, 👍) nos balões de mensagem do cliente/lead.
  - **Guardrails Ativados:** Injetados nos prompts de F3 (WhatsApp), I1 (Instagram Direct), M9 (CRM Follow-up), M11 (Personal Proativo VIP) e no Painel Admin (/api/vip/:id/cobrar-dados).
- [x] P15 — Smartwatch Hub (Strava & Apple/Android), Prontuário Clínico & Exclusividade Balança VIP (3 Meses Grátis -> R$ 19,90/mês) Concluída!
  - **Regra de Exclusividade da Balança:** O monitoramento aprofundado de Smartwatch (batimentos cardíacos, pontualidade de horários e diagnóstico de "Treino Bom vs. Treino Fofo") é 100% exclusivo para alunos que compraram a Balança de Bioimpedância 360°.
  - **Reconhecimento Multicanal de Compra da Balança:** (1) Webhook de venda aprovada (/api/webhooks/compra-balanca); (2) Leitura visual automática da primeira pesagem via balanca_engine.py; (3) Palavra-chave do unboxing ("CHEGOU MINHA BALANCA"); (4) Ativação manual no Painel Admin.
  - **Esteira de Retenção e Transbordo:** 90 dias (3 meses) gratuitos de mentoria total com contagem regressiva em clientes_balanca, transbordando para assinatura de R$ 19,90/mês gerenciada pelo Stripe e workflow M10.
  - **Opção 2 Ativa (Apple Shortcuts & Android Webhook):** Endpoint /api/webhooks/treino-relogio ativo, avaliando FC média, picos de esforço e disparando feedback humanizado em múltiplos balões curtos via Evolution API.
  - **Opção 1 Ativa (Strava API):** Credenciais cadastradas no .env (Client ID: 187215, Client Secret, Refresh Token), módulo `apps/api/strava_service.py` e rotas em `apps/admin/server.js` conectadas com handshake, callback OAuth e processamento de atividades.
- [x] P16 — Integração Completa do Strava & Smartwatch Hub Concluída!
  - **Credenciais & Renovação de Token:** Client ID 187215 e Segredo integrados. Renovação automática de access token implementada via OAuth 2.0.
  - **Fluxo do Aluno em 1 Clique:** Endpoint `/api/integracoes/strava/auth-url` gera o link de autorização com state atrelado ao WhatsApp do aluno. Após autorização na web do Strava, a rota `/api/integracoes/strava/callback` armazena os tokens do atleta em `clientes_balanca` e envia boas-vindas automáticas no WhatsApp.
  - **Diagnóstico Fisiológico em Tempo Real:** Webhook `/api/integracoes/strava/webhook` recebe eventos `activity:create`, extrai distância, pace, FC média e FC máxima, avalia se o treino foi "Treino Monstro" ou "Treino Fofo" (Zonas de FC) e responde no WhatsApp em 2 a 3 balões curtos com presença humana.
- [x] P17 — Motor de Vídeo com IA para Reels Verticais 9:16 (ElevenLabs & Motion Design) Concluído!
  - **Importação da Tecnologia:** Módulos de geração de vídeo, composição e sound design portados para `apps/api/video_engine/` sem alterar a pasta original `Editor de Video IA`.
  - **Identidade Visual com o Rosto de Evandro:** Utilização das fotos de referência de `assets/evandro` para geração de keyframes cinematográficos atléticos em academia moderna (9:16 vertical), respeitando a regra de persona (fotos de Evandro para fitness/treino/creatina).
  - **Voz ElevenLabs Multilíngue (Zero OpenRouter):** Narração fitness inspiradora gerada via ElevenLabs com voz `Adam` (`pNInz6obpgDQGcFmaJgB`) em português brasileiro, preservando tokens do OpenRouter.
  - **Soundscape & Trilha Sonora:** Gerador em Python (`soundscape.py`) com sub-bass analógico de 50Hz, LFO pulsante e varredura atmosférica a -16dB.
  - **Compositor FFmpeg Master:** Enquadramento 9:16 (1080x1920), movimentos de câmera cinematográficos (push-in, tracking pan), legendas dinâmicas em amarelo/branco com borda de alto contraste e mixagem de áudio com atempo de precisão (10.2s).
- [x] P18 — Vídeo com Movimento Real de Filme (LTX-Video Diffusion) & Publicador Oficial de Reels via n8n (Workflow I3) Concluído!
  - **Geração de Vídeo Real com IA (LTX-Video):** Substituição de zooms estáticos por difusão de vídeo com movimentos corporais reais (rosca direta com halteres pesados, contração de bíceps, levantamento de barra no perfil e treinador em slow-motion inspirador). Autenticação via HF_TOKEN privada na fila ZeroGPU.
  - **Novo Workflow Oficial no n8n (I3):** Criado e ativado no n8n o workflow `I3 - Publicador de Reels Automáticos com IA (Marcão & Evandro)` (ID: `Fm7B8X0snUoQoBEg`).
  - **Endpoint de Webhook Ativo:** `https://n8n.marcaopersonal.com/webhook/publicar-reels-marcao` recebe JSON com `video_url`, `caption` e `share_to_feed`, orquestrando a criação do container de Reels na Meta Graph API, aguardando o processamento do vídeo (`FINISHED`) e executando a publicação.
  - **Primeira Publicação Oficial em Produção:** Reel publicado com sucesso no Instagram `@marcaopersonalfitness` (ID: `17909372640482561`, Link: `https://www.instagram.com/reel/DeqHNv1gLFY/`).
- [x] P19 — Autonomia Total de Vendas na Braip, Varredura do Catálogo & Blindagem dos Workflows F4/M8 Concluída!
  - **Validação de Token na API Oficial da Braip:** Token pessoal de Evandro da Silva Gallina testado e validado em `https://ev.braip.com/api/user` (HTTP 200) e `https://ev.braip.com/api/vendas`. Chave gravada em `.env` (`BRAIP_API_TOKEN`, User ID `18771924`).
  - **Varredura Completa do Catálogo Braip:** 5 produtos oficiais já ativos com links rastreados no Supabase (`products`) e em `catalog_service.py`: Creatina Micronizada Pura (R$ 169,90), Colágeno + Ácido Hialurônico (R$ 164,90), Kit IArmonize Capilar (R$ 1.256,00), Vision Prime (R$ 199,00) e Caneta Azempika (R$ 99,00).
  - **Postback na Braip Confirmado:** Configuração ativa no painel da Braip (código `cowlv3jj`) apontando para `https://n8n.marcaopersonal.com/webhook/braip-postback` com status Ativo.
  - **Blindagem do Workflow F4:** Adicionado nó `Registrar Pedido Braip no Supabase` salvando todas as transações diretamente na tabela `pedidos_braip`.
  - **Correção Crítica no Workflow M8 (Recuperador):** Corrigido o filtro da query Supabase de `status` (inexistente) para `status_pagamento=in.(aguardando_pagamento,gerado)`, desbloqueando a recuperação diária automática de boletos e Pix não pagos.
- [x] P20 — Autonomia Plena de Vendas Multicanal (Amazon + Braip), Catálogo Oficial Homologado & Consciência Comercial de Caçador (Closer Concluída!)
  - **Balança Inteligente Shopee R$ 34,90 Ativada como Carro-Chefe Nº 1:** Link oficial Shopee `https://s.shopee.com.br/2BFoInIBeb` integrado no site, Supabase e catálogo com 3 fotos oficiais (design preto com display LCD azul, relatório do app com 13 biomarcadores e pesagem real com BLE). Preço direto de fábrica de apenas R$ 34,90 (R$ 0,09/dia). Protocolo oficial de ativação: pesagem de 3s nos 4 eletrodos BIA -> app gera laudo -> aluno envia print no WhatsApp do Marcão para leitura em 5s via Visão Computacional.
  - **Catálogo Expandido Unificado (17 Produtos Homologados no Supabase & `catalog_service.py`):**
    1. *Balança Inteligente de Bioimpedância Shopee* (R$ 34,90, Shopee `https://s.shopee.com.br/2BFoInIBeb`) — Carro-chefe nº 1: 13 biomarcadores a preço direto de fábrica com acompanhamento Marcão AI no WhatsApp (R$ 0,09/dia).
    2. *Balança Xiaomi Mi Body Composition Scale 2* (R$ 149,90, Amazon) — Opção premium alternativa: 13 parâmetros clínicos com sensor G de manganês e mentoria VIP (R$ 0,41/dia).
    2. *100% Whey Pure Max Titanium 900g* (R$ 99,90, Amazon) — 21g proteína, R$ 3,33/dia.
    3. *Whey Protein Concentrado DUX Nutrition 900g* (R$ 149,90, Amazon) — Matéria-prima importada, sabor premium, R$ 4,99/dia.
    4. *100% Whey Gold Standard Optimum Nutrition 907g* (R$ 249,90, Amazon) — Padrão ouro mundial, isolado microfiltrado, R$ 8,33/dia.
    6. *Creatina Micronizada 100% Pura Nature's Prime 300g* (R$ 169,90, Braip) — 100 doses, R$ 1,69/dia.
    7. *Creatina Creapure DUX Nutrition 250g* (R$ 139,90, Amazon) — Selo Creapure alemão, R$ 1,68/dia.
    8. *Smartwatch Xiaomi Smart Band 8* (R$ 239,00, Amazon) — Monitor cardíaco 24/7, sono e Strava, R$ 0,65/dia.
    9. *Smartwatch Amazfit Bip 5 com GPS Integrado* (R$ 399,00, Amazon) — GPS 4 satélites e chamadas, R$ 1,09/dia.
    10. *Camiseta Térmica Compressão UV50+ Dry Fit* (R$ 49,90, Amazon) — Retorno venoso e secagem rápida, R$ 0,27/dia.
    11. *Bermuda Térmica Compressão Fitness com Bolso* (R$ 59,90, Amazon) — Suporte muscular e zero assaduras, R$ 0,33/dia.
    12. *Ômega 3 Ultra Concentrado 1000mg EPA/DHA DUX* (R$ 99,90, Amazon) — Blindagem de joelhos, tendões e articulações, R$ 1,66/dia.
    13. *Complexo Sono Reparador Melatonina + Magnésio Dimalato* (R$ 69,90, Amazon) — Sono profundo e liberação de GH, R$ 1,16/dia.
    14. *Colágeno + Ácido Hialurônico Nature's Prime* (R$ 164,90, Braip) — Pele, tônus e sustentação articular, R$ 5,40/dia.
    15. *Caneta Peniana Azempika Original* (R$ 99,00, Braip) — Saciedade noturna e vigor masculino (exclusivamente modelos grisalhos maduros de IA).
    16. *Vision Prime 60 Cápsulas* (R$ 199,00, Braip) — Fadiga ocular e proteção contra luz azul.
    17. *KIT IArmonize Capilar em 4 Fases* (R$ 1.256,00, Braip) — Tratamento antiqueda intensivo.
    + *Assinatura VIP Stripe Mensal* (R$ 19,90/mês) — Continuidade pós-90 dias.
  - **Matriz de Disparo Autônomo de Vendas (Dor -> Solução Imediata):** Mapeamento léxico e semântico ativo no `catalog_service.py` e injetado diretamente no cérebro do Marcão para WhatsApp (`marcao_engine.py`) e Instagram (`I1`). Marcão opera como Closer consultivo implacável: identifica o sintoma do lead, diagnostica com autoridade de coach, quebra a objeção com cálculo de custo por dia e envia o link direto oficial no último balão.
  - **Motor Diário de Reels & Stories (`daily_reel_generator.py`):** Ampliado com temas automáticos de Whey Protein, Smartwatch + Strava, Roupas de Compressão e Saúde Articular, com legendas dinâmicas, narração oficial ElevenLabs e rotação de produtos.
  - **Shopee:** Cadastro submetido e aguardando aprovação fiscal pela equipe da Shopee para integração via GraphQL API.
- [x] P21 — Blindagem de Gênero nos Comentários do Instagram & Nova Esteira de Vídeos HD com Fidelidade Facial do Evandro e Rotação Anti-Repetição Concluída!
  - **Detecção de Gênero e Neutralidade Total (Workflow I1 no n8n):**
    * Resolvido o incidente em que o Marcão chamou uma seguidora mulher (`@evamaria3243`) de "campeão".
    * Implementada a função `detectarGenero(username, nome)` nos nós `Montar Prompt Comentário Marcão` e `Processar Decisão Comentário e DM` do workflow `I1` (ID `jlG1OPBCsaAx75zQ`).
    * Dicionário exaustivo de prenomes femininos e masculinos brasileiros e marcadores de arroba.
    * Se mulher: `@usuario Tamo junto, campeã! Bora pra cima! 💪🦁` (ou `Fala, campeã!` no Direct).
    * Se homem: `@usuario Tamo junto, campeão! Bora pra cima! 💪🦁` (ou `Fala, campeão!` no Direct).
    * Se neutro / indeterminado: `@usuario Tamo junto! Bora pra cima com tudo! 💪🦁` (ou `Fala aí! Marcão Personal na área! 🦁` no Direct) — 100% blindado contra gafe.
    * Se pedido de link/post: `@usuario Te mandei no direct! Dá uma olhada lá! 👊🔥` (100% neutro, educado e maromba).
    * Regra 6 do `GEMINI.md` atualizada permanentemente.
  - **Fidelidade Facial Máxima do Evandro (OpenRouter + Gemini 2.5 Flash Image):**
    * Integração com a foto matriz do Diretor Evandro (`assets/evandro/evandro_front_master.jpg`), replicando seus traços faciais, mandíbula, formato dos olhos, cabelo escuro e porte atlético com 100% de autenticidade (respeitando a Regra 4: nunca para Azempika).
    * Gerados e validados 8 takes verticais 9:16 fotorealistas em 8K para os 8 temas da esteira (Balança Xiaomi, Creatina Micronizada, Smartwatch Strava, Whey Protein, Sono GH, Articulações Ômega/Colágeno, Roupas de Compressão e Constância).
  - **Resolução Nativa 1080x1920 (9:16) & Movimento Cinematográfico (compose_reel.py):**
    * Eliminação completa dos takes borrados em 704x512 recortados. Agora todos os vídeos são compostos em 1080x1920 nativo a 30fps (CRF 18) via FFmpeg 9.0.1.
    * Movimento contínuo de câmera lenta (Ken Burns suave com zoom e pan) com filtro de nitidez extrema (`unsharp=5:5:0.8`).
    * Legendas dinâmicas sincronizadas queimadas na tela (Regra 9 inviolável): fonte `Montserrat Bold` / `Anton`, tamanho 50-52px, contorno de 5px preto, sombra e palavras-chave em amarelo ouro (`#FFD700`) e branco na zona de segurança inferior.
    * Mixagem de áudio profissional com voz brasileira nativa (`marcao_voice.py`) em 1.35x e trilha de fundo com fadeout suave de 1.2s.
  - **Fim da Repetição de Vídeos & Rotação Anti-Repetição (daily_reel_generator.py + Workflow I3):**
    * Resolvida a causa raiz da repetição: o workflow `I3` (ID `Fm7B8X0snUoQoBEg`) tinha um gatilho agendado às 19:00h que caía num fallback estático hardcoded de um único vídeo.
    * O código do nó no workflow `I3` foi reformulado no n8n com banco de 4 Master Reels HD rotativos (`reel_balanca_xiaomi_hd.mp4`, `reel_creatina_mito_hd.mp4`, `reel_smartwatch_strava_hd.mp4`, `reel_whey_protein_hd.mp4`) com rotação diária automática por dia do mês (`diaDoMes % REELS_ROTATIVOS.length`).
    * Motor local `daily_reel_generator.py` agora possui `historico_reels.json` persistente e sincronização com o `content_calendar` do Supabase, garantindo que o tema mais antigo ou inédito seja sempre o próximo a ser renderizado e postado.

## 14. Padrão Cinematográfico BeatDesign: Multi-Cenas (6-8 Cortes) e Matriz Facial Fiel (frente.jpg + lado2.jpg)
- **Zero Boomerang / Zero Cena Única:** Todo vídeo deve conter entre 6 a 8 cortes cinematográficos de alta retenção (3.5s a 4.5s cada).
- **Diversidade de Ambientes:** Praia ao pôr do sol, trilha na natureza, parque urbano / futebol, cozinha / nutrição e academia de luxo.
- **Elementos Visuais:** Células 3D, produto girando 360°, display LED e eletrodos acendendo, app Marcão AI no celular e contração muscular real.
- **Fidelidade Facial Evandro:** Triangulação obrigatória de frente.jpg e lado2.jpg.
- **Agendamento Automático:** Todos os dias às 18:00h pontualmente via n8n (I3) e Meta Graph API.


## 15. Arquitetura de Cibersegurança & Proteção de Dados (Anti-Vibecoding Homologado)
- **Motivação:** Auditoria técnica de segurança contra os 3 riscos críticos de desenvolvimento com IA (demonstrados em `WhatsApp Video 2026-10-21 at 10.31.25 PM.mp4`):
  1. Vazamento de chaves secretas no cliente via DevTools Sources.
  2. Burlar telas privadas excluindo cookies ou manipulando rotas frontend.
  3. Ausência de rate limiting, permitindo ataques de brute-force, DoS e esgotamento financeiro de créditos de API.
- **Implementações Ativas:**
  - **Site Oficial (`apps/site`):**
    * Helmet ativo com remoção de `X-Powered-By`, proteção contra clickjacking (`X-Frame-Options: SAMEORIGIN`) e MIME-sniffing (`X-Content-Type-Options: nosniff`).
    * Rate Limiting estrito de 30 requisições/minuto em `/api/lead` e `/api/track` (Meta Conversions API) e 300 reqs/15min em navegação.
    * Limite de payload JSON de 30KB contra DoS por estouro de buffer (HTTP 413).
    * Remoção de qualquer segredo no frontend; isolamento total das chamadas à Meta via relay backend.
  - **Centro de Comando Admin (`apps/admin`):**
    * Remoção completa de chaves e segredos default hardcoded no código (`SUPABASE_KEY` e tokens Strava).
    * `Login Gate` executivo com autenticação por chave mestra (`ADMIN_MASTER_PASSWORD`).
    * Assinatura criptográfica de sessão via HMAC-SHA256 e cookie HTTP-Only (`marcao_admin_session`) com SameSite.
    * Middleware `requireAdminAuth` protegendo todas as rotas sensíveis (`/api/vip/*`, `/api/approvals/*`, `/api/cfo/*`, `/api/creatives/*`, `/api/sales/*`).
    * Validação estrita: se o usuário ou invasor excluir o cookie ou manipular a UI no DevTools, o backend responde imediatamente com HTTP 401 Unauthorized e a tela é bloqueada na hora.
    * Rate Limiting anti-brute-force no login (máximo 5 tentativas a cada 15 minutos).
    * Rate Limiting de processamento pesado de IA (máximo 3 gerações por minuto).
    * Botão de Bloqueio Instantâneo no cabeçalho do painel ("Bloquear Painel").
  - **Motor de Inteligência e Automações (`apps/api`):**
    * Middleware de segurança com Rate Limiting: 10 requisições/minuto para rotas pesadas de IA (`/api/voz/`, `/api/visao/`, `/api/creatives/`) e 120 reqs/minuto para rotas gerais.
    * Limite de upload de 20MB para fotos de avaliação corporal/bioimpedância.
    * Cabeçalhos de segurança HTTP e HSTS injetados em todas as respostas.
    * `apps/api/strava_service.py` e scripts de automação limpos de segredos estáticos, lendo exclusivamente de variáveis de ambiente.
  - **Repositório & Git:**
    * `.gitignore` rigoroso protegendo `.env`, `.env.local`, `*.key`, `*.pem`, `APYKEYs/` e credenciais.


## 16. Ativação das 9 Instagram Skills & Esteira Cinematográfica Multi-Cenas
- **Framework Ativo:** `sergebulaev/instagram-skills` integrado ao Antigravity (`.agents/skills/`, `skills/` e `apps/api/instagram_skills_engine.py`).
- **As 9 Skills Implementadas:**
  1. `ig-audience-insights`: Leitura ao vivo da Meta Graph API para guiar decisões por números reais.
  2. `ig-hook-extractor`: 10 fórmulas canônicas de 2026 nos primeiros 3 segundos.
  3. `ig-caption-writer`: Gancho estrito <125 caracteres antes do "...mais", tópicos escaneáveis e CTA única.
  4. `ig-carousel-planner`: Arquitetura de 5 a 10 lâminas otimizadas para Salvamento.
  5. `ig-content-planner`: Grade semanal multi-formatos e alavancas de compartilhamento.
  6. `ig-hashtag-strategist`: 3 a 5 hashtags dimensionadas por nicho, tamanho médio e amplo.
  7. `ig-humanizer`: Desintoxicação de IA e voz marcante do Marcão Personal.
  8. `ig-profile-optimizer`: Diagnóstico de 9 pontos da biografia e destaques.
  9. `ig-repurposer`: Adaptação de estudos em carrosséis e roteiros 9:16.
- **Produção Multi-Cenas Ativa (Zero Boomerang / Zero Ping-Pong):**
  * Concatenação de 5 a 8 takes em 1080x1920 nativo por vídeo.
  * Diversidade total de locações: Cozinha preparando suplementos, Praia/Orla ao entardecer, Academia moderna de luxo, Trilha na natureza, Pista de atletismo e Living room com a Balança Shopee.
  * Rotação anti-repetição contínua em `historico_reels.json` e `content_calendar` do Supabase.


## 17. Auditoria Rígida de Onboarding & Varredura Automática de Prontuários (Zero Dados Incompletos)
- **Regra do Sistema:** É proibido permitir alunos com prontuário incompleto ou dados biométricos ausentes.
- **Auditoria de 8 Dimensões em `apps/api/fichas_engine.py`:**
  1. Identificação completa (Nome e WhatsApp).
  2. Biometria estrita: Peso numérico válido (35kg a 250kg) e Altura válida (110cm a 230cm).
  3. Idade real (12 a 95 anos).
  4. Objetivo de treino claro (Hipertrofia, Queima de Gordura, Definição ou Saúde).
  5. Triagem clínica ortopédica (Pressão arterial, medicamentos contínuos e lesões articulares).
  6. Fisiologia circadiana (Horas de sono e litros de água habitual).
  7. Rotina esportiva (Local: Casa ou Academia; Dias disponíveis na semana).
  8. Termo de consentimento LGPD formalizado.
- **Portão de Entrada Rígido no Onboarding:**
  * O aluno NÃO avança para a fase concluída se deixar peso ou altura de fora.
  * O Marcão interrompe imediatamente e cobra os dados que faltam com simpatia e autoridade de personal trainer.
- **Motor de Varredura Geral (`/api/admin/varredura-onboarding` e `/api/fichas/varredura-onboarding`):**
  * Varredura periódica em todas as fichas no Supabase.
  * Cálculo em tempo real da Taxa de Conformidade (%) e lista detalhada de pendências.
  * Geração instantânea de mensagens de cobrança em 2 balões curtos (Regra 5) com botão de disparo em lote via Evolution API.

## 18. Alunos de Demonstração Executiva & Otimização Total para Tablet (Investor Mode)
- **Ambiente de Apresentação ao Investidor no Tablet (iPad / Galaxy Tab - 768px a 1024px):**
  * **Admin (`admin.marcaopersonal.com`):**
    - Banner Executivo no topo da aba VIP: `[ 💼 APRESENTAÇÃO EXECUTIVA | VISÃO DO INVESTIDOR ]` com 4 KPIs-chave (Balanças BLE Ativas, Retenção de 94.2%, LTV Projetado de R$ 418,80 e Taxa de Conformidade de 85%).
    - Painel interativo de Varredura de Onboarding com barra de progresso em tempo real e botões `⚡ Rodar Varredura Agora` e `📲 Cobrar Todos os Pendentes (WhatsApp)`.
    - Alunos fictícios de demonstração de alta performance:
      * **Dra. Mariana Souza Bittencourt:** Médica, 31 anos, 61.2kg, 21.4% gordura, Balança Shopee ativa, 14d streak, Ficha 100% Completa com treino ABCD e macros calibrados.
      * **Rodrigo Mendes Fagundes:** Empresário, 44 anos, 84.8kg (-4.4kg eliminados), 23.9% gordura, Balança Shopee ativa, 21d streak, Ficha 100% Completa com treino ABC metabólico e sono anabólico GH.
      * **Lucas Martins Oliveira:** Arquiteto, 29 anos, 78.5kg, Ficha 60% (Em Onboarding) para demonstrar ao investidor a IA cobrando dados pendentes ao vivo.
    - Media queries dedicadas para tablet, botões com altura mínima de 44px para toque suave e tabela responsiva com scroll horizontal fluido.
  * **Landing Page (`marcaopersonal.com`):**
    - Seção Destaque Executivo / Investor Proof: **O Flywheel de Conversão & LTV** (Entrada Low-Ticket Balança R$ 34,90 -> Visão Multimodal OCR 13 Biomarcadores -> Auditoria Ativa de Onboarding -> Assinatura Stripe R$ 19,90/mês).
    - Grid responsivo de 2 colunas refinado no tablet (768px - 1024px) com alinhamento perfeito de títulos, mockups e cartões de bioimpedância.


## 19. Blindagem Anti-Repetição no n8n e Proibição de Criativos Genéricos com Shaker
- **Causa Raiz Identificada e Extirpada:**
  * O workflow do n8n `I2 - Fábrica de Criativos & Publicador Instagram 2x/dia (Marcão)` (ID: `jd2hOvXwJO2dwUaE`) possuía um item de Creatina travado com `status: 'ready'` no Supabase `content_calendar` porque o comando PATCH falhava silenciosamente ao atualizar a linha após o disparo.
  * Além disso, a esteira não consultava o histórico recente do Instagram antes de publicar, fazendo o mesmo carrossel de Creatina sair 4 dias seguidos (22/10 a 25/10).
- **Correções Aplicadas:**
  1. **Sentinela Anti-Repetição no n8n `I2`:** Antes de qualquer postagem, o nó orquestrador consulta os últimos 10 posts na Meta Graph API. Se "creatina" ou qualquer outro tema apareceu recentemente, o tópico é **100% bloqueado** para o dia.
  2. **Atualização Blindada do Supabase:** O PATCH agora utiliza cabeçalhos restritos com `Prefer: return=minimal` e tratamento de erros explícito, garantindo que o item seja marcado como `published` na hora.
  3. **Extinção do Prompt "Homem Loiro Bebendo em Garrafa":** O prompt genérico que gerava um homem loiro com coqueteleira plástica foi substituído por renders científicos em 3D de alta definição (contração de fibras musculares e síntese de ATP mitocondrial) e personas reais diversificadas (Evandro, Mulher Atlética e Homem Maduro Grisalho).
  4. **Fila Restante no Supabase Limpa:** O item duplicado de Creatina foi marcado como `published`, liberando os temas inéditos da fila: *Saúde Articular & Longevidade aos 40+*, *Mito do Suor no Emagrecimento*, *Musculação na Terceira Idade (60+)* e o *Comercial da Balança Shopee*.


## 20. Shopee Affiliate Open API & Autonomia Total de Vendas do Marcão Personal
- **Integração Homologada:** Credenciais da Shopee Affiliate Open API inseridas no `.env`:
  * `SHOPEE_APP_ID=18302091279`
  * `SHOPEE_SECRET=4KLNIQLXFE7TNE7UTNZHE44BBRIIHDOS`
  * `SHOPEE_GRAPHQL_URL=https://open-api.affiliate.shopee.com.br/graphql`
- **Mecanismo de Assinatura Criptográfica:** SHA256 compacto de `AppId + Timestamp + PayloadJSON + Secret` enviado no cabeçalho `Authorization: SHA256 Credential=...,Timestamp=...,Signature=...`.
- **Motor Central (`apps/api/shopee_affiliate_engine.py`):**
  * `buscar_produtos_shopee(keyword, limit, sort_type)`: Busca produtos com fallback automático, extraindo título, preço, avaliação, fotos, comissão e link encurtado oficial (`https://s.shopee.com.br/...`).
  * `gerar_link_afiliado_shopee(url_original, sub_id)`: Converte qualquer link da Shopee em link rastreado com SubID (identificador do aluno ou campanha).
  * `prescrever_produto_autonomo(mensagem_aluno, sub_id)`: Mapeador semântico de dores biomecânicas (joelho -> joelheira compressão, lombar -> cinto agachamento, antebraço/pegada -> strap, ombro -> faixa manguito, treino em casa -> kit elásticos, gravação de treino -> suporte magnético de celular, hidratação -> garrafa térmica 2L, etc.).
  * `obter_relatorio_vendas_shopee(dias)`: Monitoramento em tempo real de pedidos e comissões geradas via `partnerOrderReport`.
- **Comportamento Autônomo no WhatsApp e Instagram:**
  * O Marcão não depende de catálogo estático. Quando o aluno relata uma queixa física ou pede um acessório, a IA consulta a Shopee ao vivo, seleciona o item campeão e fecha a venda em 2 a 4 balões curtos com a quebra do custo por dia e o link oficial de afiliado.
- **Endpoints REST Expostos (`apps/api/main.py`):**
  * `GET /api/shopee/busca?q={termo}`
  * `POST /api/shopee/gerar-link`
  * `POST /api/shopee/prescrever`
  * `GET /api/shopee/relatorio-vendas`


## 21. Motor Híbrido de Vídeo: HyperFrames + RunPod.io GPU + Auto Viral Pipeline
- **Problema Anterior Resolvido:**
  * Anteriormente, a geração de vídeos automáticos no Instagram estava desativada ou restrita (VIDEO_POSTING_CANCELADO = True no build_video_marcao.py) devido ao visual pobre de cartões estáticos feitos com PIL e legendas sem sincronia dinâmica.
  * O repositório HeyGen HyperFrames (heygen-com/hyperframes, Apache 2.0) foi transferido e integrado com sucesso para transformar a esteira de vídeos do Marcão Personal.
- **Estrutura Implementada:**
  * pps/api/video_engine/marcao_hyperframes_engine.py: Motor de templates GSAP em HTML/CSS para renderização a 60fps via Chrome headless em 1080x1920 nativo (Custo zero de GPU).
  * pps/api/video_engine/vendor/gsap.min.js: Cópia local offline do GreenSock GSAP para imunidade a bloqueios de rede.
  * pps/api/video_engine/runpod_gpu_manager.py & 
unpod_open_engine.py: Gerenciador de GPU Serverless para geração de takes 3D hiper-realistas (Wan 2.1 & FLUX.1) sob demanda.
  * pps/api/video_engine/compose_reel.py: Pipeline FFmpeg com junção da abertura em Motion Design (motion_intro_path), corte dinâmico punch zoom (1.15x) a cada 3.5s sem perda de proporção (SAR 1:1), e legendas Hormozi em amarelo canário queimadas com libass.
  * pps/api/video_engine/daily_reel_generator.py: Orquestrador completo que escolhe o tema pelo sentinela anti-repetição, gera a voz nativa em português brasileiro do Marcão, cria a introdução motion correspondente (ex: 13 biomarcadores na balança ou ressíntese de ATP na creatina), compõe o master reel e publica no Instagram Reels e Stories.
- **Modelos Customizados para o Treinador Marcão:**
  1. marcao_kinetic_hook: Tipografia cinética de impacto nos primeiros segundos com destaque visual e sound design.
  2. marcao_balanca_bioimpedancia: Scanner de 13 biomarcadores de precisão (massa muscular, gordura visceral, idade metabólica) com oferta Shopee de R$ 0,09/dia e bônus de 3 meses de mentoria VIP.
  3. marcao_creatina_science: Demonstração científica em 3D da via de ATP mitocondrial e ganho de força com saturação contínua.
  4. marcao_myth_buster: Desmistificação didática em formato de cartões interativos.
  5. compose_with_ai: Criação inteligente de animações através de IA para qualquer texto do roteiro.
- **Exemplo de Execução:**
  * python apps/api/video_engine/daily_reel_generator.py --tema balanca_ia
  * python apps/api/video_engine/daily_reel_generator.py --tema creatina_mito

### [31/10/2026] Reestruturação da Seção Carro-Chefe (Balança Shopee R$ 34,90)
- **Eliminação Total de Vácuos:** O espaço anteriormente vazio na coluna direita foi 100% preenchido com o showcase visual em alta definição da balança oficial (alanca_shopee_preta.webp), acompanhada das duas imagens de demonstração prática (alanca_shopee_app_metricas.webp e alanca_shopee_uso_real.webp).
- **Desencavalamento dos 13 Biomarcadores:** As 13 métricas clínicas ganharam uma faixa horizontal dedicada de largura total (.biomarkers-full-strip) em grid simétrico de 4 colunas no Desktop, com ícones vetoriais SVG neon e espaçamento generoso que impede qualquer quebra indevida ou sobreposição.
- **Centralização da Placa de Precificação na Área Segura:** A placa de precificação (.pricing-central-card) foi centralizada no coração do container, destacando o valor de R$ 34,90 (R$ 0,09/dia), o benefício dos 90 dias de mentoria VIP no WhatsApp e os botões oficiais de conversão Shopee e WhatsApp dispostos lado a lado com harmonia estética.

## 22. Diretrizes Invioláveis do Portal do Aluno, Biometria Real, PWA & Ranking Semanal Dinâmico (Leis Máximas)
- **Links Shopee Específicos por Acessório:**
  * Joelheira Neoprene: `https://s.shopee.com.br/AUvD3t2pKw` (R$ 21,00 a R$ 29,90)
  * Cinto de Musculação com Suporte Lombar: `https://s.shopee.com.br/4fxQZlKctc` (R$ 49,90)
  * Faixas Elásticas Manguito Rotador: `https://s.shopee.com.br/4Ve0NSPas4` (R$ 24,90 a R$ 29,90)
  * Kit Elásticos Extensores Treino em Casa: `https://s.shopee.com.br/6fiUxRLoRK` (R$ 29,00 a R$ 49,90)
  * Straps de Algodão Reforçado: `https://s.shopee.com.br/2BG5b2xhm2` (R$ 19,00 a R$ 19,90)
  * Balança Inteligente de Bioimpedância (Carro-Chefe): `https://s.shopee.com.br/2BFoInIBeb` (R$ 34,90)
  * Regra: Proibido redirecionar acessórios para o link da balança.
- **PWA & Adicionar à Tela Inicial do Celular:**
  * O Marcão instrui ativamente em 4 a 5 balões como adicionar o portal como ícone na tela inicial do celular (iOS: Compartilhar > Adicionar à Tela de Início; Android: 3 pontinhos > Adicionar à tela inicial).
  * O portal `aluno.html` conta com banner de acesso rápido e modal interativo com guia passo a passo para iPhone e Android.
- **Ranking Semanal dos Leões Dinâmico:**
  * Motor: `calcular_ranking_top5` consulta o Supabase `fichas_alunos`, lê `treino_atual.historico_treinos`, streak e check-ins reais para computar a pontuação de consistência (0 a 100%).
  * Semanalmente (Domingos às 19:00), o Marcão envia a atualização do ranking para todos os alunos com incentivo para subir no pódio.
- **Biometria Real sem Dados Fictícios:**
  * Proibido usar valores padrão genéricos (170cm, 70kg) como se fossem medições reais.
  * Alunos sem altura ou peso confirmados (inclusive o Diretor Evandro) são sinalizados com `dados_pendentes: True` e alerta no portal.
  * O Marcão cobra ativamente a altura em cm e peso via WhatsApp e atualiza imediatamente no Supabase.
- **Incentivo e Follow-up Contínuo (Mínimo 3x por semana):**
  * Segundas, Quartas e Sextas às 18:00 (treinos e pendências).
  * Segundas a Sextas às 12:30 (avaliação de almoço/dieta).
  * Domingos às 19:00 (entrega da plataforma semanal e ranking).

## 16. Matriz de 31 Dias de Conteúdo no Instagram & 31 Cenários Únicos via RUNPOD.IO
- **Matriz Canônica:** pps/api/matriz_31_dias.py com 31 temas, 31 roteiros, legendas Hormozi, ganchos e 31 cenários visuais únicos.
- **Janela Anti-Repetição:** Verificação estrita dos últimos 30 posts (historico[-30:]). Nenhum tema ou cenário pode se repetir antes de todos os 30 outros terem sido publicados.
- **Motor Open-Source RUNPOD.IO GPU:** Renderização via Wan 2.1 (vídeo) e FLUX.1 (imagens cinematográficas 9:16) em GPU serverless.
- **Repostagem nos Stories:** Reels são postados no Feed e replicados automaticamente nos Stories (postar_stories=True).

- **Blindagem Anti-Duplicação de Follow-ups:** Trava de idempotência diária (`adquirir_trava_deduplicacao`) ativada em `apps/api/marcao_autonomous_cron.py` para impedir qualquer mensagem repetida para o mesmo aluno no mesmo dia. Execução restrita ao container de produção na VPS Linux.
