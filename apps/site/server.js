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

// Redirecionamento SPA / fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Loja Marcão Personal rodando na porta ${PORT}`);
});
