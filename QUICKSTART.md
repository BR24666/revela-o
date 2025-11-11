# ⚡ Guia Rápido - Super Analista

## 🎯 Setup em 5 Minutos

### 1️⃣ Setup do Banco de Dados (Supabase)

```bash
# 1. Acesse: https://supabase.com
# 2. Vá para o projeto "Trading OB"
# 3. Abra SQL Editor
# 4. Execute o arquivo: lib/supabase/schema.sql
```

✅ Banco de dados configurado!

---

### 2️⃣ Instalar Dependências

**Frontend (Next.js):**
```bash
npm install
```

**Backend (Python):**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar
pip install -r requirements.txt
```

✅ Dependências instaladas!

---

### 3️⃣ Treinar o Modelo (PRIMEIRA VEZ)

```bash
cd python_backend
python ml_model.py
```

⏱️ Aguarde 10-30 minutos (depende da quantidade de dados)

Para teste rápido (30 dias), edite `ml_model.py`:
```python
USE_FULL_DATASET = False
```

✅ Modelo treinado!

---

### 4️⃣ Executar o Sistema

**Terminal 1 - Backend (Engine):**
```bash
cd python_backend
python realtime_engine.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

---

### 5️⃣ Acessar o Sistema

Abra o navegador em: **http://localhost:3000**

✅ Sistema rodando!

---

## 📊 O que você verá:

### Tela de Sinais
- Sinal atual (CALL/PUT)
- Score de confiança
- Preço de entrada
- Histórico dos últimos sinais

### Dashboard de Performance
- Winrate total
- Estatísticas por faixa de confiança
- Total de acertos/erros

### Configurações
- Ajustar confiança mínima (70-95%)
- Ativar notificações

---

## 🚀 Próximos Passos

### Deploy em Produção

1. **Frontend:** Deploy no Vercel (automático ao fazer push)
2. **Backend:** Deploy em VPS (DigitalOcean, AWS)

Ver guia completo: `DEPLOY.md`

---

## 🔧 Comandos Úteis

### Verificar Status do Backend
```bash
# Ver logs em tempo real
tail -f python_backend/logs.txt  # (se configurado)

# Testar conexão Binance
python -c "from binance.client import Client; print(Client().get_server_time())"
```

### Retreinar Modelo
```bash
cd python_backend
python ml_model.py
```

### Ver Sinais no Banco
```sql
-- No SQL Editor do Supabase
SELECT * FROM signals 
ORDER BY timestamp DESC 
LIMIT 10;
```

### Calcular Winrate Manual
```sql
-- No SQL Editor do Supabase
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
  ROUND(AVG(CASE WHEN result = 'WIN' THEN 100 ELSE 0 END), 2) as winrate
FROM signals
WHERE result IN ('WIN', 'LOSS');
```

---

## 🐛 Troubleshooting

### ❌ "Modelo não encontrado"
```bash
cd python_backend
python ml_model.py  # Treinar modelo
```

### ❌ "Erro de conexão com Supabase"
Verifique:
1. Credenciais em `.env.local` (frontend) ou `.env` (backend)
2. Se o schema SQL foi executado
3. Se o projeto Supabase está ativo

### ❌ "Não recebe dados da Binance"
```bash
# Testar conexão
python -c "from binance.client import Client; print(Client().get_server_time())"
```

### ❌ Frontend não mostra sinais
1. Verifique console do navegador (F12)
2. Confirme que o backend está rodando
3. Verifique se há sinais no banco: `SELECT * FROM signals`

---

## 📈 Dicas para Melhorar o Winrate

1. **Use confiança mínima de 80%+**
   - Menos sinais, mas mais precisos

2. **Retreine semanalmente**
   - Modelo se adapta às mudanças do mercado

3. **Opere nos melhores horários**
   - Ver tabela no README.md

4. **Aguarde dados suficientes**
   - 100+ sinais para estatísticas confiáveis

5. **Combine com análise manual**
   - Sistema é assistente, não substitui análise

---

## 📞 Precisa de Ajuda?

- 📖 README completo: `README.md`
- 🚀 Guia de deploy: `DEPLOY.md`
- 🐛 Issues: GitHub Issues

---

**Bons trades! 🚀📈**

