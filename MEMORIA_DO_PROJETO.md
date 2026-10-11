# MEMÓRIA DO PROJETO — Centro de Comando de IA (E-commerce automatizado)

> Arquivo vivo. Ler SEMPRE no início de cada sessão e atualizar a cada decisão.

## Contexto
- Diretor/Empreendedor: Evandro da Silva Gallina (CNPJ MEI: 68.746.249/0001-84).
- Domínio principal registrado: `marcaopersonal.com`
- Subdomínio Administrativo (Painel de Controle e Aprovações): `admin.marcaopersonal.com`
- Subdomínio Loja / Landing Page: `loja.marcaopersonal.com` ou raiz `marcaopersonal.com`
- Subdomínio n8n / Automações: `n8n.marcaopersonal.com`
- Nicho Escolhido: **Emagrecimento, Musculação e Estética Corporal (Corpo & Beleza)**
  - Foco: Produtos que unem perda de peso, definição e beleza estética (ex: Creatina, Termogênicos/Drenantes naturais, Colágeno/Firmadores).
  - Vantagem: Altíssimo apelo visual no Instagram/TikTok, compra recorrente (recompra mensal) e ticket médio atrativo (kits de R$ 97 a R$ 197).
- Modelo: Revenda sem estoque (Dropshipping Nacional / Afiliado Oficial com envio direto pelo fabricante).
- Infraestrutura confirmada:
  - PC Local com Antigravity + Git
  - Repositório GitHub: https://github.com/silvaevandro815/Agentesdevendas
  - VPS Hostinger KVM 4 com Coolify e Docker
  - Domínio registrado: marcaopersonal.com (com DNS apontando para a VPS)
- Painel de Aprovação do Diretor: Opção C (Painel Web em `admin.marcaopersonal.com`, reproduzindo fielmente a interface "Sua Empresa 24h" do vídeo com cards de agentes, aprovações de anúncios e chat com o Cérebro).
- Canais de Venda: Site próprio (Landing Page no domínio), TikTok Shop, Shopee, Mercado Livre, Instagram e WhatsApp.
- Orçamento de Tráfego Pago: R$ 500 / mês (aprox. R$ 16,50 / dia).

## Confirmação do Vídeo de Referência (Assistido e Transcrito)
- Sistema: "Sua Empresa 24h" (Central de comando de IA conectada a um Cérebro Central com objetivos do mês, ofertas, números e políticas).
- Agentes e Departamentos identificados exatamente na interface do vídeo:
  - Marketing & Conteúdo: Bela (SEO/Artigos), Lia (Copywriter), Téo (Criativos), Rui (Tráfego), Nina (Social Media).
  - Vendas & Atendimento: Sofia (Atendimento 24h via WhatsApp), Davi (Follow-up de vendas e recuperação).
  - Financeiro & Dados: Iago (Analista de Dados / Relatório Executivo), Marta (Analista Financeira / Fluxo de Caixa).
  - Operações, Gente & Jurídico: Alan (Jurídico / Contratos / Compliance), Otto (Processos / SOPs / Despacho), Paulo (RH / Onboarding e contratação de novos agentes).
  - Ações padrão dos agentes: `Buscar no Cérebro` e `Emitir artefato`.


## Análise Regulatória & Fiscal (Alerta Estratégico)
- O MEI atual tem CNAE `7319-0/02` (Promoção de vendas).
- Se trabalhar como **Afiliado Oficial** (Shopee Afiliados, TikTok Shop Afiliado, Mercado Livre Afiliado): o CNAE `7319-0/02` é 100% aderente, sem risco de estoque, nota emitida pela plataforma/fornecedor.
- Se for **Dropshipping / Revenda com checkout próprio** (o cliente paga a você e você repassa ao fornecedor): recomenda-se adicionar no MEI a atividade de *Comércio varejista de cosméticos* (CNAE 4772-5/00) pelo Portal do Empreendedor (gratuito e instantâneo).
- Conformidade ANVISA: o fornecedor/fabricante é o responsável técnico pelo registro na ANVISA. Nossos agentes de copy e marketing serão blindados contra "alegações terapêuticas ou cura de calvície", mantendo conformidade com RDC/ANVISA para cosméticos.

## Agentes planejados
- Marketing: Bela (SEO/Artigos), Lia (Copywriter persuasiva), Téo (Criativos para Reels/TikTok), Rui (Gestor de Tráfego - monta campanhas pausadas), Nina (Social Media & Calendário).
- Vendas: Sofia (Atendimento WhatsApp & Dúvidas sobre o produto com RAG), Davi (Recuperação de carrinho e follow-up).
- Dados/Finanças: Iago (Relatório diário de vendas e ROAS), Marta (Controle de custos e margem líquida).
- Operações: Otto (Integração de pedidos e rastreio), Alan (Jurídico, LGPD e compliance de claims ANVISA), João (Chefe de Gabinete / Orquestrador via Telegram).

## Guardrails
- Nenhuma campanha ou gasto é ativado sem aprovação explícita de Evandro (via bot Telegram ou painel).
- Teto diário de anúncio: travado no orçamento estabelecido (R$ 16,50/dia inicialmente).
- Nenhuma chave de API ou credencial real no repositório público (.gitignore + .env.example).
- Cópias sem promessas proibidas por ANVISA/CONAR.

## Status das Fases
- [x] Pré-alinhamento & Definição da Infraestrutura
- [ ] P0 — Fundação Técnica (Estrutura Monorepo, Docker Compose, Git connect, Setup Coolify)
- [ ] P1 — O Cérebro (/brain) estruturado e persona dos agentes
- [ ] P2 — Máquina de Criativos e Conteúdo (Téo, Lia, Nina)
- [ ] P3 — Motor de Vendas & Atendimento (Sofia no WhatsApp + integração canais)
- [ ] P4 — Campanhas de Tráfego Pago (Rui + aprovação Telegram)
- [ ] P5 — Operação e Logística sem estoque (Otto + Rastreio)
- [ ] P6 — Painel Gerencial & Métricas (Iago + Marta)

