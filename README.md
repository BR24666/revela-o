# 🤖 Super Analista BTC/USDT - Sistema de Previsão com IA

Sistema de análise preditiva que utiliza Machine Learning para prever a cor (Verde/Vermelha) da próxima vela de 1 minuto (M1) no par BTC/USDT.

## 📋 Visão Geral

O Super Analista é um assistente de decisão que fornece sinais (CALL/PUT) com base em um "Score de Confiança". O sistema analisa:

- **10 Regras Probabilísticas** (Engolfo, Três Soldados, MHI, etc.)
- **Indicadores Técnicos** (RSI, EMA, Bollinger Bands)
- **Price Action** (Suporte/Resistência, Pivots, Wicks)

### ⚠️ Aviso Importante

Este sistema é apenas uma **ferramenta de assistência**. Não é um bot de trade automático. Sempre faça sua própria análise antes de operar.

## 🛠️ Stack Tecnológica

### Frontend
- **Next.js 14** (React + TypeScript)
- **Tailwind CSS** para estilização
- **Supabase Client** para realtime updates
- **Vercel** para deploy

### Backend
- **Python 3.10+**
- **XGBoost** para Machine Learning
- **Binance API** para dados de mercado
- **Supabase** como banco de dados
- **WebSocket** para dados em tempo real

## 🚀 Instalação e Setup

### 1. Clone o Repositório

```bash
git clone https://github.com/BR24666/revela-o.git
cd revela-o
```

### 2. Setup do Frontend (Next.js)

```bash
# Instalar dependências
npm install

# Criar arquivo .env.local (já está configurado)
# NEXT_PUBLIC_SUPABASE_URL=...
# NEXT_PUBLIC_SUPABASE_ANON_KEY=...

# Executar em desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

### 3. Setup do Backend Python

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar Supabase

1. Acesse o [Supabase Dashboard](https://supabase.com)
2. Vá para o projeto: **Trading OB**
3. Abra o **SQL Editor**
4. Execute o script `lib/supabase/schema.sql`

Isso criará todas as tabelas necessárias:
- `signals` - Sinais gerados pela IA
- `performance_stats` - Estatísticas de performance
- `user_settings` - Configurações do usuário
- `market_data` - Cache de dados de mercado

## 📊 Treinamento do Modelo

Antes de usar o sistema, você precisa treinar o modelo de ML:

```bash
cd python_backend
python ml_model.py
```

Este processo:
1. Coleta dados históricos da Binance (3-5 anos recomendado)
2. Calcula todas as features (regras + indicadores)
3. Treina o modelo XGBoost
4. Valida em dados de teste
5. Salva o modelo treinado em `ml_models/`

**Importante:** O treinamento inicial pode levar de 10 minutos a 2 horas, dependendo da quantidade de dados.

### Teste Rápido (30 dias)

Para testar rapidamente, edite `ml_model.py`:

```python
USE_FULL_DATASET = False  # Usa apenas 30 dias
```

## 🔴 Executar o Sistema em Produção

### Engine de Tempo Real (Backend)

Este processo conecta ao WebSocket da Binance, processa velas M1 em tempo real e gera sinais:

```bash
cd python_backend
python realtime_engine.py
```

O engine ficará rodando 24/7 e:
- Recebe velas M1 via WebSocket
- Calcula features em tempo real
- Faz previsões quando a vela fecha
- Salva sinais no Supabase (se confiança >= threshold)
- Verifica resultado após 60 segundos (WIN/LOSS)

### Frontend (Next.js)

```bash
npm run dev  # Desenvolvimento
# ou
npm run build && npm start  # Produção
```

## 📱 Funcionalidades

### Tela de Sinais
- Mostra o sinal atual (CALL/PUT)
- Exibe score de confiança
- Histórico dos últimos 10 sinais
- Atualização em tempo real via Supabase Realtime

### Dashboard de Performance
- Winrate total
- Estatísticas por faixa de confiança
- Total de acertos/erros
- Insights automáticos

### Tela de Configurações
- Ajustar nível mínimo de confiança (50-95%)
- Ativar/desativar notificações
- Informações sobre o modelo

## 🌐 Deploy

### Deploy do Frontend (Vercel)

1. Conecte seu repositório ao Vercel
2. Configure as variáveis de ambiente:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Deploy automático a cada push

### Deploy do Backend Python

Recomendado: **VPS** (AWS EC2, DigitalOcean, Vultr)

```bash
# Instalar dependências no servidor
pip install -r requirements.txt

# Executar com screen/tmux para manter rodando
screen -S super-analista
python python_backend/realtime_engine.py
# Ctrl+A+D para detach
```

Ou use **Docker** (opcional):

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY python_backend/ ./python_backend/
CMD ["python", "python_backend/realtime_engine.py"]
```

## 📈 Winrate Esperado das Regras

| Regra | Winrate Teórico | Melhor Horário | Melhor Dia |
|-------|----------------|----------------|------------|
| Engolfo de Cor Única | 92.9% | 8h | Sábado |
| Três Soldados Brancos | 92.0% | 14h | Quarta |
| Vela de Força | 90.9% | 13h | Sexta |
| Três Vales/Picos | 85.7% | 12h | Quarta |
| MHI | 85.0% | 10h | Segunda |
| Reversão Pós-Doji | 84.2% | 15h | Segunda |
| Minoria | 80.0% | 9h | Terça |
| Primeira Vela Quadrante | 75.0% | 10h | Domingo |
| Alternância de Cores | 72.2% | 11h | Quinta |
| Sequência Ímpar | 71.4% | 9h | Terça |

**Nota:** Estes winrates são teóricos. O modelo de ML combina múltiplas regras e indicadores para gerar previsões mais robustas.

## 🔧 Manutenção

### Retreinamento do Modelo

Recomenda-se retreinar o modelo semanalmente para adaptar-se às mudanças do mercado:

```bash
# Executar script de treinamento
cd python_backend
python ml_model.py
```

### Backup do Banco de Dados

O Supabase faz backups automáticos, mas você pode exportar manualmente:

```bash
# No Supabase Dashboard > Database > Backups
```

## 📁 Estrutura do Projeto

```
revela-cor/
├── app/                    # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/             # Componentes React
│   ├── Navigation.tsx
│   ├── SignalsScreen.tsx
│   ├── PerformanceScreen.tsx
│   └── SettingsScreen.tsx
├── lib/
│   └── supabase/          # Configuração Supabase
│       ├── client.ts
│       ├── types.ts
│       └── schema.sql
├── python_backend/         # Backend Python
│   ├── config.py          # Configurações
│   ├── data_collector.py  # Coleta de dados Binance
│   ├── feature_engineering.py  # Cálculo de features
│   ├── ml_model.py        # Modelo de ML
│   └── realtime_engine.py # Engine tempo real
├── ml_models/             # Modelos treinados (gerado)
├── package.json
├── requirements.txt
└── README.md
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é privado e proprietário.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Email: [seu-email]

---

**Desenvolvido com 🚀 usando Vercel + Supabase + Python**

