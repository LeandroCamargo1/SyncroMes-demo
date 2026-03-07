# Synchro MES — Descritivo Técnico Detalhado

> **Versão:** 2.0.0  
> **Tipo:** Sistema MES (Manufacturing Execution System) para indústria de injeção plástica  
> **Arquitetura:** Full-stack — Backend Python + Frontend React  
> **Última atualização:** Março/2026

---

## Sumário

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Stack Tecnológica](#2-stack-tecnológica)
3. [Backend — FastAPI](#3-backend--fastapi)
   - 3.1 [Configuração e Inicialização](#31-configuração-e-inicialização)
   - 3.2 [Banco de Dados](#32-banco-de-dados)
   - 3.3 [Modelos de Dados (16 tabelas)](#33-modelos-de-dados-16-tabelas)
   - 3.4 [Schemas Pydantic](#34-schemas-pydantic)
   - 3.5 [Serviços (Business Logic)](#35-serviços-business-logic)
   - 3.6 [Routers — API REST (22 endpoints)](#36-routers--api-rest-22-endpoints)
   - 3.7 [WebSocket — Tempo Real](#37-websocket--tempo-real)
   - 3.8 [Autenticação e Autorização (RBAC)](#38-autenticação-e-autorização-rbac)
   - 3.9 [Seed de Dados Fictícios](#39-seed-de-dados-fictícios)
   - 3.10 [Migrações com Alembic](#310-migrações-com-alembic)
4. [Frontend — React](#4-frontend--react)
   - 4.1 [Roteamento e Proteção de Rotas](#41-roteamento-e-proteção-de-rotas)
   - 4.2 [Contexto de Autenticação](#42-contexto-de-autenticação)
   - 4.3 [Services (API, Auth, WebSocket)](#43-services-api-auth-websocket)
   - 4.4 [Custom Hooks](#44-custom-hooks)
   - 4.5 [Páginas (6 views)](#45-páginas-6-views)
   - 4.6 [Componentes Reutilizáveis](#46-componentes-reutilizáveis)
   - 4.7 [Design System (Tailwind)](#47-design-system-tailwind)
5. [Infraestrutura e Deploy](#5-infraestrutura-e-deploy)
6. [Diagrama do Banco de Dados](#6-diagrama-do-banco-de-dados)
7. [Fluxos Principais](#7-fluxos-principais)
8. [Observações e Pontos de Evolução](#8-observações-e-pontos-de-evolução)

---

## 1. Visão Geral da Arquitetura

O Synchro MES é um sistema de manufatura industrial completo, projetado para monitorar e controlar a produção em plantas de injeção plástica. A arquitetura segue o padrão de separação clara entre frontend e backend, comunicando-se via API REST e WebSocket.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Navegador)                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  React 18  ·  Vite 6  ·  Tailwind CSS 3  ·  Recharts        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │  Login   │  │Dashboard │  │Produção  │  │Qualidade │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  │  ┌──────────┐  ┌──────────┐                                  │  │
│  │  │ Paradas  │  │Planejam. │   Services: API · Auth · WS     │  │
│  │  └──────────┘  └──────────┘                                  │  │
│  └───────────────────────────┬───────────────────────────────────┘  │
│                              │ HTTP/REST + WebSocket                │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      SERVIDOR (FastAPI)                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  7 Routers · 22 Endpoints · CORS · JWT · WebSocket Manager   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │AuthSvc   │  │DashSvc   │  │OeeSvc    │  │WS Manager│     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  │  ┌─────────────────────────────────────────────────────┐     │  │
│  │  │  SQLAlchemy 2.0 Async + Pydantic v2 Schemas         │     │  │
│  │  └───────────────────────┬─────────────────────────────┘     │  │
│  └──────────────────────────┼────────────────────────────────────┘  │
│                             │                                       │
│                             ▼                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL 16 (produção) / SQLite (desenvolvimento)          │  │
│  │  16 tabelas · 200+ colunas · Seed com ~2.000 registros       │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

**Padrão de comunicação:**
- **REST API** — CRUD de recursos, autenticação, consultas com filtros
- **WebSocket** — Canais por tópico (`dashboard`, `machine:{code}`, `notifications`) para push em tempo real
- **JWT Bearer** — Autenticação stateless em todos os endpoints protegidos

---

## 2. Stack Tecnológica

### Backend (Python 3.12+)

| Tecnologia | Versão | Função |
|------------|--------|--------|
| FastAPI | 0.115.6 | Framework web assíncrono |
| Uvicorn | 0.34.0 | Servidor ASGI |
| SQLAlchemy | 2.0.36 | ORM assíncrono |
| asyncpg | 0.30.0 | Driver PostgreSQL async |
| aiosqlite | 0.20.0 | Driver SQLite async (dev) |
| Alembic | 1.14.1 | Migrações de banco |
| Pydantic | 2.10.4 | Validação e serialização |
| pydantic-settings | 2.7.1 | Configuração via .env |
| python-jose | 3.3.0 | JWT tokens |
| passlib + bcrypt | 1.7.4 / 4.2.1 | Hashing de senhas |
| websockets | 14.1 | Protocolo WebSocket |
| httpx | 0.28.1 | Cliente HTTP (testes) |
| pytest + pytest-asyncio | 8.3.4 / 0.25.0 | Framework de testes |

### Frontend (Node.js 20+)

| Tecnologia | Versão | Função |
|------------|--------|--------|
| React | 18.3.1 | Biblioteca de UI |
| React DOM | 18.3.1 | Renderização DOM |
| React Router DOM | 6.28.0 | Roteamento SPA |
| Vite | 6.0.3 | Build tool + dev server |
| Tailwind CSS | 3.4.17 | Framework CSS utilitário |
| Recharts | 2.14.1 | Gráficos e visualizações |
| Lucide React | 0.468.0 | Biblioteca de ícones |
| Axios | 1.7.9 | Cliente HTTP |
| date-fns | 4.1.0 | Manipulação de datas |
| clsx | 2.1.1 | Composição de classes CSS |

### Infraestrutura

| Tecnologia | Versão | Função |
|------------|--------|--------|
| PostgreSQL | 16 (Alpine) | Banco relacional (produção) |
| SQLite | — | Banco embutido (desenvolvimento) |
| Docker + Compose | 3.9 | Containerização |

---

## 3. Backend — FastAPI

### 3.1 Configuração e Inicialização

#### Arquivo: `backend/app/config.py`

Utiliza `pydantic-settings` para carregar variáveis de ambiente com fallback para defaults. Carrega automaticamente de `.env` (UTF-8).

| Variável | Tipo | Default | Descrição |
|----------|------|---------|-----------|
| `DATABASE_URL` | string | `sqlite+aiosqlite:///./synchro_mes.db` | URI de conexão |
| `SECRET_KEY` | string | `synchro-mes-demo-secret-key-...` | Chave para assinatura JWT |
| `ALGORITHM` | string | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `480` (8h) | Expiração do token |
| `CORS_ORIGINS` | string | `http://localhost:5173,http://localhost:3000` | Origens permitidas (CSV) |
| `APP_TITLE` | string | `Synchro MES` | Título da aplicação |
| `APP_VERSION` | string | `2.0.0` | Versão atual |
| `DEBUG` | bool | `True` | Modo debug (echo SQL) |

#### Arquivo: `backend/app/main.py`

**Ciclo de vida (lifespan):**
1. **Startup:** Cria todas as tabelas (`Base.metadata.create_all`) → Executa seed de dados fictícios (idempotente)
2. **Shutdown:** Encerramento limpo

**Middleware registrado:**
- CORS — origens dinâmicas, credentials habilitados, todos os métodos e headers

**Routers registrados (7):**

| Router | Prefixo | Tag Swagger |
|--------|---------|-------------|
| Auth | `/api/auth` | Auth |
| Machines | `/api/machines` | Machines |
| Production | `/api/production` | Production |
| Downtimes | `/api/downtimes` | Downtimes |
| Quality | `/api/quality` | Quality |
| Dashboard | `/api/dashboard` | Dashboard |
| OEE | `/api/oee` | OEE |

**Endpoints especiais:**
- `GET /health` — Health check (`{status, app, version, ws_connections}`)
- `WS /ws/{channel}` — WebSocket por canal

**Documentação automática:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### 3.2 Banco de Dados

#### Arquivo: `backend/app/database.py`

- **Engine:** `create_async_engine` com detecção automática de driver
- **SQLite:** `check_same_thread=False`, pool `StaticPool` (dev local)
- **PostgreSQL:** pool de 20 conexões, overflow de 10 (produção)
- **Session:** `async_sessionmaker` com `expire_on_commit=False`
- **Base:** `DeclarativeBase` do SQLAlchemy como classe-raiz de todos os models
- **Dependency Injection:** `get_db()` fornece sessão por request com cleanup automático

---

### 3.3 Modelos de Dados (16 tabelas)

O sistema possui 16 tabelas organizadas em 10 arquivos de modelo. Todas usam `id` (Integer, PK, auto-increment) como chave primária e possuem `created_at` com `server_default=func.now()`.

#### 3.3.1 `users` — Usuários e Autenticação

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | Identificador |
| `email` | String(255) | NOT NULL | — | E-mail (unique, index) |
| `name` | String(255) | NOT NULL | — | Nome completo |
| `hashed_password` | String(255) | NOT NULL | — | Hash bcrypt da senha |
| `role` | String(50) | NOT NULL | `"operador"` | Perfil de acesso |
| `is_active` | Boolean | — | `True` | Usuário ativo |
| `custom_claims` | JSON | — | `{}` | Claims customizados (role, permissions[], sector) |
| `sector` | String(100) | — | `"producao"` | Setor do usuário |
| `avatar_initials` | String(5) | — | `"US"` | Iniciais para avatar |
| `created_at` | DateTime(tz) | — | `now()` | Criação |
| `updated_at` | DateTime(tz) | — | on update | Última atualização |
| `last_login` | DateTime(tz) | YES | `None` | Último login |

**Roles:** `admin`, `supervisor`, `operador`, `qualidade`, `pcp`

#### 3.3.2 `machines` — Máquinas (Injetoras)

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | Identificador |
| `code` | String(20) | NOT NULL | — | Código único (ex: INJ-01) |
| `name` | String(100) | NOT NULL | — | Nome descritivo |
| `type` | String(50) | — | `"injetora"` | Tipo de equipamento |
| `tonnage` | Float | YES | — | Tonelagem de fechamento |
| `status` | String(30) | — | `"stopped"` | Estado atual |
| `current_product` | String(100) | YES | — | Produto em produção |
| `current_mold` | String(100) | YES | — | Molde montado |
| `current_operator` | String(100) | YES | — | Operador atual |
| `cycle_time_seconds` | Float | YES | — | Tempo de ciclo atual (s) |
| `cavities` | Integer | — | `1` | Número de cavidades |
| `efficiency` | Float | — | `0.0` | Eficiência atual (%) |
| `location` | String(100) | — | `"Galpão Principal"` | Localização física |
| `metadata_extra` | JSON | — | `{}` | Metadados adicionais |
| `is_active` | Boolean | — | `True` | Máquina ativa |
| `created_at` | DateTime(tz) | — | `now()` | — |
| `updated_at` | DateTime(tz) | — | on update | — |

**Status possíveis:** `running`, `stopped`, `maintenance`, `setup`

#### 3.3.3 `molds` — Ferramentaria (Moldes)

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `code` | String(50) | NOT NULL | — | Código único (ex: MLD-001) |
| `name` | String(150) | NOT NULL | — | Nome descritivo |
| `cavities` | Integer | — | `1` | Número de cavidades |
| `cycle_time_ideal` | Float | YES | — | Tempo de ciclo ideal (s) |
| `product_code` | String(50) | YES | — | Produto produzido |
| `status` | String(30) | — | `"disponivel"` | Estado |
| `total_cycles` | Integer | — | `0` | Total de batidas acumuladas |
| `max_cycles` | Integer | YES | — | Limite de batidas |
| `last_maintenance` | DateTime(tz) | YES | — | Última manutenção |
| `weight_grams` | Float | YES | — | Peso da peça (g) |
| `material_type` | String(100) | YES | — | Tipo de material |
| `created_at` | DateTime(tz) | — | `now()` | — |
| `updated_at` | DateTime(tz) | — | on update | — |

#### 3.3.4 `products` — Cadastro de Produtos

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `code` | String(50) | NOT NULL | — | Código do produto (ex: TFT-28) |
| `name` | String(200) | NOT NULL | — | Nome completo |
| `description` | String(500) | YES | — | Descrição detalhada |
| `weight_grams` | Float | YES | — | Peso em gramas |
| `material` | String(100) | YES | — | Matéria-prima (PP, PET, PEAD...) |
| `color` | String(50) | YES | — | Cor |
| `mold_code` | String(50) | YES | — | Molde associado |
| `cycle_time_ideal` | Float | YES | — | Tempo de ciclo ideal (s) |
| `cavities` | Integer | — | `1` | Cavidades no molde |
| `category` | String(100) | YES | — | Categoria |
| `client` | String(200) | YES | — | Cliente principal |
| `ean` | String(20) | YES | — | Código de barras |
| `is_active` | Boolean | — | `True` | Produto ativo |
| `specs` | JSON | — | `{}` | Especificações técnicas adicionais |
| `created_at` | DateTime(tz) | — | `now()` | — |
| `updated_at` | DateTime(tz) | — | on update | — |

#### 3.3.5 `operators` — Cadastro de Operadores

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `registration` | String(20) | NOT NULL | — | Matrícula (unique) |
| `name` | String(150) | NOT NULL | — | Nome completo |
| `shift` | String(20) | YES | — | Turno (A, B, C) |
| `sector` | String(100) | — | `"injeção"` | Setor |
| `role` | String(50) | — | `"operador"` | Função |
| `skills` | JSON | — | `[]` | Máquinas habilitadas |
| `is_active` | Boolean | — | `True` | Operador ativo |
| `phone` | String(20) | YES | — | Telefone |
| `created_at` | DateTime(tz) | — | `now()` | — |
| `updated_at` | DateTime(tz) | — | on update | — |

#### 3.3.6 `production_orders` — Ordens de Produção

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `order_number` | String(50) | NOT NULL | — | Número da OP (unique, ex: OP-2025-001) |
| `product_code` | String(50) | NOT NULL | — | Código do produto (index) |
| `product_name` | String(200) | NOT NULL | — | Nome do produto |
| `quantity_planned` | Integer | NOT NULL | — | Quantidade planejada |
| `quantity_produced` | Integer | — | `0` | Quantidade produzida |
| `quantity_good` | Integer | — | `0` | Peças boas |
| `quantity_rejected` | Integer | — | `0` | Peças refugadas |
| `status` | String(30) | — | `"planned"` | Status da ordem |
| `priority` | String(20) | — | `"normal"` | Prioridade |
| `machine_code` | String(20) | YES | — | Máquina designada |
| `mold_code` | String(50) | YES | — | Molde designado |
| `operator_name` | String(100) | YES | — | Operador designado |
| `start_date` | DateTime(tz) | YES | — | Início real |
| `end_date` | DateTime(tz) | YES | — | Término real |
| `due_date` | Date | YES | — | Data de entrega |
| `client` | String(200) | YES | — | Cliente da ordem |
| `notes` | String(500) | YES | — | Observações |
| `metadata_extra` | JSON | — | `{}` | Dados adicionais |
| `created_at` | DateTime(tz) | — | `now()` | — |
| `updated_at` | DateTime(tz) | — | on update | — |

**Status:** `planned` · `in_progress` · `completed` · `cancelled`  
**Prioridade:** `low` · `normal` · `high` · `urgent`

#### 3.3.7 `planning` — Planejamento de Produção

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `product_code` | String(50) | NOT NULL | — | Código do produto |
| `product_name` | String(200) | NOT NULL | — | Nome do produto |
| `mold_code` | String(50) | YES | — | Molde |
| `order_number` | String(50) | YES | — | OP vinculada |
| `quantity_planned` | Integer | NOT NULL | — | Quantidade planejada |
| `cycle_time_seconds` | Float | YES | — | Tempo de ciclo (s) |
| `cavities` | Integer | — | `1` | Cavidades |
| `weight_grams` | Float | YES | — | Peso da peça (g) |
| `material` | String(100) | YES | — | Material |
| `color` | String(50) | YES | — | Cor |
| `shift` | String(20) | YES | — | Turno |
| `date` | Date | NOT NULL | — | Data planejada (index) |
| `sequence` | Integer | — | `1` | Sequência na máquina |
| `status` | String(30) | — | `"pendente"` | Estado |
| `operator_name` | String(100) | YES | — | Operador |
| `created_at` | DateTime(tz) | — | `now()` | — |
| `updated_at` | DateTime(tz) | — | on update | — |

**Status:** `pendente` · `em_andamento` · `concluido`

#### 3.3.8 `production_entries` — Lançamentos de Produção

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `product_code` | String(50) | NOT NULL | — | Produto |
| `product_name` | String(200) | YES | — | Nome do produto |
| `order_number` | String(50) | YES | — | OP vinculada (index) |
| `operator_name` | String(100) | YES | — | Operador |
| `shift` | String(20) | YES | — | Turno |
| `quantity_good` | Integer | — | `0` | Peças boas |
| `quantity_rejected` | Integer | — | `0` | Refugo |
| `weight_kg` | Float | YES | — | Peso total (kg) |
| `cycle_time_actual` | Float | YES | — | Ciclo real (s) |
| `cycle_time_ideal` | Float | YES | — | Ciclo ideal (s) |
| `cavities` | Integer | — | `1` | Cavidades |
| `material` | String(100) | YES | — | Material |
| `notes` | String(500) | YES | — | Observações |
| `timestamp` | DateTime(tz) | — | `now()` | Momento do lançamento (index) |
| `created_at` | DateTime(tz) | — | `now()` | — |

#### 3.3.9 `active_downtimes` — Paradas Ativas

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `reason` | String(200) | NOT NULL | — | Motivo da parada |
| `category` | String(50) | NOT NULL | — | Categoria |
| `subcategory` | String(100) | YES | — | Subcategoria |
| `operator_name` | String(100) | YES | — | Operador |
| `shift` | String(20) | YES | — | Turno |
| `start_time` | DateTime(tz) | — | `now()` | Início da parada |
| `notes` | String(500) | YES | — | Observações |
| `is_planned` | Boolean | — | `False` | Parada planejada? |
| `created_at` | DateTime(tz) | — | `now()` | — |

**Categorias:** `mecanica` · `eletrica` · `setup` · `processo` · `qualidade` · `falta_material` · `programada`

#### 3.3.10 `downtime_history` — Histórico de Paradas

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `reason` | String(200) | NOT NULL | — | Motivo |
| `category` | String(50) | NOT NULL | — | Categoria |
| `subcategory` | String(100) | YES | — | Subcategoria |
| `operator_name` | String(100) | YES | — | Operador |
| `shift` | String(20) | YES | — | Turno |
| `start_time` | DateTime(tz) | NOT NULL | — | Início |
| `end_time` | DateTime(tz) | NOT NULL | — | Fim |
| `duration_minutes` | Float | NOT NULL | — | Duração calculada (min) |
| `is_planned` | Boolean | — | `False` | Planejada? |
| `notes` | String(500) | YES | — | Observações |
| `resolved_by` | String(100) | YES | — | Resolvido por |
| `created_at` | DateTime(tz) | — | `now()` | — |

#### 3.3.11 `quality_measurements` — Medições de Qualidade

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `product_code` | String(50) | NOT NULL | — | Produto (index) |
| `order_number` | String(50) | YES | — | OP vinculada |
| `operator_name` | String(100) | YES | — | Operador |
| `inspector` | String(100) | YES | — | Inspetor |
| `dimension_name` | String(100) | YES | — | Nome da dimensão |
| `nominal_value` | Float | YES | — | Valor nominal |
| `measured_value` | Float | YES | — | Valor medido |
| `tolerance_upper` | Float | YES | — | Tolerância superior |
| `tolerance_lower` | Float | YES | — | Tolerância inferior |
| `unit` | String(20) | — | `"mm"` | Unidade de medida |
| `is_approved` | Boolean | — | `True` | Aprovado? |
| `defect_type` | String(100) | YES | — | Tipo de defeito |
| `defect_severity` | String(20) | YES | — | Severidade |
| `sample_size` | Integer | — | `1` | Tamanho da amostra |
| `notes` | String(500) | YES | — | Observações |
| `timestamp` | DateTime(tz) | — | `now()` | Momento (index) |
| `created_at` | DateTime(tz) | — | `now()` | — |

**Tipos de defeito:** `rebarba` · `bolha` · `mancha` · `dimensional` · `deformação`  
**Severidade:** `minor` · `major` · `critical`

#### 3.3.12 `rework_entries` — Registros de Retrabalho

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `product_code` | String(50) | NOT NULL | — | Produto |
| `order_number` | String(50) | YES | — | OP vinculada |
| `quantity` | Integer | NOT NULL | — | Quantidade retrabalhada |
| `reason` | String(200) | NOT NULL | — | Motivo do retrabalho |
| `action_taken` | String(300) | YES | — | Ação corretiva |
| `operator_name` | String(100) | YES | — | Operador |
| `shift` | String(20) | YES | — | Turno |
| `status` | String(30) | — | `"pendente"` | Estado |
| `timestamp` | DateTime(tz) | — | `now()` | — |
| `created_at` | DateTime(tz) | — | `now()` | — |

**Status:** `pendente` · `em_andamento` · `concluido` · `descartado`

#### 3.3.13 `spc_data` — Controle Estatístico de Processo

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `product_code` | String(50) | NOT NULL | — | Produto |
| `parameter_name` | String(100) | NOT NULL | — | Parâmetro monitorado |
| `value` | Float | NOT NULL | — | Valor medido |
| `ucl` | Float | YES | — | Limite superior de controle |
| `lcl` | Float | YES | — | Limite inferior de controle |
| `target` | Float | YES | — | Valor-alvo |
| `is_out_of_control` | Boolean | — | `False` | Fora de controle? |
| `subgroup` | Integer | YES | — | Subgrupo |
| `sample_number` | Integer | YES | — | Número da amostra |
| `timestamp` | DateTime(tz) | — | `now()` | Momento (index) |

#### 3.3.14 `oee_history` — Histórico de OEE

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `machine_code` | String(20) | NOT NULL | — | Máquina (index) |
| `date` | Date | NOT NULL | — | Data (index) |
| `shift` | String(20) | YES | — | Turno |
| `availability` | Float | NOT NULL | `0.0` | Disponibilidade (%) |
| `performance` | Float | NOT NULL | `0.0` | Performance (%) |
| `quality_rate` | Float | NOT NULL | `0.0` | Qualidade (%) |
| `oee` | Float | NOT NULL | `0.0` | OEE calculado (%) |
| `planned_time_minutes` | Float | — | `480.0` | Tempo planejado (min) |
| `running_time_minutes` | Float | — | `0.0` | Tempo em produção (min) |
| `downtime_minutes` | Float | — | `0.0` | Tempo de parada (min) |
| `total_produced` | Integer | — | `0` | Total produzido |
| `good_produced` | Integer | — | `0` | Peças boas |
| `rejected` | Integer | — | `0` | Refugo |
| `ideal_cycle_seconds` | Float | YES | — | Ciclo ideal (s) |
| `actual_cycle_seconds` | Float | YES | — | Ciclo real (s) |
| `created_at` | DateTime(tz) | — | `now()` | — |

**Fórmula OEE:** `OEE = (Disponibilidade × Performance × Qualidade) / 10.000`

#### 3.3.15 `notifications` — Notificações

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `title` | String(200) | NOT NULL | — | Título |
| `message` | String(500) | NOT NULL | — | Mensagem |
| `type` | String(30) | — | `"info"` | Tipo visual |
| `target_role` | String(50) | YES | — | Perfil-alvo |
| `target_user_id` | Integer | YES | — | Usuário-alvo |
| `is_read` | Boolean | — | `False` | Lida? |
| `machine_code` | String(20) | YES | — | Máquina relacionada |
| `link` | String(300) | YES | — | Link de ação |
| `created_at` | DateTime(tz) | — | `now()` | — |

**Tipos:** `info` · `warning` · `error` · `success`

#### 3.3.16 `system_logs` — Log de Auditoria

| Coluna | Tipo | Null | Default | Descrição |
|--------|------|------|---------|-----------|
| `id` | Integer | PK | auto | — |
| `action` | String(100) | NOT NULL | — | Ação realizada (index) |
| `user_email` | String(255) | YES | — | E-mail do usuário |
| `user_name` | String(150) | YES | — | Nome do usuário |
| `details` | JSON | — | `{}` | Detalhes adicionais |
| `ip_address` | String(45) | YES | — | IP de origem |
| `user_agent` | String(300) | YES | — | User-Agent |
| `module` | String(50) | YES | — | Módulo do sistema |
| `timestamp` | DateTime(tz) | — | `now()` | Momento (index) |

---

### 3.4 Schemas Pydantic

Os schemas Pydantic v2 são organizados em 7 módulos e servem para validação de entrada, serialização de saída e documentação automática da API (Swagger/ReDoc).

#### Schemas de Autenticação (`schemas/user.py`)

| Schema | Uso | Campos principais |
|--------|-----|-------------------|
| `LoginRequest` | Request body do login | `email: EmailStr`, `password: str` |
| `Token` | Response do login | `access_token`, `token_type="bearer"`, `user: UserRead` |
| `TokenData` | Payload decodificado do JWT | `email`, `role` |
| `UserBase` | Base compartilhada | `email: EmailStr`, `name` (2-255 chars), `role` (enum validado), `sector` |
| `UserCreate` | Cadastro de usuário | extends UserBase + `password` (4-128 chars) |
| `UserUpdate` | Atualização parcial | `name?`, `role?`, `sector?`, `is_active?` |
| `UserRead` | Response de leitura | extends UserBase + `id`, `is_active`, `avatar_initials`, `custom_claims`, `created_at`, `last_login` |

#### Schemas de Máquinas (`schemas/machine.py`)

| Schema | Uso | Campos |
|--------|-----|--------|
| `MachineRead` | Response | Todos os campos de `machines` exceto `metadata_extra`, `created_at`, `updated_at` |
| `MachineUpdate` | PATCH body | `status?`, `current_product?`, `current_mold?`, `current_operator?`, `cycle_time_seconds?`, `efficiency?` |
| `MoldRead` | Response | Campos principais de `molds` |

#### Schemas de Produção (`schemas/production.py`)

| Schema | Uso | Validações |
|--------|-----|------------|
| `ProductionOrderCreate` | POST body | `quantity_planned > 0` |
| `ProductionOrderUpdate` | PATCH body | Todos opcionais |
| `ProductionOrderRead` | Response | `from_attributes=True` |
| `PlanningCreate` | POST body | `quantity_planned > 0` |
| `PlanningRead` | Response | `from_attributes=True` |
| `ProductionEntryCreate` | POST body | `quantity_good >= 0`, `quantity_rejected >= 0` |
| `ProductionEntryRead` | Response | `from_attributes=True` |

#### Schemas de Paradas (`schemas/downtime.py`)

| Schema | Uso |
|--------|-----|
| `ActiveDowntimeCreate` | POST body — iniciar parada |
| `ActiveDowntimeRead` | Response — parada ativa |
| `DowntimeHistoryRead` | Response — parada encerrada |

#### Schemas de Qualidade (`schemas/quality.py`)

| Schema | Uso |
|--------|-----|
| `QualityMeasurementCreate` | POST body — registrar medição |
| `QualityMeasurementRead` | Response — leitura de medição |

#### Schemas de OEE (`schemas/oee.py`)

| Schema | Uso |
|--------|-----|
| `OeeHistoryRead` | Response — registro histórico de OEE |
| `OeeSummary` | Response — resumo OEE com trend |

#### Schemas de Dashboard (`schemas/dashboard.py`)

| Schema | Uso |
|--------|-----|
| `MachineCardData` | Card individual de máquina no dashboard |
| `DashboardSummary` | Resumo completo: KPIs + lista de `MachineCardData` |

---

### 3.5 Serviços (Business Logic)

#### `AuthService` (`services/auth_service.py`)

Responsável por toda a lógica de autenticação e autorização.

| Método | Tipo | Descrição |
|--------|------|-----------|
| `hash_password(password)` | Static | Gera hash bcrypt da senha |
| `verify_password(plain, hashed)` | Static | Verifica senha contra hash |
| `create_access_token(data, expires_delta?)` | Static | Cria JWT com payload e expiração (default 480 min) |
| `decode_token(token)` | Static | Decodifica JWT; levanta HTTP 401 se inválido/expirado |
| `authenticate_user(db, email, password)` | Static/Async | Busca user, verifica senha, atualiza `last_login`; retorna `User` ou `None` |
| `get_current_user(token, db)` | Dependency | Extrai user do token JWT; levanta 401 se inativo/inexistente |
| `require_role(*roles)` | Factory | Retorna dependency que verifica role do user; levanta 403 se não autorizado |

**Tecnologias internas:** `CryptContext(schemes=["bcrypt"])`, `OAuth2PasswordBearer(tokenUrl="/api/auth/login")`

#### `DashboardService` (`services/dashboard_service.py`)

| Método | Descrição |
|--------|-----------|
| `get_summary(db)` | Agrega dados de múltiplas tabelas: contagem de máquinas por status, SUM produção do dia, AVG OEE do dia, COUNT ordens ativas/planejadas, GROUP BY motivos de parada para top reason, monta `MachineCardData` para cada máquina com produção individual + parada ativa |

#### `OeeService` (`services/oee_service.py`)

| Método | Descrição |
|--------|-----------|
| `get_history(db, machine_code?, start_date?, end_date?, limit=30)` | Registros OEE com filtros, ordenados por data desc |
| `get_summary_by_machine(db, machine_code, target_date?)` | OEE de uma máquina para data; retorna zeros se sem registro |
| `get_factory_average(db, target_date?)` | Média OEE da fábrica (AVG availability, performance, quality, oee) + count máquinas |
| `calculate_oee(planned, running, total, good, ideal_cycle)` | Cálculo puro — `Availability = running/planned × 100`, `Performance = produced/max_possible × 100`, `Quality = good/total × 100`, `OEE = A × P × Q / 10.000` |

#### `ConnectionManager` (`services/websocket_manager.py`)

| Método | Descrição |
|--------|-----------|
| `connect(websocket, channel)` | Aceita conexão, adiciona ao set do canal |
| `disconnect(websocket, channel)` | Remove conexão; limpa canal se vazio |
| `broadcast(channel, data)` | Envia JSON para todos os clientes do canal; remove conexões mortas |
| `broadcast_all(data)` | Envia para todos os canais |
| `active_connections_count` | Property — soma de conexões em todos os canais |

**Estrutura interna:** `Dict[str, Set[WebSocket]]`

---

### 3.6 Routers — API REST (22 endpoints)

#### Auth — `/api/auth`

| Método | Endpoint | Auth | Body/Params | Response | Descrição |
|--------|----------|------|-------------|----------|-----------|
| `POST` | `/login` | — | `LoginRequest` | `Token` | Autentica e retorna JWT + dados do user |
| `GET` | `/me` | JWT | — | `UserRead` | Dados do usuário autenticado |
| `POST` | `/register` | Admin only | `UserCreate` | `UserRead` (201) | Cadastra novo usuário (verifica duplicata 409) |

#### Dashboard — `/api/dashboard`

| Método | Endpoint | Auth | Response | Descrição |
|--------|----------|------|----------|-----------|
| `GET` | `/summary` | JWT | `DashboardSummary` | Resumo completo com KPIs + cards de todas as máquinas |

#### Machines — `/api/machines`

| Método | Endpoint | Auth | Body/Params | Response | Descrição |
|--------|----------|------|-------------|----------|-----------|
| `GET` | `/` | JWT | — | `list[MachineRead]` | Lista máquinas ativas, ordenadas por code |
| `GET` | `/{code}` | JWT | path: code | `MachineRead` | Busca máquina por código (404) |
| `PATCH` | `/{code}` | Admin/Supervisor | `MachineUpdate` | `MachineRead` | Atualiza campos da máquina |
| `GET` | `/molds/all` | JWT | — | `list[MoldRead]` | Lista todos os moldes |

#### Production — `/api/production`

| Método | Endpoint | Auth | Body/Params | Response | Descrição |
|--------|----------|------|-------------|----------|-----------|
| `GET` | `/orders` | JWT | `status?`, `limit=50` (max 200) | `list[ProductionOrderRead]` | Ordens desc por created_at |
| `POST` | `/orders` | Admin/Supervisor/PCP | `ProductionOrderCreate` | `ProductionOrderRead` (201) | Cria ordem |
| `PATCH` | `/orders/{id}` | Admin/Supervisor/Operador | `ProductionOrderUpdate` | `ProductionOrderRead` | Atualiza ordem |
| `GET` | `/planning` | JWT | `machine_code?`, `target_date?` | `list[PlanningRead]` | Planejamento por data/máquina |
| `POST` | `/planning` | Admin/Supervisor/PCP | `PlanningCreate` | `PlanningRead` (201) | Cria item de planejamento |
| `GET` | `/entries` | JWT | `machine_code?`, `order_number?`, `limit=100` (max 500) | `list[ProductionEntryRead]` | Lançamentos desc por timestamp |
| `POST` | `/entries` | Admin/Supervisor/Operador | `ProductionEntryCreate` | `ProductionEntryRead` (201) | Registra lançamento |

#### Downtimes — `/api/downtimes`

| Método | Endpoint | Auth | Body/Params | Response | Descrição |
|--------|----------|------|-------------|----------|-----------|
| `GET` | `/active` | JWT | `machine_code?` | `list[ActiveDowntimeRead]` | Paradas ativas |
| `POST` | `/start` | Admin/Supervisor/Operador | `ActiveDowntimeCreate` | `ActiveDowntimeRead` (201) | Inicia parada; altera status máquina → `stopped` |
| `POST` | `/stop/{id}` | Admin/Supervisor/Operador | path: id, `resolved_by?` | `DowntimeHistoryRead` | Encerra parada → calcula duração, move para history, restaura máquina → `running` |
| `GET` | `/history` | JWT | `machine_code?`, `limit=100` (max 500) | `list[DowntimeHistoryRead]` | Histórico de paradas |

#### Quality — `/api/quality`

| Método | Endpoint | Auth | Body/Params | Response | Descrição |
|--------|----------|------|-------------|----------|-----------|
| `GET` | `/measurements` | JWT | `machine_code?`, `product_code?`, `approved?`, `limit=100` (max 500) | `list[QualityMeasurementRead]` | Medições de qualidade |
| `POST` | `/measurements` | Admin/Supervisor/Qualidade/Operador | `QualityMeasurementCreate` | `QualityMeasurementRead` (201) | Registra medição |

#### OEE — `/api/oee`

| Método | Endpoint | Auth | Body/Params | Response | Descrição |
|--------|----------|------|-------------|----------|-----------|
| `GET` | `/history` | JWT | `machine_code?`, `start_date?`, `end_date?`, `limit=30` (max 365) | `list[OeeHistoryRead]` | Histórico OEE |
| `GET` | `/machine/{code}` | JWT | path: code, `target_date?` | `OeeSummary` | OEE de uma máquina |
| `GET` | `/factory` | JWT | `target_date?` | `dict` | Média OEE da fábrica |

---

### 3.7 WebSocket — Tempo Real

**Endpoint:** `ws://localhost:8000/ws/{channel}`

**Canais suportados:**
- `dashboard` — atualizações gerais do dashboard
- `machine:{code}` — eventos de uma máquina específica (ex: `machine:INJ-01`)
- `notifications` — notificações push

**Protocolo:**
1. Cliente conecta ao canal via URL
2. Servidor aceita e registra no `ConnectionManager`
3. Servidor pode broadcast JSON para todos os clientes de um canal
4. Na desconexão, a conexão é removida automaticamente

---

### 3.8 Autenticação e Autorização (RBAC)

**Fluxo de autenticação:**
1. Cliente envia `POST /api/auth/login` com email + senha
2. Servidor busca user no banco, verifica bcrypt hash
3. Retorna JWT contendo `{sub: email, role: "admin", exp: timestamp}`
4. Cliente armazena token no `localStorage`
5. Todas as requests subsequentes enviam `Authorization: Bearer <token>`

**Hierarquia de permissões:**

| Perfil | Permissões |
|--------|------------|
| `admin` | dashboard, producao, qualidade, paradas, planejamento, relatorios, admin, usuarios, configuracoes |
| `supervisor` | dashboard, producao, qualidade, paradas, planejamento, relatorios |
| `operador` | dashboard, producao, paradas |
| `qualidade` | dashboard, qualidade, relatorios |
| `pcp` | dashboard, planejamento, relatorios |

**Dependencies FastAPI:**
- `get_current_user` — Extrai e valida o user do token JWT (HTTP 401)
- `require_role("admin", "supervisor")` — Verifica se o role do user está na lista (HTTP 403)

---

### 3.9 Seed de Dados Fictícios

O seed é executado automaticamente no startup e é **idempotente** (verifica se já existem registros na tabela `users`).

| Entidade | Quantidade | Detalhes |
|----------|------------|----------|
| Usuários | 5 | admin, supervisor, operador, qualidade, pcp — senha `demo1234` |
| Máquinas | 10 | INJ-01 a INJ-10; tonelagem 150-650t; 7 running, 2 stopped, 1 maintenance |
| Produtos | 12 | TFT-28, FR-500, PF-22G, CV-110, BR-45, PL-80, CX-200, TB-12, RG-30, FD-60, GR-25, TP-500 |
| Moldes | 6 | MLD-001 a MLD-006; cavidades 1-8 |
| Operadores | 15 | OP-001 a OP-015; turnos A/B/C |
| Ordens de Produção | 12 | OP-2025-001 a 012; 4 in_progress, 5 planned, 3 completed |
| Planejamento | 70 | 7 dias × 10 máquinas |
| Lançamentos | ~1.200 | 30 dias × 10 máquinas × 2-6/dia |
| Paradas Ativas | 2 | INJ-05 (setup 45min), INJ-09 (falta material 120min) |
| Hist. Paradas | ~165 | 30 dias × 3-8/dia; 12 motivos; 7 categorias |
| Histórico OEE | 300 | 30 dias × 10 máquinas |
| Medições Qualidade | ~150 | 15 dias × 5-15/dia |
| Notificações | 4 | 1 warning, 1 error, 1 success, 1 info |

**Total estimado: ~2.000 registros**

Todos os nomes de produtos, clientes, operadores e empresas são **fictícios**.

---

### 3.10 Migrações com Alembic

- **Configuração:** `alembic.ini` + `alembic/env.py`
- **Engine:** Usa `async_engine_from_config` com `pool.NullPool`
- **Metadata:** Importa todos os models para registro automático em `Base.metadata`
- **Modos:** Suporta geração offline (SQL puro) e online (conexão direta)

**Comandos:**
```bash
# Criar nova migração
alembic revision --autogenerate -m "descricao"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1
```

---

## 4. Frontend — React

### 4.1 Roteamento e Proteção de Rotas

**Arquivo:** `src/App.jsx`

| Rota | Componente | Protegida | Descrição |
|------|-----------|-----------|-----------|
| `/login` | `<Login />` | Não | Tela de autenticação |
| `/` | `<Dashboard />` | Sim | Dashboard principal |
| `/production` | `<Production />` | Sim | Ordens e lançamentos |
| `/quality` | `<Quality />` | Sim | Medições de qualidade |
| `/downtimes` | `<Downtimes />` | Sim | Paradas ativas e histórico |
| `/planning` | `<Planning />` | Sim | Planejamento diário |
| `*` | Redirect → `/` | — | Catch-all |

**`ProtectedRoute`**: Wrapper que verifica `user` do `useAuth()`. Se não autenticado, redireciona para `/login`.

**Estrutura:** `BrowserRouter > AuthProvider > Routes`

---

### 4.2 Contexto de Autenticação

**Arquivo:** `src/context/AuthContext.jsx`

Provê via React Context:

| Valor | Tipo | Descrição |
|-------|------|-----------|
| `user` | object \| null | Dados do usuário logado |
| `loading` | boolean | Carregamento inicial |
| `login(email, password)` | async function | Autentica e armazena no state + localStorage |
| `logout()` | function | Limpa sessão e localStorage |
| `hasPermission(perm)` | function | Verifica se `user.custom_claims.permissions` contém a permissão |

---

### 4.3 Services (API, Auth, WebSocket)

#### `services/api.js` — Cliente HTTP

- **Base URL:** `/api` (proxy Vite → backend)
- **Request interceptor:** Adiciona `Authorization: Bearer <token>` do localStorage
- **Response interceptor:** Status 401 → remove token, redireciona para `/login`

#### `services/auth.js` — Serviço de Autenticação

| Método | Descrição |
|--------|-----------|
| `login(email, password)` | POST `/auth/login`, armazena token + user no localStorage |
| `logout()` | Remove token e user do localStorage |
| `getStoredUser()` | Recupera user do localStorage |
| `getToken()` | Retorna token do localStorage |
| `isAuthenticated()` | Retorna `!!token` |
| `getProfile()` | GET `/auth/me` |

#### `services/websocket.js` — WebSocket Client

| Método | Descrição |
|--------|-----------|
| `connect(channel="dashboard")` | Conecta ao canal WS (auto-detect http/https → ws/wss) |
| `on(type, callback)` | Registra listener por tipo de mensagem (ou `*` wildcard) |
| `disconnect()` | Fecha conexão e limpa timer de reconexão |

**Reconexão automática** em 5 segundos após desconexão.

---

### 4.4 Custom Hooks

**Arquivo:** `src/hooks/index.js`

| Hook | Assinatura | Retorno | Descrição |
|------|-----------|---------|-----------|
| `useApi` | `(url, {autoFetch?, params?})` | `{data, loading, error, refetch, setData}` | GET com gerenciamento de estado |
| `usePolling` | `(callback, intervalMs=30000)` | void | Executa callback imediatamente + a cada N ms |
| `useDebounce` | `(value, delay=300)` | `debouncedValue` | Debounce de valores |

---

### 4.5 Páginas (6 views)

#### Login (`pages/Login.jsx`)

- Layout de tela cheia com gradiente purple/indigo
- Formulário com email e senha (toggle visibilidade)
- 5 botões de credenciais demo (preenchem automaticamente)
- Erro exibido em alert vermelho
- Ícones: `Factory`, `Lock`, `Mail`, `Eye`, `EyeOff`

#### Dashboard (`pages/Dashboard.jsx`)

- **Polling:** `GET /dashboard/summary` a cada 30 segundos
- **KPI Cards** (grid 2→3→6 colunas): Máquinas Rodando, OEE Médio, Produzido Hoje, Refugo %, Ordens Ativas, Paradas Ativas
- **OEE Gauge:** Componente `<OeeGauge>` com arco 270°
- **Machine Grid:** Grid responsivo com card por máquina

#### Production (`pages/Production.jsx`)

- **Tabs:** "Ordens" | "Lançamentos"
- **Ordens:** Tabela com Ordem, Produto, Máquina, Qtd Plan., Produzido, Refugo, Status, Cliente
- **Lançamentos:** Tabela com Máquina, Produto, Operador, Turno, Boas, Refugo, Ciclo, Data/Hora
- **APIs:** `GET /production/orders`, `GET /production/entries?limit=50`

#### Quality (`pages/Quality.jsx`)

- **Filtros:** Todas | Aprovadas | Reprovadas
- **Tabela:** Máquina, Produto, Dimensão, Nominal, Medido, Tol. Inf., Tol. Sup., Resultado (OK/NOK), Inspetor
- **API:** `GET /quality/measurements?limit=50&approved=true|false`

#### Downtimes (`pages/Downtimes.jsx`)

- **Tabs:** "Ativas (count)" | "Histórico"
- **Ativas:** Cards com borda vermelha, tempo decorrido calculado, categoria colorida
- **Histórico:** Tabela com Máquina, Motivo, Categoria, Duração, Operador, Início, Fim
- **Cores por categoria:** mecânica=red, elétrica=orange, setup=blue, processo=purple, qualidade=yellow, falta material=gray, programada=emerald

#### Planning (`pages/Planning.jsx`)

- **Date picker:** Input com navegação ±1 dia
- **Agrupamento:** Por `machine_code` com reduce
- **Grid 1→2→3 colunas:** Card por máquina com items de planejamento internos
- **API:** `GET /production/planning?target_date={date}`

---

### 4.6 Componentes Reutilizáveis

#### Layout (`components/layout/`)

| Componente | Props | Descrição |
|------------|-------|-----------|
| `Layout` | — | Container principal: Sidebar + Header + `<Outlet>`. State: `sidebarOpen`. |
| `Header` | `onMenuClick` | Barra superior: menu mobile, título "Industry 4.0", avatar com iniciais, nome, role, botão logout |
| `Sidebar` | `isOpen`, `onClose` | Navegação lateral (w-64, fixed z-40). 5 itens com ícones, filtrados por `hasPermission`. Footer: "Synchro MES v2.0" |

**Itens do menu:**

| Path | Label | Ícone | Permissão |
|------|-------|-------|-----------|
| `/` | Dashboard | `LayoutDashboard` | `dashboard` |
| `/production` | Produção | `Package` | `producao` |
| `/quality` | Qualidade | `ShieldCheck` | `qualidade` |
| `/downtimes` | Paradas | `AlertOctagon` | `paradas` |
| `/planning` | Planejamento | `CalendarDays` | `planejamento` |

#### Dashboard (`components/dashboard/`)

| Componente | Props | Descrição |
|------------|-------|-----------|
| `OeeGauge` | `value: number` | SVG gauge 270° (raio 70, strokeWidth 12). Faixas: ≥85% emerald "World Class", ≥75% primary "Bom", ≥60% amber "Regular", <60% red "Crítico" |
| `MachineGrid` | `machines: MachineCardData[]` | Grid responsivo (1→2→3→5 cols). Cards com: borda lateral por status, código (mono bold), dot animado, produto/operador, métricas OEE/boas/refugo, alerta de parada |

#### Comuns (`components/common/`)

| Componente | Props | Descrição |
|------------|-------|-----------|
| `LoadingSpinner` | `size: "sm"|"md"|"lg"`, `className?` | Ícone `Loader2` com animação spin |
| `PageLoading` | — | Spinner centralizado em h-64 |
| `EmptyState` | `icon?`, `title`, `description?`, `action?` | Card de estado vazio com ícone + texto + ação |
| `StatusBadge` | `status: string` | Badge colorido. Mapeia 11 status (running→Produzindo, stopped→Parada, etc.) |

---

### 4.7 Design System (Tailwind)

#### Paleta de cores customizada

| Token | Hex | Uso |
|-------|-----|-----|
| `primary-50` a `primary-900` | #eef2ff → #312e81 | Cor principal (indigo/violet) |
| `primary-500` (base) | #667eea | Botões, links, sidebar ativo |
| `success` | #10b981 | Status running, aprovado |
| `warning` | #f59e0b | Alertas, setup, manutenção |
| `danger` | #ef4444 | Erros, paradas, rejeitado |
| `industrial.dark` | #1e293b | Fundo sidebar |
| `industrial.gray` | #64748b | Textos secundários |

#### Tipografia

| Token | Família |
|-------|---------|
| `font-sans` | Inter, system-ui, sans-serif |
| `font-mono` | JetBrains Mono, monospace |

#### Classes de componentes CSS

| Classe | Estilos |
|--------|---------|
| `.card` | `bg-white rounded-xl shadow-sm border border-gray-200 p-6` |
| `.btn-primary` | `bg-primary-500 hover:bg-primary-600 text-white font-medium px-4 py-2 rounded-lg transition-colors` |
| `.btn-secondary` | `bg-gray-100 hover:bg-gray-200 text-gray-700 ...` |
| `.btn-danger` | `bg-red-500 hover:bg-red-600 text-white ...` |
| `.input-field` | `w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ...` |
| `.badge` | `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium` |
| `.badge-running` | `badge bg-emerald-100 text-emerald-800` |
| `.badge-stopped` | `badge bg-red-100 text-red-800` |
| `.badge-maintenance` | `badge bg-amber-100 text-amber-800` |
| `.badge-setup` | `badge bg-blue-100 text-blue-800` |

---

## 5. Infraestrutura e Deploy

### Docker Compose (`docker-compose.yml`)

| Serviço | Imagem | Porta | Descrição |
|---------|--------|-------|-----------|
| `db` | postgres:16-alpine | 5432 | PostgreSQL; DB=synchro_mes; healthcheck pg_isready |
| `backend` | Build `./backend` | 8000 | FastAPI + Uvicorn; depende de db (healthy) |
| `frontend` | Build `./frontend` | 5173 | Vite dev server; depende de backend |

**Volumes:** `pgdata` (dados PostgreSQL persistentes), `app/` e `src/` (hot-reload)

### Backend Dockerfile

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt . && pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Frontend Dockerfile

```dockerfile
FROM node:20-alpine
COPY package.json package-lock.json* . && npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Proxy Vite (`vite.config.js`)

| Path | Destino | Tipo |
|------|---------|------|
| `/api` | `http://localhost:8000` | HTTP (changeOrigin) |
| `/ws` | `ws://localhost:8000` | WebSocket |

### Modos de Execução

| Modo | Banco | Comando |
|------|-------|---------|
| **Desenvolvimento local** | SQLite (automático) | `uvicorn app.main:app --reload` + `npm run dev` |
| **Docker Compose** | PostgreSQL 16 | `docker compose up --build` |
| **Produção** | PostgreSQL externo | Definir `DATABASE_URL` via .env com asyncpg |

---

## 6. Diagrama do Banco de Dados

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│     users        │     │    machines       │     │     products     │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK)          │     │ id (PK)          │     │ id (PK)          │
│ email (UNIQUE)   │     │ code (UNIQUE)    │     │ code (UNIQUE)    │
│ name             │     │ name             │     │ name             │
│ hashed_password  │     │ type             │     │ weight_grams     │
│ role             │     │ tonnage          │     │ material         │
│ is_active        │     │ status           │     │ color            │
│ custom_claims    │     │ current_product ─┼──>  │ cycle_time_ideal │
│ sector           │     │ current_operator │     │ cavities         │
│ avatar_initials  │     │ cycle_time_secs  │     │ client           │
│ last_login       │     │ cavities         │     │ specs (JSON)     │
└──────────────────┘     │ efficiency       │     └──────────────────┘
                         │ metadata (JSON)  │
                         └───────┬──────────┘
                                 │ machine_code (string ref)
            ┌────────────────┬───┴───────────┬──────────────────┐
            ▼                ▼               ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ production_orders│ │active_downtime│ │ oee_history  │ │quality_measur│
├──────────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ order_number(UQ) │ │ machine_code │ │ machine_code │ │ machine_code │
│ product_code     │ │ reason       │ │ date         │ │ product_code │
│ quantity_planned │ │ category     │ │ availability │ │ nominal_value│
│ quantity_produced│ │ operator_name│ │ performance  │ │ measured_val │
│ status           │ │ start_time   │ │ quality_rate │ │ is_approved  │
│ priority         │ │ is_planned   │ │ oee          │ │ defect_type  │
│ machine_code     │ └──────────────┘ │ total_produc.│ │ inspector    │
│ client           │                  │ good_produced│ └──────────────┘
│ due_date         │ ┌──────────────┐ └──────────────┘
└──────────────────┘ │downtime_hist.│       ┌──────────────────┐
                     ├──────────────┤       │    operators     │
┌──────────────────┐ │ machine_code │       ├──────────────────┤
│    planning      │ │ reason       │       │ registration(UQ) │
├──────────────────┤ │ category     │       │ name             │
│ machine_code     │ │ start_time   │       │ shift            │
│ product_code     │ │ end_time     │       │ skills (JSON)    │
│ quantity_planned │ │ duration_min │       └──────────────────┘
│ date             │ │ resolved_by  │
│ shift            │ └──────────────┘  ┌──────────────────┐
│ sequence         │                   │   molds          │
│ status           │  ┌──────────────┐ ├──────────────────┤
└──────────────────┘  │ prod_entries │ │ code (UNIQUE)    │
                      ├──────────────┤ │ name             │
┌──────────────────┐  │ machine_code │ │ cavities         │
│  notifications   │  │ product_code │ │ cycle_time_ideal │
├──────────────────┤  │ order_number │ │ total_cycles     │
│ title            │  │ operator_name│ │ product_code     │
│ message          │  │ quantity_good│ └──────────────────┘
│ type             │  │ qty_rejected │
│ target_role      │  │ cycle_actual │ ┌──────────────────┐
│ is_read          │  │ timestamp    │ │   system_logs    │
│ machine_code     │  └──────────────┘ ├──────────────────┤
└──────────────────┘                   │ action           │
                     ┌──────────────┐  │ user_email       │
                     │  spc_data    │  │ details (JSON)   │
                     ├──────────────┤  │ ip_address       │
                     │ machine_code │  │ timestamp        │
                     │ product_code │  └──────────────────┘
                     │ parameter    │
                     │ value        │  ┌──────────────────┐
                     │ ucl / lcl    │  │  rework_entries  │
                     │ is_out_ctrl  │  ├──────────────────┤
                     └──────────────┘  │ machine_code     │
                                       │ product_code     │
                                       │ quantity         │
                                       │ reason           │
                                       │ status           │
                                       └──────────────────┘
```

> **Nota:** As relações entre tabelas são via `machine_code`, `product_code` e `order_number` (strings), sem Foreign Keys definidas no ORM. Isso simplifica o esquema para demo mas não valida integridade referencial no banco.

---

## 7. Fluxos Principais

### 7.1 Fluxo de Autenticação

```
[Login Page] ──POST /api/auth/login──> [AuthService]
                                          │
                                  busca user por email
                                  verifica bcrypt hash
                                  gera JWT (8h exp)
                                  atualiza last_login
                                          │
            <── {access_token, user} ─────┘
                     │
         salva token + user no localStorage
         Axios interceptor adiciona Bearer em toda request
         AuthContext provê user/login/logout/hasPermission
```

### 7.2 Fluxo de Produção

```
[Operador] ──(seleciona máquina + produto)──> POST /api/production/entries
                                                  │
                                           cria ProductionEntry
                                           (machine_code, product_code,
                                            quantity_good, quantity_rejected,
                                            operator_name, shift, cycle_time)
                                                  │
[Dashboard] ──GET /api/dashboard/summary──> [DashboardService]
                                                  │
                                       SUM entries do dia por máquina
                                       AVG OEE do dia
                                       COUNT ordens ativas
                                       Monta MachineCardData[]
```

### 7.3 Fluxo de Paradas (Downtime)

```
1. Máquina para
   POST /api/downtimes/start {machine_code, reason, category}
   ├── cria ActiveDowntime
   └── seta machine.status = "stopped"

2. Máquina volta
   POST /api/downtimes/stop/{id}
   ├── calcula duration_minutes = (now - start_time)
   ├── cria DowntimeHistory com duração
   ├── deleta ActiveDowntime
   └── seta machine.status = "running" (se sem outras paradas)
```

### 7.4 Cálculo de OEE

```
OEE = Disponibilidade × Performance × Qualidade

Disponibilidade (%) = (Tempo em Produção / Tempo Planejado) × 100
    Tempo Planejado = 480 min (turno de 8h)
    Tempo em Produção = Planejado - Paradas

Performance (%) = (Produção Real / Produção Máxima Teórica) × 100
    Produção Máxima = Tempo em Produção / Ciclo Ideal × Cavidades

Qualidade (%) = (Peças Boas / Total Produzido) × 100

OEE (%) = (A × P × Q) / 10.000

Faixas de referência:
    ≥ 85%  → World Class (verde)
    ≥ 75%  → Bom (azul)
    ≥ 60%  → Regular (amarelo)
    < 60%  → Crítico (vermelho)
```

---

## 8. Observações e Pontos de Evolução

### Arquitetura Atual

1. **Sem Foreign Keys no ORM** — Relações entre tabelas usam strings (`machine_code`, `product_code`), sem `ForeignKey()` ou `relationship()` do SQLAlchemy. Funcional para demo, mas sem integridade referencial.

2. **Models sem endpoints** — 6 tabelas existem no banco mas não possuem routers/endpoints próprios: `products`, `operators`, `rework_entries`, `spc_data`, `notifications`, `system_logs`.

3. **WebSocket configurado mas não utilizado** — O backend suporta broadcast por canal e o frontend tem `WebSocketService`, porém o Dashboard usa polling (`setInterval` 30s) ao invés de WebSocket.

### Pontos de Evolução Recomendados

4. **CRUD completo para Products e Operators** — Criar routers para gestão de cadastros
5. **Gráficos com Recharts** — A biblioteca está instalada mas ainda não é utilizada; adicionar gráficos de tendência OEE, Pareto de paradas, histogramas de qualidade
6. **Dashboard WS** — Migrar o polling do Dashboard para WebSocket nativo
7. **Testes automatizados** — pytest e pytest-asyncio estão instalados; criar testes para services e routers
8. **PWA** — Adicionar manifest.json e service worker para experiência mobile
9. **Cartas SPC** — A tabela `spc_data` existe; implementar cartas de controle X-barra/R no frontend
10. **Sistema de Notificações** — A tabela e WebSocket channel existem; implementar push notifications no frontend

---

*Documento gerado para fins de documentação técnica e portfolio — Synchro MES v2.0*
