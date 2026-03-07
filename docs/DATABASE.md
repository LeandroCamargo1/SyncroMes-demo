# Synchro MES — Schema do Banco de Dados

> Documentação completa de todos os modelos, enums e relacionamentos.

**ORM**: SQLAlchemy 2.0 (async)  
**Dev**: SQLite + aiosqlite  
**Produção**: PostgreSQL 16  
**Migrações**: Alembic 1.14.1

---

## Base Abstrata

Todos os modelos herdam de `Base` com as colunas:

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `id` | Integer | primary_key, auto_increment, index |
| `created_at` | DateTime(tz=True) | default=utcnow, not null |
| `updated_at` | DateTime(tz=True) | default=utcnow, onupdate=utcnow |

---

## Enums (24)

### Recursos e Status

| Enum | Valores |
|------|---------|
| **MachineStatus** | `running`, `stopped`, `maintenance`, `setup` |
| **MoldStatus** | `disponivel`, `em_uso`, `manutencao` |
| **UserRole** | `admin`, `supervisor`, `operador`, `qualidade`, `pcp` |

### Produção

| Enum | Valores |
|------|---------|
| **OrderStatus** | `planned`, `in_progress`, `completed`, `cancelled` |
| **OrderPriority** | `low`, `normal`, `high`, `urgent` |
| **PlanningStatus** | `pendente`, `em_andamento`, `concluido` |
| **Shift** | `A`, `B`, `C` |

### Paradas e Qualidade

| Enum | Valores |
|------|---------|
| **DowntimeCategory** | `mecanica`, `eletrica`, `setup`, `processo`, `qualidade`, `falta_material`, `programada` |
| **QualityLotStatus** | `quarentena`, `em_triagem`, `concluida` |
| **ReworkStatus** | `pendente`, `em_andamento`, `concluido`, `descartado` |
| **DefectSeverity** | `minor`, `major`, `critical` |
| **LossCategory** | `refugo`, `rebarba`, `dimensional`, `cor`, `contaminacao` |

### Setup e PMP

| Enum | Valores |
|------|---------|
| **SetupType** | `troca_molde`, `troca_cor`, `troca_material`, `ajuste` |
| **SetupStatus** | `em_andamento`, `concluido` |
| **PmpType** | `moido`, `borra`, `sucata` |
| **PmpDestination** | `reprocesso`, `descarte`, `venda` |

### Manutenção

| Enum | Valores |
|------|---------|
| **MaintenanceType** | `preventiva`, `corretiva`, `limpeza` |
| **MaintenanceStatus** | `pendente`, `em_andamento`, `concluida` |
| **MaintenancePriority** | `baixa`, `media`, `alta`, `critica` |

### Materiais

| Enum | Valores |
|------|---------|
| **MaterialType** | `resina`, `masterbatch`, `aditivo`, `embalagem`, `inserto` |
| **MaterialUnit** | `kg`, `g`, `un`, `m`, `l` |
| **InventoryMovementType** | `entrada`, `saida`, `ajuste`, `consumo`, `devolucao` |

### Outros

| Enum | Valores |
|------|---------|
| **NotificationType** | `info`, `warning`, `error`, `success` |
| **PcpMessageType** | `info`, `warning`, `urgent` |
| **AbsenteeismReason** | `falta`, `atestado`, `atraso`, `ferias`, `folga` |

---

## Modelos — Hierarquia ISA-95

### Site — `sites`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `code` | String(20) | unique, not null, index |
| `name` | String(200) | not null |
| `address` | String(500) | nullable |
| `city` | String(100) | nullable |
| `state` | String(50) | nullable |
| `timezone` | String(50) | default="America/Sao_Paulo" |
| `is_active` | Boolean | default=True |

→ `areas` (1:N)

### Area — `areas`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `code` | String(20) | unique, not null, index |
| `name` | String(200) | not null |
| `description` | String(500) | nullable |
| `site_id` | Integer | FK → sites.id, not null |
| `is_active` | Boolean | default=True |

→ `work_centers` (1:N)

### WorkCenter — `work_centers`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `code` | String(20) | unique, not null, index |
| `name` | String(200) | not null |
| `description` | String(500) | nullable |
| `area_id` | Integer | FK → areas.id, not null |
| `capacity` | Integer | default=1 |
| `is_active` | Boolean | default=True |

→ `machines` (1:N)

---

## Modelos — Recursos

### Machine — `machines`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `code` | String(20) | unique, not null, index |
| `name` | String(100) | not null |
| `type` | String(50) | default="injetora" |
| `tonnage` | Float | nullable |
| `status` | Enum(MachineStatus) | default=stopped |
| `current_product` | String(100) | nullable |
| `current_mold` | String(100) | nullable |
| `current_operator` | String(100) | nullable |
| `cycle_time_seconds` | Float | nullable |
| `cavities` | Integer | default=1 |
| `efficiency` | Float | default=0.0 |
| `location` | String(100) | default="Galpão Principal" |
| `work_center_id` | Integer | FK → work_centers.id, nullable |
| `metadata_extra` | JSON | default={} |
| `is_active` | Boolean | default=True |

Relacionamentos: production_orders, planning_entries, production_entries, active_downtimes, downtime_history, quality_measurements, oee_history, loss_entries, setup_entries, pmp_entries, quality_lots, notifications, machine_maintenances, operator_schedules, rework_entries, spc_data

### Mold — `molds`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `code` | String(50) | unique, not null, index |
| `name` | String(150) | not null |
| `cavities` | Integer | default=1 |
| `cycle_time_ideal` | Float | nullable |
| `product_id` | Integer | FK → products.id, nullable |
| `status` | Enum(MoldStatus) | default=disponivel |
| `total_cycles` | Integer | default=0 |
| `max_cycles` | Integer | nullable |
| `last_maintenance` | DateTime(tz=True) | nullable |
| `weight_grams` | Float | nullable |
| `material_type` | String(100) | nullable |

→ `product`, `maintenances`, `production_orders`

### Operator — `operators`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `registration` | String(20) | unique, not null, index |
| `name` | String(150) | not null |
| `shift` | String(20) | nullable |
| `sector` | String(100) | default="injeção" |
| `role` | String(50) | default="operador" |
| `skills` | JSON | default=[] |
| `is_active` | Boolean | default=True |
| `phone` | String(20) | nullable |

### User — `users`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `email` | String(255) | unique, not null, index |
| `name` | String(255) | not null |
| `hashed_password` | String(255) | not null |
| `role` | Enum(UserRole) | default=operador |
| `is_active` | Boolean | default=True |
| `custom_claims` | JSON | default={} |
| `sector` | String(100) | default="producao" |
| `avatar_initials` | String(5) | default="US" |
| `last_login` | DateTime(tz=True) | nullable |

### Product — `products`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `code` | String(50) | unique, not null, index |
| `name` | String(200) | not null |
| `description` | String(500) | nullable |
| `weight_grams` | Float | nullable |
| `material` | String(100) | nullable |
| `color` | String(50) | nullable |
| `cycle_time_ideal` | Float | nullable |
| `cavities` | Integer | default=1 |
| `category` | String(100) | nullable |
| `client` | String(200) | nullable |
| `ean` | String(20) | nullable |
| `is_active` | Boolean | default=True |
| `specs` | JSON | default={} |

### Material — `materials`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `code` | String(50) | unique, not null, index |
| `name` | String(200) | not null |
| `type` | Enum(MaterialType) | not null |
| `unit` | Enum(MaterialUnit) | default=kg |
| `density` | Float | nullable |
| `supplier` | String(200) | nullable |
| `min_stock` | Float | default=0 |
| `current_stock` | Float | default=0 |
| `cost_per_unit` | Float | nullable |
| `is_active` | Boolean | default=True |

---

## Modelos — Produção

### ProductionOrder — `production_orders`

Índices: `ix_po_product_status` (product_id, status)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `order_number` | String(50) | unique, not null, index |
| `product_id` | Integer | FK → products.id, not null |
| `product_name` | String(200) | not null |
| `quantity_planned` | Integer | not null |
| `quantity_produced` | Integer | default=0 |
| `quantity_good` | Integer | default=0 |
| `quantity_rejected` | Integer | default=0 |
| `status` | Enum(OrderStatus) | default=planned |
| `priority` | Enum(OrderPriority) | default=normal |
| `machine_id` | Integer | FK → machines.id, nullable |
| `mold_id` | Integer | FK → molds.id, nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `start_date` | DateTime(tz=True) | nullable |
| `end_date` | DateTime(tz=True) | nullable |
| `due_date` | Date | nullable |
| `client` | String(200) | nullable |
| `notes` | String(500) | nullable |
| `metadata_extra` | JSON | default={} |

→ `product`, `machine`, `mold`, `operator`, `production_entries`, `planning_entries`

### Planning — `planning`

Índices: `ix_planning_machine_date` (machine_id, date)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `product_id` | Integer | FK → products.id, not null |
| `product_name` | String(200) | not null |
| `mold_id` | Integer | FK → molds.id, nullable |
| `order_id` | Integer | FK → production_orders.id, nullable |
| `quantity_planned` | Integer | not null |
| `cycle_time_seconds` | Float | nullable |
| `cavities` | Integer | default=1 |
| `weight_grams` | Float | nullable |
| `material` | String(100) | nullable |
| `color` | String(50) | nullable |
| `shift` | String(20) | nullable |
| `date` | Date | not null, index |
| `sequence` | Integer | default=1 |
| `status` | Enum(PlanningStatus) | default=pendente |
| `operator_id` | Integer | FK → operators.id, nullable |

### ProductionEntry — `production_entries`

Índices: `ix_pe_machine_timestamp` (machine_id, timestamp)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `product_id` | Integer | FK → products.id, not null |
| `product_name` | String(200) | nullable |
| `order_id` | Integer | FK → production_orders.id, nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `shift` | String(20) | nullable |
| `quantity_good` | Integer | default=0 |
| `quantity_rejected` | Integer | default=0 |
| `weight_kg` | Float | nullable |
| `cycle_time_actual` | Float | nullable |
| `cycle_time_ideal` | Float | nullable |
| `cavities` | Integer | default=1 |
| `material` | String(100) | nullable |
| `notes` | String(500) | nullable |
| `timestamp` | DateTime(tz=True) | not null, index |

### BomLine — `bom_lines`

Constraint: `uq_bom_product_material` (product_id, material_id)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `product_id` | Integer | FK → products.id, not null |
| `material_id` | Integer | FK → materials.id, not null |
| `quantity_per_unit` | Float | not null |
| `unit` | Enum(MaterialUnit) | default=kg |
| `is_primary` | Boolean | default=False |
| `notes` | String(300) | nullable |

### InventoryMovement — `inventory_movements`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `material_id` | Integer | FK → materials.id, not null |
| `movement_type` | Enum(InventoryMovementType) | not null |
| `quantity` | Float | not null |
| `lot_number` | String(50) | nullable |
| `reference` | String(200) | nullable |
| `performed_by` | String(100) | nullable |
| `notes` | String(500) | nullable |
| `timestamp` | DateTime(tz=True) | nullable |

---

## Modelos — Paradas

### ActiveDowntime — `active_downtimes`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null, index |
| `reason` | String(200) | not null |
| `category` | Enum(DowntimeCategory) | not null |
| `subcategory` | String(100) | nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `shift` | String(20) | nullable |
| `start_time` | DateTime(tz=True) | not null |
| `notes` | String(500) | nullable |
| `is_planned` | Boolean | default=False |

### DowntimeHistory — `downtime_history`

Índices: `ix_dth_machine_start` (machine_id, start_time), `ix_dth_category` (category)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `reason` | String(200) | not null |
| `category` | Enum(DowntimeCategory) | not null |
| `subcategory` | String(100) | nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `shift` | String(20) | nullable |
| `start_time` | DateTime(tz=True) | not null |
| `end_time` | DateTime(tz=True) | not null |
| `duration_minutes` | Float | not null |
| `is_planned` | Boolean | default=False |
| `notes` | String(500) | nullable |
| `resolved_by` | String(100) | nullable |

---

## Modelos — Qualidade

### QualityMeasurement — `quality_measurements`

Índices: `ix_qm_product_machine` (product_id, machine_id)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `product_id` | Integer | FK → products.id, not null |
| `order_id` | Integer | FK → production_orders.id, nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `inspector` | String(100) | nullable |
| `dimension_name` | String(100) | nullable |
| `nominal_value` | Float | nullable |
| `measured_value` | Float | nullable |
| `tolerance_upper` | Float | nullable |
| `tolerance_lower` | Float | nullable |
| `unit` | String(20) | default="mm" |
| `is_approved` | Boolean | default=True |
| `defect_type` | String(100) | nullable |
| `defect_severity` | Enum(DefectSeverity) | nullable |
| `sample_size` | Integer | default=1 |
| `notes` | String(500) | nullable |
| `timestamp` | DateTime(tz=True) | not null, index |

### ReworkEntry — `rework_entries`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `product_id` | Integer | FK → products.id, not null |
| `order_id` | Integer | FK → production_orders.id, nullable |
| `quantity` | Integer | not null |
| `reason` | String(200) | not null |
| `action_taken` | String(300) | nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `shift` | String(20) | nullable |
| `status` | Enum(ReworkStatus) | default=pendente |
| `timestamp` | DateTime(tz=True) | not null |

### SpcData — `spc_data`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `product_id` | Integer | FK → products.id, not null |
| `parameter_name` | String(100) | not null |
| `value` | Float | not null |
| `ucl` | Float | nullable |
| `lcl` | Float | nullable |
| `target` | Float | nullable |
| `is_out_of_control` | Boolean | default=False |
| `subgroup` | Integer | nullable |
| `sample_number` | Integer | nullable |
| `timestamp` | DateTime(tz=True) | not null, index |

### QualityLot — `quality_lots`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `lot_number` | String(50) | unique, not null, index |
| `machine_id` | Integer | FK → machines.id, not null |
| `product_id` | Integer | FK → products.id, not null |
| `order_id` | Integer | FK → production_orders.id, nullable |
| `quantity` | Integer | not null |
| `weight_kg` | Float | nullable |
| `reason` | String(200) | not null |
| `status` | Enum(QualityLotStatus) | default=quarentena |
| `approved_qty` | Integer | default=0 |
| `rejected_qty` | Integer | default=0 |
| `returned_to_production` | Boolean | default=False |
| `operator_id` | Integer | FK → operators.id, nullable |
| `inspector` | String(100) | nullable |
| `shift` | String(20) | nullable |
| `notes` | String(500) | nullable |
| `conclusion_notes` | String(500) | nullable |
| `concluded_at` | DateTime(tz=True) | nullable |

---

## Modelos — OEE & Perdas

### OeeHistory — `oee_history`

Índices: `ix_oee_machine_date_shift` (machine_id, date, shift) — **unique**

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `date` | Date | not null, index |
| `shift` | String(20) | nullable |
| `availability` | Float | default=0.0 |
| `performance` | Float | default=0.0 |
| `quality_rate` | Float | default=0.0 |
| `oee` | Float | default=0.0 |
| `planned_time_minutes` | Float | default=480.0 |
| `running_time_minutes` | Float | default=0.0 |
| `downtime_minutes` | Float | default=0.0 |
| `total_produced` | Integer | default=0 |
| `good_produced` | Integer | default=0 |
| `rejected` | Integer | default=0 |
| `ideal_cycle_seconds` | Float | nullable |
| `actual_cycle_seconds` | Float | nullable |

### LossEntry — `loss_entries`

Índices: `ix_loss_category_ts` (category, timestamp)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `product_id` | Integer | FK → products.id, not null |
| `order_id` | Integer | FK → production_orders.id, nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `shift` | String(20) | nullable |
| `quantity` | Integer | not null |
| `weight_kg` | Float | nullable |
| `reason` | String(200) | not null |
| `category` | Enum(LossCategory) | not null |
| `material` | String(100) | nullable |
| `is_manual` | Boolean | default=False |
| `notes` | String(500) | nullable |
| `timestamp` | DateTime(tz=True) | not null, index |

---

## Modelos — Setup & PMP

### SetupEntry — `setup_entries`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `setup_type` | Enum(SetupType) | not null |
| `mold_from` | String(50) | nullable |
| `mold_to` | String(50) | nullable |
| `product_from` | String(50) | nullable |
| `product_to` | String(50) | nullable |
| `operator_id` | Integer | FK → operators.id, nullable |
| `shift` | String(20) | nullable |
| `start_time` | DateTime(tz=True) | not null |
| `end_time` | DateTime(tz=True) | nullable |
| `duration_minutes` | Float | nullable |
| `status` | Enum(SetupStatus) | default=em_andamento |
| `notes` | String(500) | nullable |

### PmpEntry — `pmp_entries`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `type` | Enum(PmpType) | not null, index |
| `machine_id` | Integer | FK → machines.id, nullable |
| `product_id` | Integer | FK → products.id, nullable |
| `material` | String(100) | nullable |
| `weight_kg` | Float | not null |
| `operator_id` | Integer | FK → operators.id, nullable |
| `shift` | String(20) | nullable |
| `destination` | Enum(PmpDestination) | nullable |
| `notes` | String(500) | nullable |
| `timestamp` | DateTime(tz=True) | not null, index |

---

## Modelos — Manutenção

### MoldMaintenance — `mold_maintenances`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `mold_id` | Integer | FK → molds.id, not null |
| `maintenance_type` | Enum(MaintenanceType) | not null |
| `description` | String(500) | nullable |
| `technician` | String(100) | nullable |
| `start_time` | DateTime(tz=True) | not null |
| `end_time` | DateTime(tz=True) | nullable |
| `duration_hours` | Float | nullable |
| `cost` | Float | nullable |
| `parts_replaced` | String(500) | nullable |
| `status` | Enum(MaintenanceStatus) | default=em_andamento |
| `notes` | String(500) | nullable |

### MachineMaintenance — `machine_maintenances`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `machine_id` | Integer | FK → machines.id, not null |
| `maintenance_type` | Enum(MaintenanceType) | not null |
| `priority` | Enum(MaintenancePriority) | default=media |
| `description` | String(500) | nullable |
| `technician` | String(100) | nullable |
| `scheduled_date` | Date | nullable |
| `start_time` | DateTime(tz=True) | nullable |
| `end_time` | DateTime(tz=True) | nullable |
| `duration_hours` | Float | nullable |
| `cost` | Float | default=0 |
| `parts_replaced` | String(500) | nullable |
| `status` | Enum(MaintenanceStatus) | default=pendente |
| `notes` | String(500) | nullable |

---

## Modelos — Liderança

### OperatorSchedule — `operator_schedules`

Índices: `ix_opsch_operator_date` (operator_id, date)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `operator_id` | Integer | FK → operators.id, not null |
| `operator_name` | String(150) | not null |
| `date` | Date | not null, index |
| `shift` | String(20) | not null |
| `machine_id` | Integer | FK → machines.id, nullable |
| `position` | String(50) | default="operador" |
| `notes` | String(300) | nullable |

### AbsenteeismEntry — `absenteeism_entries`

Índices: `ix_abs_operator_date` (operator_id, date)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `operator_id` | Integer | FK → operators.id, not null |
| `operator_name` | String(150) | not null |
| `date` | Date | not null, index |
| `shift` | String(20) | nullable |
| `reason` | Enum(AbsenteeismReason) | not null |
| `hours_absent` | Integer | default=8 |
| `justified` | Boolean | default=False |
| `notes` | String(500) | nullable |

---

## Modelos — Notificações & Logs

### Notification — `notifications`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `title` | String(200) | not null |
| `message` | String(500) | not null |
| `type` | Enum(NotificationType) | default=info |
| `target_role` | String(50) | nullable |
| `target_user_id` | Integer | FK → users.id, nullable |
| `is_read` | Boolean | default=False |
| `machine_id` | Integer | FK → machines.id, nullable |
| `link` | String(300) | nullable |

### SystemLog — `system_logs`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `action` | String(100) | not null, index |
| `user_id` | Integer | FK → users.id, nullable |
| `user_email` | String(255) | nullable |
| `user_name` | String(150) | nullable |
| `entity_type` | String(50) | nullable, index |
| `entity_id` | Integer | nullable |
| `details` | JSON | default={} |
| `ip_address` | String(45) | nullable |
| `user_agent` | String(300) | nullable |
| `module` | String(50) | nullable |
| `timestamp` | DateTime(tz=True) | not null, index |

---

## Modelos — PCP & Processo

### PcpMessage — `pcp_messages`

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `message` | String(500) | not null |
| `priority` | Integer | default=0 |
| `type` | Enum(PcpMessageType) | default=info |
| `target_machine_id` | Integer | FK → machines.id, nullable |
| `is_active` | Boolean | default=True |
| `created_by` | String(100) | nullable |
| `expires_at` | DateTime(tz=True) | nullable |

### ProcessSegment — `process_segments`

Constraint: `uq_process_product_machine_type` (product_id, machine_type)

| Coluna | Tipo | Detalhes |
|--------|------|---------|
| `product_id` | Integer | FK → products.id, not null |
| `machine_type` | String(50) | default="injetora" |
| `cycle_time_ideal` | Float | nullable |
| `injection_pressure` | Float | nullable |
| `holding_pressure` | Float | nullable |
| `melt_temperature` | Float | nullable |
| `mold_temperature` | Float | nullable |
| `cooling_time` | Float | nullable |
| `injection_speed` | Float | nullable |
| `screw_rpm` | Float | nullable |
| `back_pressure` | Float | nullable |
| `clamping_force` | Float | nullable |
| `notes` | String(500) | nullable |

---

## Diagrama de Relacionamentos (Simplificado)

```
Site ──1:N──▶ Area ──1:N──▶ WorkCenter ──1:N──▶ Machine
                                                   │
               ┌──────────────┬──────────────┬─────┤
               ▼              ▼              ▼     ▼
       ProductionOrder    Planning    ProductionEntry  ActiveDowntime
               │              │              │              │
               ▼              ▼              ▼              ▼
           Product          Mold         Operator    DowntimeHistory
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 BomLine   QualityLot  LossEntry
    │
    ▼
 Material ──1:N──▶ InventoryMovement

Machine ──1:N──▶ OeeHistory
Machine ──1:N──▶ MachineMaintenance
Mold ───1:N──▶ MoldMaintenance
Operator ──1:N──▶ OperatorSchedule
Operator ──1:N──▶ AbsenteeismEntry
User ───1:N──▶ Notification
User ───1:N──▶ SystemLog
```

---

## Resumo

| Item | Quantidade |
|------|-----------|
| **Modelos** | 31 |
| **Tabelas** | 31 |
| **Enums** | 24 |
| **Foreign Keys** | ~40 |
| **Índices compostos** | 8 |
| **Unique Constraints** | 2 |
