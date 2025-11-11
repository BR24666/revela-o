# 🚀 Guia de Deploy - Super Analista

## Deploy do Frontend no Vercel

### 1. Conectar Repositório

1. Acesse [vercel.com](https://vercel.com)
2. Clique em "New Project"
3. Importe o repositório: `https://github.com/BR24666/revela-o.git`

### 2. Configurar Variáveis de Ambiente

No dashboard do Vercel, vá em **Settings > Environment Variables** e adicione:

```
NEXT_PUBLIC_SUPABASE_URL=https://utmouqkyveodxrkqyies.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0bW91cWt5dmVvZHhya3F5aWVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2MzM5NzYsImV4cCI6MjA2MDIwOTk3Nn0.XttMuImhCt3UcF5MfuGkAVBm0vGgeZswXyMw_h5X20w
```

### 3. Deploy

Clique em **Deploy**. O Vercel irá:
- Instalar dependências (`npm install`)
- Buildar o projeto (`npm run build`)
- Deploy automático

🎉 Seu frontend estará disponível em: `https://seu-projeto.vercel.app`

---

## Deploy do Backend Python

O backend Python precisa rodar 24/7 num servidor. Aqui estão as opções:

### Opção 1: DigitalOcean Droplet (Recomendado)

**Custo:** $6/mês (Droplet básico)

#### 1.1. Criar Droplet

1. Acesse [DigitalOcean](https://digitalocean.com)
2. Create > Droplets
3. Escolha:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($6/mês)
   - **Region:** São Paulo (mais próximo do Brasil)

#### 1.2. Conectar via SSH

```bash
ssh root@seu-ip-do-droplet
```

#### 1.3. Setup no Servidor

```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Python 3.10+
apt install python3 python3-pip python3-venv git -y

# Clonar repositório
git clone https://github.com/BR24666/revela-o.git
cd revela-o

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
cat > .env << EOF
NEXT_PUBLIC_SUPABASE_URL=https://utmouqkyveodxrkqyies.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0bW91cWt5dmVvZHhya3F5aWVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDYzMzk3NiwiZXhwIjoyMDYwMjA5OTc2fQ.KXoC9VovMN5lj9ssoy7JfsuDz1xAWNuCQQurnC6AeYs
EOF
```

#### 1.4. Treinar Modelo

```bash
cd python_backend
python ml_model.py
```

Aguarde o treinamento (10-60 min).

#### 1.5. Executar Engine em Background

```bash
# Instalar screen para manter processo rodando
apt install screen -y

# Criar sessão
screen -S super-analista

# Executar engine
python realtime_engine.py

# Detach da sessão: Ctrl+A seguido de D
```

Para reconectar:
```bash
screen -r super-analista
```

#### 1.6. (Opcional) Configurar Systemd Service

Para iniciar automaticamente ao reiniciar servidor:

```bash
cat > /etc/systemd/system/super-analista.service << EOF
[Unit]
Description=Super Analista Realtime Engine
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/revela-o/python_backend
Environment=PATH=/root/revela-o/venv/bin
ExecStart=/root/revela-o/venv/bin/python realtime_engine.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Ativar serviço
systemctl enable super-analista
systemctl start super-analista

# Ver logs
journalctl -u super-analista -f
```

---

### Opção 2: AWS EC2

Similar ao DigitalOcean, mas:
1. Crie uma instância t3.micro (Free Tier)
2. Escolha Ubuntu 22.04
3. Configure Security Group (permitir SSH)
4. Siga os mesmos passos do DigitalOcean

---

### Opção 3: Railway.app

**Custo:** $5/mês

1. Acesse [railway.app](https://railway.app)
2. New Project > Deploy from GitHub repo
3. Selecione o repositório
4. Adicione variáveis de ambiente
5. Configure Start Command: `python python_backend/realtime_engine.py`

---

## Monitoramento

### Verificar se Backend está Rodando

```bash
# Via SSH
ps aux | grep realtime_engine.py

# Via logs do systemd
journalctl -u super-analista -f
```

### Verificar Sinais no Supabase

1. Acesse o [Supabase Dashboard](https://supabase.com)
2. Vá para **Table Editor** > `signals`
3. Verifique se novos sinais estão sendo inseridos

### Verificar Frontend

Acesse `https://seu-projeto.vercel.app` e:
- A tela de sinais deve mostrar sinais recentes
- A dashboard de performance deve mostrar estatísticas

---

## Manutenção

### Atualizar Código

```bash
# No servidor
cd /root/revela-o
git pull

# Reiniciar serviço
systemctl restart super-analista
```

### Retreinar Modelo

```bash
cd /root/revela-o/python_backend
source ../venv/bin/activate
python ml_model.py

# Reiniciar engine
systemctl restart super-analista
```

---

## Troubleshooting

### Backend não está gerando sinais

1. Verifique logs: `journalctl -u super-analista -f`
2. Verifique se o modelo existe: `ls ml_models/`
3. Teste conexão com Binance: `python -c "from binance.client import Client; print(Client().get_server_time())"`

### Frontend não mostra sinais

1. Verifique console do navegador (F12)
2. Confirme que as variáveis de ambiente estão corretas
3. Teste conexão com Supabase no navegador

### Modelo com baixo winrate

1. Retreine com mais dados históricos (3-5 anos)
2. Ajuste threshold de confiança mínima
3. Aguarde mais sinais para estatísticas estabilizarem (100+ sinais)

---

## Custos Estimados

| Serviço | Custo Mensal |
|---------|--------------|
| Vercel (Frontend) | $0 (Free) |
| Supabase | $0 (Free até 500MB) |
| DigitalOcean VPS | $6 |
| **Total** | **$6/mês** |

---

## Checklist de Deploy

- [ ] Frontend deployado no Vercel
- [ ] Variáveis de ambiente configuradas
- [ ] Schema SQL executado no Supabase
- [ ] VPS criado e configurado
- [ ] Backend clonado no VPS
- [ ] Modelo treinado
- [ ] Engine rodando em background/systemd
- [ ] Teste: novos sinais aparecem no frontend
- [ ] Dashboard de performance funcionando

---

🎉 **Deploy completo! Seu Super Analista está no ar!**

