# BRIEF ANTI-GRAVITY — OPERAÇÃO MARCÃO 360° (v2)
## E-commerce de tecnologia fitness com agentes de IA — Fase Afiliado + Protocolo Marcão

> Continuidade do projeto existente (site marcaopersonal.com + Coolify com n8n, Evolution API, Postgres, Redis).
> Este documento define o modelo de negócio, o Supabase (memória dos agentes), os agentes, as integrações e o plano de replicação.

## 0. CONTEXTO E OBJETIVO
- Marca: **Marcão Personal** — "O Personal que não te deixa gastar dinheiro com bobagem".
- Público: homens e mulheres do universo fitness/estética (25–45 anos, Brasil).
- Produto-âncora em validação: **Balança de Bioimpedância Bluetooth com app** (commodity: igual em todo lugar).
- Diferencial que ninguém copia: **Protocolo Marcão** — depois da compra, o cliente entra em um programa
  de acompanhamento semanal gerado pelos agentes (dados da balança + objetivo + check-ins no WhatsApp).
- Estratégia em 2 fases:
  - **FASE 1 (agora, zero estoque): modelo de afiliado.** O cliente compra no marketplace pelo link do
    Marcão; o marketplace cobra, embala e entrega. Nossa margem = comissão. O Protocolo é entregue
    DIGITALMENTE: o cliente manda o comprovante para a Sofia no WhatsApp e é onboardado no programa.
  - **FASE 2 (após validação de ROAS/CPA): estoque próprio / dropshipping nacional.** Compramos lote do
    fornecedor nacional (ou via plataforma tipo Dropi), imprimimos etiqueta **QR "Protocolo Marcão"** dentro
    da caixa, despachamos com Melhor Envio. Margem sobe de ~10% (comissão) para 50–70% (produto próprio).
- Regra de ouro: a balança atrai (CPA baixo), o Protocolo retém e a **creatina/colágeno/kit IArmonize
  dão a margem recorrente** (upsell no pós-compra).

## 1. FLUXO DE VENDAS (o que os agentes executam)
FASE 1 (afiliado):
1. Téo/Lia geram criativos → card no Telegram → eu aprovo (F1).
2. Nina publica no IG/TikTok + Rui sobe anúncio PAUSADO → eu aprovo e ativo.
3. Cliente clica no **link de afiliado** (ML/Amazon/Magalu/Shopee) e compra lá.
4. Marketplace entrega (logística deles). Afiliado não toca em estoque/frete.
5. Cliente manda comprovante pro WhatsApp → Sofia valida (OCR ou leitura simples),
   cria `orders`, onboarda no **Protocolo Marcão** (coleta objetivo + dados da balança → plano semanal).
6. Check-ins seg/qui automáticos → no dia 20 do ciclo, upsell recorrente (creatina/colágeno).
7. Comissão cai no painel do afiliado → Iago consolida no relatório das 21h.

FASE 2 (estoque próprio): checkout Braip no site → Otto compra do fornecedor/Dropi → etiqueta Melhor
Envio → rastreio automático no WhatsApp → QR da caixa abre `protocolo.marcaopersonal.com` → onboarding.

## 2. INFRA EXISTENTE (NÃO RE-CRIAR)
- VPS Hostinger KVM 4 + Coolify: n8n (queue mode), Evolution API, Postgres, Redis rodando.
- GitHub conectado no Antigravity via MCP. Monorepo `loja-ia/` com `/brain` (método PARA).
- Papel do usuário: DIRETOR. Aprova criativos, campanhas e gastos pelo Telegram.

## 3. SUPABASE NA COOLIFY (MEMÓRIA DOS AGENTES) — SUA PRIMEIRA TAREFA
1. Deploy do template **Supabase** na Coolify (mesma VPS): Postgres+pgvector, Auth, Storage, Realtime.
   Limitar recursos (~1,5 GB RAM). Domínio: `supabase.<meudominio>` + SSL.
2. Guardar em `.env` (nunca no repo): `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`.
3. Aplicar o schema abaixo como migração SQL versionada em `db/migrations/001_init.sql`.

### 3.1 SCHEMA (SQL)
```sql
create extension if not exists vector;

create table contacts (
  id uuid primary key default gen_random_uuid(),
  channel text check (channel in ('whatsapp','instagram','tiktok','site')),
  external_id text not null,            -- telefone (E.164) ou PSID/IG ID
  name text,
  first_seen timestamptz default now(),
  last_seen timestamptz default now(),
  unique(channel, external_id)
);

create table conversations (
  id uuid primary key default gen_random_uuid(),
  contact_id uuid references contacts(id) on delete cascade,
  channel text,
  status text default 'open',           -- open | handoff | closed
  opened_at timestamptz default now()
);

create table messages (
  id bigserial primary key,
  conversation_id uuid references conversations(id) on delete cascade,
  role text check (role in ('customer','agent','human')),
  content text,
  meta jsonb,                           -- ids de plataforma, mídia, etc.
  created_at timestamptz default now()
);
create index on messages (conversation_id, created_at desc);

create table customer_state (
  contact_id uuid primary key references contacts(id) on delete cascade,
  funnel_stage text default 'lead',     -- lead|qualificado|comprou|protocolo_ativo|recorrente
  cart_url text,
  last_intent text,
  updated_at timestamptz default now()
);

create table leads (
  contact_id uuid primary key references contacts(id) on delete cascade,
  source text,                          -- comentario_ig | anuncio | site | dm_tiktok
  temperature int default 0,            -- 0-100
  updated_at timestamptz default now()
);

create table products (
  id uuid primary key default gen_random_uuid(),
  sku text unique,
  name text not null,
  model text check (model in ('proprio','afiliado_ml','afiliado_amazon','afiliado_magalu','afiliado_shopee','dropi')),
  affiliate_url text,
  commission_pct numeric,
  price numeric
);

create table orders (
  id uuid primary key default gen_random_uuid(),
  contact_id uuid references contacts(id),
  product_id uuid references products(id),
  marketplace text,
  total numeric,
  status text default 'pago',           -- pago|protocolo_ativo|entregue|recorrente|reembolsado
  proof_url text,                       -- comprovante do afiliado (fase 1)
  created_at timestamptz default now()
);

create table protocols (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders(id),
  contact_id uuid references contacts(id),
  goal text,                            -- definicao|emagrecimento|performance|saude
  metrics jsonb,                        -- dados da balança/medidas iniciais
  week_plan jsonb,                      -- plano semanal gerado pela IA
  started_at timestamptz default now()
);

create table protocol_checkins (
  id bigserial primary key,
  protocol_id uuid references protocols(id) on delete cascade,
  due_date date not null,
  done boolean default false,
  notes text
);

create table content_calendar (
  id uuid primary key default gen_random_uuid(),
  content_id text unique,
  platform text,                        -- instagram | tiktok
  caption text,
  media_url text,
  scheduled_at timestamptz,
  published_at timestamptz,
  status text default 'agendado'        -- agendado|publicado|falhou
);

create table approvals (
  id uuid primary key default gen_random_uuid(),
  type text,                            -- criativo | campanha | gasto | post
  payload jsonb,
  status text default 'pendente',       -- pendente|aprovado|rejeitado|editado
  decided_by text,
  decided_at timestamptz,
  created_at timestamptz default now()
);

create table campaign_state (
  campaign_id text primary key,
  platform text,
  status text,
  spend numeric,
  roas numeric,
  cpa numeric,
  snapshot_date date default current_date
);

create table daily_reports (
  day date primary key,
  payload jsonb
);

create table exceptions (
  id bigserial primary key,
  level text,                           -- info|warn|critical
  message text,
  context jsonb,
  created_at timestamptz default now()
);

-- RAG do cérebro (chunks do /brain versionados no GitHub)
create table brain_chunks (
  id bigserial primary key,
  source text,                          -- caminho do arquivo no /brain
  chunk text,
  embedding vector(1536),
  created_at timestamptz default now()
);

create or replace function match_brain_chunks(query_embedding vector(1536), k int default 5)
returns table (id bigint, source text, chunk text, similarity float)
language sql stable as $$
  select id, source, chunk, 1 - (embedding <=> query_embedding) as similarity
  from brain_chunks
  order by embedding <=> query_embedding
  limit k;
$$;
```

### 3.2 QUERIES PRONTAS (usar nos nós n8n/Supabase)
- Novo contato: `insert into contacts ... on conflict (channel, external_id) do update set last_seen=now() returning id;`
- Subir temperatura do lead: `update leads set temperature = least(100, temperature+20) where contact_id=$1;`
- Memória do agente (últimas 20 msgs): `select role, content from messages where conversation_id=$1 order by created_at desc limit 20;`
- Cliente aguardando follow-up: `select contact_id from customer_state where funnel_stage='comprou' and updated_at < now() - interval '24 hours';`
- Upsell dia 20: `select contact_id from protocols where started_at < now() - interval '20 days';`
- Relatório do dia: agregações de `orders`, `campaign_state`, `approvals` → gravar em `daily_reports`.

## 4. OS AGENTES (postar, responder, vender, follow-up, tráfego)
| Agente | Canal/Ferramenta | Memória |
|---|---|---|
| **Sofia** (atendimento/vendas) | WhatsApp via Evolution API (modo oficial) | 3 camadas: Redis (últimas msgs, TTL 24h) → `messages`/`customer_state` no Supabase → RAG `match_brain_chunks` (catálogo, objeções, claims) |
| **Marcão DM** (comentários/DM IG e TikTok) | Meta Graph API (comments/DM), TikTok | Redis por thread (TTL 7d) + `leads.temperature` + RAG voz do Marcão |
| **Téo/Lia** (criativos/copy) | LLM (Gemini/GPT) | Stateless; brief + RAG `/brain` (ofertas, provas, claims permitidos) → sempre para `approvals` |
| **Nina** (publicações) | IG Graph API + TikTok Content Posting API | `content_calendar` (idempotente por `content_id`) |
| **Rui** (tráfego) | Meta Marketing API (campanha PAUSADA) | `campaign_state` + regras em `/brain/05-marketing/regras-trafego.md`; NUNCA ativa sem F1 |
| **Otto** (pedidos/logística) | Webhooks Braip/MP + Melhor Envio + Dropi (fase 2) | `orders` como máquina de estados |
| **Iago** (dados) | SQL Supabase | Stateless → `daily_reports` + resumo Telegram 21h |
| **João** (orquestrador) | n8n + Telegram | `exceptions` → escalar ao DIRETOR |

## 5. N8N OU PYTHON? (DECISÃO)
**Híbrido: n8n orquestra, Python calcula.**
- **n8n**: webhooks (WhatsApp/IG/TikTok/Braip), agendamentos, nós prontos (Supabase, Telegram, HTTP),
  aprovações F1 — 80% dos fluxos, manutenção visual.
- **Python (FastAPI) em `apps/api` no mesmo Coolify**: parsing de comprovante, geração do plano semanal
  do Protocolo (regras + LLM), embeddings/RAG, score de leads. n8n chama via nó HTTP.
- Motivo: lógica complexa em JSON de workflow vira legado ilegível; Python versionado no GitHub é testável
  e reutilizável na REPLICAÇÃO (vendemos os dois: fluxos + API).

## 6. LIMITES DE PLATAFORMA (OBRIGATÓRIO RESPEITAR)
- **WhatsApp Cloud/Evolution oficial**: janela de atendimento de 24h (dentro dela, respostas livres e
  gratuitas); fora da janela, só **templates pré-aprovados** (follow-ups/upsell = templates de marketing,
  pagos por conversa). Sem disparo em massa frio (número é bloqueado).
- **Meta**: automação de comentários/DM permitida dentro das políticas (sem engagement bait, com rate
  limit); Marketing API exige app review + verificação de empresa (7–10 dias) — enquanto isso, Rui opera
  "semi-auto": monta campanha pausada, DIRETOR publica na interface.
- **Gasto de anúncio: 100% com aprovação humana (F1)**, teto diário hardcoded.
- **ANVISA**: claims cosméticos/comportamentais apenas; PROIBIDO prometer cura/emagrecimento ("seca e
  drena" vetado). Whitelist em `/brain/08-juridico/claims.md`. **Caneta Azempika fora de toda automação.**
- **LGPD**: consentimento no onboarding do Protocolo; dados só no Supabase próprio.

## 7. INTEGRAÇÕES
GEMINI_API_KEY ou OPENAI_API_KEY · TELEGRAM_BOT_TOKEN/CHAT_ID · WHATSAPP (Evolution API) ·
META_APP_ID/SECRET + META_AD_ACCOUNT_ID + INSTAGRAM_BUSINESS_ID · TIKTOK_CONTENT_POSTING ·
SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY · MELHOR_ENVIO_TOKEN (fase 2) · DROPI (fase 2) ·
MERCADO_PAGO/BRAIP webhooks · Links de afiliado ML/Amazon/Magalu/Shopee em `products.affiliate_url`.

## 8. FASES DE EXECUÇÃO (1 PR por fase)
- **P0**: Supabase na Coolify + migrations 3.1 + seed dos produtos (balança nos 4 marketplaces + creatina +
  colágeno + IArmonize) + F1 (Telegram approvals) + F3 (Sofia WhatsApp com as 3 memórias).
- **P1**: F4 comentários/DM IG + F2 publicações + 30 roteiros aprovados.
- **P2**: F7 tráfego semi-auto (Meta) + orçamento R$ 30–50/dia aprovado.
- **P3**: F5/Protocolo digital (comprovante → onboarding → check-ins seg/qui) + upsell dia 20.
- **P4**: TikTok Shop (balança; suplemento só com categoria liberada) + fase 2 (Dropi/Melhor Envio/QR).
- **P5**: Metabase + F8 relatório + F9 alertas.

## 9. PLANO DE REPLICAÇÃO (vender a infra depois — só depois da minha rodar)
1. **Empacotar**: docker-compose (Coolify templates) + migrations SQL + JSONs n8n + `apps/api` parametrizados
   por `.env` e por `/brain` do cliente (a marca muda, a máquina não).
2. **Onboarding em 5 dias**: dia 1 deploy Coolify; dia 2 marca/produtos no /brain; dia 3 credenciais;
   dia 4 testes; dia 5 go-live.
3. **Precificação de mercado (dados 2026)**: setup R$ 5–30k (mercado cobra US$ 2,5–15k) + retainer
   R$ 2,5–25k/mês (mercado: US$ 500–5k+/mês). Começar em R$ 5k + R$ 1,5k/mês para academias/personais.
4. **Produtos digitais paralelos**: template "Agente de Vendas WhatsApp p/ fitness BR" (JSON+SQL) em
   marketplace (mercado de templates n8n paga recorrente).

## 10. COMECE AGORA
1) Gere: docker-compose/Supabase, `db/migrations/001_init.sql`, seed de produtos, JSON dos fluxos F1/F3,
   esqueleto `apps/api` (FastAPI: /ocr-comprovante, /gerar-protocolo, /score-lead).
2) Faça push no GitHub e me dê o checklist de deploy na Coolify.
3) Me pergunte o que faltar (credenciais pendentes, links de afiliado reais para o seed).
