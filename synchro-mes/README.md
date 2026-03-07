# Synchro MES

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Firebase-12-FFCA28?logo=firebase&logoColor=black" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

> Sistema MES (Manufacturing Execution System) completo e moderno, inspirado no Siemens Opcenter, para controle de chão de fábrica em indústrias de injeção plástica.

---

## Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Stack Tecnológica](#stack-tecnológica)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Backend — API](#backend--api)
- [Frontend — Interface](#frontend--interface)
- [Firebase — Cloud Database](#firebase--cloud-database)
- [ML Service — Predições](#ml-service--predições)
- [Documentação Complementar](#documentação-complementar)
- [Licença](#licença)

---

## Visão Geral

O **Synchro MES** é uma plataforma integrada de gestão de manufatura que monitora, controla e otimiza operações produtivas em tempo real. O sistema abrange desde o planejamento de produção (PCP) até a análise de indicadores avançados (OEE, SPC, Pareto), passando por controle de qualidade, rastreabilidade de materiais e manutenção de equipamentos.

### Destaques

- **19 telas** cobrindo todo o fluxo produtivo
- **80+ endpoints RESTful** com documentação Swagger automática
- **32 coleções Firestore** com dados sincronizados na nuvem
- **30 modelos de dados** com 24 enums tipados
- **9 componentes de gráficos** estilo Siemens Opcenter (Recharts)
- **4 modelos de Machine Learning** para predições (OEE, paradas, qualidade, manutenção)
- **WebSocket** em tempo real para dashboard e notificações
- **Dashboard TV** otimizado para monitores de chão de fábrica
- **Sistema de auditoria** automático por middleware

---

## Funcionalidades

### Produção

| Módulo | Descrição |
|--------|-----------|
| **Dashboard** | Visão geral com OEE gauge, grid de máquinas, gráficos de produção e ranking |
| **Dashboard TV** | Tela fullscreen para monitores do chão de fábrica (auto-refresh 30s) |
| **Produção** | Ordens de produção (CRUD), apontamentos, gráficos output vs target |
| **Lançamento** | Registro rápido de produção por operador |
| **Planejamento** | Sequenciamento de ordens por máquina e turno |
| **PCP** | Mensagens, fila de prioridade, comunicação com chão de fábrica |

### Qualidade

| Módulo | Descrição |
|--------|-----------|
| **Qualidade** | Medições dimensionais, carta SPC (UCL/LCL), donut de aprovação |
| **Lotes** | Rastreabilidade por lote, triagem, quarentena |
| **Perdas** | Registro de refugo/rebarba por categoria, gráficos Pareto |
| **PMP** | Controle de material processado (moído, borra, sucata) |

### Equipamentos

| Módulo | Descrição |
|--------|-----------|
| **Máquinas** | Cadastro, status em tempo real, setup, ciclo |
| **Setup** | Registro de trocas (molde, cor, material), tempo vs meta |
| **Ferramental** | Gestão de moldes, alertas de vida útil, manutenções |
| **Manutenção** | Preventiva/corretiva de máquinas, prioridades, custos |

### Gestão

| Módulo | Descrição |
|--------|-----------|
| **Análise** | 7 abas: OEE trend, Pareto, donuts, comparativos, SPC |
| **Relatórios** | Produção, OEE, Qualidade, Paradas — com gráficos inline |
| **Liderança** | Escala de operadores, absenteísmo, justificativas |
| **Histórico** | Log completo de todas as operações do sistema |
| **Admin** | Cadastro de produtos, operadores, máquinas, materiais |

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React 18 · TypeScript · Tailwind CSS · Recharts · Firebase  │
│  Vite 6 · 19 páginas · 9 chart components · WebSocket        │
├───────────────┬──────────────────┬───────────────────────────┤
│  REST /api    │  WebSocket /ws   │  REST /ml                 │
├───────────────┴──────────────────┴───────────────────────────┤
│                        BACKEND                               │
│  FastAPI 0.115 · SQLAlchemy 2.0 (async) · Alembic            │
│  21 routers · 80+ endpoints · JWT Auth · Audit Middleware     │
├──────────────────────────────────────────────────────────────┤
│                      ML SERVICE                              │
│  FastAPI · scikit-learn · PyTorch · 4 modelos preditivos     │
├──────────────────────────────────────────────────────────────┤
│                       DATABASES                              │
│  PostgreSQL 16 (prod) │ SQLite (dev) │ Firestore (cloud)     │
└──────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológica

### Backend

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| Python | 3.12 | Runtime |
| FastAPI | 0.115.6 | Framework web async |
| SQLAlchemy | 2.0.36 | ORM async |
| PostgreSQL | 16 | Banco de produção |
| SQLite + aiosqlite | 0.20.0 | Banco de dev |
| Alembic | 1.14.1 | Migrações de schema |
| python-jose | 3.3.0 | JWT authentication |
| Pydantic | 2.10.4 | Validação de dados |
| WebSockets | 14.1 | Comunicação real-time |
| Uvicorn | 0.34.0 | ASGI server |

### Frontend

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| React | 18.3.1 | UI framework |
| TypeScript | 5.9.3 | Tipagem estática |
| Vite | 6.0.3 | Build tool |
| Tailwind CSS | 3.4.17 | Utility-first CSS |
| Recharts | 2.14.1 | Gráficos (9 componentes) |
| Axios | 1.7.9 | HTTP client |
| Firebase | 12.10.0 | Cloud database (Firestore) |
| Lucide React | 0.468.0 | Ícones |
| React Router | 6.28.0 | Roteamento SPA |

### ML Service

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| scikit-learn | 1.6.1 | Modelos ML clássicos |
| PyTorch | 2.6.0 | Deep learning |
| pandas | 2.2.3 | Processamento de dados |

---

## Pré-requisitos

- **Python** 3.12+
- **Node.js** 18+ e npm
- **Docker** e Docker Compose (para PostgreSQL/produção)
- Projeto Firebase configurado (para Firestore)

---

## Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/LeandroCamargo1/controleproducao.git
cd controleproducao/synchro-mes
```

### 2. Backend (Dev com SQLite)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

O backend estará em **http://localhost:8000** com docs Swagger em **/docs**.

### 3. Frontend

```bash
cd frontend
npm install
# Editar .env com credenciais Firebase
npm run dev
```

Frontend em **http://localhost:5173**.

### 4. Docker Compose (Produção)

```bash
docker compose up -d
```

Sobe PostgreSQL (5432), Backend (8000), ML Service (8001) e Frontend (5173).

### 5. Popular Firestore

1. Criar Firestore Database no Firebase Console (modo teste)
2. Preencher `frontend/.env` com credenciais
3. Acessar **http://localhost:5173/seed** → clicar "Executar Seed"

---

## Estrutura do Projeto

```
synchro-mes/
├── docker-compose.yml
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── API.md                  # Referência da API (80+ endpoints)
│   ├── FRONTEND.md             # Arquitetura frontend
│   ├── DATABASE.md             # Schema do banco (30 modelos)
│   └── DEPLOY.md               # Guia de deploy
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   └── app/
│       ├── main.py             # Entry point FastAPI
│       ├── config.py           # Settings
│       ├── database.py         # SQLAlchemy async
│       ├── models/             # 30 modelos + 24 enums
│       ├── routers/            # 21 routers
│       ├── schemas/            # Pydantic schemas
│       ├── services/           # Lógica de negócio
│       └── seed/               # Dados iniciais
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── App.tsx             # 19 rotas
│       ├── lib/firebase.ts     # Inicialização Firebase
│       ├── components/
│       │   ├── charts/         # 9 componentes Recharts
│       │   ├── common/
│       │   ├── dashboard/      # MachineGrid, OeeGauge
│       │   └── layout/         # Header, Sidebar, Layout
│       ├── context/            # AuthContext
│       ├── hooks/              # useApi, usePolling, useDebounce
│       ├── pages/              # 19 páginas
│       ├── services/           # api, auth, firestore, websocket, ml
│       └── types/              # 16 arquivos de tipos TS
│
└── ml-service/
    ├── Dockerfile
    └── app/
        ├── main.py
        ├── routers/
        └── models/             # 4 modelos preditivos
```

---

## Backend — API

### Autenticação

- **JWT** com HS256, token válido por 8 horas
- `POST /api/auth/login` — login email/senha
- `GET /api/auth/me` — perfil do usuário
- **Dev mode**: `DEV_BYPASS_AUTH=True` desativa autenticação

### Routers (21)

| Prefixo | Módulo | Principais |
|---------|--------|-----------|
| `/api/auth` | Autenticação | login, me, register |
| `/api/dashboard` | Dashboard | summary |
| `/api/machines` | Máquinas | CRUD, molds |
| `/api/production` | Produção | orders, planning, entries |
| `/api/downtimes` | Paradas | start, stop, history |
| `/api/quality` | Qualidade | measurements |
| `/api/quality-lots` | Lotes | lots, summary, reports |
| `/api/oee` | OEE | history, machine, factory |
| `/api/losses` | Perdas | CRUD, summary |
| `/api/setup` | Setup | CRUD, finish |
| `/api/pmp` | PMP | CRUD, summary |
| `/api/tooling` | Ferramental | molds, maintenance, alerts |
| `/api/pcp` | PCP | messages, queue |
| `/api/leadership` | Liderança | schedule, absenteeism |
| `/api/history` | Histórico | logs paginados |
| `/api/admin` | Admin | products, operators |
| `/api/hierarchy` | Hierarquia | sites, areas, tree |
| `/api/materials` | Materiais | CRUD, BOM, movements |
| `/api/maintenance` | Manutenção | CRUD, pending |
| `/api/kpis` | KPIs | advanced, process-segments |
| `/api/notifications` | Notificações | count, read-all |

### WebSocket

```
ws://localhost:8000/ws/{channel}
```

Canais: `dashboard`, `production`, `quality`.

---

## Frontend — Interface

### Gráficos (9 componentes Recharts)

| Componente | Tipo | Aplicação |
|-----------|------|-----------|
| `OeeTrendChart` | LineChart | Tendência A×P×Q com meta 85% |
| `ProductionBarChart` | BarChart | Boas vs refugo por máquina |
| `DonutChart` | PieChart | Distribuição com valor central |
| `ParetoChart` | ComposedChart | Barras + linha 80% cumulativo |
| `SpcChart` | LineChart | Carta SPC (UCL/LCL/Nominal) |
| `ProductionAreaChart` | AreaChart | Tendência produção empilhada |
| `HorizontalBarChart` | BarChart | Ranking com linha de meta |
| `Sparkline` | LineChart | Mini gráfico inline |
| `OutputVsTargetChart` | BarChart | Planejado vs produzido |

### Design System

- **Paleta**: primary #5c7cfa, emerald, amber, red, blue, violet
- **Fontes**: Inter (sans), JetBrains Mono (mono)
- **CSS classes**: `.card`, `.btn-primary`, `.btn-outline`, `.tab-bar`, `.table-modern`

---

## Firebase — Cloud Database

- **Projeto**: syncro-mes
- **32 coleções** com ~1500+ documentos de dados realistas
- **Serviço genérico**: `createService<T>(collection)` em `src/services/firestore.ts`
- **Seed via UI**: página `/seed` com botão de popular e limpar dados

---

## ML Service — Predições

| Endpoint | Descrição |
|----------|-----------|
| `POST /predictions/oee` | Prever OEE do próximo turno |
| `POST /predictions/downtime` | Probabilidade de parada |
| `POST /predictions/quality` | Taxa de defeito prevista |
| `POST /predictions/maintenance` | Necessidade de manutenção |
| `POST /ml/train-all` | Treinar todos os modelos |
| `GET /ml/health` | Status dos modelos |

---

## Documentação Complementar

| Documento | Descrição |
|-----------|-----------|
| [docs/API.md](docs/API.md) | Referência completa da API (80+ endpoints) |
| [docs/FRONTEND.md](docs/FRONTEND.md) | Arquitetura frontend, componentes, hooks |
| [docs/DATABASE.md](docs/DATABASE.md) | Schema do banco (30 modelos, 24 enums) |
| [docs/DEPLOY.md](docs/DEPLOY.md) | Guia de deploy e configuração |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões |

---

## Variáveis de Ambiente

### Backend

| Variável | Default | Descrição |
|----------|---------|-----------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./synchro_mes_v2.db` | URL do banco |
| `SECRET_KEY` | (gerar) | Chave JWT |
| `DEV_BYPASS_AUTH` | `True` | Desativar auth em dev |
| `CORS_ORIGINS` | `http://localhost:5173` | Origens CORS |

### Frontend (.env)

| Variável | Descrição |
|----------|-----------|
| `VITE_FIREBASE_API_KEY` | API Key do Firebase |
| `VITE_FIREBASE_AUTH_DOMAIN` | Auth domain |
| `VITE_FIREBASE_PROJECT_ID` | Project ID |
| `VITE_FIREBASE_STORAGE_BUCKET` | Storage bucket |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Sender ID |
| `VITE_FIREBASE_APP_ID` | App ID |

---

## Licença

Este projeto está sob a licença **MIT**. Consulte [LICENSE](LICENSE).

---

<p align="center">
  <strong>Synchro MES</strong> — Controle inteligente para o chão de fábrica<br/>
  <sub>v2.1.0 · Fase 1 de desenvolvimento concluída</sub>
</p>
