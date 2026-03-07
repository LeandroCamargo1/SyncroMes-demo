# Changelog — Synchro MES

Todas as mudanças notáveis do projeto são documentadas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [2.1.0] — 2025-01-20

### Adicionado — Firebase & Firestore

- Integração completa com Firebase SDK 12.10.0
- Serviço genérico `createService<T>()` para CRUD no Firestore
- 32 coleções Firestore com dados realistas de fábrica
- Página `/seed` para popular Firestore com ~1500 documentos
- Arquivo `lib/firebase.ts` para inicialização do SDK
- Variáveis de ambiente `VITE_FIREBASE_*` para configuração

---

## [2.0.0] — 2025-01-18

### Adicionado — Gráficos Siemens Opcenter

- 9 componentes de gráficos com Recharts 2.14.1:
  - `OeeTrendChart` — Tendência OEE (Disponibilidade × Performance × Qualidade)
  - `ProductionBarChart` — Boas vs refugo por máquina
  - `DonutChart` — Distribuição com valor central
  - `ParetoChart` — Barras + linha cumulativa 80%
  - `SpcChart` — Carta SPC com limites de controle
  - `ProductionAreaChart` — Áreas empilhadas
  - `HorizontalBarChart` — Ranking horizontal com meta
  - `Sparkline` — Mini gráfico inline
  - `OutputVsTargetChart` — Planejado vs produzido
- Gráficos integrados em 8 páginas: Dashboard, Production, Quality, Downtimes, Analysis, Reports, Pmp, Leadership

---

## [1.3.0] — 2025-01-15

### Adicionado — Phase 3: Real-Time & Notifications

- `EventDispatcher` — sistema de eventos assíncrono para desacoplar lógica
- `NotificationCenter` — painel de notificações no header com badge
- WebSocket com canais: `dashboard`, `production`, `quality`, `notifications`, `machine:{code}`
- Notificações automáticas: parada iniciada, qualidade reprovada, estoque baixo
- Correção de N+1 queries no Dashboard com eager loading
- Auth interceptor no Axios com redirect para `/login` em 401
- Endpoint `GET /api/notifications/count` para contagem de não-lidas
- Endpoint `PATCH /api/notifications/read-all` para marcar tudo como lido

---

## [1.2.0] — 2025-01-12

### Adicionado — Phase 2: ISA-95, Materiais & KPIs

- **Hierarquia ISA-95**: Site → Area → WorkCenter → Machine
  - 3 modelos: `Site`, `Area`, `WorkCenter`
  - Router `/api/hierarchy` com 7 endpoints + árvore hierárquica
- **Materiais & BOM**:
  - 3 modelos: `Material`, `BomLine`, `InventoryMovement`
  - Router `/api/materials` com 8 endpoints
  - Controle de estoque com alertas de mínimo
  - Bill of Materials (BOM) por produto
- **Manutenção de Máquinas**:
  - Modelo `MachineMaintenance` com prioridade e custo
  - Router `/api/maintenance` com 4 endpoints
- **KPIs Avançados (ISO-22400)**:
  - TEEP, NEE, MTBF, MTTR, Setup Ratio, FPY, Scrap Rate
  - `ProcessSegment` para parâmetros de injeção por produto
  - Router `/api/kpis` com 3 endpoints

### Alterado

- Modelos `Machine` e `Product` receberam novos campos e relações
- Total de endpoints: 72 → 80+

---

## [1.1.0] — 2025-01-08

### Adicionado — Phase 1: Fundação Robusta

- **Foreign Keys** em todos os modelos (antes eram string references)
- **24 Enums tipados** para status, categorias, prioridades
- **Audit Middleware** automático — registra todas as operações em `system_logs`
- **FK Resolver** — resolve códigos em IDs automaticamente nos endpoints
- **Seed completo** reescrito com dados realistas e relacionamentos corretos
- **TypeScript migration**: Todo o frontend convertido de JSX para TSX
  - 16 arquivos de tipos em `src/types/`
  - Todos os componentes, hooks, serviços e páginas tipados
- Verificação de 18 endpoints com `curl`

---

## [1.0.0] — 2025-01-01

### Adicionado — Release Inicial

- **Backend FastAPI** com 16 routers e ~50 endpoints
- **Frontend React** com 15 páginas
- **Modelos**: Machine, Mold, Product, Operator, User, ProductionOrder, Planning, ProductionEntry, ActiveDowntime, DowntimeHistory, QualityMeasurement, OeeHistory, LossEntry, SetupEntry, PmpEntry, QualityLot, MoldMaintenance, PcpMessage, OperatorSchedule, AbsenteeismEntry, Notification, SystemLog
- **Autenticação JWT** com roles (admin, supervisor, operador, qualidade, pcp)
- **Dashboard** com OEE gauge e grid de máquinas
- **Dashboard TV** para monitores de chão de fábrica
- **Paradas** com início/parada e histórico
- **Qualidade** com medições dimensionais
- **Lotes** com quarentena e triagem
- **OEE** com cálculo por máquina e fábrica
- **Setup** com registro de trocas e tempo
- **PMP** para moído, borra e sucata
- **Ferramental** com manutenção de moldes e alertas de vida útil
- **PCP** com mensagens e fila de produção
- **Liderança** com escala e absenteísmo
- **Admin** com cadastro de produtos, operadores, máquinas
- **Docker Compose** com PostgreSQL, Backend, Frontend
- **SQLite** como banco de desenvolvimento
- **Seed** com dados iniciais para teste
