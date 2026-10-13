const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Rota de status e saúde
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', brand: 'Marcão Personal', timestamp: new Date() });
});

// Captura opcional de lead direcionando para WhatsApp
app.post('/api/lead', (req, res) => {
  const { name, phone, objective } = req.body;
  console.log(`[Lead Recebido] Nome: ${name}, Tel: ${phone}, Objetivo: ${objective}`);
  res.json({ success: true, message: 'Lead registrado' });
});

// Meta Conversions API (CAPI) Server-Side Relay
app.post('/api/track', async (req, res) => {
  const { event_name, event_source_url, custom_data, user_data } = req.body;
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
              client_ip_address: clientIp.split(',')[0].trim()
            },
            custom_data: custom_data || {}
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
      return res.json({ success: true, capi_status: metaResp.status, meta_response: metaData });
    } catch (err) {
      console.error('Erro CAPI server:', err.message);
    }
  }

  res.json({ success: true, queued: true });
});

// Redirecionamento SPA / fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Loja Marcão Personal rodando na porta ${PORT}`);
});
