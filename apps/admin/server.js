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
const SUPABASE_KEY = process.env.SUPABASE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || '';
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
      { name: "Sofia", role: "Atendimento ao Cliente", tag: "Cliente respondido em minutos", badges: ["playbook-de-atendimento", "Buscar no Cérebro"], active: true },
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
  const pythonCmd = `python apps/api/creative_factory.py --tipo ${tipo || 'manha'} --formato ${formato || 'carrossel'} --sem-ia`;
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

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Centro de Comando Marcão Personal rodando na porta ${PORT}`);
});
