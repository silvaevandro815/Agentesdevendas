# CÉREBRO — 06. PROCESSOS & EXPEDIÇÃO SEM ESTOQUE (Otto)

Procedimento Operacional Padrão (SOP) para envio de pedidos sem estoque físico.

---

## 1. Fluxo do Pedido Aprovado (Passo a Passo)
```
[Cliente Compra (Site / Shopee / WhatsApp)]
                 │
                 ▼
       [Pagamento Confirmado]
                 │
                 ▼
       [Otto Recebe o Webhook]
                 │
                 ├──► Se Shopee/TikTok Shop: Etiqueta é gerada direto na plataforma do Marketplace
                 │
                 └──► Se Loja Própria/WhatsApp: 
                          1. Transmite pedido ao fornecedor dropshipping parceiro
                          2. Cota e gera frete via Melhor Envio (ou etiqueta do fornecedor)
                          3. Recebe código de rastreamento
                          4. Envia código de rastreio automático no WhatsApp da cliente
```

---

## 2. Prazos & Notificações ao Cliente
- Notificação imediata: "Pagamento recebido! Seu pedido está sendo embalado pelo nosso centro de distribuição."
- Notificação com Rastreio (dentro de 24h úteis): "Seu pedido está a caminho! Acompanhe aqui: [Link de rastreio]."
