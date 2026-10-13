-- ============================================================================
-- SCHEMA: BALANÇA DE BIOIMPEDÂNCIA VIP & MOTOR DE VENDAS (SUPABASE / POSTGRESQL)
-- ============================================================================

-- 1. TABELA DE CLIENTES DA BALANÇA & ACOMPANHAMENTO VIP (3 MESES GRÁTIS -> R$ 19,90/MÊS)
CREATE TABLE IF NOT EXISTS clientes_balanca (
    id BIGSERIAL PRIMARY KEY,
    remote_jid VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(30) NOT NULL,
    nome_cliente VARCHAR(150),
    data_compra TIMESTAMPTZ DEFAULT NOW(),
    data_expiracao_vip TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '90 days'),
    status_vip VARCHAR(50) DEFAULT 'ativo_gratis', -- 'ativo_gratis', 'expirando', 'assinante_pago', 'expirado'
    streak_dias INT DEFAULT 1,
    ultimo_peso NUMERIC(5, 2),
    ultima_gordura_pct NUMERIC(5, 2),
    ultimo_musculo_kg NUMERIC(5, 2),
    dados_bioimpedancia JSONB DEFAULT '{}'::jsonb,
    historico_pesagens JSONB DEFAULT '[]'::jsonb,
    link_renovacao VARCHAR(255) DEFAULT 'https://marcaopersonal.com#renovacao-vip',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABELA DE ASSINATURAS VIP (R$ 19,90/MÊS PÓS-90 DIAS)
CREATE TABLE IF NOT EXISTS assinaturas_vip (
    id BIGSERIAL PRIMARY KEY,
    telefone VARCHAR(30) NOT NULL,
    nome_cliente VARCHAR(150),
    valor_mensal NUMERIC(10, 2) DEFAULT 19.90,
    status_assinatura VARCHAR(50) DEFAULT 'pendente', -- 'ativo', 'pendente', 'cancelado', 'atrasado'
    data_inicio TIMESTAMPTZ DEFAULT NOW(),
    proximo_vencimento TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
    transacao_id VARCHAR(100),
    link_checkout VARCHAR(255) DEFAULT 'https://marcaopersonal.com#renovacao-vip',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. TABELA DE MÉTRICAS EXECUTIVAS DO CFO (IAGO & MARTA)
CREATE TABLE IF NOT EXISTS metricas_cfo (
    id BIGSERIAL PRIMARY KEY,
    data DATE UNIQUE DEFAULT CURRENT_DATE,
    faturamento_bruto NUMERIC(10, 2) DEFAULT 0.00,
    custo_anuncios_meta NUMERIC(10, 2) DEFAULT 0.00,
    comissoes_liquidas NUMERIC(10, 2) DEFAULT 0.00,
    lucro_liquido NUMERIC(10, 2) DEFAULT 0.00,
    roas NUMERIC(5, 2) DEFAULT 0.00,
    total_pedidos INT DEFAULT 0,
    total_leads INT DEFAULT 0,
    detalhes_produtos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. TABELA DE LEADS SCORING & FUNIL INTELIGENTE (SOFIA & DAVI)
CREATE TABLE IF NOT EXISTS leads_scoring (
    id BIGSERIAL PRIMARY KEY,
    remote_jid VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(30) NOT NULL,
    nome VARCHAR(150),
    pontuacao INT DEFAULT 20, -- 0 a 100
    estagio_funil VARCHAR(50) DEFAULT 'qualificacao', -- 'qualificacao', 'apresentacao', 'objecao', 'fechamento', 'recuperacao', 'vip_balanca'
    sinais_compra JSONB DEFAULT '[]'::jsonb,
    objecao_atual VARCHAR(100),
    produto_alvo VARCHAR(100),
    tentativas_recuperacao INT DEFAULT 0,
    ultimo_contato TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
