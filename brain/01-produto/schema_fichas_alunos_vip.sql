-- ============================================================================
-- SCHEMA: FICHAS DE ALUNOS VIP & ACOMPANHAMENTO INDIVIDUALIZADO (SUPABASE / POSTGRES)
-- ============================================================================

CREATE TABLE IF NOT EXISTS fichas_alunos (
    id BIGSERIAL PRIMARY KEY,
    remote_jid VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(30) NOT NULL,
    nome VARCHAR(150),
    idade INT,
    genero VARCHAR(20) DEFAULT 'homem',
    objetivo VARCHAR(100),
    dias_disponiveis_semana INT DEFAULT 3,
    dias_treino JSONB DEFAULT '["segunda", "quarta", "sexta"]'::jsonb,
    local_treino VARCHAR(50) DEFAULT 'academia',
    restricoes_saude TEXT DEFAULT 'Nenhuma dor ou lesão reportada',
    experiencia_nivel VARCHAR(30) DEFAULT 'iniciante',
    
    -- Ficha de Treino e Nutrição Gerada pelo Marcão
    treino_divisao JSONB DEFAULT '{}'::jsonb,
    metas_nutricionais JSONB DEFAULT '{}'::jsonb,
    
    -- LGPD e Segurança
    consentimento_lgpd BOOLEAN DEFAULT FALSE,
    data_consentimento_lgpd TIMESTAMPTZ,
    termo_lgpd_versao VARCHAR(20) DEFAULT 'v1.0',
    
    -- Fotos Criptografadas (AES-256)
    fotos_criptografadas JSONB DEFAULT '[]'::jsonb,
    
    -- Gamificação & Acompanhamento
    etapa_onboarding INT DEFAULT 0,
    streak_dias INT DEFAULT 0,
    ultimo_checkin_data DATE DEFAULT CURRENT_DATE,
    ultimo_treino_registrado VARCHAR(50),
    ultimo_prato_avaliado JSONB DEFAULT '{}'::jsonb,
    
    -- Ofertas Contextuais e Upsells a cada 30 dias
    data_inicio_vip TIMESTAMPTZ DEFAULT NOW(),
    dias_ativos INT DEFAULT 0,
    produtos_oferecidos JSONB DEFAULT '[]'::jsonb,
    ultimo_upsell_data TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
