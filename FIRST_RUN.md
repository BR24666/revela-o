# 🎬 Primeira Execução - Super Analista

## 🎯 Guia Completo para a Primeira Vez

Siga estes passos **na ordem** para ter o sistema funcionando pela primeira vez.

---

## ⚠️ Pré-requisitos

Certifique-se de ter instalado:
- [x] **Node.js 18+** ([download](https://nodejs.org/))
- [x] **Python 3.10+** ([download](https://python.org/))
- [x] **Git** ([download](https://git-scm.com/))
- [x] Conta no **Supabase** (já criada: Trading OB)
- [x] Conta no **Vercel** (para deploy) - opcional

---

## 📋 PASSO 1: Configurar Banco de Dados

### 1.1. Acessar Supabase

1. Vá para [supabase.com](https://supabase.com)
2. Faça login
3. Selecione o projeto: **Trading OB**
   - ID: `utmouqkyveodxrkqyies`

### 1.2. Executar Schema SQL

1. No menu lateral, clique em **SQL Editor**
2. Clique em **New Query**
3. Abra o arquivo `lib/supabase/schema.sql` deste projeto
4. Copie **TODO** o conteúdo do arquivo
5. Cole no editor SQL do Supabase
6. Clique em **Run** (canto inferior direito)

✅ Você verá mensagens de sucesso. As tabelas foram criadas!

### 1.3. Verificar Tabelas

1. Vá em **Table Editor** no menu lateral
2. Você deve ver as tabelas:
   - `signals`
   - `performance_stats`
   - `user_settings`
   - `market_data`

✅ **Banco de dados configurado!**

---

## 📦 PASSO 2: Instalar Dependências

### 2.1. Frontend (Node.js)

Abra o terminal na raiz do projeto:

```bash
# Windows
cd "C:\Users\br246\OneDrive\Documentos\revela cor"

# Instalar dependências
npm install
```

Aguarde... isso pode levar 2-5 minutos.

✅ **Dependências do frontend instaladas!**

### 2.2. Backend (Python)

No mesmo terminal:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Você verá (venv) no início da linha

# Instalar dependências
pip install -r requirements.txt
```

Aguarde... isso pode levar 5-10 minutos.

✅ **Dependências do backend instaladas!**

---

## 🧠 PASSO 3: Treinar o Modelo de IA

Este é o passo mais importante e demorado.

### 3.1. Opção Rápida (RECOMENDADO PARA TESTE)

```bash
cd python_backend

# Editar ml_model.py antes de executar
```

Abra `python_backend/ml_model.py` e encontre esta linha (linha ~217):

```python
USE_FULL_DATASET = False  # Certifique-se que está False
```

Agora execute:

```bash
python ml_model.py
```

**O que vai acontecer:**
- Vai baixar 30 dias de dados do BTC/USDT da Binance
- Vai calcular ~30 features para cada vela
- Vai treinar o modelo XGBoost
- Vai validar e mostrar winrate
- Vai salvar o modelo em `ml_models/`

**Tempo estimado:** 10-20 minutos

### 3.2. Opção Completa (PRODUÇÃO)

Se quiser treinar com 3-5 anos de dados (mais preciso):

```python
USE_FULL_DATASET = True  # Mudar para True
```

```bash
python ml_model.py
```

**Tempo estimado:** 30-120 minutos

### 3.3. Verificar Sucesso

Ao final, você deve ver algo como:

```
========================================
TREINAMENTO CONCLUÍDO!
========================================

Test Accuracy: 62.45%

✓ Modelo salvo em: ml_models/trained_model.pkl
✓ Scaler salvo em: ml_models/scaler.pkl
```

✅ **Modelo treinado com sucesso!**

---

## 🚀 PASSO 4: Executar o Sistema

Agora você precisa de **2 terminais abertos**.

### Terminal 1: Backend (Engine de Tempo Real)

```bash
cd python_backend

# Se não estiver com (venv) ativo:
..\venv\Scripts\activate  # Windows
# source ../venv/bin/activate  # Linux/Mac

# Executar engine
python realtime_engine.py
```

**O que vai acontecer:**
- Conecta ao WebSocket da Binance
- Aguarda velas M1 de BTC/USDT
- Quando uma vela fecha, faz a previsão
- Se confiança >= 70%, salva sinal no banco
- Verifica resultado após 60 segundos

Você verá logs como:
```
========================================
SUPER ANALISTA - ENGINE DE TEMPO REAL
========================================

✓ Modelo carregado com sucesso
✓ Buffer inicializado com 100 velas
Conectando ao WebSocket...
✓ Conectado! Aguardando velas...
```

### Terminal 2: Frontend (Next.js)

Abra um **NOVO** terminal:

```bash
# Na raiz do projeto
npm run dev
```

Você verá:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## 🌐 PASSO 5: Acessar o Sistema

1. Abra seu navegador
2. Acesse: **http://localhost:3000**

### O que você verá:

#### Tela de Sinais
- "Aguardando próximo sinal..."
- Quando o backend gerar um sinal (a cada 1-5 minutos em média), ele aparecerá aqui
- Mostrará: CALL ou PUT, confiança, preço

#### Dashboard de Performance
- Inicialmente vazio (0 sinais)
- Após alguns sinais, mostrará winrate e estatísticas

#### Configurações
- Você pode ajustar o nível mínimo de confiança
- Padrão: 75%

---

## 🎯 PASSO 6: Aguardar Primeiro Sinal

**Seja paciente!** O sistema só gera sinais quando:
1. Uma vela M1 fecha (a cada 60 segundos)
2. A previsão tem confiança >= threshold (75% padrão)

**Tempo médio até primeiro sinal:** 2-10 minutos

Quando o sinal aparecer:
- ✅ Aparecerá na tela de Sinais
- ✅ Será salvo no banco (tabela `signals`)
- ✅ Após 60s, terá resultado (WIN/LOSS)

---

## ✅ Checklist de Sucesso

Marque conforme for completando:

- [ ] Tabelas criadas no Supabase
- [ ] `npm install` executado sem erros
- [ ] `pip install -r requirements.txt` executado sem erros
- [ ] Modelo treinado (`ml_models/trained_model.pkl` existe)
- [ ] Backend rodando (vejo logs no terminal 1)
- [ ] Frontend rodando (acesso http://localhost:3000)
- [ ] Primeiro sinal gerado e apareceu na tela

---

## 🐛 Problemas Comuns

### ❌ Erro: "Module not found"

**Solução:**
```bash
# Certifique-se que está com (venv) ativo
venv\Scripts\activate

# Reinstale
pip install -r requirements.txt
```

### ❌ Erro: "Modelo não encontrado"

**Solução:**
```bash
cd python_backend
python ml_model.py  # Treinar modelo
```

### ❌ Erro: "Cannot connect to Supabase"

**Solução:**
1. Verifique se executou o schema SQL
2. Verifique as credenciais no código
3. Confirme que o projeto Supabase está ativo

### ❌ Frontend não mostra sinais

**Solução:**
1. Verifique se o backend está rodando
2. Abra F12 no navegador, veja se há erros
3. Vá no Supabase > Table Editor > `signals` e veja se tem dados

### ❌ Sinais não têm resultado (sempre PENDING)

**Solução:**
- É normal! O resultado só aparece após 60 segundos
- Se após 2 minutos ainda está PENDING, verifique logs do backend

---

## 📊 Primeiros Resultados

### Após 10 sinais:
- Dashboard começará a mostrar estatísticas
- Ainda é cedo para conclusões

### Após 50 sinais:
- Winrate começará a estabilizar
- Você terá uma boa noção da performance

### Após 100+ sinais:
- Estatísticas confiáveis
- Pode começar a usar em produção com confiança

---

## 🎓 Próximos Passos

Agora que está funcionando:

1. **Deixe rodando por 24h**
   - Acumule sinais
   - Veja a performance em diferentes horários

2. **Ajuste o threshold**
   - Teste com 80%, 85%, 90%
   - Veja como afeta winrate vs. quantidade de sinais

3. **Estude os padrões**
   - Quais horários têm melhor performance?
   - Qual faixa de confiança é mais lucrativa?

4. **Deploy em produção**
   - Ver `DEPLOY.md` para rodar 24/7

---

## 🚀 Deploy (Opcional)

Se quiser deixar rodando 24/7:

### Frontend
```bash
# Conecte repositório no Vercel
# Deploy automático!
```

### Backend
```bash
# Contrate VPS DigitalOcean ($6/mês)
# Ver DEPLOY.md para instruções completas
```

---

## 📞 Ajuda

Ainda com problemas?

1. Leia `README.md` completo
2. Veja `QUICKSTART.md` para referência rápida
3. Abra issue no GitHub

---

**Boa sorte com seu Super Analista! 🚀📈**

Lembre-se: Este é um assistente de decisão, não um bot automático.  
Sempre faça sua própria análise antes de operar!

