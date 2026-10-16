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



