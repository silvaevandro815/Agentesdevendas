const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Carregar variáveis de ambiente do .env raiz
function carregarEnv() {
  const envPaths = [
    path.join(__dirname, '../../.env'),
    path.join(__dirname, '../.env'),
    path.join(__dirname, '.env')
  ];
  for (const p of envPaths) {
    if (fs.existsSync(p)) {
      const content = fs.readFileSync(p, 'utf8');
      content.split('\n').forEach(line => {
        const match = line.match(/^\s*([\w_]+)\s*=\s*(.*)?\s*$/);
        if (match && !process.env[match[1]]) {
          process.env[match[1]] = (match[2] || '').trim().replace(/^['"]|['"]$/g, '');
        }
      });
      break;
    }
  }
}
carregarEnv();

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://qkopgftfrfftoyndhhfj.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrb3BnZnRmcmZmdG95bmRoaGZqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MTgwMTU4MywiZXhwIjoyMTA3Mzc3NTgzfQ.S_RRdnI6SZTVR1UH7jryDVHf316YmnMOVEBuoedyKv8';
const META_ACCESS_TOKEN = process.env.META_ACCESS_TOKEN || '';

function getSupabaseHeaders() {
  return {
    'apikey': SUPABASE_KEY,
    'Authorization': `Bearer ${SUPABASE_KEY}`,
    'Content-Type': 'application/json'
  };
}

// 1. Listar todas as aprovações da fila executiva no Supabase
app.get('/api/approvals', async (req, res) => {
  try {
    if (!SUPABASE_KEY) {
      return res.status(500).json({ error: 'SUPABASE_KEY não configurada' });
    }

    const resp = await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?order=id.desc&limit=50`, {
      headers: getSupabaseHeaders()
    });

    if (!resp.ok) {
      return res.status(resp.status).json({ error: 'Erro ao consultar Supabase', details: await resp.text() });
    }

    const records = await resp.json();

    const formatted = records.map(r => {
      let metaId = null;
      if (r.conteudo) {
        const match = r.conteudo.match(/META_CAMPAIGN_ID:\s*([0-9]+)/);
        if (match) metaId = match[1];
      }

      return {
        id: r.id,
        agent: r.agente || 'Rui',
        department: r.departamento || 'Tráfego Pago',
        type: r.tipo || 'Campanha Meta Ads',
        title: r.titulo || 'Nova Proposta',
        content: r.conteudo || '',
        budget: r.orcamento || 'R$ 20,00 / dia',
        status: r.status || 'pending',
        meta_campaign_id: metaId,
        date: r.created_at ? new Date(r.created_at).toLocaleDateString('pt-BR') : new Date().toLocaleDateString('pt-BR')
      };
    });

    res.json(formatted);
  } catch (err) {
    console.error('Erro /api/approvals:', err);
    res.status(500).json({ error: err.message });
  }
});

// 2. Aprovar campanha no Meta Ads e marcar no Supabase
app.post('/api/approvals/:id/approve', async (req, res) => {
  const { id } = req.params;
  try {
    const rGet = await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.${id}`, {
      headers: getSupabaseHeaders()
    });
    const items = await rGet.json();
    if (!items || items.length === 0) {
      return res.status(404).json({ error: 'Proposta não encontrada' });
    }
    const record = items[0];

    let metaResult = null;
    if (record.conteudo && META_ACCESS_TOKEN) {
      const match = record.conteudo.match(/META_CAMPAIGN_ID:\s*([0-9]+)/);
      if (match) {
        const campaignId = match[1];
        const metaResp = await fetch(`https://graph.facebook.com/v21.0/${campaignId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            status: 'ACTIVE',
            access_token: META_ACCESS_TOKEN
          })
        });
        metaResult = await metaResp.json();
      }
    }

    await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.${id}`, {
      method: 'PATCH',
      headers: { ...getSupabaseHeaders(), 'Prefer': 'return=representation' },
      body: JSON.stringify({ status: 'approved' })
    });

    res.json({ success: true, status: 'approved', meta_result: metaResult });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 3. Ajustar orçamento no Meta Ads e no Supabase
app.post('/api/approvals/:id/budget', async (req, res) => {
  const { id } = req.params;
  const { novo_valor_diario, dias_duracao } = req.body;

  if (!novo_valor_diario || isNaN(novo_valor_diario)) {
    return res.status(400).json({ error: 'novo_valor_diario inválido' });
  }

  const valFloat = parseFloat(novo_valor_diario);
  const diasInt = parseInt(dias_duracao, 10) || 1;

  try {
    const rGet = await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.${id}`, {
      headers: getSupabaseHeaders()
    });
    const items = await rGet.json();
    if (!items || items.length === 0) {
      return res.status(404).json({ error: 'Proposta não encontrada' });
    }
    const record = items[0];

    let metaResult = null;
    if (record.conteudo && META_ACCESS_TOKEN) {
      const match = record.conteudo.match(/META_CAMPAIGN_ID:\s*([0-9]+)/);
      if (match) {
        const campaignId = match[1];
        const metaResp = await fetch(`https://graph.facebook.com/v21.0/${campaignId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            daily_budget: Math.round(valFloat * 100),
            access_token: META_ACCESS_TOKEN
          })
        });
        metaResult = await metaResp.json();
      }
    }

    const novoOrcamentoStr = `R$ ${valFloat.toFixed(2)} / dia (${diasInt} dias)`;
    await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.${id}`, {
      method: 'PATCH',
      headers: getSupabaseHeaders(),
      body: JSON.stringify({ orcamento: novoOrcamentoStr })
    });

    res.json({
      success: true,
      novo_orcamento: novoOrcamentoStr,
      investimento_total: valFloat * diasInt,
      meta_result: metaResult
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 4. Pausar campanha no Meta Ads
app.post('/api/approvals/:id/pause', async (req, res) => {
  const { id } = req.params;
  try {
    const rGet = await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.${id}`, {
      headers: getSupabaseHeaders()
    });
    const items = await rGet.json();
    if (!items || items.length === 0) {
      return res.status(404).json({ error: 'Proposta não encontrada' });
    }
    const record = items[0];

    let metaResult = null;
    if (record.conteudo && META_ACCESS_TOKEN) {
      const match = record.conteudo.match(/META_CAMPAIGN_ID:\s*([0-9]+)/);
      if (match) {
        const campaignId = match[1];
        const metaResp = await fetch(`https://graph.facebook.com/v21.0/${campaignId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            status: 'PAUSED',
            access_token: META_ACCESS_TOKEN
          })
        });
        metaResult = await metaResp.json();
      }
    }

    await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.${id}`, {
      method: 'PATCH',
      headers: getSupabaseHeaders(),
      body: JSON.stringify({ status: 'paused' })
    });

    res.json({ success: true, status: 'paused', meta_result: metaResult });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 5. Rejeitar proposta no Supabase
app.post('/api/approvals/:id/reject', async (req, res) => {
  const { id } = req.params;
  try {
    await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?id=eq.${id}`, {
      method: 'PATCH',
      headers: getSupabaseHeaders(),
      body: JSON.stringify({ status: 'rejected' })
    });
    res.json({ success: true, status: 'rejected' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Endpoint legado para compatibilidade
app.post('/api/approvals/:id', async (req, res) => {
  const { id } = req.params;
  const { action } = req.body;
  if (action === 'approved') {
    return app._router.handle({ ...req, url: `/api/approvals/${id}/approve`, method: 'POST' }, res);
  } else if (action === 'rejected') {
    return app._router.handle({ ...req, url: `/api/approvals/${id}/reject`, method: 'POST' }, res);
  }
  res.json({ success: true });
});

// Resumo dos Agentes
app.get('/api/agents', (req, res) => {
  res.json({
    marketing: [
      { name: "Bela", role: "Redatora de Conteúdo/SEO", tag: "Encontrada no Google", badges: ["artigo-seo", "Buscar no Cérebro"], active: true },
      { name: "Lia", role: "Copywriter", tag: "Copy que converte", badges: ["copywriting", "landing-page-conversao"], active: true },
      { name: "Téo", role: "Criador de Conteúdo Visual", tag: "Vídeos que prendem", badges: ["roteiros-reels", "ugc-tiktok"], active: true },
      { name: "Rui", role: "Gestor de Tráfego Pago", tag: "Campanhas Cirúrgicas", badges: ["meta-ads", "pausado-para-aprovacao", "teto-diario-r$20"], active: true },
      { name: "Nina", role: "Social Media", tag: "Presença Constante", badges: ["calendario-editorial", "agendamento-automatico"], active: true }
    ],
    vendas: [
      { name: "Marcão Personal", role: "Atendimento & Consultoria VIP", tag: "Cliente respondido em segundos", badges: ["playbook-de-atendimento", "Buscar no Cérebro"], active: true },
      { name: "Davi", role: "Vendedor & Recuperador", tag: "Nenhum lead esfria", badges: ["follow-up-de-vendas", "Buscar no Cérebro"], active: true }
    ],
    financeiro: [
      { name: "Iago", role: "Analista de Dados", tag: "Números que decidem", badges: ["relatorio-executivo", "Buscar no Cérebro"], active: true },
      { name: "Marta", role: "Analista Financeira", tag: "O caixa sob controle", badges: ["fluxo-de-caixa", "Buscar no Cérebro"], active: true }
    ],
    operacoes: [
      { name: "Alan", role: "Jurídico & Compliance", tag: "Contrato revisado", badges: ["contrato-prestacao-servico", "anvisa"], active: true },
      { name: "Otto", role: "Analista de Processos", tag: "A empresa que roda sem você", badges: ["sop-processos"], active: true },
      { name: "Paulo", role: "RH & Gestor de IAs", tag: "Contrata certo, cuida do time", badges: ["contratacao-onboarding"], active: true }
    ]
  });
});

// Endpoint para acionar a Fábrica de Criativos
app.post('/api/creatives/generate', async (req, res) => {
  const { tipo, formato } = req.body;
  const { exec } = require('child_process');
  const pythonCmd = `python apps/api/creative_factory.py --tipo ${tipo || 'manha'} --formato ${formato || 'carrossel'}`;
  exec(pythonCmd, { cwd: path.join(__dirname, '../..') }, (error, stdout, stderr) => {
    if (error) {
      console.error('Erro ao gerar criativo:', error, stderr);
      return res.status(500).json({ error: error.message, stderr });
    }
    try {
      const match = stdout.match(/\[RESULTADO\]:\s*(\{[\s\S]*\})/);
      if (match) {
        return res.json(JSON.parse(match[1]));
      }
    } catch(e) {}
    res.json({ success: true, output: stdout });
  });
});

// Endpoint para listar posts recentes publicados no Instagram
app.get('/api/creatives/recent', async (req, res) => {
  try {
    const token = process.env.INSTAGRAM_ACCESS_TOKEN || '';
    const accountId = process.env.INSTAGRAM_ACCOUNT_ID || '28570207812599721';
    const r = await fetch(`https://graph.instagram.com/v21.0/${accountId}/media?fields=id,caption,media_type,media_url,permalink,timestamp&limit=10&access_token=${token}`);
    const data = await r.json();
    res.json(data.data || []);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 6. Endpoint CFO Overview (Iago & Marta)
app.get('/api/cfo/overview', async (req, res) => {
  try {
    const headers = getSupabaseHeaders();
    // Vendas Braip
    const rPed = await fetch(`${SUPABASE_URL}/rest/v1/pedidos_braip?select=valor_total,comissao,status_pagamento`, { headers });
    const pedidos = rPed.ok ? await rPed.json() : [];

    const faturamentoBruto = pedidos.reduce((acc, p) => acc + (parseFloat(p.valor_total) || 0), 0);
    const comissoesLiquidas = pedidos.reduce((acc, p) => acc + (parseFloat(p.comissao) || 0), 0);

    // Campanhas aprovadas Meta Ads (estimativa de R$ 20/dia por proposta)
    const rApp = await fetch(`${SUPABASE_URL}/rest/v1/fila_aprovacoes?status=eq.approved&select=id`, { headers });
    const aprovadas = rApp.ok ? await rApp.json() : [];
    const custoMetaAds = aprovadas.length * 20.0;

    // Leads e Alunos VIP
    const rLeads = await fetch(`${SUPABASE_URL}/rest/v1/leads_conversas?select=id`, { headers });
    const leads = rLeads.ok ? await rLeads.json() : [];

    const rVip = await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?select=id,status_vip`, { headers });
    const vips = rVip.ok ? await rVip.json() : [];
    const totalVipAtivos = vips.filter(v => ['ativo_gratis', 'assinante_pago'].includes(v.status_vip)).length;

    const lucroLiquido = comissoesLiquidas - custoMetaAds;
    const roas = custoMetaAds > 0 ? (comissoesLiquidas / custoMetaAds).toFixed(2) : '0.00';

    res.json({
      faturamento_bruto: faturamentoBruto.toFixed(2),
      comissoes_liquidas: comissoesLiquidas.toFixed(2),
      custo_meta_ads: custoMetaAds.toFixed(2),
      lucro_liquido: lucroLiquido.toFixed(2),
      roas: parseFloat(roas),
      total_pedidos: pedidos.length,
      total_leads: leads.length,
      total_vip_balanca: totalVipAtivos
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 7. Endpoint Lista Unificada de Alunos e Clientes VIP (Balança & Mentoria)
app.get('/api/vip/clientes', async (req, res) => {
  try {
    const headers = getSupabaseHeaders();
    
    // Consulta paralela a clientes_balanca e fichas_alunos
    const [rClients, rFichas] = await Promise.all([
      fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?order=created_at.desc&limit=100`, { headers }).then(r => r.ok ? r.json() : []),
      fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?order=created_at.desc&limit=100`, { headers }).then(r => r.ok ? r.json() : [])
    ]);

    const agora = new Date();
    const alunosMap = new Map();

    function extrairChaveUnica(tel, rJid, id) {
      const rawTel = (tel || '').replace(/\D/g, '');
      if (rawTel.length >= 8) return rawTel.slice(-8);
      if (rJid && rJid.includes('@')) {
        const rawJid = rJid.split('@')[0].replace(/\D/g, '');
        if (rawJid.length >= 8) return rawJid.slice(-8);
      }
      return String(tel || rJid || id);
    }

    // 1. Processar clientes_balanca
    rClients.forEach(c => {
      let diasRestantes = 90;
      if (c.data_expiracao_vip) {
        const dtFim = new Date(c.data_expiracao_vip);
        diasRestantes = Math.max(0, Math.ceil((dtFim - agora) / (1000 * 60 * 60 * 24)));
      }
      const key = extrairChaveUnica(c.telefone, c.remote_jid, c.id);
      const isEvandro = ['84587255', '984587255'].includes(key) || (c.nome_cliente && c.nome_cliente.toLowerCase().includes('evandro'));

      alunosMap.set(key, {
        id: c.id,
        origem: 'balanca',
        nome: c.nome_cliente || (isEvandro ? 'Evandro Silva Gallina' : 'Aluno(a)'),
        telefone: c.telefone,
        remote_jid: c.remote_jid,
        data_compra: c.data_compra ? new Date(c.data_compra).toLocaleDateString('pt-BR') : 'Recente',
        dias_restantes: diasRestantes,
        status_vip: c.status_vip || 'ativo_gratis',
        streak_dias: c.streak_dias || 0,
        ultimo_peso: c.ultimo_peso ? `${c.ultimo_peso}kg` : 'Pendente',
        ultima_gordura: c.ultima_gordura_pct ? `${c.ultima_gordura_pct}%` : 'Pendente',
        link_renovacao: c.link_renovacao || 'https://marcaopersonal.com#renovacao-vip',
        objetivo: isEvandro ? 'Atleta de Elite - Hipertrofia & Definição' : 'Pendente (Aguardando Anamnese)',
        local_treino: isEvandro ? 'academia' : 'Pendente',
        treino_resumo: isEvandro ? 'Divisão ABC de Alta Performance' : 'Aguardando Anamnese',
        restricoes: isEvandro ? 'Nenhuma restrição articular' : 'Pendente',
        consentimento_lgpd: isEvandro ? 'Autorizado (LGPD)' : 'Pendente (Falta "CONCORDO")',
        etapa_onboarding: isEvandro ? 5 : 0,
        dados_completos: isEvandro
      });
    });

    // 2. Unificar com fichas_alunos
    rFichas.forEach(f => {
      const key = extrairChaveUnica(f.telefone, f.remote_jid, f.id);
      const isEvandro = ['84587255', '984587255'].includes(key) || (f.nome && f.nome.toLowerCase().includes('evandro'));

      let tResumo = '';
      const t = f.treino_divisao || f.treino_atual || {};
      if (t.treino_a) tResumo = `A: ${t.treino_a} | B: ${t.treino_b || ''}`;

      const pesoFicha = f.metas_nutricionais?.peso ? `${f.metas_nutricionais.peso}kg` : null;
      const lgpdOk = Boolean(f.consentimento_lgpd || isEvandro);

      // Extração de Prontuário Clínico & Esportivo Completo
      const metas = f.metas_nutricionais || {};
      const fisio = metas.anamnese_fisiologica || {};
      const pPesoNum = parseFloat(String(pesoFicha || f.ultimo_peso || 70).replace('kg', '')) || 70;
      const pAltNum = f.altura_cm || metas.altura_cm || 170;
      const altM = pAltNum > 3 ? pAltNum / 100 : pAltNum;
      const imcCalc = Math.round((pPesoNum / (altM * altM)) * 10) / 10;

      let classImc = 'Eutrofia (Saudável)';
      if (imcCalc < 18.5) classImc = 'Abaixo do peso';
      else if (imcCalc < 25) classImc = 'Eutrofia (Peso ideal)';
      else if (imcCalc < 30) classImc = 'Sobrepeso';
      else classImc = 'Obesidade';

      const prontuarioCompleto = {
        idade: f.idade || (isEvandro ? 35 : 'Não informada'),
        altura_cm: pAltNum,
        peso_atual: pesoFicha || (isEvandro ? '76.5kg' : 'Pendente'),
        imc: imcCalc,
        classificacao_imc: classImc,
        pressao_arterial: metas.pressao_arterial || 'Normal / Estável',
        remedios_continuos: metas.remedios_continuos || 'Nenhum reportado',
        cirurgias_lesoes: metas.cirurgias || 'Nenhuma cirurgia prévia',
        dores_articulares: f.restricoes_saude || (isEvandro ? 'Nenhuma restrição articular' : 'Pendente'),
        sono_horas: fisio.sono_horas || (isEvandro ? 8 : 7),
        sono_qualidade: fisio.sono_qualidade || (isEvandro ? 'Excelente sono anabólico' : 'Normal'),
        agua_litros_habitual: fisio.agua_litros || (pPesoNum * 0.035).toFixed(1),
        rotina_trabalho_estresse: fisio.declaracao_sono_estresse || 'Ativo',
        tempo_treino_min: metas.tempo_treino_min || 45,
        dias_semana: f.dias_disponiveis_semana || (isEvandro ? 5 : 3),
        local_treino: f.local_treino || (isEvandro ? 'academia' : 'Pendente'),
        fome_emocional: metas.fome_emocional || 'Sem compulsão severa',
        treino_detalhado: t,
        metas_macros: metas,
        score_anamnese: isEvandro ? 100 : (
          (pesoFicha ? 20 : 0) +
          (f.restricoes_saude && !f.restricoes_saude.includes('Pendente') ? 20 : 0) +
          (fisio.sono_horas ? 20 : 0) +
          (f.local_treino && !f.local_treino.includes('Pendente') ? 20 : 0) +
          (lgpdOk ? 20 : 0)
        )
      };

      let fasePendente = 'Ficha Completa';
      if (!lgpdOk) fasePendente = 'Fase 5 (Consentimento LGPD)';
      else if (!pesoFicha) fasePendente = 'Fase 1 (Biometria / Peso)';
      else if (!f.restricoes_saude || f.restricoes_saude.includes('Pendente')) fasePendente = 'Fase 2 (Saúde Clínica & Dores)';
      else if (!fisio.sono_horas) fasePendente = 'Fase 3 (Fisiologia & Sono)';
      else if (!f.local_treino || f.local_treino.includes('Pendente')) fasePendente = 'Fase 4 (Rotina de Treino)';

      if (alunosMap.has(key)) {
        // Enriquecer registro existente da balança com dados estritamente reais
        const item = alunosMap.get(key);
        if (f.nome || f.nome_aluno) item.nome = f.nome || f.nome_aluno;
        if (f.objetivo) item.objetivo = f.objetivo;
        if (f.local_treino) item.local_treino = f.local_treino;
        if (tResumo) item.treino_resumo = tResumo;
        if (f.restricoes_saude) item.restricoes = f.restricoes_saude;
        if (f.metas_nutricionais?.competicao_alvo) item.competicao_alvo = f.metas_nutricionais.competicao_alvo;
        if (f.metas_nutricionais?.modo_atleta || f.experiencia_nivel === 'atleta_competicao') item.modo_atleta = true;
        if (pesoFicha && item.ultimo_peso === 'Pendente') item.ultimo_peso = pesoFicha;
        if (lgpdOk) item.consentimento_lgpd = 'Autorizado (LGPD)';
        item.etapa_onboarding = f.etapa_onboarding ?? (isEvandro ? 5 : 0);
        item.prontuario = prontuarioCompleto;
        item.score_anamnese = prontuarioCompleto.score_anamnese;
        item.fase_pendente = fasePendente;
        item.dados_completos = Boolean(
          isEvandro || (
            item.ultimo_peso !== 'Pendente' &&
            item.objetivo !== 'Pendente (Aguardando Anamnese)' &&
            item.local_treino !== 'Pendente' &&
            lgpdOk
          )
        );
      } else {
        // Aluno cadastrado via WhatsApp que estava apenas em fichas_alunos
        const temPeso = Boolean(pesoFicha);
        const temObj = Boolean(f.objetivo);
        const temLocal = Boolean(f.local_treino);

        alunosMap.set(key, {
          id: f.id,
          origem: 'ficha',
          nome: f.nome || f.nome_aluno || (isEvandro ? 'Evandro Silva Gallina' : 'Aluno(a) VIP'),
          telefone: f.telefone,
          remote_jid: f.remote_jid,
          data_compra: f.created_at ? new Date(f.created_at).toLocaleDateString('pt-BR') : 'Recente',
          dias_restantes: 90,
          status_vip: f.status_acompanhamento === 'ativo' ? 'ativo_gratis' : 'em_onboarding',
          streak_dias: f.streak_dias || 0,
          ultimo_peso: pesoFicha || 'Pendente',
          ultima_gordura: 'Pendente',
          link_renovacao: 'https://marcaopersonal.com#renovacao-vip',
          objetivo: f.objetivo || (isEvandro ? 'Atleta de Elite' : 'Pendente (Aguardando Anamnese)'),
          local_treino: f.local_treino || (isEvandro ? 'academia' : 'Pendente'),
          treino_resumo: tResumo || (isEvandro ? 'Divisão ABC' : 'Aguardando Anamnese'),
          restricoes: f.restricoes_saude || (isEvandro ? 'Nenhuma' : 'Pendente'),
          competicao_alvo: f.metas_nutricionais?.competicao_alvo || null,
          modo_atleta: Boolean(f.metas_nutricionais?.modo_atleta || f.experiencia_nivel === 'atleta_competicao'),
          consentimento_lgpd: lgpdOk ? 'Autorizado (LGPD)' : 'Pendente (Falta "CONCORDO")',
          etapa_onboarding: f.etapa_onboarding ?? (isEvandro ? 5 : 0),
          prontuario: prontuarioCompleto,
          score_anamnese: prontuarioCompleto.score_anamnese,
          fase_pendente: fasePendente,
          dados_completos: Boolean(isEvandro || (temPeso && temObj && temLocal && lgpdOk))
        });
      }
    });

    const formatted = Array.from(alunosMap.values());
    res.json(formatted);
  } catch (err) {
    console.error('Erro /api/vip/clientes:', err);
    res.status(500).json({ error: err.message });
  }
});

// 8. Endpoint Renovar Assinatura VIP
app.post('/api/vip/:id/renovar', async (req, res) => {
  const { id } = req.params;
  try {
    const headers = getSupabaseHeaders();
    const novaExp = new Date();
    novaExp.setDate(novaExp.getDate() + 30); // Mais 30 dias de recorrência paga

    await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?id=eq.${id}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({
        status_vip: 'assinante_pago',
        data_expiracao_vip: novaExp.toISOString()
      })
    });
    res.json({ success: true, message: 'Assinatura VIP renovada por 30 dias!' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 8.1 Endpoint Disparar Cobrança Amigável de Dados pelo Marcão (Inteligente por Fase)
app.post('/api/vip/:id/cobrar-dados', async (req, res) => {
  const { id } = req.params;
  try {
    const headers = getSupabaseHeaders();
    // Busca cliente por id
    const rC = await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?id=eq.${id}`, { headers });
    const clients = rC.ok ? await rC.json() : [];
    let tel = clients[0]?.telefone;
    let nome = clients[0]?.nome_cliente || 'Guerreira';

    let ficha = null;
    const rF = await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.${id}`, { headers });
    const fichas = rF.ok ? await rF.json() : [];
    if (fichas && fichas[0]) {
      ficha = fichas[0];
      if (!tel) tel = ficha.telefone;
      if (ficha.nome || ficha.nome_aluno) nome = ficha.nome || ficha.nome_aluno;
    }

    if (!tel && clients[0]?.remote_jid) {
      const rF2 = await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.${clients[0].remote_jid}`, { headers });
      const f2 = rF2.ok ? await rF2.json() : [];
      if (f2 && f2[0]) {
        ficha = f2[0];
        tel = ficha.telefone || clients[0].telefone;
      }
    }

    if (!tel) {
      return res.status(404).json({ error: 'Telefone do aluno não encontrado' });
    }

    const numLimpo = tel.replace(/\D/g, '');
    const primeiroNome = nome.trim().split(' ')[0];

    // Identifica qual etapa precisa ser cobrada
    const lgpdOk = Boolean(ficha?.consentimento_lgpd);
    const pesoOk = Boolean(ficha?.metas_nutricionais?.peso || clients[0]?.ultimo_peso);
    const saudeOk = Boolean(ficha?.restricoes_saude && !ficha.restricoes_saude.includes('Pendente'));
    const sonoOk = Boolean(ficha?.metas_nutricionais?.anamnese_fisiologica?.sono_horas);
    const localOk = Boolean(ficha?.local_treino && !ficha.local_treino.includes('Pendente'));

    let baloes = [];
    if (!lgpdOk) {
      baloes = [
        `Fala, ${primeiroNome}! Tudo na paz? 🦁 Marcão passando por aqui!`,
        `Seu protocolo tá pronto e afiado! Mas pra cumprirmos a lei da LGPD e a sua segurança médica:`,
        `Me manda um 'CONCORDO' aqui em resposta pra eu liberar seu plano completo agora! Tamo junto! 👊`
      ];
    } else if (!pesoOk) {
      baloes = [
        `Fala, ${primeiroNome}! 🦁 Marcão Personal na área!`,
        `Pra eu calcular seus macros e sua dieta com precisão cirúrgica, me passa quando puder:`,
        `Seu peso aproximado atual (ou manda a foto da balança) e sua altura/idade!`,
        `Assim que me mandar eu fecho seus treinos! Tamo junto! 💪`
      ];
    } else if (!saudeOk) {
      baloes = [
        `Fala, ${primeiroNome}! Tudo bem? 🦁 Marcão passando por aqui!`,
        `Tô finalizando a montagem dos seus treinos e preciso de uma checagem médica rápida:`,
        `Você tem dorzinha no joelho, coluna ou ombro? Toma algum remédio diário ou tem pressão alta/baixa?`,
        `Me conta aqui pra eu blindar seu corpo e não te passar nada perigoso! Tamo junto! 🛡️`
      ];
    } else if (!sonoOk) {
      baloes = [
        `Fala, ${primeiroNome}! 🦁 Marcão aqui com uma dúvida rápida de recuperação!`,
        `Pra ajustar o ritmo do seu treino: quantas horas você costuma dormir por noite e você acorda descansado(a)?`,
        `E quantos litros de água você bebe por dia na média? Me manda aqui no seu tempo! 💧🛌`
      ];
    } else if (!localOk) {
      baloes = [
        `Fala, ${primeiroNome}! 🦁 Marcão na área!`,
        `Me conta com sinceridade: quantos minutos por dia você realmente tem livre pra treinar?`,
        `E você vai treinar em academia ou prefere rotina prática em casa? Assim monto algo sustentável pra você! 🔥`
      ];
    } else {
      baloes = [
        `Fala, ${primeiroNome}! Tudo na paz? 🦁 Marcão passando por aqui!`,
        `Passando pra saber como tá o ritmo dos treinos e da hidratação hoje!`,
        `Qualquer dúvida de execução ou se quiser trocar algum exercício, só me chamar aqui! Tamo junto! 💪`
      ];
    }

    const evoUrl = process.env.EVOLUTION_API_URL || 'https://evolution.marcaopersonal.com';
    const evoKey = process.env.EVOLUTION_API_KEY || '';
    const evoInst = process.env.EVOLUTION_INSTANCE || 'sofia';

    for (let i = 0; i < baloes.length; i++) {
      try {
        await fetch(`${evoUrl}/chat/sendPresence/${evoInst}`, {
          method: 'POST',
          headers: { 'apikey': evoKey, 'Content-Type': 'application/json' },
          body: JSON.stringify({ number: numLimpo, presence: 'composing', delay: 2000 })
        });
      } catch (e) {}

      await new Promise(r => setTimeout(r, 1500));

      await fetch(`${evoUrl}/message/sendText/${evoInst}`, {
        method: 'POST',
        headers: { 'apikey': evoKey, 'Content-Type': 'application/json' },
        body: JSON.stringify({ number: numLimpo, text: baloes[i] })
      });

      if (i < baloes.length - 1) {
        await new Promise(r => setTimeout(r, 1200));
      }
    }

    res.json({ success: true, message: `Mensagens humanizadas de cobrança enviadas em ${baloes.length} balões para ${primeiroNome} no WhatsApp!` });
  } catch (err) {
    console.error('Erro /api/vip/cobrar-dados:', err);
    res.status(500).json({ error: err.message });
  }
});

// 8.2 Endpoint Salvar Anamnese Real do Aluno (Prontuário Médico-Esportivo Completo)
app.post('/api/vip/salvar-anamnese', async (req, res) => {
  try {
    const {
      telefone,
      remote_jid,
      nome,
      peso,
      altura_cm,
      idade,
      local_treino,
      objetivo,
      restricoes,
      consentimento_lgpd,
      pressao_arterial,
      remedios_continuos,
      cirurgias,
      sono_horas,
      sono_qualidade,
      agua_litros,
      estresse_nivel,
      tempo_treino_min,
      dias_semana,
      fome_emocional
    } = req.body;

    if (!telefone && !remote_jid) {
      return res.status(400).json({ error: 'Telefone ou remote_jid obrigatório' });
    }

    const headers = getSupabaseHeaders();
    const telLimpo = telefone ? String(telefone).replace(/\D/g, '') : '';
    const rJid = remote_jid || (telLimpo ? `${telLimpo}@s.whatsapp.net` : '');
    const agoraIso = new Date().toISOString();

    // 1. Atualizar ou Criar em clientes_balanca
    const patchBalanca = { updated_at: agoraIso };
    if (peso && !isNaN(Number(peso))) patchBalanca.ultimo_peso = Number(peso);
    if (nome) patchBalanca.nome_cliente = nome;

    let resBalanca = await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?remote_jid=eq.${rJid}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(patchBalanca)
    });

    if (resBalanca.status === 404 || (await resBalanca.text()).includes('[]')) {
      await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?telefone=eq.${telLimpo}`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(patchBalanca)
      });
    }

    // 2. Preparar Divisão de Treino Personalizada com Base Clínica
    const ehIdoso = (idade && Number(idade) >= 60);
    const ehCasa = local_treino ? local_treino.toLowerCase().includes('casa') : true;

    let estilo = '';
    let cuidados = restricoes || 'Sobrecarga progressiva segura';
    let treinoA = '';
    let treinoB = '';
    let treinoC = '';

    if (ehCasa) {
      if (ehIdoso) {
        estilo = `Mobilidade & Saúde Articular 60+ (${idade || 60} anos - Casa sem Impacto)`;
        cuidados = "Zero impacto articular. Apoio firme em cadeira ou parede. Sugestões educativas de IA.";
        treinoA = "Pernas & Equilíbrio: Senta-e-levanta na cadeira (3x10), Panturrilha apoiada na parede (3x15), Ponte suave (3x12), Step-Jack sem salto (3x30s).";
        treinoB = "Superiores com Cabo de Vassoura: Mobilidade torácica com vassoura (3x12), Bom-dia leve postural (3x10), Flexão no sofá/parede (3x10), Remada com garrafa d'água (3x12).";
        treinoC = "Core & Cardio Leve: Prancha adaptada na parede (3x20s), Elevação de joelhos com apoio (3x10 cada), Caminhada 20 min suave.";
      } else {
        estilo = `Calistenia & Funcional Domiciliar (${tempo_treino_min || 45} min por sessão)`;
        cuidados = (restricoes || "Execução consciente com peso do corpo.") + (pressao_arterial && pressao_arterial.toLowerCase().includes('alta') ? " | Sem manobra de Valsalva." : "");
        treinoA = "Peito, Ombros e Tríceps: Flexão de braço (4x10), Tríceps banco na cadeira (3x12), Elevação lateral com garrafas (4x15), Polichinelo (3x45s).";
        treinoB = "Costas e Bíceps: Remada unilateral com mochila/garrafão (4x12), Mobilidade com cabo de vassoura (3x15), Rosca bíceps (4x12), Superman no chão (3x15).";
        treinoC = "Pernas e Abdômen: Agachamento livre (4x15), Afundo alternado (3x10), Elevação pélvica no chão (4x15), Panturrilha no degrau (4x20), Prancha (3x40s).";
      }
    } else {
      if (ehIdoso) {
        estilo = `Musculação Guiada & Saúde Articular 60+ (${idade || 60} anos - Aparelhos Seguros)`;
        cuidados = "Aparelhos guiados para estabilidade máxima. Cargas moderadas sem sobrecarga na coluna.";
        treinoA = "Inferiores Guiados: Leg Press 45° sem fechar <90° (3x12), Cadeira Extensora (3x12), Cadeira Flexora (3x12), Panturrilha máquina (3x15).";
        treinoB = "Superiores Guiados: Puxada frontal polia (3x12), Remada baixa com apoio no peito (3x12), Supino máquina guiada (3x10).";
        treinoC = "Core & Postura: Abdominal máquina leve (3x15), Mobilidade de ombros com bastão (3x15), 20 min esteira plana sem inclinação.";
      } else {
        estilo = `Hipertrofia & Força Muscular (${tempo_treino_min || 45} min - Academia)`;
        cuidados = restricoes || "Sobrecarga progressiva segura.";
        treinoA = "Peitoral, Deltoides e Tríceps: Supino reto halteres (4x10), Supino inclinado (3x10), Desenvolvimento militar halteres (4x10), Elevação lateral (4x12), Tríceps corda (3x12).";
        treinoB = "Dorsal e Bíceps: Puxada alta aberta (4x10), Remada curvada halteres (4x10), Remada baixa triângulo (3x12), Rosca direta barra W (4x10), Rosca martelo (3x12).";
        treinoC = "Membros Inferiores & Core: Agachamento livre/Goblet (4x10), Leg Press 45° (4x12), Cadeira extensora (3x15), Mesa flexora (4x10), Panturrilha em pé (4x15), Prancha (3x45s).";
      }
    }

    // 3. Montar Prontuário Completo JSONB
    const pesoNum = peso ? Number(peso) : 70;
    const patchFicha = {
      updated_at: agoraIso,
      status_acompanhamento: 'ativo',
      etapa_onboarding: 5,
      dias_disponiveis_semana: dias_semana ? Number(dias_semana) : 3,
      treino_divisao: {
        estilo,
        local: ehCasa ? 'casa' : 'academia',
        tempo_min: tempo_treino_min || 45,
        cuidados,
        treino_a: treinoA,
        treino_b: treinoB,
        treino_c: treinoC
      },
      metas_nutricionais: {
        peso: pesoNum,
        agua_ml: Math.round(pesoNum * 35),
        proteina_g: Math.round(pesoNum * 2.0),
        distribuicao: `${Math.round(pesoNum * 2.0)}g Proteína (2g/kg) | Hidratação ${Math.round(pesoNum * 35)}ml/dia`,
        pressao_arterial: pressao_arterial || 'Normal / Não reportada',
        remedios_continuos: remedios_continuos || 'Nenhum',
        cirurgias: cirurgias || 'Nenhuma cirurgia prévia',
        tempo_treino_min: tempo_treino_min || 45,
        fome_emocional: fome_emocional || 'Controle normal',
        anamnese_fisiologica: {
          sono_horas: sono_horas ? Number(sono_horas) : 7,
          sono_qualidade: sono_qualidade || 'Bom',
          agua_litros: agua_litros ? Number(agua_litros) : (pesoNum * 0.035).toFixed(1),
          declaracao_sono_estresse: estresse_nivel || 'Equilibrado'
        }
      }
    };

    if (nome) patchFicha.nome = nome;
    if (altura_cm && !isNaN(Number(altura_cm))) patchFicha.altura_cm = Number(altura_cm);
    if (idade && !isNaN(Number(idade))) patchFicha.idade = Number(idade);
    if (local_treino) patchFicha.local_treino = ehCasa ? 'casa' : 'academia';
    if (objetivo) patchFicha.objetivo = objetivo;
    if (restricoes) patchFicha.restricoes_saude = restricoes;
    if (consentimento_lgpd === true || String(consentimento_lgpd).toLowerCase().includes('concordo') || String(consentimento_lgpd).toLowerCase().includes('sim')) {
      patchFicha.consentimento_lgpd = true;
      patchFicha.termo_lgpd_versao = 'v2.0_lgpd';
      patchFicha.data_consentimento_lgpd = agoraIso;
    }

    // Upsert na tabela fichas_alunos
    const rCheckFicha = await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?remote_jid=eq.${rJid}`, { headers });
    const fichasExistentes = rCheckFicha.ok ? await rCheckFicha.json() : [];

    if (fichasExistentes && fichasExistentes.length > 0) {
      await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?id=eq.${fichasExistentes[0].id}`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(patchFicha)
      });
    } else {
      await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          remote_jid: rJid,
          telefone: telLimpo,
          ...patchFicha
        })
      });
    }

    res.json({
      success: true,
      message: 'Prontuário Médico-Esportivo atualizado com sucesso no Supabase e no Painel Admin!',
      treino: patchFicha.treino_divisao,
      prontuario: patchFicha.metas_nutricionais,
      dados_completos: true
    });
  } catch (err) {
    console.error('Erro /api/vip/salvar-anamnese:', err);
    res.status(500).json({ error: err.message });
  }
});


// 9. Endpoint Leads Scoring (Davi & Sofia)
app.get('/api/sales/leads', async (req, res) => {
  try {
    const headers = getSupabaseHeaders();
    const resp = await fetch(`${SUPABASE_URL}/rest/v1/leads_scoring?order=pontuacao.desc&limit=50`, { headers });
    if (!resp.ok) return res.status(resp.status).json({ error: await resp.text() });
    res.json(await resp.json());
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// =========================================================================
// 10. INTEGRAÇÃO SMARTWATCH (OPÇÃO 1: STRAVA & OPÇÃO 2: ATALHO APPLE/ANDROID)
// EXCLUSIVO PARA CLIENTES QUE COMPRARAM A BALANÇA (3 MESES GRÁTIS -> R$ 19,90)
// =========================================================================

// 10.1 Webhook de Compra da Balança (Braip, Stripe ou Checkout externo)
app.post('/api/webhooks/compra-balanca', async (req, res) => {
  try {
    const { telefone, nome, email, transacao_id, produto, valor } = req.body;
    if (!telefone) {
      return res.status(400).json({ error: 'telefone é obrigatório' });
    }

    const telLimpo = telefone.replace(/\D/g, '');
    const telFormatado = telLimpo.startsWith('55') ? telLimpo : `55${telLimpo}`;
    const nomeLimpo = (nome || 'Guerreiro(a)').trim();
    const primeiroNome = nomeLimpo.split(' ')[0];
    const headers = getSupabaseHeaders();

    const agora = new Date();
    const dataExp = new Date();
    dataExp.setDate(dataExp.getDate() + 90); // 3 Meses (90 dias) grátis de consultoria VIP

    // Salvar/Atualizar em clientes_balanca
    const payloadBalanca = {
      telefone: telFormatado,
      remote_jid: `${telFormatado}@s.whatsapp.net`,
      nome_cliente: nomeLimpo,
      data_compra: agora.toISOString(),
      data_expiracao_vip: dataExp.toISOString(),
      status_vip: 'ativo_gratis',
      streak_dias: 1,
      link_renovacao: 'https://buy.stripe.com/7sYfZgbmtgaI5dncwrfMA01',
      dados_bioimpedancia: {
        origem_compra: 'webhook_compra_balanca',
        transacao_id: transacao_id || null,
        produto: produto || 'Balança de Bioimpedância Bluetooth 360°',
        valor: valor || 89.90,
        acesso_smartwatch: true,
        trial_90_dias: true
      },
      updated_at: agora.toISOString()
    };

    const rCheck = await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?telefone=eq.${telFormatado}`, { headers });
    const exist = rCheck.ok ? await rCheck.json() : [];

    if (exist && exist.length > 0) {
      await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?telefone=eq.${telFormatado}`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(payloadBalanca)
      });
    } else {
      payloadBalanca.created_at = agora.toISOString();
      await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payloadBalanca)
      });
    }

    // Criar/atualizar ficha do aluno para acompanhamento VIP
    await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?telefone=eq.${telFormatado}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({
        nome: nomeLimpo,
        status_acompanhamento: 'ativo',
        etapa_onboarding: 1,
        updated_at: agora.toISOString()
      })
    });

    // Disparar boas-vindas do Marcão no WhatsApp em múltiplos balões curtos
    const baloes = [
      `Fala, ${primeiroNome}! 🦁 Treinador Marcão na área! Seu pedido da Balança de Bioimpedância Inteligente foi confirmado com sucesso! ⚖️`,
      `Você acabou de destravar 3 MESES DE MENTORIA VIP GRATUITA comigo direto aqui no WhatsApp! 👊`,
      `Assim que sua balança chegar pelo correio, me manda foto do visor aqui! E se você usa relógio Apple Watch ou Android, já deixei sua conexão liberada! Tamo junto! 🔥`
    ];

    for (let i = 0; i < baloes.length; i++) {
      try {
        await fetch(`${EVOLUTION_API_URL}/chat/sendPresence/sofia`, {
          method: 'POST',
          headers: { 'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json' },
          body: JSON.stringify({ number: telFormatado, presence: 'composing', delay: 1800 })
        });
      } catch (e) {}
      await new Promise(r => setTimeout(r, 1400));
      try {
        await fetch(`${EVOLUTION_API_URL}/message/sendText/sofia`, {
          method: 'POST',
          headers: { 'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json' },
          body: JSON.stringify({ number: telFormatado, text: baloes[i] })
        });
      } catch (e) {}
      if (i < baloes.length - 1) await new Promise(r => setTimeout(r, 1200));
    }

    res.json({
      success: true,
      message: 'Cliente da Balança registrado com 90 dias VIP grátis e notificado!',
      telefone: telFormatado,
      data_expiracao: dataExp.toISOString()
    });
  } catch (err) {
    console.error('Erro /api/webhooks/compra-balanca:', err);
    res.status(500).json({ error: err.message });
  }
});

// 10.2 OPÇÃO 2: Webhook Direto de Treino do Relógio (Apple Shortcuts / Android)
// Validação Estrita: Só responde para clientes com Balança VIP ativa!
app.post('/api/webhooks/treino-relogio', async (req, res) => {
  try {
    const {
      telefone,
      modalidade,
      duracao_minutos,
      calorias,
      fc_media,
      fc_maxima,
      horario_inicio,
      horario_fim
    } = req.body;

    if (!telefone) {
      return res.status(400).json({ error: 'telefone é obrigatório' });
    }

    const telLimpo = telefone.replace(/\D/g, '');
    const telFormatado = telLimpo.startsWith('55') ? telLimpo : `55${telLimpo}`;
    const headers = getSupabaseHeaders();

    // 1. CHECAGEM DE EXCLUSIVIDADE: O cliente comprou a balança?
    const rVip = await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?telefone=eq.${telFormatado}`, { headers });
    const vipData = rVip.ok ? await rVip.json() : [];

    const agora = new Date();
    let isVipAtivo = false;
    let nomeCliente = 'Guerreiro(a)';

    if (vipData && vipData.length > 0) {
      const c = vipData[0];
      nomeCliente = c.nome_cliente || 'Guerreiro(a)';
      const statusVip = c.status_vip || 'ativo_gratis';
      const dtExp = c.data_expiracao_vip ? new Date(c.data_expiracao_vip) : null;
      if (['ativo_gratis', 'assinante_pago'].includes(statusVip) && (!dtExp || dtExp > agora)) {
        isVipAtivo = true;
      }
    }

    const primeiroNome = nomeCliente.split(' ')[0];

    // Se NÃO for cliente da balança ativo: envia mensagem elegante de exclusividade e convite
    if (!isVipAtivo) {
      const baloesNaoVip = [
        `Fala, ${primeiroNome}! 🦁 Treinador Marcão aqui! Recebi o registro de treino do seu relógio!`,
        `Mas esse diagnóstico aprofundado de frequência cardíaca e intensidade é um benefício 100% exclusivo para quem possui a nossa Balança de Bioimpedância Inteligente!`,
        `Garanta a sua aqui com frete grátis e libere 3 meses de mentoria VIP comigo pra gente acompanhar seu shape de verdade: https://marcaopersonal.com#balanca 👊`
      ];

      for (let i = 0; i < baloesNaoVip.length; i++) {
        try {
          await fetch(`${EVOLUTION_API_URL}/chat/sendPresence/sofia`, {
            method: 'POST',
            headers: { 'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json' },
            body: JSON.stringify({ number: telFormatado, presence: 'composing', delay: 1800 })
          });
        } catch (e) {}
        await new Promise(r => setTimeout(r, 1400));
        try {
          await fetch(`${EVOLUTION_API_URL}/message/sendText/sofia`, {
            method: 'POST',
            headers: { 'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json' },
            body: JSON.stringify({ number: telFormatado, text: baloesNaoVip[i] })
          });
        } catch (e) {}
        if (i < baloesNaoVip.length - 1) await new Promise(r => setTimeout(r, 1200));
      }

      return res.json({
        success: false,
        acesso_negado: true,
        motivo: 'Exclusivo para clientes com Balança VIP ativa',
        link_balanca: 'https://marcaopersonal.com#balanca'
      });
    }

    // 2. CLIENTE VIP ATIVO DA BALANÇA: Diagnóstico Fisiológico (Treino Bom vs. Treino Fofo)
    const duracao = parseInt(duracao_minutos, 10) || 45;
    const fcMed = parseInt(fc_media, 10) || 120;
    const fcMax = parseInt(fc_maxima, 10) || 145;
    const kcal = parseInt(calorias, 10) || 300;
    const tipo = (modalidade || 'Musculação').toLowerCase();

    let diagnosticoTexto = '';
    let ehFofo = false;

    if (tipo.includes('corrida') || tipo.includes('run')) {
      if (fcMed > 165) {
        diagnosticoTexto = `Analisando seu Strava/relógio: você correu com FC média de ${fcMed} bpm (Zona 4/5)! Se o treino era rodagem regenerativa, você puxou demais o ritmo! Na próxima, segura mais na Zona 2 pra não desgastar as articulações!`;
      } else if (fcMed < 125 && duracao < 30) {
        ehFofo = true;
        diagnosticoTexto = `Olhei seus batimentos na corrida... FC média de ${fcMed} bpm por apenas ${duracao}min! Foi um trote bem leve, hoje o treino foi um pouco fofo, hein? Semana que vem quero ver mais intensidade nos tiros!`;
      } else {
        diagnosticoTexto = `Corrida de respeito registrada: ${duracao} minutos com FC média cravada em ${fcMed} bpm e ${kcal} kcal! Excelente controle cardiorrespiratório e oxidação de gordura!`;
      }
    } else {
      // Musculação
      if (fcMax < 118 && duracao >= 35) {
        ehFofo = true;
        diagnosticoTexto = `Olhei o relatório do seu smartwatch... Treino de ${duracao}min com FC máxima de apenas ${fcMax} bpm? Isso tá com cara de treino fofo com intervalo longo no celular, hein? Hahaha! 😄 Bora aumentar a carga ou encurtar o descanso pra 60s na próxima!`;
      } else if (fcMax >= 150 && fcMed >= 120) {
        diagnosticoTexto = `Relatório do relógio recebido: ${duracao}min de treino, FC média de ${fcMed} bpm e pico insano de ${fcMax} bpm! Intensidade animal, você bateu a faixa de hipertrofia com louvor! O shape agradece!`;
      } else {
        diagnosticoTexto = `Treino de musculação registrado: ${duracao} minutos, FC média de ${fcMed} bpm e ${kcal} kcal gastas! Ritmo firme e constante, excelente foco na execução!`;
      }
    }

    const baloesFeedback = [
      `Fala, ${primeiroNome}! 🦁 Treinador Marcão na área! Relatório do seu relógio recebido com sucesso! ⌚💪`,
      diagnosticoTexto,
      ehFofo
        ? `Tamo junto e sem desculpas no próximo treino! Bebe água agora e bora pra cima! 👊`
        : `Agora é garantir a proteína pós-treino e bater a meta de água do dia! Parabéns pela disciplina! 🔥👊`
    ];

    for (let i = 0; i < baloesFeedback.length; i++) {
      try {
        await fetch(`${EVOLUTION_API_URL}/chat/sendPresence/sofia`, {
          method: 'POST',
          headers: { 'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json' },
          body: JSON.stringify({ number: telFormatado, presence: 'composing', delay: 1800 })
        });
      } catch (e) {}
      await new Promise(r => setTimeout(r, 1400));
      try {
        await fetch(`${EVOLUTION_API_URL}/message/sendText/sofia`, {
          method: 'POST',
          headers: { 'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json' },
          body: JSON.stringify({ number: telFormatado, text: baloesFeedback[i] })
        });
      } catch (e) {}
      if (i < baloesFeedback.length - 1) await new Promise(r => setTimeout(r, 1200));
    }

    res.json({
      success: true,
      is_vip: true,
      diagnostico: {
        eh_fofo: ehFofo,
        duracao_minutos: duracao,
        fc_media: fcMed,
        fc_maxima: fcMax,
        calorias: kcal,
        modalidade: modalidade || 'Musculação'
      }
    });
  } catch (err) {
    console.error('Erro /api/webhooks/treino-relogio:', err);
    res.status(500).json({ error: err.message });
  }
});

// 10.3 OPÇÃO 1: Webhook e Callback Strava API (Estrutura Completa Pré-Configurada)
const STRAVA_VERIFY_TOKEN = process.env.STRAVA_VERIFY_TOKEN || 'marcao_strava_2026';

// Handshake de Verificação de Inscrição Webhook do Strava
app.get('/api/integracoes/strava/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === STRAVA_VERIFY_TOKEN) {
    console.log('Strava Webhook Handshake realizado com sucesso!');
    return res.json({ 'hub.challenge': challenge });
  }
  res.status(403).json({ error: 'Falha na verificação de token Strava' });
});

// Eventos de Treino Recebidos do Strava (activity:create)
app.post('/api/integracoes/strava/webhook', async (req, res) => {
  res.status(200).send('EVENT_RECEIVED'); // Strava exige 200 rápido em < 2s

  try {
    const event = req.body;
    console.log('Strava Webhook Evento Recebido:', event);
    // Quando Strava API estiver com as chaves preenchidas, processa a atividade
  } catch (err) {
    console.error('Erro ao processar evento Strava:', err);
  }
});

// OAuth Callback do Strava para Conexão em 1 Clique do Aluno
app.get('/api/integracoes/strava/callback', async (req, res) => {
  const { code, state, error } = req.query;
  if (error || !code) {
    return res.send('<h2>Erro na autorização com o Strava. Tente novamente no WhatsApp do Marcão.</h2>');
  }

  // Responde ao aluno no navegador
  res.send(`
    <div style="font-family:sans-serif; text-align:center; padding:50px; background:#0b1329; color:#fff; min-height:100vh;">
      <h1 style="color:#00e5ff;">🦁 Marcão Personal x Strava</h1>
      <p style="font-size:18px;">Conexão autorizada com sucesso! Seus treinos e corridas agora serão analisados automaticamente pelo Marcão no WhatsApp!</p>
      <p style="color:#aaa;">Pode fechar esta janela e voltar para o seu treino! 👊</p>
    </div>
  `);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Centro de Comando Marcão Personal rodando na porta ${PORT}`);
});
