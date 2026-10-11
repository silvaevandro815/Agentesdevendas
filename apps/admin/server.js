const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Estado em memória (persistido via arquivo ou Postgres)
let pendingApprovals = [
  {
    id: 1,
    agent: "Téo",
    department: "Marketing",
    type: "Criativo Reels/TikTok",
    title: "Roteiro: Mito da Creatina Feminina & Tônus sem Inchaço",
    content: "Gancho (0-3s): 'Menina, se você acha que creatina incha seu corpo, você está perdendo o melhor queimador de gordura...'\nCTA: 'Comente DEFINIR para receber a oferta no WhatsApp.'",
    budget: null,
    status: "pending",
    date: new Date().toLocaleDateString('pt-BR')
  },
  {
    id: 2,
    agent: "Rui",
    department: "Tráfego Pago",
    type: "Campanha Meta Ads (Instagram)",
    title: "Campanha Feed/Stories: Kit Definição & Beleza",
    content: "Público: Mulheres 25-45 anos, interesse em Fitness, Emagrecimento, Pilates e Beleza.\nCriativo: Vídeo 1 da Lia/Téo.\nDestino: Conversa WhatsApp com Sofia.",
    budget: "R$ 16,50 / dia (Teto Diário)",
    status: "pending",
    date: new Date().toLocaleDateString('pt-BR')
  }
];

// Listar aprovações pendentes
app.get('/api/approvals', (req, res) => {
  res.json(pendingApprovals);
});

// Ação de aprovar / rejeitar
app.post('/api/approvals/:id', (req, res) => {
  const { id } = req.params;
  const { action } = req.body; // 'approved' ou 'rejected'
  
  const item = pendingApprovals.find(a => a.id === parseInt(id));
  if (item) {
    item.status = action;
    return res.json({ success: true, item });
  }
  res.status(404).json({ error: "Item não encontrado" });
});

// Resumo dos Agentes
app.get('/api/agents', (req, res) => {
  res.json({
    marketing: [
      { name: "Bela", role: "Redatora de Conteúdo/SEO", tag: "Encontrada no Google", badges: ["artigo-seo", "Buscar no Cérebro", "Emitir artefato"], active: true },
      { name: "Lia", role: "Copywriter", tag: "Copy que converte", badges: ["copywriting", "landing-page-conversao", "Estúdio de copy"], active: true },
      { name: "Téo", role: "Criador de Conteúdo Visual", tag: "Vídeos que prendem", badges: ["roteiros-reels", "ugc-tiktok", "Emitir artefato"], active: true },
      { name: "Rui", role: "Gestor de Tráfego Pago", tag: "Campanhas Cirúrgicas", badges: ["meta-ads", "pausado-para-aprovacao", "teto-diario"], active: true },
      { name: "Nina", role: "Social Media", tag: "Presença Constante", badges: ["calendario-editorial", "agendamento-automatico"], active: true }
    ],
    vendas: [
      { name: "Sofia", role: "Atendimento ao Cliente", tag: "Cliente respondido em minutos", badges: ["playbook-de-atendimento", "Buscar no Cérebro", "Emitir artefato"], active: true },
      { name: "Davi", role: "Vendedor & Recuperador", tag: "Nenhum lead esfria", badges: ["follow-up-de-vendas", "Buscar no Cérebro", "Emitir artefato"], active: true }
    ],
    financeiro: [
      { name: "Iago", role: "Analista de Dados", tag: "Números que decidem", badges: ["relatorio-executivo", "Buscar no Cérebro", "Emitir artefato"], active: true },
      { name: "Marta", role: "Analista Financeira", tag: "O caixa sob controle", badges: ["fluxo-de-caixa", "Buscar no Cérebro", "Emitir artefato"], active: true }
    ],
    operacoes: [
      { name: "Alan", role: "Jurídico & Compliance", tag: "Contrato revisado antes de assinar", badges: ["contrato-prestacao-servico", "nda-confidencialidade", "conformidade-anvisa"], active: true },
      { name: "Otto", role: "Analista de Processos", tag: "A empresa que roda sem você", badges: ["sop-processos", "Buscar no Cérebro", "Emitir artefato"], active: true },
      { name: "Paulo", role: "RH & Gestor de IAs", tag: "Contrata certo, cuida do time", badges: ["contratacao-e-onboarding", "Buscar no Cérebro", "Emitir artefato"], active: true }
    ]
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Centro de Comando rodando na porta ${PORT}`);
});
