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
    type: "Roteiro Reels/TikTok",
    title: "Roteiro 01: 'O Ralo do Chuveiro Não Mente' (KIT IArmonize)",
    content: "Gancho (0-3s): 'Se o ralo do seu chuveiro parece uma peruca todo dia... para tudo e escuta o Marcão!'\nSolução: Nutrição profunda e tônico vital com silício inteligente e biotina.\nCTA: 'Toca no link da bio e garanta o seu com frete grátis antes que esgote o lote!'",
    budget: null,
    status: "pending",
    date: new Date().toLocaleDateString('pt-BR')
  },
  {
    id: 2,
    agent: "Téo",
    department: "Marketing",
    type: "Roteiro Reels/TikTok",
    title: "Roteiro 05: 'Mito da Creatina Feminina & Tônus sem Inchaço'",
    content: "Gancho (0-3s): 'Menina, quem foi que te falou que Creatina engorda e dá retenção? Que absurdo!'\nExplicação: Água dentro da célula muscular (hidratação pura) vs debaixo da pele.\nCTA: 'Comente DEFINIR para receber a oferta no WhatsApp ou clique no link da bio.'",
    budget: null,
    status: "pending",
    date: new Date().toLocaleDateString('pt-BR')
  },
  {
    id: 3,
    agent: "Lia",
    department: "Marketing",
    type: "Copy Anúncio Feed/Stories",
    title: "Anúncio 03: Colágeno Hidrolisado + Ácido Hialurônico Nature's Prime",
    content: "Texto: 'A partir dos 25 anos você perde 1% de colágeno ao ano. Não adianta tomar colágeno de farmácia que o estômago destrói: precisa ser Hidrolisado com Hialurônico.'\nHeadline: Pele firme e hidratada sem gastar fortunas ✨\nPreço: R$ 164,90 (300g Abacaxi c/ Hortelã)",
    budget: null,
    status: "pending",
    date: new Date().toLocaleDateString('pt-BR')
  },
  {
    id: 4,
    agent: "Rui",
    department: "Tráfego Pago",
    type: "Campanha Meta Ads (Instagram)",
    title: "Campanha 01: 'Creatina Pura & Tônus sem Inchaço' (Vídeo Téo + Copy Lia)",
    content: "Público: Mulheres 24-48 anos, interesse em Fitness, Musculação, Emagrecimento e Pilates.\nDestino: Conversa WhatsApp com Sofia ou Checkout Braip.\nStatus no Gerenciador: PAUSADA (Aguardando Aprovação de Evandro).",
    budget: "R$ 16,50 / dia (Teto Diário)",
    status: "pending",
    date: new Date().toLocaleDateString('pt-BR')
  },
  {
    id: 5,
    agent: "Rui",
    department: "Tráfego Pago",
    type: "Campanha Meta Ads (Instagram)",
    title: "Campanha 02: 'Caneta Azempika — Queima Térmica & Fome Noturna'",
    content: "Público: Homens e Mulheres 25-55 anos com interesse em Emagrecimento Saudável e Ansiedade.\nDestino: Checkout Braip Direto (R$ 99,00).\nStatus no Gerenciador: PAUSADA.",
    budget: "R$ 16,50 / dia (Teto Diário)",
    status: "pending",
    date: new Date().toLocaleDateString('pt-BR')
  },
  {
    id: 6,
    agent: "Nina",
    department: "Marketing",
    type: "Calendário Editorial",
    title: "Cronograma de Conteúdo Semanal (Instagram & TikTok — Semana 1)",
    content: "7 postagens programadas cobrindo os 4 pilares: Mitos (Creatina), Alertas de Queda Capilar (IArmonize), Rotina de Pele (Colágeno) e Prova de Pureza com laudo de laboratório.",
    budget: null,
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
