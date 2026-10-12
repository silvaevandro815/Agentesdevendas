-- ============================================================================
-- BANCO DE DADOS DO CÉREBRO — MARCÃO PERSONAL (SUPABASE / POSTGRESQL + PGVECTOR)
-- ============================================================================

-- Habilitar extensão de vetores para busca semântica RAG (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. TABELA DE CONHECIMENTO DO CÉREBRO (RAG PARA SOFIA E AGENTES)
CREATE TABLE IF NOT EXISTS cerebro_conhecimento (
    id SERIAL PRIMARY KEY,
    produto VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL, -- 'dosagem', 'beneficios', 'objecoes', 'preco', 'politica'
    titulo VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,
    embedding vector(1536), -- Compatível com OpenAI Text-Embedding-3 ou similar
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELA DE LEADS & HISTÓRICO DE CONVERSAS NO WHATSAPP
CREATE TABLE IF NOT EXISTS leads_conversas (
    id SERIAL PRIMARY KEY,
    remote_jid VARCHAR(100) UNIQUE NOT NULL, -- Ex: 5511999999999@s.whatsapp.net
    push_name VARCHAR(150),
    telefone VARCHAR(30) NOT NULL,
    etapa_funil VARCHAR(50) DEFAULT 'novo_lead', -- 'novo_lead', 'em_atendimento', 'link_enviado', 'comprou', 'recuperacao'
    produto_interesse VARCHAR(100),
    ultima_mensagem TEXT,
    historico_mensagens JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABELA DE PEDIDOS & VENDAS DA BRAIP
CREATE TABLE IF NOT EXISTS pedidos_braip (
    id SERIAL PRIMARY KEY,
    trans_codigo VARCHAR(100) UNIQUE NOT NULL,
    cliente_nome VARCHAR(150),
    cliente_cel VARCHAR(30),
    cliente_email VARCHAR(150),
    produto_nome VARCHAR(150),
    valor_total NUMERIC(10, 2),
    comissao NUMERIC(10, 2),
    status_pagamento VARCHAR(50), -- 'Aguardando Pagamento', 'Pagamento Aprovado', 'Cancelada'
    codigo_rastreio VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABELA DE APROVAÇÕES HUMAN-IN-THE-LOOP (EVANDRO)
CREATE TABLE IF NOT EXISTS fila_aprovacoes (
    id SERIAL PRIMARY KEY,
    agente VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,
    orcamento VARCHAR(50),
    status VARCHAR(30) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SEED DE DADOS — CONHECIMENTO DOS 5 PRODUTOS OFICIAIS DA BRAIP
-- ============================================================================

INSERT INTO cerebro_conhecimento (produto, categoria, titulo, conteudo) VALUES
(
    'KIT IArmonize Capilar',
    'produto_completo',
    'Bula e Benefícios do KIT IArmonize Capilar',
    'O KIT IArmonize é um tratamento clínico antiqueda e regeneração capilar de 4 fases desenvolvido pela Integra Pharma. Composto por: 1) Cápsulas Hair: ricas em Silício Inteligente, Biotina, Zinco e Vitaminas do Complexo B que fortalecem a raiz e cessam a queda; 2) Sérum Vital: gotas tópicas para aplicação no couro cabeludo que estimulam novos folículos; 3) Energy: disposição para treinar e acelerar o metabolismo; 4) Sleep: melhora do sono anabólico e regulação hormonal reparadora. Preço: R$ 1.256,00 (ou em até 12x no cartão com Frete Grátis). Link oficial de checkout: https://ev.braip.com/ref?pl=plav449r&ck=cheq89gn&af=afilx3y72p'
),
(
    'Colágeno + Ácido Hialurônico Nature''s Prime',
    'produto_completo',
    'Bula e Benefícios do Colágeno Hidrolisado Nature''s Prime',
    'Pote de 300g no delicioso sabor Abacaxi com Hortelã. Combina Colágeno Hidrolisado Verisol de altíssima absorção com Ácido Hialurônico e Vitamina C. Atua diretamente na sustentação da pele, prevenindo flacidez facial e corporal, suavizando linhas de expressão e fortalecendo unhas e cabelos. A partir dos 25 anos o corpo perde 1% de colágeno ao ano, sendo essencial a reposição diária. Modo de usar: dissolver 1 scoop (10g) em 200ml de água fria uma vez ao dia pela manhã. Preço: R$ 164,90. Link oficial de checkout: https://ev.braip.com/ref?pl=plawdmnw&ck=chen80pq&af=afi659l8pg'
),
(
    'Creatina Micronizada 100% Pura Nature''s Prime',
    'produto_completo',
    'Bula e Benefícios da Creatina Micronizada Nature''s Prime (300g)',
    'Creatina Monohidratada 100% pura micronizada. O suplemento com maior comprovação científica do mundo. Proporciona aumento imediato de força muscular, recuperação acelerada e síntese proteica. MITO: Creatina NÃO engorda e NÃO incha mulheres! A creatina retém água DENTRO da célula muscular (hidratação intracelular benéfica que dá tônus ao glúteo e pernas), e não embaixo da pele. Não contém açúcar, amido ou glúten. Dissolve instantaneamente. Modo de usar: 1 scoop de 3g a 5g diluído em água todos os dias (mesmo em dias sem treino). Pote de 300g rende até 100 dias. Preço: R$ 169,90. Link oficial de checkout: https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621'
),
(
    'Caneta Azempika Original',
    'produto_completo',
    'Bula e Benefícios da Caneta Azempika Original',
    'A Caneta Azempika Original é um nutracêutico acelerador metabólico formulado pela Penina Original para controle do apetite, redução da ansiedade alimentar e combate à compulsão por doces e carboidratos no período noturno. Promove sensação prolongada de saciedade e termogênese suave. Ideal para quem está em processo de emagrecimento ou déficit calórico. Preço promocional: R$ 99,00 com entrega discreta e rastreada pelos Correios. Link oficial de checkout: https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv'
),
(
    'Vision Prime (60 Cápsulas)',
    'produto_completo',
    'Bula e Benefícios do Vision Prime Saúde Ocular',
    'Suplemento avançado de proteção ocular formulado com Luteína e Zeaxantina puras, Zinco, Vitamina A e Vitamina E. Desenvolvido para proteger a retina contra a radiação nociva da luz azul emitida por smartphones, tablets e computadores. Alivia a sensação de vista cansada, olhos secos, vermelhidão e dores de cabeça causadas pelo excesso de telas. Frasco com 60 cápsulas (tratamento para 2 meses completos com 1 cápsula ao dia). Preço: R$ 199,00. Link oficial de checkout: https://ev.braip.com/ref?pl=pla2nz6n&ck=che76kmo&af=afi3vmxeod'
),
(
    'Geral',
    'politica_entrega',
    'Prazos, Frete e Rastreamento de Pedidos',
    'Todos os pedidos possuem estoque nacional e são despachados em até 24 horas úteis após a confirmação do pagamento. O envio é feito via Correios (Sedex ou PAC) ou Jadlog, com código de rastreio oficial enviado automaticamente no WhatsApp e e-mail do cliente. O prazo médio de entrega varia de 3 a 7 dias úteis dependendo da região do Brasil.'
),
(
    'Geral',
    'seguranca_garantia',
    'Garantia, Segurança de Pagamento e ANVISA',
    'A compra é 100% segura e processada pela Braip, uma das maiores plataformas de comércio eletrônico do Brasil. Pagamento disponível via Pix com aprovação imediata ou Cartão de Crédito em até 12 vezes. O cliente conta com 7 dias de garantia incondicional conforme o Código de Defesa do Consumidor. Todas as formulações cumprem rigorosamente os padrões de qualidade e regulamentações da ANVISA.'
);
