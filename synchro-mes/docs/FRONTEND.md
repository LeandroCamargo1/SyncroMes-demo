# Synchro MES — Arquitetura Frontend

> Documentação da arquitetura, componentes, hooks, serviços e sistema de tipos do frontend.

---

## Stack

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| React | 18.3.1 | UI framework |
| TypeScript | 5.9.3 | Tipagem estática |
| Vite | 6.0.3 | Build tool + HMR |
| Tailwind CSS | 3.4.17 | Utility-first CSS |
| Recharts | 2.14.1 | Biblioteca de gráficos |
| Firebase | 12.10.0 | Firestore cloud database |
| Axios | 1.7.9 | HTTP client |
| React Router | 6.28.0 | Roteamento SPA |
| Lucide React | 0.468.0 | Ícones SVG |
| date-fns | 4.1.0 | Manipulação de datas |
| clsx | 2.1.1 | Concatenação condicional de classes |

---

## Estrutura de Diretórios

```
src/
├── App.tsx                 # Rotas e layout principal
├── main.tsx                # Entry point React
├── index.css               # Tailwind + design system
├── lib/
│   └── firebase.ts         # Inicialização Firebase SDK
├── components/
│   ├── charts/
│   │   └── index.tsx       # 9 componentes de gráficos Recharts
│   ├── common/             # Componentes reutilizáveis
│   ├── dashboard/
│   │   ├── MachineGrid.tsx # Grid de máquinas com status
│   │   └── OeeGauge.tsx    # Gauge de OEE (SVG animado)
│   ├── layout/
│   │   ├── Header.tsx      # Header com notificações
│   │   ├── Sidebar.tsx     # Navegação lateral
│   │   ├── Layout.tsx      # Layout wrapper
│   │   └── NotificationCenter.tsx  # Painel de notificações
│   ├── production/         # Componentes de produção
│   └── quality/            # Componentes de qualidade
├── context/
│   └── AuthContext.tsx      # Contexto de autenticação
├── hooks/
│   └── index.ts            # useApi, usePolling, useDebounce
├── pages/                  # 19 páginas
├── services/
│   ├── api.ts              # Axios instance + interceptors
│   ├── auth.ts             # Serviço de autenticação
│   ├── firestore.ts        # CRUD genérico Firestore
│   ├── websocket.ts        # WebSocket manager
│   └── ml.ts               # Client ML predictions
└── types/                  # 16 arquivos de definição TypeScript
```

---

## Páginas (19)

| Página | Rota | Descrição |
|--------|------|-----------|
| `Dashboard` | `/` | Dashboard principal com OEE gauge, grid de máquinas, gráficos |
| `DashboardTV` | `/tv` | Dashboard fullscreen para monitores de chão de fábrica |
| `Production` | `/production` | Ordens de produção com gráficos output vs target |
| `Orders` | `/orders` | Gestão de ordens (CRUD) |
| `Launch` | `/launch` | Lançamento rápido de produção por operador |
| `Planning` | `/planning` | Sequenciamento de produção por máquina |
| `Analysis` | `/analysis` | 7 abas: OEE Trend, Pareto, Donuts, Comparativo, SPC, Área, Bars |
| `Quality` | `/quality` | Medições dimensionais com carta SPC e donut |
| `Downtimes` | `/downtimes` | Paradas ativas e histórico com gráficos Pareto |
| `Pmp` | `/pmp` | Controle de moído, borra, sucata |
| `Tooling` | `/tooling` | Gestão de moldes e manutenções |
| `MachineSetup` | `/setup` | Registro de trocas (molde, cor, material) |
| `Pcp` | `/pcp` | Mensagens PCP e fila de produção |
| `Leadership` | `/leadership` | Escala de operadores e absenteísmo |
| `Reports` | `/reports` | Relatórios com gráficos inline |
| `History` | `/history` | Log de auditoria do sistema |
| `AdminData` | `/admin` | Cadastro de produtos, operadores, máquinas |
| `Login` | `/login` | Tela de login |
| `SeedFirestore` | `/seed` | Popular Firestore com dados fictícios |

---

## Componentes de Gráficos (9)

Todos em `components/charts/index.tsx`, usando Recharts com paleta Siemens Opcenter.

| Componente | Tipo Recharts | Descrição |
|-----------|---------------|-----------|
| `OeeTrendChart` | `LineChart` | 3 linhas (A×P×Q) + linha de meta 85% |
| `ProductionBarChart` | `BarChart` | Barras empilhadas: boas vs refugo por máquina |
| `DonutChart` | `PieChart` | Donut com valor central e legenda |
| `ParetoChart` | `ComposedChart` | Barras + linha cumulativa 80% |
| `SpcChart` | `LineChart` | Carta SPC com UCL/LCL/Nominal (ReferenceLine) |
| `ProductionAreaChart` | `AreaChart` | Áreas empilhadas de produção |
| `HorizontalBarChart` | `BarChart` | Ranking horizontal com linha de meta |
| `Sparkline` | `LineChart` | Mini gráfico inline sem eixos |
| `OutputVsTargetChart` | `BarChart` | Planejado vs produzido por máquina |

### Paleta de Cores

```typescript
const COLORS = {
  primary: '#5c7cfa',
  emerald: '#10b981',
  amber: '#f59e0b',
  red: '#ef4444',
  blue: '#3b82f6',
  violet: '#8b5cf6',
  cyan: '#06b6d4',
  pink: '#ec4899'
};
```

---

## Hooks (3)

### `useApi<T>(url, options?)`

Hook genérico para chamadas API com tratamento de loading, erro e refetch.

```typescript
const { data, loading, error, refetch } = useApi<Machine[]>('/api/machines/');
```

### `usePolling(callback, intervalMs)`

Executa callback periodicamente (padrão 30s) para atualizar dados em tempo real.

```typescript
usePolling(() => refetch(), 30000);
```

### `useDebounce<T>(value, delay)`

Debounce de valor para inputs de busca/filtro.

```typescript
const debouncedSearch = useDebounce(searchTerm, 300);
```

---

## Serviços

### `api.ts` — Axios Instance

```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 15000
});

// Interceptor: adiciona JWT automaticamente
// Interceptor: redireciona para /login em 401
```

### `auth.ts` — Autenticação

```typescript
authService.login(email, password) → Token
authService.getMe() → User
authService.register(data) → User
```

### `firestore.ts` — CRUD Firestore

```typescript
const service = createService<Product>('products');
await service.getAll();
await service.getById(id);
await service.create(data);
await service.update(id, data);
await service.remove(id);
```

### `websocket.ts` — WebSocket Manager

```typescript
const ws = new WebSocketManager('ws://localhost:8000/ws/dashboard');
ws.connect();
ws.onMessage((data) => { ... });
ws.disconnect();
```

### `ml.ts` — ML Predictions

```typescript
mlService.predictOee(machineData) → OeePrediction
mlService.predictDowntime(machineData) → DowntimePrediction
mlService.predictQuality(processData) → QualityPrediction
mlService.predictMaintenance(machineData) → MaintenancePrediction
```

---

## Contexto — `AuthContext`

Provê estado de autenticação global via `React.createContext`.

```typescript
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}
```

### Permissões (DEV_USER)

Em modo dev, o usuário bypass tem 16 permissões:

```
dashboard:view, production:edit, quality:edit, setup:edit,
pmp:edit, downtimes:edit, losses:edit, tooling:edit,
pcp:edit, leadership:edit, reports:view, admin:edit,
history:view, analysis:view, machines:edit, planning:edit
```

---

## Sistema de Tipos (16 arquivos)

| Arquivo | Tipos Principais |
|---------|------------------|
| `auth.ts` | `User`, `Token`, `LoginRequest` |
| `common.ts` | `ApiResponse<T>`, `PaginatedResponse<T>` |
| `dashboard.ts` | `DashboardSummary`, `MachineCard` |
| `downtime.ts` | `ActiveDowntime`, `DowntimeHistory`, `DowntimeCategory` |
| `leadership.ts` | `OperatorSchedule`, `AbsenteeismEntry` |
| `loss.ts` | `LossEntry`, `LossCategory`, `LossSummary` |
| `machine.ts` | `Machine`, `Mold`, `MachineStatus` |
| `ml.ts` | `OeePrediction`, `DowntimePrediction`, `QualityPrediction` |
| `oee.ts` | `OeeHistory`, `OeeSummary` |
| `pcp.ts` | `PcpMessage`, `ProductionQueue` |
| `pmp.ts` | `PmpEntry`, `PmpType`, `PmpSummary` |
| `production.ts` | `ProductionOrder`, `Planning`, `ProductionEntry` |
| `quality.ts` | `QualityMeasurement`, `SpcData` |
| `setup.ts` | `SetupEntry`, `SetupType` |
| `tooling.ts` | `MoldMaintenance`, `MoldAlert` |
| `index.ts` | Re-exporta todos os tipos |

---

## Design System

### CSS Custom Classes (`index.css`)

```css
.card          /* Cartão com borda, sombra, border-radius */
.btn-primary   /* Botão azul primary (#5c7cfa) */
.btn-outline   /* Botão com borda, sem preenchimento */
.tab-bar       /* Barra de abas com indicador ativo */
.table-modern  /* Tabela com header cinza, hover, zebra */
```

### Fontes

- **Sans-serif**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono (Google Fonts)

### Breakpoints

| Breakpoint | Tela | Uso |
|-----------|------|-----|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop |
| `xl` | 1280px | Desktop wide |
| `2xl` | 1536px | TV/Monitor |

---

## Build

```bash
npm run dev       # Servidor de desenvolvimento (HMR)
npm run build     # Build de produção
npm run preview   # Preview do build
```

### Build Output

```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js     # Bundle JS (~800KB gzip ~250KB)
│   └── index-[hash].css    # Styles (~50KB gzip ~10KB)
```
