#!/bin/bash
set -e

echo "=========================================================="
echo "🛡️  INICIANDO BLINDAGEM DA VPS (HOSTINGER KVM)"
echo "=========================================================="

echo ""
echo ">>> [1/5] Verificando processos de alto consumo de CPU..."
ps aux --sort=-%cpu | head -n 12

echo ""
echo ">>> [2/5] Verificando contêineres Docker em execução..."
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Status}}"

echo ""
echo ">>> [3/5] Verificando agendamentos automáticos (Crontab)..."
crontab -l 2>/dev/null || echo "Nenhum crontab ativo para o usuário root."

echo ""
echo ">>> [4/5] Instalando e configurando Fail2Ban contra ataques de força bruta..."
apt-get update -qq
apt-get install -y fail2ban ufw

cat << 'EOF' > /etc/fail2ban/jail.local
[DEFAULT]
bantime  = 86400
findtime = 600
maxretry = 4

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo "✅ Fail2Ban ativo: 4 tentativas erradas de SSH = IP banido por 24 horas!"

echo ""
echo ">>> [5/5] Configurando Firewall UFW (Universal Firewall)..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

ufw allow 22/tcp comment "SSH Acesso Seguro"
ufw allow 80/tcp comment "HTTP Traefik / Let's Encrypt"
ufw allow 443/tcp comment "HTTPS Traefik SSL"
ufw allow 8000/tcp comment "Coolify UI Inicial"

echo "y" | ufw enable
ufw status verbose

echo ""
echo "=========================================================="
echo "🛡️  VPS 100% BLINDADA COM SUCESSO!"
echo "=========================================================="