const express = require('express');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3000;

// Configura proxy reverso para identificar IPs reais em produção (Traefik / Coolify)
app.set('trust proxy', 1);

// Configuração de Segurança HTTP (Helmet)
app.use(helmet({
  contentSecurityPolicy: false, // Permite carregar CDNs de fontes, Meta Pixel e Shopee sem bloqueio
  crossOriginEmbedderPolicy: false,
  crossOriginResourcePolicy: { policy: "cross-origin" }
}));

// Desabilita cabeçalho que expõe que o servidor roda Express (anti-fingerprinting)
app.disable('x-powered-by');

// Rate Limiting Geral para navegação (300 requisições por IP a cada 15 minutos)
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 300,
  standardHeaders: true,
  legacyHeaders: false,
  validate: false,
  message: { error: 'Limite de requisições excedido. Tente novamente mais tarde.' }
});
app.use(generalLimiter);

// Rate Limiting Estrito para rotas de telemetria e captura de leads (30 reqs por minuto por IP)
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 30,
  standardHeaders: true,
  legacyHeaders: false,
  validate: false,
  message: { error: 'Muitas requisições para a API. Por favor, aguarde.' }
});

app.use(cors());
// Limite rigoroso de tamanho do payload JSON contra ataques de DoS por estouro de buffer
app.use(express.json({ limit: '30kb' }));
app.use(express.static(path.join(__dirname, 'public'), {
  dotfiles: 'ignore', // NUNCA serve arquivos ocultos ou .env estaticamente
  etag: true,
  maxAge: '1h'
}));

// Rota de status e saúde
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', brand: 'Marcão Personal', timestamp: new Date() });
});

// Captura opcional de lead direcionando para WhatsApp com validação de payload e rate limit
app.post('/api/lead', apiLimiter, (req, res) => {
  const { name, phone, objective } = req.body || {};
  if (!phone || typeof phone !== 'string' || phone.length > 50) {
    return res.status(400).json({ error: 'Dados inválidos' });
  }
  const cleanName = (name || '').slice(0, 100);
  const cleanObj = (objective || '').slice(0, 200);
  console.log(`[Lead Recebido] Nome: ${cleanName}, Tel: ${phone.slice(0, 20)}, Objetivo: ${cleanObj}`);
  res.json({ success: true, message: 'Lead registrado' });
});

// Meta Conversions API (CAPI) Server-Side Relay com rate limit e isolamento total de segredos
app.post('/api/track', apiLimiter, async (req, res) => {
  const { event_name, event_source_url, custom_data, user_data } = req.body || {};
  
  if (!event_name || typeof event_name !== 'string' || event_name.length > 50) {
    return res.status(400).json({ error: 'Evento inválido' });
  }

  const pixelId = process.env.META_PIXEL_ID || '1417931927184389';
  let token = process.env.META_ACCESS_TOKEN;
  if (!token) {
    try {
      const fs = require('fs');
      const envPath = path.join(__dirname, '../../.env');
      if (fs.existsSync(envPath)) {
        const envContent = fs.readFileSync(envPath, 'utf8');
        const match = envContent.match(/META_ACCESS_TOKEN=([^\r\n]+)/);
        if (match) token = match[1].trim();
      }
    } catch (e) {}
  }

  console.log(`[Telemetria Site CAPI] Evento: ${event_name} | URL: ${event_source_url}`);

  if (pixelId && token) {
    try {
      const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '177.130.242.56';
      const userAgent = req.headers['user-agent'] || (user_data && user_data.client_user_agent) || 'Mozilla/5.0';

      const payload = {
        data: [
          {
            event_name: event_name,
            event_time: Math.floor(Date.now() / 1000),
            action_source: 'website',
            event_source_url: event_source_url || 'https://marcaopersonal.com',
            user_data: {
              client_user_agent: userAgent,
              client_ip_address: String(clientIp).split(',')[0].trim()
            },
            custom_data: (custom_data && typeof custom_data === 'object') ? custom_data : {}
          }
        ],
        access_token: token
      };

      const metaResp = await fetch(`https://graph.facebook.com/v21.0/${pixelId}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const metaData = await metaResp.json();
      return res.json({ success: true, capi_status: metaResp.status });
    } catch (err) {
      console.error('Erro CAPI server:', err.message);
    }
  }

  res.json({ success: true, queued: true });
});

// Portal / Landing Page Individual do Aluno (OpenGym + Marcão AI)
app.get('/aluno', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'aluno.html'));
});

app.get('/aluno/:id', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'aluno.html'));
});

// Upload de foto de perfil do aluno (suporta até 10MB) com gravação estática no site
app.post('/api/aluno/avatar/:id', express.json({ limit: '10mb' }), async (req, res) => {
  const alunoId = req.params.id || '';
  const idLimpo = (alunoId || '').replace(/\D/g, '') || 'avatar_usuario';
  
  // Salva localmente no container site para acesso imediato via URL estática
  try {
    const imgData = (req.body || {}).image || '';
    if (imgData) {
      const base64Str = imgData.includes('base64,') ? imgData.split('base64,')[1] : imgData;
      const avatarDir = path.join(__dirname, 'public', 'uploads', 'avatars');
      await fs.promises.mkdir(avatarDir, { recursive: true });
      await fs.promises.writeFile(path.join(avatarDir, `${idLimpo}.jpg`), Buffer.from(base64Str, 'base64'));
    }
  } catch (errLocal) {
    console.error('[AVATAR LOCAL WRITE]', errLocal.message);
  }

  const candidateUrls = [
    process.env.API_URL,
    'http://api:8000',
    'http://127.0.0.1:8000'
  ].filter(Boolean);

  for (const base of candidateUrls) {
    try {
      const apiRes = await fetch(`${base}/api/aluno/avatar/${alunoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req.body)
      });
      const data = await apiRes.json();
      return res.status(apiRes.status).json(data);
    } catch (e) {
      // tenta proximo
    }
  }

  return res.json({ sucesso: true, foto_url: `/uploads/avatars/${idLimpo}.jpg` });
});

// Redirecionamento Strava OAuth direto na plataforma
app.get('/api/integracoes/strava/oauth', (req, res) => {
  const tel = req.query.tel || '';
  const redirectUri = encodeURIComponent('https://api.marcaopersonal.com/api/integracoes/strava/callback');
  const clientId = process.env.STRAVA_CLIENT_ID || '146959';
  const stravaUrl = `https://www.strava.com/oauth/authorize?client_id=${clientId}&response_type=code&redirect_uri=${redirectUri}&scope=read,activity:read_all&state=${tel}`;
  return res.redirect(stravaUrl);
});

// Proxy relay seguro para os dados do portal do aluno
app.get('/api/aluno/portal/:id', async (req, res) => {
  const alunoId = req.params.id || '';
  const candidateUrls = [
    process.env.API_URL,
    'http://api:8000',
    'http://127.0.0.1:8000'
  ].filter(Boolean);

  for (const base of candidateUrls) {
    try {
      const apiRes = await fetch(`${base}/api/aluno/portal/${alunoId}`);
      if (apiRes.ok) {
        const data = await apiRes.json();
        return res.json(data);
      }
    } catch (e) {
      // continua tentando próximo candidato
    }
  }

  return res.json({
    sucesso: true,
    aluno: { nome: 'Guerreiro(a)', objetivo: 'Evolução Física 360°', badge_local: 'Treino Personalizado', streak_dias: 3 },
    matematica_fisica: { agua_ml_diaria: 2800, agua_garrafas_500ml: 5.6, proteina_g_diaria: 150, calorias_alvo_dieta: 1800, tipo_dieta: 'Plano Personalizado Marcão', peso_kg: 70 },
    rotina_treinos: { dias: [] },
    arsenal_produtos: []
  });
});

// Proxy relay seguro para salvar treino diário do aluno
app.post('/api/aluno/treino/salvar/:id', express.json(), async (req, res) => {
  const alunoId = req.params.id || '';
  const candidateUrls = [
    process.env.API_URL,
    'http://api:8000',
    'http://127.0.0.1:8000'
  ].filter(Boolean);

  for (const base of candidateUrls) {
    try {
      const apiRes = await fetch(`${base}/api/aluno/treino/salvar/${alunoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req.body)
      });
      const data = await apiRes.json();
      return res.status(apiRes.status).json(data);
    } catch (e) {
      // tenta proximo
    }
  }

  return res.status(500).json({ sucesso: false, erro: 'Erro conectando a API Marcao' });
});

// Proxy relay seguro para reformular ficha de treino
app.post('/api/aluno/ficha/reformular/:id', express.json(), async (req, res) => {
  const alunoId = req.params.id || '';
  const candidateUrls = [
    process.env.API_URL,
    'http://api:8000',
    'http://127.0.0.1:8000'
  ].filter(Boolean);

  for (const base of candidateUrls) {
    try {
      const apiRes = await fetch(`${base}/api/aluno/ficha/reformular/${alunoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req.body)
      });
      const data = await apiRes.json();
      return res.status(apiRes.status).json(data);
    } catch (e) {
      // tenta proximo
    }
  }

  return res.status(500).json({ sucesso: false, erro: 'Erro conectando a API Marcao' });
});

// Redirecionamento SPA / fallback seguro
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Middleware genérico para captura de erros sem vazar stacktrace
app.use((err, req, res, next) => {
  console.error('[SITE ERROR]', err.message);
  const status = err.status || err.statusCode || 500;
  res.status(status).json({ error: status === 413 ? 'Payload excessivamente grande.' : 'Erro interno no servidor' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Loja Marcão Personal rodando com proteção ativa na porta ${PORT}`);
});
