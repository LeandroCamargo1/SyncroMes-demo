# Synchro MES — Referência da API

> Documentação completa de todos os endpoints REST e WebSocket do backend.

**Base URL**: `http://localhost:8000`  
**Swagger UI**: `http://localhost:8000/docs`  
**ReDoc**: `http://localhost:8000/redoc`

---

## Autenticação

- **JWT** com algoritmo HS256
- Token válido por **480 minutos** (8 horas)
- Header: `Authorization: Bearer <token>`
- **Dev mode**: `DEV_BYPASS_AUTH=True` desativa autenticação (bypass automático com usuário dev)

---

## Health Check

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/health` | Status da aplicação, versão, conexões WebSocket ativas |

---

## 1. Auth — `/api/auth`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| POST | `/api/auth/login` | Autenticação por email/senha | `LoginRequest` | `Token` |
| GET | `/api/auth/me` | Dados do usuário autenticado | — | `UserRead` |
| POST | `/api/auth/register` | Cadastro de usuário (admin) | `UserCreate` | `UserRead` |

### Exemplo — Login

```json
// POST /api/auth/login
{
  "email": "admin@synchromes.com",
  "password": "admin123"
}

// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 2. Dashboard — `/api/dashboard`

| Método | Path | Descrição | Response |
|--------|------|-----------|----------|
| GET | `/api/dashboard/summary` | Resumo completo com todas as máquinas | `DashboardSummary` |

Retorna: contadores (máquinas ativas, paradas, em manutenção), OEE da fábrica, produção do dia, grid de máquinas com status em tempo real.

---

## 3. Machines — `/api/machines`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/machines/` | Lista todas as máquinas ativas | — | `list[MachineRead]` |
| GET | `/api/machines/{code}` | Busca máquina por código | — | `MachineRead` |
| PATCH | `/api/machines/{code}` | Atualiza dados (admin/supervisor) | `MachineUpdate` | `MachineRead` |
| GET | `/api/machines/molds/all` | Lista todos os moldes | — | `list[MoldRead]` |

**Eventos**: Atualização de status dispara evento via `EventDispatcher` e notificação via WebSocket.

---

## 4. Production — `/api/production`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/production/orders` | Lista ordens (filtro: `status`) | — | `list[ProductionOrderRead]` |
| POST | `/api/production/orders` | Cria ordem de produção | `ProductionOrderCreate` | `ProductionOrderRead` |
| PATCH | `/api/production/orders/{order_id}` | Atualiza ordem | `ProductionOrderUpdate` | `ProductionOrderRead` |
| GET | `/api/production/planning` | Lista planejamento (filtro: `machine_id`, `date`) | — | `list[PlanningRead]` |
| POST | `/api/production/planning` | Cria planejamento | `PlanningCreate` | `PlanningRead` |
| GET | `/api/production/entries` | Lista lançamentos (filtro: `machine_id`, `order_id`) | — | `list[ProductionEntryRead]` |
| POST | `/api/production/entries` | Registra produção | `ProductionEntryCreate` | `ProductionEntryRead` |

### Exemplo — Criar Ordem

```json
// POST /api/production/orders
{
  "order_number": "OP-2025-0001",
  "product_id": 1,
  "product_name": "Tampa Flip-Top 28mm",
  "quantity_planned": 5000,
  "priority": "high",
  "machine_id": 1,
  "due_date": "2025-02-15"
}
```

---

## 5. Downtimes — `/api/downtimes`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/downtimes/active` | Paradas ativas (filtro: `machine_id`) | — | `list[ActiveDowntimeRead]` |
| POST | `/api/downtimes/start` | Inicia parada | `ActiveDowntimeCreate` | `ActiveDowntimeRead` |
| POST | `/api/downtimes/stop/{downtime_id}` | Encerra parada (query: `resolved_by`) | — | `DowntimeHistoryRead` |
| GET | `/api/downtimes/history` | Histórico de paradas (filtro: `machine_id`) | — | `list[DowntimeHistoryRead]` |

**Comportamento**: Iniciar parada altera status da máquina para `stopped`. Encerrar restaura para `running` se não há outras paradas ativas.

---

## 6. Quality — `/api/quality`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/quality/measurements` | Lista medições (filtros: `machine_id`, `product_id`, `is_approved`) | — | `list[QualityMeasurementRead]` |
| POST | `/api/quality/measurements` | Cria medição dimensional | `QualityMeasurementCreate` | `QualityMeasurementRead` |

**Eventos**: Medição reprovada com defeito dispara notificação automática.

---

## 7. Quality Lots — `/api/quality-lots`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/quality-lots/lots` | Lista lotes (filtro: `status`) | — | `list[QualityLotRead]` |
| POST | `/api/quality-lots/lots` | Cria lote de quarentena/triagem | `QualityLotCreate` | `QualityLotRead` |
| PATCH | `/api/quality-lots/lots/{lot_id}` | Atualiza lote | `QualityLotUpdate` | `QualityLotRead` |
| GET | `/api/quality-lots/lots/summary` | Resumo por status | — | `dict` |
| GET | `/api/quality-lots/reports` | Relatório de aprovação | — | `dict` |

---

## 8. OEE — `/api/oee`

| Método | Path | Descrição | Response |
|--------|------|-----------|----------|
| GET | `/api/oee/history` | Histórico OEE (filtros: `machine_id`, `date_from`, `date_to`) | `list[OeeHistoryRead]` |
| GET | `/api/oee/machine/{machine_code}` | OEE resumido de uma máquina | `OeeSummary` |
| GET | `/api/oee/factory` | OEE médio da fábrica | `dict` |

### Cálculo OEE

```
OEE = Disponibilidade × Performance × Qualidade

Disponibilidade = (Tempo Planejado - Paradas) / Tempo Planejado
Performance = (Ciclo Ideal × Peças Produzidas) / Tempo Disponível
Qualidade = Peças Boas / Total Produzido
```

---

## 9. Losses — `/api/losses`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/losses/` | Lista perdas (filtros: `machine_id`, `category`) | — | `list[LossEntryRead]` |
| POST | `/api/losses/` | Registra perda | `LossEntryCreate` | `LossEntryRead` |
| GET | `/api/losses/summary` | Resumo por categoria | — | `dict` |

**Categorias**: `refugo`, `rebarba`, `dimensional`, `cor`, `contaminacao`

---

## 10. Setup — `/api/setup`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/setup/` | Lista setups (filtros: `machine_id`, `status`) | — | `list[SetupEntryRead]` |
| POST | `/api/setup/` | Inicia setup | `SetupEntryCreate` | `SetupEntryRead` |
| PATCH | `/api/setup/{setup_id}/finish` | Finaliza setup (calcula duração) | `SetupEntryFinish` | `SetupEntryRead` |

---

## 11. PMP — `/api/pmp`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/pmp/` | Lista registros PMP (filtros: `type`, `machine_id`) | — | `list[PmpEntryRead]` |
| POST | `/api/pmp/` | Cria registro (moído/borra/sucata) | `PmpEntryCreate` | `PmpEntryRead` |
| GET | `/api/pmp/summary` | Resumo por tipo (total kg) | — | `list[dict]` |

---

## 12. Tooling — `/api/tooling`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/tooling/molds` | Lista moldes com detalhes | — | `list[dict]` |
| PATCH | `/api/tooling/molds/{mold_code}` | Atualiza molde | `MoldUpdate` | `dict` |
| GET | `/api/tooling/maintenance` | Lista manutenções de moldes (filtros: `mold_id`, `status`) | — | `list[MoldMaintenanceRead]` |
| POST | `/api/tooling/maintenance` | Cria manutenção de molde | `MoldMaintenanceCreate` | `MoldMaintenanceRead` |
| PATCH | `/api/tooling/maintenance/{maint_id}/finish` | Finaliza manutenção | `MoldMaintenanceFinish` | `MoldMaintenanceRead` |
| GET | `/api/tooling/alerts` | Alertas: ciclos próximos do limite + pendências | — | `list[dict]` |

---

## 13. PCP — `/api/pcp`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/pcp/messages` | Lista mensagens (filtros: `is_active`, `priority`) | — | `list[PcpMessageRead]` |
| POST | `/api/pcp/messages` | Cria mensagem PCP | `PcpMessageCreate` | `PcpMessageRead` |
| PATCH | `/api/pcp/messages/{msg_id}/deactivate` | Desativa mensagem | — | `dict` |
| GET | `/api/pcp/queue` | Fila de produção priorizada | — | `list[dict]` |

---

## 14. Leadership — `/api/leadership`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/leadership/schedule` | Escala de operadores (filtros: `shift`, `date`) | — | `list[OperatorScheduleRead]` |
| POST | `/api/leadership/schedule` | Criar registro de escala | `OperatorScheduleCreate` | `OperatorScheduleRead` |
| GET | `/api/leadership/absenteeism` | Absenteísmo (filtro: `reason`) | — | `list[AbsenteeismRead]` |
| POST | `/api/leadership/absenteeism` | Registrar absenteísmo | `AbsenteeismCreate` | `AbsenteeismRead` |
| GET | `/api/leadership/summary` | Resumo: escalados, ausências, justificadas | — | `dict` |

---

## 15. History — `/api/history`

| Método | Path | Descrição | Response |
|--------|------|-----------|----------|
| GET | `/api/history/` | Log de auditoria (admin only). Filtros: `action`, `user_email`, `entity_type` | `list[SystemLogRead]` |

---

## 16. Admin Data — `/api/admin`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/admin/products` | Lista produtos | — | `list[dict]` |
| POST | `/api/admin/products` | Cria produto (admin) | `dict` | `dict` |
| GET | `/api/admin/operators` | Lista operadores | — | `list[dict]` |
| POST | `/api/admin/operators` | Cria operador (admin) | `dict` | `dict` |
| GET | `/api/admin/machines-admin` | Lista máquinas (admin) | — | `list[dict]` |
| GET | `/api/admin/molds-admin` | Lista moldes (admin) | — | `list[dict]` |

---

## 17. Hierarchy (ISA-95) — `/api/hierarchy`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/hierarchy/sites` | Lista sites | — | `list[SiteRead]` |
| POST | `/api/hierarchy/sites` | Cria site (admin) | `SiteCreate` | `SiteRead` |
| GET | `/api/hierarchy/areas` | Lista áreas (filtro: `site_id`) | — | `list[AreaRead]` |
| POST | `/api/hierarchy/areas` | Cria área | `AreaCreate` | `AreaRead` |
| GET | `/api/hierarchy/work-centers` | Lista work centers (filtro: `area_id`) | — | `list[WorkCenterRead]` |
| POST | `/api/hierarchy/work-centers` | Cria work center | `WorkCenterCreate` | `WorkCenterRead` |
| GET | `/api/hierarchy/tree` | Árvore hierárquica completa | — | `list[dict]` |

### Exemplo — Árvore ISA-95

```json
// GET /api/hierarchy/tree
[
  {
    "id": 1,
    "code": "SITE-SP",
    "name": "Planta São Paulo",
    "areas": [
      {
        "id": 1,
        "code": "AREA-INJ",
        "name": "Setor de Injeção",
        "work_centers": [
          {
            "id": 1,
            "code": "WC-INJ-A",
            "name": "Célula Injeção A",
            "machines": [
              { "id": 1, "code": "INJ-01", "name": "Injetora 01", "status": "running" }
            ]
          }
        ]
      }
    ]
  }
]
```

---

## 18. Materials — `/api/materials`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/materials/` | Lista materiais (filtro: `type`) | — | `list[MaterialRead]` |
| POST | `/api/materials/` | Cria material | `MaterialCreate` | `MaterialRead` |
| PATCH | `/api/materials/{code}` | Atualiza material | `MaterialUpdate` | `MaterialRead` |
| GET | `/api/materials/alerts` | Materiais com estoque abaixo do mínimo | — | `list[dict]` |
| GET | `/api/materials/bom/{product_code}` | BOM de um produto | — | `list[BomLineRead]` |
| POST | `/api/materials/bom` | Cria linha na BOM | `BomLineCreate` | `BomLineRead` |
| GET | `/api/materials/movements` | Movimentações de estoque (filtro: `material_id`) | — | `list[InventoryMovementRead]` |
| POST | `/api/materials/movements` | Registra movimentação (atualiza estoque) | `InventoryMovementCreate` | `InventoryMovementRead` |

---

## 19. Maintenance — `/api/maintenance`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/maintenance/` | Lista manutenções (filtros: `machine_id`, `status`) | — | `list[MachineMaintenanceRead]` |
| POST | `/api/maintenance/` | Cria manutenção (preventiva/corretiva) | `MachineMaintenanceCreate` | `MachineMaintenanceRead` |
| PATCH | `/api/maintenance/{maint_id}/finish` | Finaliza manutenção | `MachineMaintenanceFinish` | `MachineMaintenanceRead` |
| GET | `/api/maintenance/pending` | Manutenções pendentes/em andamento | — | `list[dict]` |

---

## 20. KPIs — `/api/kpis`

| Método | Path | Descrição | Response |
|--------|------|-----------|----------|
| GET | `/api/kpis/advanced` | KPIs avançados ISO-22400: TEEP, NEE, MTBF, MTTR, Setup Ratio | `AdvancedKpiResponse` |
| GET | `/api/kpis/process-segments` | Lista segmentos de processo | `list[ProcessSegmentRead]` |
| POST | `/api/kpis/process-segments` | Cria segmento de processo | `ProcessSegmentCreate` → `ProcessSegmentRead` |

### KPIs Avançados

| KPI | Descrição |
|-----|-----------|
| **TEEP** | Total Effective Equipment Performance |
| **NEE** | Net Equipment Effectiveness |
| **MTBF** | Mean Time Between Failures |
| **MTTR** | Mean Time To Repair |
| **Setup Ratio** | % tempo de setup / tempo total |
| **Scrap Rate** | % de refugo |
| **FPY** | First Pass Yield |

---

## 21. Notifications — `/api/notifications`

| Método | Path | Descrição | Body | Response |
|--------|------|-----------|------|----------|
| GET | `/api/notifications/` | Lista notificações (filtro: `unread_only`) | — | `list[NotificationRead]` |
| GET | `/api/notifications/count` | Contagem de não lidas | — | `{ unread: number }` |
| PATCH | `/api/notifications/read` | Marca como lidas por IDs | `NotificationMarkRead` | `{ marked: number }` |
| PATCH | `/api/notifications/read-all` | Marca todas como lidas | — | `{ marked: number }` |

---

## WebSocket

```
ws://localhost:8000/ws/{channel}
```

### Canais Disponíveis

| Canal | Descrição |
|-------|-----------|
| `dashboard` | Atualizações do dashboard (máquinas, OEE) |
| `production` | Eventos de produção |
| `quality` | Alertas de qualidade |
| `notifications` | Notificações em tempo real |
| `machine:{code}` | Eventos de uma máquina específica (ex: `machine:INJ-01`) |

### Exemplo — Conectar ao WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Atualização:', data);
};
```

---

## Códigos de Resposta

| Código | Descrição |
|--------|-----------|
| `200` | Sucesso |
| `201` | Criado com sucesso |
| `400` | Dados inválidos |
| `401` | Não autenticado |
| `403` | Sem permissão |
| `404` | Recurso não encontrado |
| `422` | Erro de validação (Pydantic) |
| `500` | Erro interno do servidor |

---

## Resumo

| Método | Quantidade |
|--------|-----------|
| GET | 42 |
| POST | 21 |
| PATCH | 10 |
| WebSocket | 1 |
| **Total** | **74** |
