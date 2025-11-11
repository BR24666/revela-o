# 🏗️ Arquitetura do Sistema - Super Analista

## 📊 Diagrama de Fluxo Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUÁRIO                                   │
│                     (Navegador Web)                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Next.js 14 + React + TypeScript                          │  │
│  │  - SignalsScreen (Tela de Sinais)                         │  │
│  │  - PerformanceScreen (Dashboard)                          │  │
│  │  - SettingsScreen (Configurações)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ Supabase Realtime (WebSocket)
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SUPABASE (Database)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL + Realtime                                    │  │
│  │  - signals (sinais gerados)                               │  │
│  │  - performance_stats (estatísticas)                       │  │
│  │  - user_settings (configurações)                          │  │
│  │  - market_data (cache de dados)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ REST API (INSERT/SELECT)
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│               BACKEND PYTHON (VPS/Cloud)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Realtime Engine (realtime_engine.py)                     │  │
│  │  ├─ WebSocket Binance (recebe velas M1)                   │  │
│  │  ├─ Feature Engineering (calcula 30+ features)            │  │
│  │  ├─ ML Predictor (faz previsão)                           │  │
│  │  ├─ Signal Generator (gera sinais)                        │  │
│  │  └─ Result Tracker (verifica Win/Loss)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ WebSocket
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BINANCE API                                     │
│  - Dados históricos (REST)                                       │
│  - Stream de velas M1 (WebSocket)                                │
│  - BTC/USDT                                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados Detalhado

### 1. Coleta de Dados (Data Collection)

```
Binance WebSocket → Realtime Engine → Buffer (últimas 100 velas)
    │
    └─→ A cada vela fechada (60s):
        ├─ Timestamp
        ├─ OHLC (Open, High, Low, Close)
        └─ Volume
```

### 2. Processamento (Feature Engineering)

```
Velas OHLC → Feature Engineer → 30+ Features
    │
    ├─ Pilar 1: 10 Regras Probabilísticas
    │   ├─ rule_engolfo (-1, 0, 1)
    │   ├─ rule_tres_soldados (0, 1)
    │   ├─ rule_vela_forca (-1, 0, 1)
    │   └─ ... (mais 7 regras)
    │
    ├─ Pilar 2: Indicadores Técnicos
    │   ├─ RSI (valor + oversold/overbought)
    │   ├─ EMA 9 e 21 (valores + cruzamentos)
    │   └─ Bollinger Bands (upper, middle, lower, width, position)
    │
    └─ Pilar 3: Price Action
        ├─ Distância para suporte/resistência
        ├─ Estrutura de pivots (+2 a -2)
        └─ Análise de pavios (wick %)
```

### 3. Predição (ML Model)

```
Features → XGBoost Model → Previsão
    │
    ├─ Input: Array[30+ features]
    │
    ├─ Processamento:
    │   ├─ Normalização (StandardScaler)
    │   ├─ XGBoost Classifier
    │   └─ Probability Estimation
    │
    └─ Output:
        ├─ Prediction: 0 (PUT) ou 1 (CALL)
        └─ Confidence: 0-100%
```

### 4. Geração de Sinais

```
Previsão → Verificação de Threshold → Sinal (se confiança >= 75%)
    │
    ├─ Se confiança >= threshold:
    │   ├─ Salva sinal no Supabase
    │   ├─ Frontend recebe via Realtime
    │   └─ Usuário vê na tela
    │
    └─ Se confiança < threshold:
        └─ Descarta (não gera sinal)
```

### 5. Verificação de Resultado

```
Sinal gerado → Aguardar 60s → Verificar resultado
    │
    ├─ Buscar preço de fechamento após 60s
    │
    ├─ Comparar:
    │   ├─ CALL + (close > open) → WIN
    │   ├─ CALL + (close < open) → LOSS
    │   ├─ PUT + (close < open) → WIN
    │   └─ PUT + (close > open) → LOSS
    │
    └─ Atualizar sinal no banco:
        ├─ close_price = novo preço
        └─ result = 'WIN' ou 'LOSS'
```

---

## 🧩 Módulos Python (Backend)

### config.py
- Configurações globais
- Credenciais Supabase/Binance
- Lista de features
- Thresholds

### data_collector.py (BinanceDataCollector)
```python
.get_historical_klines()     # Buscar dados históricos
.get_large_historical_dataset()  # Baixar 3-5 anos
.get_latest_candles()        # Últimas N velas
```

### feature_engineering.py (FeatureEngineer)
```python
.calculate_all_features()    # Calcula todas features
._calculate_probabilistic_rules()  # 10 regras
._calculate_technical_indicators()  # RSI, EMA, BB
._calculate_price_action()   # S/R, Pivots, Wicks
```

### ml_model.py (MLPredictor)
```python
.train_model()               # Treinar modelo
.predict()                   # Fazer previsão
.predict_with_details()      # Previsão + detalhes
.save_model()                # Salvar modelo
.load_model()                # Carregar modelo
```

### realtime_engine.py (RealtimeEngine)
```python
.start()                     # Iniciar engine
._init_buffer()              # Inicializar buffer
._process_message()          # Processar vela do WebSocket
._make_prediction()          # Fazer previsão
._save_signal()              # Salvar no banco
._verify_signal_result()     # Verificar Win/Loss
```

---

## 🎨 Componentes React (Frontend)

### Navigation.tsx
- Navegação entre telas
- 3 botões: Sinais, Performance, Configurações

### SignalsScreen.tsx
```typescript
// Estado
- latestSignal: último sinal gerado
- recentSignals: lista dos últimos 10
- loading: estado de carregamento

// Realtime
- Supabase subscription (INSERT + UPDATE)
- Atualiza automaticamente quando novo sinal

// UI
- Card grande com sinal atual
- Lista de sinais recentes
- Resultado (WIN/LOSS) quando disponível
```

### PerformanceScreen.tsx
```typescript
// Estado
- overallStats: total, wins, losses, winrate
- confidenceStats: stats por faixa de confiança

// Funções
- loadPerformanceData(): buscar do banco
- calcular stats por faixa (70-75%, 75-80%, etc)

// UI
- 4 cards: Total, Wins, Losses, Winrate
- Barras de progresso por confiança
- Insights automáticos
```

### SettingsScreen.tsx
```typescript
// Estado
- minConfidence: threshold (50-95%)
- notification: ativar/desativar

// Storage
- localStorage (persistência local)

// UI
- Slider para ajustar threshold
- Toggle de notificações
- Info sobre o modelo
```

---

## 💾 Schema do Banco (Supabase)

### Tabela: signals
```sql
id: UUID (PK)
timestamp: TIMESTAMP
symbol: VARCHAR ('BTC/USDT')
timeframe: VARCHAR ('M1')
prediction: VARCHAR ('CALL' ou 'PUT')
confidence_score: DECIMAL (0-100)
open_price: DECIMAL
close_price: DECIMAL (NULL até resultado)
result: VARCHAR ('WIN', 'LOSS', 'PENDING')
features: JSONB (features usadas na previsão)
```

### Tabela: performance_stats
```sql
id: UUID (PK)
period: VARCHAR ('daily', 'weekly', etc)
total_signals: INTEGER
wins: INTEGER
losses: INTEGER
winrate: DECIMAL
confidence_range: VARCHAR ('80-90%', etc)
avg_confidence: DECIMAL
```

### Tabela: user_settings
```sql
id: UUID (PK)
user_id: VARCHAR
min_confidence_threshold: DECIMAL (default: 75.0)
notification_enabled: BOOLEAN
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

### Tabela: market_data (cache)
```sql
id: UUID (PK)
timestamp: TIMESTAMP
symbol: VARCHAR
timeframe: VARCHAR
open, high, low, close, volume: DECIMAL
```

---

## 🔐 Segurança

### Frontend
- Usa ANON KEY (pública)
- Row Level Security (RLS) ativo
- Apenas leitura de `signals` e `performance_stats`

### Backend
- Usa SERVICE ROLE KEY (privada)
- Pode inserir/atualizar dados
- Nunca exposta ao cliente

### Binance
- Apenas endpoints públicos (não requer API key)
- Para endpoints privados, usar variáveis de ambiente

---

## 📈 Performance

### Frontend
- Next.js com Server Side Rendering
- Componentes otimizados
- Supabase Realtime (baixa latência)

### Backend
- WebSocket para dados em tempo real
- Buffer em memória (últimas 100 velas)
- Processamento assíncrono
- Previsão em < 1 segundo

### Banco de Dados
- Índices em campos frequentes
- Views materializadas
- Queries otimizadas

---

## 🔄 Ciclo de Vida do Sinal

```
1. Vela fecha (Binance) → 0s
2. Backend recebe via WebSocket → +0.1s
3. Calcula features → +0.5s
4. Faz previsão → +0.2s
5. Se confiança OK, salva no banco → +0.1s
6. Frontend recebe via Realtime → +0.2s
7. Usuário vê sinal na tela → +0.1s

Total: ~1.2 segundos do fechamento da vela até aparecer na tela

60 segundos depois:
8. Backend busca preço de fechamento → +60s
9. Calcula resultado (WIN/LOSS) → +0.1s
10. Atualiza no banco → +0.1s
11. Frontend atualiza resultado → +0.2s

Total: ~60.4 segundos até resultado final
```

---

## 🚀 Escalabilidade

### Limitações Atuais
- 1 símbolo (BTC/USDT)
- 1 timeframe (M1)
- 1 instância do backend

### Como Escalar
1. **Múltiplos símbolos:**
   - Criar 1 engine por símbolo
   - Separar por tabelas no banco

2. **Múltiplos timeframes:**
   - Rodar engines em paralelo
   - M1, M5, M15, etc

3. **Múltiplos usuários:**
   - Frontend já suporta
   - Adicionar autenticação (Supabase Auth)
   - RLS personalizado por usuário

4. **Alta disponibilidade:**
   - Múltiplas instâncias do backend
   - Load balancer
   - Database replication

---

## 📊 Métricas de Monitoramento

### Backend
- Total de velas processadas
- Sinais gerados por hora
- Tempo médio de previsão
- Erros/exceções

### Banco de Dados
- Tamanho das tabelas
- Queries mais lentas
- Conexões ativas

### Performance
- Winrate geral
- Winrate por horário
- Winrate por dia da semana
- Winrate por faixa de confiança

---

**Arquitetura robusta, escalável e de fácil manutenção! 🏗️**

