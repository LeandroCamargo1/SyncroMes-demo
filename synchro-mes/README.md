# Synchro MES - Sistema de Execução de Manufatura

Sistema MES completo e moderno para monitoramento de produção industrial, construído com **FastAPI** (Python) + **React** + **Tailwind CSS** + **PostgreSQL**.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![React](https://img.shields.io/badge/React-18-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Funcionalidades

- **Dashboard em tempo real** — KPIs, OEE gauge, grid de máquinas com status ao vivo
- **Gestão de Produção** — Ordens, planejamento por turno, lançamento de peças e refugos
- **Controle de Paradas** — Registro/encerramento de paradas com categorização Pareto
- **Qualidade** — Medições dimensionais, cartas SPC, aprovado/rejeitado
- **OEE** — Cálculo automático (Disponibilidade × Performance × Qualidade)
- **WebSocket** — Atualizações push em tempo real no dashboard
- **RBAC** — 5 perfis de acesso (admin, supervisor, operador, qualidade, PCP)
- **Responsivo** — Funciona em PC, tablet e celular

## Arquitetura

```
synchro-mes/
├── backend/                 # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models/          # 10 modelos SQLAlchemy
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   ├── services/        # Lógica de negócio (Auth, OEE, Dashboard)
│   │   ├── routers/         # 7 routers de API REST
│   │   ├── seed/            # Dados fictícios (seed)
│   │   ├── config.py        # Configuração via .env
│   │   ├── database.py      # Engine async + sessão
│   │   └── main.py          # Entry point FastAPI
│   ├── alembic/             # Migrações de banco
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React + Vite + Tailwind
│   ├── src/
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── pages/           # 6 páginas (Login, Dashboard, Produção...)
│   │   ├── services/        # API client, Auth, WebSocket
│   │   ├── context/         # AuthContext (React Context)
│   │   └── hooks/           # Custom hooks (useApi, usePolling)
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml       # PostgreSQL + Backend + Frontend
```

## Quick Start (Docker)

```bash
# Clonar o repositório
git clone https://github.com/LeandroCamargo1/synchro-mes.git
cd synchro-mes

# Subir tudo com Docker Compose
docker compose up --build

# Acessar:
# Frontend:  http://localhost:5173
# API:       http://localhost:8000
# Swagger:   http://localhost:8000/docs
```

## Setup Manual (Desenvolvimento)

### Pré-requisitos
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+

### Backend

```bash
cd backend

# Criar e ativar venv
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais de banco

# Rodar migrações
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar dev server
npm run dev
```

## Usuários Demo

O seed cria 5 usuários para demonstração:

| Usuário | Email | Senha | Perfil |
|---------|-------|-------|--------|
| Admin | admin@synchro.com | demo1234 | admin |
| Supervisor | supervisor@synchro.com | demo1234 | supervisor |
| Operador | operador@synchro.com | demo1234 | operador |
| Qualidade | qualidade@synchro.com | demo1234 | qualidade |
| PCP | pcp@synchro.com | demo1234 | pcp |

## API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/login` | Login (retorna JWT) |
| POST | `/api/auth/register` | Cadastrar usuário |
| GET | `/api/dashboard/summary` | Dashboard resumo |
| GET | `/api/machines` | Listar máquinas |
| GET | `/api/production/orders` | Ordens de produção |
| GET | `/api/production/entries` | Lançamentos |
| POST | `/api/downtimes/start` | Registrar parada |
| POST | `/api/downtimes/{id}/stop` | Encerrar parada |
| GET | `/api/quality/measurements` | Medições de qualidade |
| GET | `/api/oee/factory` | OEE da fábrica |
| WS | `/ws/{channel}` | WebSocket em tempo real |

Documentação completa: `http://localhost:8000/docs` (Swagger UI)

## Stack Tecnológica

### Backend
- **FastAPI** — Framework web async de alta performance
- **SQLAlchemy 2.0** — ORM async com suporte a PostgreSQL
- **Pydantic v2** — Validação e serialização de dados
- **python-jose** — JWT tokens para autenticação
- **Alembic** — Migrações de banco de dados
- **asyncpg** — Driver PostgreSQL async

### Frontend
- **React 18** — UI library com hooks
- **Vite 6** — Build tool ultrarrápido
- **Tailwind CSS 3** — Utility-first CSS framework
- **Recharts** — Gráficos e visualizações
- **Lucide React** — Ícones modernos
- **React Router DOM 6** — Roteamento SPA

### Infraestrutura
- **PostgreSQL 16** — Banco de dados relacional
- **Docker + Docker Compose** — Containerização

## Licença

MIT License — consulte o arquivo [LICENSE](LICENSE) para detalhes.
