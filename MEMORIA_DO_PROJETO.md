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

