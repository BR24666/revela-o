# 🔧 Troubleshooting - Super Analista

## 🎯 Sistema Aparece Mas Está "Estático"

### Diagnóstico Rápido

Se você vê as 3 abas mas nenhum dado aparece, é porque:

✅ **Frontend está funcionando** (Next.js OK)  
✅ **Supabase conectado** (sem erros de conexão)  
❌ **Não há dados no banco** (tabela `signals` vazia)  
❌ **Backend Python não está rodando** (não está gerando sinais)

---

## 🚀 Solução Rápida (2 opções)

### Opção A: Inserir Dados de Teste (Mais Rápido)

Para testar o frontend imediatamente SEM rodar o backend completo:

```bash
cd python_backend

# Ativar ambiente virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Inserir 15 sinais de teste
python test_insert_signals.py
```

**Resultado:**
- ✅ 15 sinais dummy inseridos
- ✅ Frontend mostra sinais imediatamente
- ✅ Dashboard mostra estatísticas
- ✅ Você pode testar a interface

**Para remover dados de teste depois:**
```bash
python test_insert_signals.py clear
```

---

### Opção B: Rodar Backend Completo (Produção)

Para gerar sinais REAIS do Bitcoin:

**Passo 1: Treinar Modelo (se ainda não fez)**
```bash
cd python_backend
venv\Scripts\activate
python ml_model.py
```
⏱️ Aguarde 10-30 minutos

**Passo 2: Executar Engine em Tempo Real**
```bash
python realtime_engine.py
```

**O que vai acontecer:**
- 🔌 Conecta ao WebSocket da Binance
- 📊 Recebe velas M1 de BTC/USDT
- 🤖 Faz previsões com IA
- 💾 Salva sinais no Supabase (se confiança >= 70%)
- ⏱️ Primeiro sinal em 2-10 minutos

---

## 🐛 Erros Comuns e Soluções

### ❌ Erro: evmAsk.js (Cannot redefine property: ethereum)

**O que é:**
- Extensão de wallet no navegador (MetaMask/Phantom)
- Tentando injetar código na página

**Solução:**
- ✅ **Pode ignorar completamente**
- Este erro NÃO afeta o sistema
- Se incomoda, desative a extensão para este site

---

### ❌ Erro: Failed to load favicon.ico (404)

**O que é:**
- Navegador procura ícone do site

**Solução:**
- ✅ **Já corrigido!** (arquivo criado)
- Fazer commit e push:
```bash
git add app/favicon.ico python_backend/test_insert_signals.py
git commit -m "Add: favicon e script de teste"
git push
```

---

### ❌ Tela de Sinais: "Aguardando próximo sinal..."

**Causa 1: Não há dados no banco**

**Solução:**
```bash
# Opção A: Dados de teste
python test_insert_signals.py

# Opção B: Backend real
python realtime_engine.py
```

**Causa 2: Confiança mínima muito alta**

**Solução:**
1. Vá na aba "Configurações"
2. Reduza threshold para 70%
3. Salvar

---

### ❌ Dashboard: "Sem dados suficientes ainda"

**Causa:**
- Menos de 10 sinais no banco
- Ou todos os sinais estão PENDING

**Solução:**
```bash
# Inserir dados de teste
python test_insert_signals.py
```

---

### ❌ Backend Python: "Modelo não encontrado"

**Erro:**
```
⚠ Erro ao carregar modelo: [Errno 2] No such file or directory: 'ml_models/trained_model.pkl'
```

**Solução:**
```bash
cd python_backend
python ml_model.py  # Treinar modelo primeiro
```

---

### ❌ Backend Python: Erro de conexão Supabase

**Erro:**
```
Error connecting to Supabase
```

**Solução:**
1. Verificar se as credenciais estão corretas em `config.py`
2. Verificar se tabelas existem no Supabase
3. Verificar conexão com internet

---

## 📊 Como Verificar Se Está Funcionando

### 1. Verificar Banco de Dados

Acesse: https://supabase.com/dashboard/project/utmouqkyveodxrkqyies

Vá em **Table Editor** > **signals**

**Se tiver dados:**
- ✅ Sistema está gerando/salvando sinais
- Volte ao frontend e recarregue (F5)

**Se estiver vazio:**
- ❌ Backend não está rodando OU
- ❌ Não gerou nenhum sinal ainda (confiança < threshold)

---

### 2. Verificar Backend (se rodando)

No terminal onde executou `realtime_engine.py`, você deve ver:

```
✓ Modelo carregado com sucesso
✓ Buffer inicializado com 100 velas
Conectando ao WebSocket...
✓ Conectado! Aguardando velas...

========================================
NOVA VELA FECHADA - 2025-01-11 10:37:00
========================================
O: 43250.50 | H: 43260.00 | L: 43240.00 | C: 43255.00

--- PREVISÃO ---
Direção: CALL (🟩)
Confiança: 78.45%

✓ SINAL GERADO! (Confiança acima de 70%)
✓ Sinal salvo no banco de dados (ID: xxx-xxx-xxx)
```

**Se não vê logs:**
- ❌ Backend não está rodando
- Execute: `python realtime_engine.py`

---

### 3. Verificar Frontend

No navegador (F12 > Console), você deve ver:

```javascript
Novo sinal recebido: {prediction: 'CALL', confidence_score: 78.45, ...}
```

**Se vê isso:**
- ✅ Supabase Realtime funcionando
- ✅ Frontend recebendo atualizações

**Se não vê:**
- Recarregue a página (F5)
- Verifique se há sinais no banco

---

## 🎯 Checklist Completo

Para o sistema estar 100% funcional:

- [ ] Frontend rodando (`npm run dev`)
- [ ] Supabase configurado (tabelas criadas)
- [ ] Backend Python:
  - [ ] Ambiente virtual ativo
  - [ ] Dependências instaladas (`pip install -r requirements.txt`)
  - [ ] Modelo treinado (`ml_models/trained_model.pkl` existe)
  - [ ] Engine rodando (`python realtime_engine.py`)
- [ ] Sinais aparecendo no frontend

---

## 🔄 Fluxo Completo de Debug

```bash
# 1. Verificar se tabelas existem
# Acesse Supabase > Table Editor
# Deve ter: signals, performance_stats, user_settings, market_data

# 2. Inserir dados de teste
cd python_backend
venv\Scripts\activate
python test_insert_signals.py

# 3. Verificar frontend
# Abra http://localhost:3000
# Deve mostrar os 15 sinais de teste

# 4. Se funcionou, remover dados de teste
python test_insert_signals.py clear

# 5. Treinar modelo (se necessário)
python ml_model.py

# 6. Rodar backend real
python realtime_engine.py

# 7. Aguardar primeiro sinal real (2-10 min)
```

---

## 📞 Ainda com Problemas?

1. **Leia README.md completo**
2. **Veja FIRST_RUN.md** (passo a passo)
3. **Abra issue no GitHub**
4. **Verifique logs do backend**

---

## ✅ Resumo das Soluções

| Problema | Solução Rápida |
|----------|----------------|
| Sistema estático | `python test_insert_signals.py` |
| Erro evmAsk.js | Ignorar (extensão de wallet) |
| Erro favicon 404 | Já corrigido (fazer git push) |
| Sem sinais | Rodar backend OU inserir teste |
| Modelo não encontrado | `python ml_model.py` |
| Backend não conecta | Verificar credenciais Supabase |

---

**🎉 Na maioria dos casos, executar `python test_insert_signals.py` resolve!**

