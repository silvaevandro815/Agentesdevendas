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
// Middleware de body parser dinâmico: permite até 25MB para fotos de perfil do aluno e 50KB para rotas públicas
app.use((req, res, next) => {
  if (req.originalUrl && req.originalUrl.includes('/api/aluno/avatar')) {
    return express.json({ limit: '25mb' })(req, res, next);
  }
  return express.json({ limit: '50kb' })(req, res, next);
});
app.use(express.static(path.join(__dirname, 'public'), {
  dotfiles: 'ignore', // NUNCA serve arquivos ocultos ou .env estaticamente
  etag: true,
  setHeaders: (res, filePath) => {
    // 1. Arquivos HTML nunca devem ficar presos no cache do navegador (atualizacoes imediatas)
    if (filePath.endsWith('.html')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
    } else if (filePath.match(/\.(css|js)$/i)) {
      // 2. CSS e JS usam version query string (ex: styles.css?v=...)
      res.setHeader('Cache-Control', 'public, max-age=300, must-revalidate');
    } else if (filePath.match(/\.(jpg|jpeg|png|webp|svg|ico)$/i)) {
      // 3. Imagens de alta performance
      res.setHeader('Cache-Control', 'public, max-age=86400, immutable');
    }
  }
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

// Upload de foto de perfil do aluno com gravação estática no site e relay para a API/Supabase
app.post('/api/aluno/avatar/:id', async (req, res) => {
  const alunoId = req.params.id || '';
  const idLimpo = (alunoId || '').replace(/\D/g, '') || 'avatar_usuario';
  let staticUrl = `/uploads/avatars/${idLimpo}.jpg`;
  
  // 1. Salva localmente no container site para acesso imediato via URL estática
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

  // 2. Encaminha para o container da API (FastAPI) para gravar no Supabase
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
      if (apiRes.ok) {
        const data = await apiRes.json();
        return res.status(apiRes.status).json(data);
      }
    } catch (e) {
      // tenta proximo
    }
  }

  return res.json({ sucesso: true, foto_url: staticUrl });
});

// ============================================================================
// INTEGRAÇÃO STRAVA & SMARTWATCH HUB (OAUTH, CALLBACK E WEBHOOK EM 1 CLIQUE)
// ============================================================================
const STRAVA_CLIENT_ID = process.env.STRAVA_CLIENT_ID || '187215';
const STRAVA_CLIENT_SECRET = process.env.STRAVA_CLIENT_SECRET || 'b04505c55803754e0ad1cac759a0c0cf2a0999a5';
const STRAVA_VERIFY_TOKEN = process.env.STRAVA_VERIFY_TOKEN || 'marcao_strava_secure_webhook_2026';
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://qkopgftfrfftoyndhhfj.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL || 'https://evolution.marcaopersonal.com';
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY || '';

// 1. Redirecionamento Strava OAuth em 1 Clique
app.get('/api/integracoes/strava/oauth', (req, res) => {
  const tel = (req.query.tel || req.query.phone || '').replace(/\D/g, '');
  const redirectUri = encodeURIComponent('https://marcaopersonal.com/api/integracoes/strava/callback');
  const stravaUrl = `https://www.strava.com/oauth/authorize?client_id=${STRAVA_CLIENT_ID}&response_type=code&redirect_uri=${redirectUri}&scope=read,activity:read_all&approval_prompt=auto&state=${tel}`;
  return res.redirect(stravaUrl);
});

// 2. Callback de Autorização Strava
app.get('/api/integracoes/strava/callback', async (req, res) => {
  const { code, state, error } = req.query;
  const telFormatado = state ? state.replace(/\D/g, '') : '';
  const portalUrl = telFormatado ? `/aluno?id=${telFormatado}` : '/aluno';

  if (error || !code) {
    return res.status(400).send(`
      <!DOCTYPE html>
      <html lang="pt-BR">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Erro Strava — Marcão Personal AI</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
          body { background: #07090e; color: #fff; display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
          .card { max-width: 480px; width: 100%; background: #0f131a; border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 36px 28px; text-align: center; }
          .icon { font-size: 54px; margin-bottom: 16px; }
          h1 { font-size: 24px; font-weight: 800; margin-bottom: 12px; color: #ff5555; }
          p { color: #8e9bb0; font-size: 15px; line-height: 1.6; margin-bottom: 24px; }
          .btn { display: inline-block; background: #fc5200; color: #fff; text-decoration: none; font-weight: 800; padding: 14px 28px; border-radius: 14px; font-size: 15px; }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="icon">⚠️</div>
          <h1>Autorização Cancelada ou Não Concluída</h1>
          <p>A sincronização com o Strava não pôde ser completada. Você pode tentar novamente a qualquer momento direto pelo seu Portal do Aluno.</p>
          <a href="${portalUrl}" class="btn">VOLTAR AO MEU PORTAL DO ALUNO</a>
        </div>
      </body>
      </html>
    `);
  }

  try {
    // Troca o authorization code pelos tokens oficiais do Strava
    const bodyParams = new URLSearchParams({
      client_id: STRAVA_CLIENT_ID,
      client_secret: STRAVA_CLIENT_SECRET,
      code: code,
      grant_type: 'authorization_code'
    });

    const tokenRes = await fetch('https://www.strava.com/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: bodyParams.toString()
    });

    if (!tokenRes.ok) {
      const errTxt = await tokenRes.text();
      console.error('[Strava Token Exchange Error]', tokenRes.status, errTxt);
      return res.status(500).send(`<h2>Erro ao processar tokens do Strava (${tokenRes.status}). <a href="${portalUrl}">Voltar</a></h2>`);
    }

    const tokenData = await tokenRes.json();
    const athlete = tokenData.athlete || {};
    const athleteNome = `${athlete.firstname || ''} ${athlete.lastname || ''}`.trim() || 'Atleta';
    const athleteFoto = athlete.profile && !athlete.profile.includes('avatar/athlete/large.png') ? athlete.profile : '';

    console.log(`[STRAVA SUCESSO] Atleta: ${athleteNome} (ID: ${athlete.id}), Tel: ${telFormatado}`);

    // Persistir tokens no Supabase (fichas_alunos e clientes_balanca)
    if (telFormatado && SUPABASE_KEY) {
      const headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json'
      };

      // 1. Atualizar em fichas_alunos
      try {
        const rFicha = await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?telefone=eq.${telFormatado}`, { headers });
        if (rFicha.ok) {
          const fichas = await rFicha.json();
          if (fichas && fichas.length > 0) {
            const f = fichas[0];
            const metas = f.metas_nutricionais || {};
            metas.strava_athlete_id = athlete.id;
            metas.strava_access_token = tokenData.access_token;
            metas.strava_refresh_token = tokenData.refresh_token;
            metas.strava_token_expires_at = tokenData.expires_at;
            metas.strava_nome_atleta = athleteNome;
            metas.strava_conectado_em = new Date().toISOString();
            metas.tem_strava = true;

            await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?telefone=eq.${telFormatado}`, {
              method: 'PATCH',
              headers,
              body: JSON.stringify({
                metas_nutricionais: metas,
                updated_at: new Date().toISOString()
              })
            });
            console.log(`[STRAVA] Ficha de aluno ${telFormatado} atualizada com sucesso!`);
          }
        }
      } catch (errFicha) {
        console.error('[STRAVA] Erro ao salvar ficha aluno:', errFicha);
      }

      // 2. Atualizar em clientes_balanca
      try {
        const rBal = await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?telefone=eq.${telFormatado}`, { headers });
        if (rBal.ok) {
          const balancas = await rBal.json();
          if (balancas && balancas.length > 0) {
            const b = balancas[0];
            const bData = b.dados_bioimpedancia || {};
            bData.strava_athlete_id = athlete.id;
            bData.strava_access_token = tokenData.access_token;
            bData.strava_refresh_token = tokenData.refresh_token;
            bData.strava_token_expires_at = tokenData.expires_at;
            bData.tem_strava = true;

            const patchBal = {
              dados_bioimpedancia: bData,
              updated_at: new Date().toISOString()
            };
            if ((!b.nome_cliente || b.nome_cliente === 'Aluno VIP') && athlete.firstname) {
              patchBal.nome_cliente = athleteNome;
            }

            await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?telefone=eq.${telFormatado}`, {
              method: 'PATCH',
              headers,
              body: JSON.stringify(patchBal)
            });
            console.log(`[STRAVA] Clientes balança ${telFormatado} atualizado com sucesso!`);
          }
        }
      } catch (errBal) {
        console.error('[STRAVA] Erro ao salvar clientes balança:', errBal);
      }

      // 3. Disparar notificação de boas-vindas no WhatsApp via Evolution API
      try {
        const pNome = athlete.firstname || 'Guerreira';
        const baloes = [
          `Fala, ${pNome}! 🦁 Treinador Marcão na área! Sua conta do Strava foi conectada com sucesso! ⌚💨`,
          `Agora todo treino de corrida, caminhada, pedal ou cardio que você salvar no Strava vem direto pra mim! Vou auditar seu ritmo, distância, pace e queima calórica! 👊🔥`,
          `Tamo junto e bora colocar esse shape pra voar! 💪🦁`
        ];

        for (const msg of baloes) {
          await fetch(`${EVOLUTION_API_URL}/message/sendText/sofia`, {
            method: 'POST',
            headers: {
              'apikey': EVOLUTION_API_KEY,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              number: telFormatado,
              text: msg,
              delay: 1500
            })
          });
        }
      } catch (errWpp) {
        console.error('[STRAVA] Erro no aviso WhatsApp:', errWpp);
      }
    }

    // Retorna página cinematográfica de sucesso
    return res.send(`
      <!DOCTYPE html>
      <html lang="pt-BR">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Strava Conectado com Sucesso! — Marcão Personal AI</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
          body {
            background: radial-gradient(circle at 50% 20%, #161c28 0%, #07090e 80%);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 24px;
          }
          .card {
            max-width: 500px;
            width: 100%;
            background: rgba(18, 23, 33, 0.95);
            border: 1px solid rgba(252, 82, 0, 0.35);
            border-radius: 28px;
            padding: 40px 32px;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0,0,0,0.6), 0 0 40px rgba(252, 82, 0, 0.15);
            backdrop-filter: blur(20px);
          }
          .badge-strava {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(252, 82, 0, 0.15);
            border: 1px solid rgba(252, 82, 0, 0.5);
            color: #fc5200;
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 20px;
            text-transform: uppercase;
          }
          .athlete-box {
            background: #0d1118;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 20px;
            padding: 20px;
            margin: 24px 0;
            display: flex;
            align-items: center;
            gap: 16px;
            text-align: left;
          }
          .athlete-img {
            width: 64px;
            height: 64px;
            border-radius: 18px;
            border: 2px solid #fc5200;
            object-fit: cover;
          }
          .athlete-placeholder {
            width: 64px;
            height: 64px;
            border-radius: 18px;
            background: linear-gradient(135deg, #fc5200, #ff8800);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            font-weight: 900;
            color: #fff;
          }
          .athlete-name { font-size: 18px; font-weight: 800; color: #fff; margin-bottom: 4px; }
          .athlete-sub { font-size: 13px; color: #00F0FF; font-weight: 700; }
          h1 { font-size: 28px; font-weight: 900; margin-bottom: 12px; letter-spacing: -0.5px; }
          h1 span { color: #fc5200; }
          p { color: #94a3b8; font-size: 15px; line-height: 1.6; margin-bottom: 28px; }
          .btn-portal {
            display: block;
            width: 100%;
            background: linear-gradient(135deg, #fc5200 0%, #ff7700 100%);
            color: #fff;
            text-decoration: none;
            font-weight: 800;
            padding: 16px;
            border-radius: 16px;
            font-size: 16px;
            letter-spacing: 0.5px;
            box-shadow: 0 10px 30px rgba(252, 82, 0, 0.4);
            transition: all 0.2s ease;
          }
          .btn-portal:hover { transform: translateY(-2px); box-shadow: 0 14px 35px rgba(252, 82, 0, 0.6); }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="badge-strava">⚡ STRAVA CONECTADO</div>
          <h1>Conta <span>Vinculada</span> com Sucesso!</h1>
          
          <div class="athlete-box">
            ${athleteFoto ? `<img src="${athleteFoto}" alt="${athleteNome}" class="athlete-img">` : `<div class="athlete-placeholder">${athleteNome.charAt(0)}</div>`}
            <div>
              <div class="athlete-name">${athleteNome}</div>
              <div class="athlete-sub">ID Strava: #${athlete.id} • Ativo no Marcão AI</div>
            </div>
          </div>

          <p>O Marcão já está sincronizado com sua conta! Toda vez que você finalizar um treino de corrida, caminhada, cardio ou pedal, os dados serão analisados com rigor profissional!</p>

          <a href="${portalUrl}" class="btn-portal">VOLTAR AO MEU PORTAL DO ALUNO ⚡</a>
        </div>
      </body>
      </html>
    `);
  } catch (errServer) {
    console.error('[STRAVA CALLBACK EXCEPTION]', errServer);
    return res.status(500).send(`<h2>Erro interno ao finalizar integração Strava. <a href="${portalUrl}">Voltar ao portal</a></h2>`);
  }
});

// 3. Handshake de Verificação do Webhook Strava
app.get('/api/integracoes/strava/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === STRAVA_VERIFY_TOKEN) {
    console.log('[STRAVA WEBHOOK] Handshake realizado com sucesso!');
    return res.json({ 'hub.challenge': challenge });
  }
  return res.status(403).json({ error: 'Falha na verificação de token Strava' });
});

// 4. Recebimento de Atividades do Strava (activity:create)
app.post('/api/integracoes/strava/webhook', async (req, res) => {
  res.status(200).send('EVENT_RECEIVED'); // Strava exige 200 rápido em < 2s

  try {
    const event = req.body;
    console.log('[STRAVA WEBHOOK EVENTO]', event);

    if (event.object_type === 'activity' && event.aspect_type === 'create') {
      const activityId = event.object_id;
      const athleteId = event.owner_id;
      const headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`
      };

      // Localiza o aluno dono do ID no Supabase (fichas_alunos ou clientes_balanca)
      let alunoTel = null;
      let alunoNome = 'Guerreira';
      let tokenAtividade = null;

      const rFicha = await fetch(`${SUPABASE_URL}/rest/v1/fichas_alunos?metas_nutricionais->>strava_athlete_id=eq.${athleteId}`, { headers });
      if (rFicha.ok) {
        const fichas = await rFicha.json();
        if (fichas && fichas.length > 0) {
          alunoTel = fichas[0].telefone;
          alunoNome = fichas[0].nome ? fichas[0].nome.split(' ')[0] : 'Guerreira';
          tokenAtividade = fichas[0].metas_nutricionais?.strava_access_token;
        }
      }

      if (!alunoTel) {
        const rBal = await fetch(`${SUPABASE_URL}/rest/v1/clientes_balanca?dados_bioimpedancia->>strava_athlete_id=eq.${athleteId}`, { headers });
        if (rBal.ok) {
          const balancas = await rBal.json();
          if (balancas && balancas.length > 0) {
            alunoTel = balancas[0].telefone;
            alunoNome = balancas[0].nome_cliente ? balancas[0].nome_cliente.split(' ')[0] : 'Guerreira';
            tokenAtividade = balancas[0].dados_bioimpedancia?.strava_access_token;
          }
        }
      }

      if (!alunoTel || !tokenAtividade) {
        console.log(`[STRAVA WEBHOOK] Atividade ${activityId} ignorada: atleta ${athleteId} não mapeado com token.`);
        return;
      }

      // Busca dados da atividade na API do Strava
      const rAct = await fetch(`https://www.strava.com/api/v3/activities/${activityId}`, {
        headers: { 'Authorization': `Bearer ${tokenAtividade}` }
      });

      if (rAct.ok) {
        const act = await rAct.json();
        const distKm = (act.distance / 1000).toFixed(2);
        const tempoMin = Math.round(act.moving_time / 60);
        const calorias = act.calories ? Math.round(act.calories) : null;
        const tipoTreino = act.type || 'Cardio';

        // Dispara mensagem no WhatsApp pelo Marcão
        const msgTreino = [
          `Sensacional, ${alunoNome}! 🦁 Vi que você acabou de registrar um treino no Strava! ⌚💨`,
          `Modalidade: ${tipoTreino} | Distância: ${distKm}km | Tempo: ${tempoMin} minutos${calorias ? ` | Queima: ~${calorias} kcal` : ''}! 🔥`,
          `Orgulho de ver sua constância e determinação! Segue o plano e bebe água agora! 👊🦁`
        ];

        for (const m of msgTreino) {
          await fetch(`${EVOLUTION_API_URL}/message/sendText/sofia`, {
            method: 'POST',
            headers: { 'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json' },
            body: JSON.stringify({ number: alunoTel, text: m, delay: 1500 })
          });
        }
      }
    }
  } catch (errWebhook) {
    console.error('[STRAVA WEBHOOK ERROR]', errWebhook);
  }
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

// Proxy relay seguro para status do WhatsApp
app.get('/api/whatsapp/status', async (req, res) => {
  const bases = [
    'http://api:8000',
    'http://8ced6ba01715:8000',
    'http://172.17.0.1:8000',
    'https://api.marcaopersonal.com'
  ];

  for (const base of bases) {
    try {
      const apiRes = await fetch(`${base}/api/whatsapp/status`, { signal: AbortSignal.timeout(6000) });
      const data = await apiRes.json();
      return res.status(apiRes.status).json(data);
    } catch (e) {
      // tenta proximo
    }
  }

  return res.status(500).json({ sucesso: false, erro: 'Erro consultando status do WhatsApp' });
});

// ============================================================================
// SEO & AI Search Engine (GEO) Endpoints
// ============================================================================

// Sitemap Oficial para Google Search Console, Bing e Motores de Busca
app.get('/sitemap.xml', (req, res) => {
  res.setHeader('Content-Type', 'application/xml; charset=UTF-8');
  res.setHeader('Cache-Control', 'public, max-age=3600, s-maxage=3600');
  res.sendFile(path.join(__dirname, 'public', 'sitemap.xml'));
});

// Robots.txt com liberacao para Googlebot e Rastreadores de IA (GPTBot, ClaudeBot, Perplexity)
app.get('/robots.txt', (req, res) => {
  res.setHeader('Content-Type', 'text/plain; charset=UTF-8');
  res.setHeader('Cache-Control', 'public, max-age=3600, s-maxage=3600');
  res.sendFile(path.join(__dirname, 'public', 'robots.txt'));
});

// LLMs.txt para Motores de Busca Generativa (GEO - Generative Engine Optimization)
app.get(['/llms.txt', '/llms-full.txt'], (req, res) => {
  res.setHeader('Content-Type', 'text/plain; charset=UTF-8');
  res.setHeader('Cache-Control', 'public, max-age=3600, s-maxage=3600');
  res.sendFile(path.join(__dirname, 'public', 'llms.txt'));
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
