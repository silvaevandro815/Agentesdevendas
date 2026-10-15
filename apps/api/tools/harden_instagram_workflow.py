import urllib.request, ssl, json

ctx = ssl._create_unverified_context()
n8n_url = "https://n8n.marcaopersonal.com/api/v1"
n8n_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZjM3ZTI2Yi1iZDRmLTQzNDItODRlMS1kNzA2MGU2YzdjOTciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZGVkMzExM2UtYzcxMy00N2EyLTk4MjctNDA0YzBlYTc4ODRhIiwiaWF0IjoxNzkxNzM3NjI3fQ.YZMR5_3sAS1sKFJtqDXtvm8TVOz3btU5AbtU_zetHz0"
headers = {"X-N8N-API-KEY": n8n_key, "Content-Type": "application/json"}

wf_id = "jlG1OPBCsaAx75zQ"
req = urllib.request.Request(f"{n8n_url}/workflows/{wf_id}", headers=headers)
with urllib.request.urlopen(req, context=ctx) as r:
    wf = json.loads(r.read().decode())

print("Fetched workflow:", wf.get("name"))

# 1. New Code for Enviar Resposta Direct IG
js_code_direct = """
const item = $('OpenRouter - Marcão Direct').item.json;

// Busca recipientId resiliente com múltiplas camadas de fallback
let recipientId = "";
try {
  recipientId = $('Processar Evento Instagram').first().json.senderId;
} catch (e) {}

if (!recipientId) {
  try {
    recipientId = $('Montar Prompt Direct Texto').first().json.senderId;
  } catch (e) {}
}

if (!recipientId) {
  try {
    recipientId = $('Montar Prompt Direct Áudio').first().json.senderId;
  } catch (e) {}
}

if (!recipientId) {
  try {
    recipientId = $('Buscar Perfil IG (Nome)').first().json.id;
  } catch (e) {}
}

recipientId = String(recipientId || "").trim();

if (!recipientId || recipientId === "undefined" || recipientId === "null") {
  return [{
    json: {
      ...item,
      error: "recipientId não encontrado nos nós anteriores. Envio cancelado para evitar erro 400 da Meta."
    }
  }];
}

const rawText = (item.choices && item.choices[0] && item.choices[0].message) 
  ? item.choices[0].message.content 
  : 'Fala, guerreiro! Marcão na área! Vamos pra cima!';

const igToken = "IGAAXMQcymNdhBZAGIzbTY4RnR5SXE4bklSVFVTdFRSY2g3SDR6Vzg0cmd4aWV2dk9WYUJ0dXJ6bVFORUxra3ZAvQ3lvYWhibGx6cnFRYmdaSkR0TW9YY0t4YnA2aWpmVEoxN1kyQ0FMVXMwaFNuRlBZAVWFB";

// 1. Isola URLs para manter links intactos
const urls = [];
const textoComPlaceholders = rawText.replace(/https?:\\/\\/\\S+/g, (match) => {
  urls.push(match);
  return `\\n__URL_${urls.length - 1}__\\n`;
});

// 2. Divide em blocos por quebra de linha (\\n+)
const blocos = textoComPlaceholders.split(/\\n+/).map(b => b.trim()).filter(b => b.length > 0);
const rawUnits = [];

for (const b of blocos) {
  if (b.startsWith('__URL_')) {
    const idx = parseInt(b.replace('__URL_', '').replace('__', ''), 10);
    if (!isNaN(idx) && urls[idx]) {
      rawUnits.push(urls[idx]);
    }
    continue;
  }

  const sents = b.split(/(?<=[.!?])\\s+/).filter(s => s.trim().length > 0);
  for (const s of sents) {
    const st = s.trim();
    if (!st) continue;

    // Se a frase for longa (> 60 caracteres), quebra em pausas humanas (, ou ; ou -)
    if (st.length > 60 && (st.includes(',') || st.includes(';') || st.includes(' - '))) {
      const partes = st.split(/(?<=[,;])\\s+|(?<=\\s-\\s)/).filter(p => p.trim().length > 0);
      for (const pt of partes) {
        if (pt.trim()) rawUnits.push(pt.trim());
      }
    } else {
      rawUnits.push(st);
    }
  }
}

// 3. Refina balões e anexa fragmentos muito curtos (ex: emojis soltos)
const finalBubbles = [];
for (const u of rawUnits) {
  if (finalBubbles.length === 0) {
    finalBubbles.push(u);
    continue;
  }
  if (u.length <= 3 && !u.startsWith('http')) {
    finalBubbles[finalBubbles.length - 1] += ' ' + u;
  } else {
    finalBubbles.push(u);
  }
}

// 4. Envio sequencial no Direct via Meta Graph API com delay humano de 1.5s
const sentResults = [];
for (let i = 0; i < finalBubbles.length; i++) {
  const bText = finalBubbles[i];
  if (!bText) continue;

  try {
    const res = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://graph.instagram.com/v21.0/me/messages',
      headers: {
        'Authorization': `Bearer ${igToken}`,
        'Content-Type': 'application/json'
      },
      body: {
        recipient: { id: recipientId },
        message: { text: bText }
      },
      json: true
    });
    sentResults.push(res);
  } catch (err) {
    const errDetails = err.response ? err.response.data : err.message;
    sentResults.push({ error: err.message, details: errDetails });
  }

  if (i < finalBubbles.length - 1) {
    await new Promise(r => setTimeout(r, 1500));
  }
}

return [{ json: { ...item, recipientId, finalBubbles, sentResults } }];
"""

# 2. New Code for Enviar Direct Privado IG (Comment to DM)
js_code_comment_dm = """
const item = $('Processar Decisão Comentário e DM').item.json;
const commentId = item.commentId || '';
const rawText = item.mensagem_direct || '';
const igToken = "IGAAXMQcymNdhBZAGIzbTY4RnR5SXE4bklSVFVTdFRSY2g3SDR6Vzg0cmd4aWV2dk9WYUJ0dXJ6bVFORUxra3ZAvQ3lvYWhibGx6cnFRYmdaSkR0TW9YY0t4YnA2aWpmVEoxN1kyQ0FMVXMwaFNuRlBZAVWFB";

if (!commentId || !rawText) {
  return [{ json: { ...item, skipped: true, reason: 'commentId or rawText empty' } }];
}

// A API da Meta de Private Replies para Comentários permite exatamente 1 envio privado usando comment_id
// Enviamos a resposta completa estruturada
const sentResults = [];
try {
  const res = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://graph.instagram.com/v21.0/me/messages',
    headers: {
      'Authorization': `Bearer ${igToken}`,
      'Content-Type': 'application/json'
    },
    body: {
      recipient: { comment_id: commentId },
      message: { text: rawText }
    },
    json: true
  });
  sentResults.push(res);
} catch (err) {
  const errDetails = err.response ? err.response.data : err.message;
  sentResults.push({ error: err.message, details: errDetails });
}

return [{ json: { ...item, commentId, sentResults } }];
"""

# Apply node updates
for n in wf["nodes"]:
    if n["name"] == "Enviar Resposta Direct IG":
        n["parameters"]["jsCode"] = js_code_direct
        print("Updated 'Enviar Resposta Direct IG'")
    elif n["name"] == "Enviar Direct Privado IG":
        n["parameters"]["jsCode"] = js_code_comment_dm
        print("Updated 'Enviar Direct Privado IG'")

# 3. Fix Connections: Processar Evento Instagram -> É Direct Message (DM)?
# And Webhook Instagram POST -> Consultar Produtos Atualizados (Supabase) in parallel
wf["connections"]["Processar Evento Instagram"] = {
    "main": [
        [
            {
                "node": "É Direct Message (DM)?",
                "type": "main",
                "index": 0
            }
        ]
    ]
}

# Webhook Instagram POST also triggers Consultar Produtos Atualizados in parallel
post_targets = wf["connections"]["Webhook Instagram POST"]["main"][0]
target_names = [t["node"] for t in post_targets]
if "Consultar Produtos Atualizados (Supabase)" not in target_names:
    post_targets.append({
        "node": "Consultar Produtos Atualizados (Supabase)",
        "type": "main",
        "index": 0
    })
print("Updated connections: Processar Evento Instagram connects directly to É Direct Message (DM)?")

# Disconnect Consultar Produtos Atualizados so it doesn't feed into É Direct Message
wf["connections"]["Consultar Produtos Atualizados (Supabase)"] = {
    "main": [[]]
}

payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

put_req = urllib.request.Request(f"{n8n_url}/workflows/{wf_id}", data=json.dumps(payload).encode(), headers=headers, method="PUT")
with urllib.request.urlopen(put_req, context=ctx) as r:
    print("I1 workflow updated successfully in n8n! HTTP", r.status)
