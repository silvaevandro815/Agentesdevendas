# 🏢 Centro de Comando de IA — Sua Empresa 24h (`marcaopersonal.com`)

> Sistema autônomo de agentes de IA para e-commerce no nicho de **Emagrecimento, Musculação e Estética Corporal (Corpo & Beleza)**, operando sem estoque sob supervisão e aprovação explícita do Diretor **Evandro da Silva Gallina**.

---

## 🧭 Visão Geral & Arquitetura

O sistema é inspirado na metodologia de Centro de Comando de IA demonstrada no vídeo de referência, onde departamentos inteiros operam 24/7 conectados a um **Cérebro Central**:

```
                         ╔═════════════════════════════════╗
                         ║      EVANDRO (DIRETOR)          ║
                         ║  admin.marcaopersonal.com       ║
                         ╚════════════════╤════════════════╝
                                          │ Aprovações em 1 clique (Human-in-the-Loop)
                                          ▼
                         ╔═════════════════════════════════╗
                         ║      O CÉREBRO DIGITAL (/brain) ║
                         ║  Regras, Políticas, Ofertas     ║
                         ╚════════════════╤════════════════╝
                                          │ Fonte Única da Verdade
        ┌───────────────────┬─────────────┴───────┬───────────────────┐
        ▼                   ▼                     ▼                   ▼
┌──────────────┐    ┌──────────────┐      ┌──────────────┐    ┌──────────────┐
│  MARKETING   │    │    VENDAS    │      │  FINANCEIRO  │    │  OPERAÇÕES   │
│ Bela (SEO)   │    │ Sofia (Zap)  │      │ Iago (Dados) │    │ Alan (Leis)  │
│ Lia (Copy)   │    │ Davi (Follow)│      │ Marta(Caixa) │    │ Otto(Logist.)│
│ Téo (Vídeo)  │    └──────────────┘      └──────────────┘    │ Paulo (RH)   │
│ Rui (Tráfego)│                                              └──────────────┘
│ Nina(Social) │
└──────────────┘
```

---

## 👥 Organograma dos Agentes

### 1. Marketing & Conteúdo
- **Bela (Redatora de Conteúdo & SEO):** Produz artigos educativos para blog e posicionamento orgânico no Google.
- **Lia (Copywriter Persuasiva):** Escreve páginas de captura, copys de alta conversão e quebra de objeções.
- **Téo (Criador de Conteúdo Visual):** Cria roteiros dinâmicos para Reels, TikTok e Shorts com ganchos virais.
- **Rui (Gestor de Tráfego Pago):** Estrutura campanhas no Meta Ads sempre em modo **PAUSADO** e com teto diário fixo (R$ 16,50/dia).
- **Nina (Social Media):** Gerencia o calendário editorial de 7 dias e programa postagens.

### 2. Vendas & Atendimento
- **Sofia (Atendimento WhatsApp 24h):** Responde dúvidas em menos de 2 minutos, quebra mitos (ex: *"creatina não engorda"*), apresenta os combos e envia links de checkout.
- **Davi (Vendedor & Recuperador):** Faz follow-up de carrinhos abandonados (máximo de 3 toques consultivos).

### 3. Financeiro & Dados
- **Iago (Analista de Dados):** Consolida métricas diárias às 21h (ROAS, CPA, volume de vendas, conversão).
- **Marta (Analista Financeira):** Monitora margens brutas (>55%), custos de gateway e fluxo de caixa.

### 4. Operações, Gente & Jurídico
- **Alan (Jurídico & Compliance ANVISA):** Garante que nenhuma copy use termos terapêuticos proibidos ou falsas promessas de emagrecimento milagroso.
- **Otto (Processos & Logística Sem Estoque):** Recebe pagamentos aprovados, transmite ao fornecedor e dispara códigos de rastreamento no WhatsApp.
- **Paulo (RH de IAs):** Integra novos agentes e gerencia permissões.

---

## 🧠 Estrutura do Cérebro (`/brain`)
- `01-produto/`: Ficha técnica, composições e margens do Kit Definição & Beleza.
- `02-marca/`: Posicionamento, tom de voz e propósito da `marcaopersonal.com`.
- `03-clientes-avatars/`: Psicologia de compra de homens e mulheres focados em estética e treino.
- `04-vendas/`: Scripts de fechamento e playbook da Sofia.
- `05-marketing/`: Ganchos de 3 segundos e diretrizes para anúncios.
- `06-processos/`: Fluxos de postagem e despacho de mercadorias sem estoque.
- `07-financeiro/`: Metas orçamentárias e limites de custo por cliente.
- `08-juridico/`: Termos legais, LGPD e limites da ANVISA.

---

## 🚀 Como Fazer o Deploy na VPS Hostinger com Coolify

### Passo 1: Configurar os Registros DNS na Hostinger
No painel do seu domínio `marcaopersonal.com`, aponte os seguintes registros **Tipo A** para o **IP da sua VPS**:
- `admin` ➔ `IP_DA_SUA_VPS`
- `n8n` ➔ `IP_DA_SUA_VPS`
- `@` (ou `loja`) ➔ `IP_DA_SUA_VPS`

### Passo 2: No Painel Coolify
1. Acesse seu Coolify na VPS (`http://IP_DA_VPS:8000`).
2. Crie um novo **Projeto** chamado `Loja IA - Marcao Personal`.
3. Escolha **Add Resource ➔ Docker Compose (ou Git Repository)**.
4. Conecte ao seu repositório: `https://github.com/silvaevandro815/Agentesdevendas`.
5. Aponte para o arquivo: `docker/docker-compose.coolify.yml`.
6. Configure as variáveis de ambiente baseadas no `.env.example`.
7. O Coolify emitirá automaticamente os certificados SSL (HTTPS gratuito via Let's Encrypt).

---

## 🛡️ Guardrails e Regras de Segurança
1. **Nenhum centavo gasto sem autorização:** Toda campanha do Rui nasce pausada e precisa do seu clique em `admin.marcaopersonal.com`.
2. **Orçamento Travado:** R$ 500/mês distribuído em R$ 16,50/dia no canal de maior conversão.
3. **Privacidade Total:** Nenhuma credencial ou chave privada é salva no Git (.gitignore estrito).
