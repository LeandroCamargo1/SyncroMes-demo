// ══════════════════════════════════════════════════════════════
// SeedFirestore — Página de admin para popular Firestore
// com dados fictícios realistas de um chão de fábrica MES
// ══════════════════════════════════════════════════════════════
import { useState } from 'react';
import { Database, Trash2, Play, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';
import { batchWrite, clearCollection } from '../services/firestore';

// ── Helpers ─────────────────────────────────────────────────

function randomFrom<T>(arr: T[]): T { return arr[Math.floor(Math.random() * arr.length)]; }
function randomBetween(min: number, max: number): number { return Math.floor(Math.random() * (max - min + 1)) + min; }
function randomFloat(min: number, max: number, decimals = 2): number {
  return parseFloat((Math.random() * (max - min) + min).toFixed(decimals));
}
function daysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString();
}
function dateStr(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().split('T')[0];
}
function uid(): string { return Math.random().toString(36).slice(2, 10); }

// ── Constantes ──────────────────────────────────────────────

const SHIFTS = ['A', 'B', 'C'];
const MACHINE_STATUSES = ['running', 'stopped', 'maintenance', 'setup'];
const ORDER_STATUSES = ['planned', 'in_progress', 'completed', 'cancelled'];
const ORDER_PRIORITIES = ['low', 'normal', 'high', 'urgent'];
const DOWNTIME_CATEGORIES = ['mecanica', 'eletrica', 'setup', 'processo', 'qualidade', 'falta_material', 'programada'];
const LOSS_CATEGORIES = ['refugo', 'rebarba', 'dimensional', 'cor', 'contaminacao'];
const PMP_TYPES = ['moido', 'borra', 'sucata'];
const PMP_DESTINATIONS = ['reprocesso', 'descarte', 'venda'];
const SETUP_TYPES = ['troca_molde', 'troca_cor', 'troca_material', 'ajuste'];
const QUALITY_LOT_STATUSES = ['quarentena', 'em_triagem', 'concluida'];
const MAINT_TYPES = ['preventiva', 'corretiva', 'limpeza'];
const MAINT_STATUSES = ['pendente', 'em_andamento', 'concluida'];
const MAINT_PRIORITIES = ['baixa', 'media', 'alta', 'critica'];
const ABSENCE_REASONS = ['falta', 'atestado', 'atraso', 'ferias', 'folga'];
const MATERIAL_TYPES = ['resina', 'masterbatch', 'aditivo', 'embalagem', 'inserto'];
const NOTIF_TYPES = ['info', 'warning', 'error', 'success'];
const PCP_MSG_TYPES = ['info', 'warning', 'urgent'];
const DEFECT_SEVERITIES = ['minor', 'major', 'critical'];

const MACHINE_CODES = ['INJ-01', 'INJ-02', 'INJ-03', 'INJ-04', 'INJ-05', 'INJ-06', 'INJ-07', 'INJ-08', 'INJ-09', 'INJ-10', 'INJ-11', 'INJ-12'];
const PRODUCT_CODES = ['PN-1001', 'PN-1002', 'PN-1003', 'PN-2001', 'PN-2002', 'PN-2003', 'PN-3001', 'PN-3002', 'PN-3003', 'PN-4001'];
const PRODUCT_NAMES = ['Tampa Flip-Top', 'Corpo Frasco 500ml', 'Base Embalagem', 'Conector Elétrico', 'Caixa Modular', 'Suporte Lateral', 'Engrenagem Z20', 'Pino Guia', 'Bucha Redutora', 'Anel Vedação'];
const COLORS = ['Branco', 'Preto', 'Azul', 'Vermelho', 'Transparente', 'Verde', 'Cinza', 'Amarelo'];
const MATERIAL_NAMES = ['PP Homopolímero', 'PEAD Sopro', 'ABS Natural', 'PA6 GF30', 'PS Cristal', 'MB Preto', 'MB Azul', 'MB Branco', 'Antioxidante UV', 'Caixa Papelão', 'Saco PE', 'Inserto M4', 'Inserto M6'];
const OPERATOR_NAMES = ['Carlos Silva', 'Maria Santos', 'João Oliveira', 'Ana Costa', 'Pedro Lima', 'Fernanda Souza', 'Ricardo Alves', 'Patrícia Rocha', 'Lucas Mendes', 'Juliana Pereira', 'Roberto Nunes', 'Camila Ferreira'];
const MOLD_CODES = ['MLD-001', 'MLD-002', 'MLD-003', 'MLD-004', 'MLD-005', 'MLD-006', 'MLD-007', 'MLD-008'];
const DOWNTIME_REASONS = [
  'Vazamento hidráulico', 'Sensor danificado', 'Aquecimento excessivo', 'Troca de molde', 'Ajuste de parâmetros',
  'Falta de matéria-prima', 'Peças com defeito', 'Manutenção preventiva', 'Falha elétrica', 'Troca de cor',
  'Bico entupido', 'Problema na rosca', 'Troca de resina', 'Limpeza do molde', 'Calibração',
];
const LOSS_REASONS = [
  'Rebarba excessiva', 'Dimensão fora do spec', 'Cor diferente', 'Contaminação material', 'Marca de fluxo',
  'Rechupe', 'Bolhas', 'Peça incompleta', 'Deformação', 'Risco superficial',
];

// ── Gerador de dados ────────────────────────────────────────

function generateAllData() {
  const now = new Date().toISOString();

  // ── Sites / Areas / Work Centers ───
  const sites = [{ code: 'PLANTA-SP', name: 'Planta São Paulo', address: 'Av. Industrial, 1500 - Guarulhos, SP', active: true }];
  const areas = [
    { code: 'INJECAO', name: 'Injeção Plástica', site_code: 'PLANTA-SP', active: true },
    { code: 'MONTAGEM', name: 'Montagem', site_code: 'PLANTA-SP', active: true },
  ];
  const workCenters = [
    { code: 'WC-INJ-A', name: 'Célula Injeção A', area_code: 'INJECAO', capacity_factor: 1.0, active: true },
    { code: 'WC-INJ-B', name: 'Célula Injeção B', area_code: 'INJECAO', capacity_factor: 0.85, active: true },
  ];

  // ── Machines ───
  const machines = MACHINE_CODES.map((code, i) => ({
    code,
    name: `Injetora ${code}`,
    type: i < 6 ? 'injetora_horizontal' : 'injetora_vertical',
    status: i < 8 ? 'running' : randomFrom(MACHINE_STATUSES),
    tonnage: randomFrom([150, 200, 250, 350, 450, 650]),
    work_center_code: i < 6 ? 'WC-INJ-A' : 'WC-INJ-B',
    current_product: i < 8 ? PRODUCT_NAMES[i % PRODUCT_NAMES.length] : null,
    cycle_time: randomFloat(12, 45, 1),
    efficiency: randomFloat(55, 98, 1),
    active: true,
  }));

  // ── Products ───
  const products = PRODUCT_CODES.map((code, i) => ({
    code,
    name: PRODUCT_NAMES[i],
    description: `Peça injetada ${PRODUCT_NAMES[i]}`,
    color: COLORS[i % COLORS.length],
    weight_g: randomFloat(5, 250, 1),
    cycle_time_s: randomFloat(12, 45, 1),
    cavities: randomFrom([1, 2, 4, 6, 8]),
    mold_code: MOLD_CODES[i % MOLD_CODES.length],
    material_code: MATERIAL_NAMES[i % 5],
    active: true,
  }));

  // ── Molds ───
  const molds = MOLD_CODES.map((code, i) => ({
    code,
    name: `Molde ${PRODUCT_NAMES[i % PRODUCT_NAMES.length]}`,
    cavities: randomFrom([1, 2, 4, 6, 8]),
    product_code: PRODUCT_CODES[i % PRODUCT_CODES.length],
    status: randomFrom(['disponivel', 'em_uso', 'manutencao']),
    total_cycles: randomBetween(50000, 500000),
    max_cycles: randomBetween(600000, 1000000),
    last_maintenance: daysAgo(randomBetween(1, 30)),
  }));

  // ── Operators ───
  const operators = OPERATOR_NAMES.map((name, i) => ({
    name,
    registration: `OP-${String(i + 1).padStart(3, '0')}`,
    shift: SHIFTS[i % 3],
    sector: 'injecao',
    role: i < 3 ? 'lider' : 'operador',
    active: true,
    phone: `(11) 9${randomBetween(1000, 9999)}-${randomBetween(1000, 9999)}`,
  }));

  // ── Users ───
  const users = [
    { email: 'admin@synchro.dev', name: 'Admin Dev', role: 'admin', is_active: true, sector: 'producao', avatar_initials: 'AD' },
    { email: 'supervisor@synchro.dev', name: 'Marcos Supervisor', role: 'supervisor', is_active: true, sector: 'injecao', avatar_initials: 'MS' },
    { email: 'qualidade@synchro.dev', name: 'Laura Qualidade', role: 'qualidade', is_active: true, sector: 'qualidade', avatar_initials: 'LQ' },
    { email: 'pcp@synchro.dev', name: 'Felipe PCP', role: 'pcp', is_active: true, sector: 'pcp', avatar_initials: 'FP' },
    { email: 'operador@synchro.dev', name: 'Carlos Operador', role: 'operador', is_active: true, sector: 'injecao', avatar_initials: 'CO' },
  ];

  // ── Materials ───
  const materials = MATERIAL_NAMES.map((name, i) => ({
    code: `MAT-${String(i + 1).padStart(3, '0')}`,
    name,
    type: MATERIAL_TYPES[Math.min(i, MATERIAL_TYPES.length - 1)],
    unit: i < 9 ? 'kg' : i < 11 ? 'un' : 'un',
    stock_qty: randomFloat(100, 5000, 1),
    min_stock: randomFloat(50, 200, 0),
    cost_per_unit: randomFloat(2, 45, 2),
    supplier: randomFrom(['Braskem', 'BASF', 'Dow', 'Clariant', 'Cabot', 'Embalagens SP']),
    active: true,
  }));

  // ── Production Orders (últimos 30 dias) ───
  const productionOrders: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    const count = randomBetween(2, 5);
    for (let j = 0; j < count; j++) {
      const pi = randomBetween(0, PRODUCT_CODES.length - 1);
      const mi = randomBetween(0, MACHINE_CODES.length - 1);
      const planned = randomBetween(500, 5000);
      const produced = d < 3 ? randomBetween(0, planned) : randomBetween(Math.floor(planned * 0.7), planned);
      const rejected = Math.floor(produced * randomFloat(0.005, 0.04));
      const status: string = d < 2 ? randomFrom(['planned', 'in_progress']) : d < 5 ? 'in_progress' : randomFrom(['completed', 'completed', 'completed', 'cancelled']);
      productionOrders.push({
        order_number: `OP-${dateStr(d).replace(/-/g, '')}-${String(j + 1).padStart(2, '0')}`,
        product_code: PRODUCT_CODES[pi],
        product_name: PRODUCT_NAMES[pi],
        machine_code: MACHINE_CODES[mi],
        mold_code: MOLD_CODES[pi % MOLD_CODES.length],
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        quantity_planned: planned,
        quantity_produced: produced,
        quantity_good: produced - rejected,
        quantity_rejected: rejected,
        status,
        priority: randomFrom(ORDER_PRIORITIES),
        shift: randomFrom(SHIFTS),
        start_date: daysAgo(d),
        end_date: status === 'completed' ? daysAgo(d) : null,
        notes: '',
      });
    }
  }

  // ── Production Entries (últimos 30 dias) ───
  const productionEntries: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    for (const mc of MACHINE_CODES.slice(0, 8)) {
      const pi = randomBetween(0, PRODUCT_CODES.length - 1);
      const qty = randomBetween(200, 2000);
      const rej = Math.floor(qty * randomFloat(0.005, 0.035));
      productionEntries.push({
        machine_code: mc,
        product_code: PRODUCT_CODES[pi],
        product_name: PRODUCT_NAMES[pi],
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        order_number: productionOrders[randomBetween(0, productionOrders.length - 1)].order_number,
        shift: SHIFTS[d % 3],
        quantity_produced: qty,
        quantity_good: qty - rej,
        quantity_rejected: rej,
        cycle_time: randomFloat(12, 40, 1),
        date: dateStr(d),
        timestamp: daysAgo(d),
      });
    }
  }

  // ── OEE History (últimos 30 dias) ───
  const oeeHistory: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    for (const mc of MACHINE_CODES.slice(0, 10)) {
      const avail = randomFloat(70, 98);
      const perf = randomFloat(65, 99);
      const qual = randomFloat(90, 99.5);
      oeeHistory.push({
        machine_code: mc,
        date: dateStr(d),
        shift: SHIFTS[d % 3],
        availability: avail,
        performance: perf,
        quality: qual,
        oee: parseFloat((avail * perf * qual / 10000).toFixed(2)),
        planned_time_min: 480,
        operating_time_min: Math.round(480 * avail / 100),
        total_produced: randomBetween(300, 2000),
        good_produced: randomBetween(280, 1950),
      });
    }
  }

  // ── Downtimes (histórico últimos 30 dias) ───
  const downtimeHistory: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    const count = randomBetween(1, 4);
    for (let j = 0; j < count; j++) {
      const duration = randomBetween(5, 180);
      const cat = randomFrom(DOWNTIME_CATEGORIES);
      downtimeHistory.push({
        machine_code: randomFrom(MACHINE_CODES),
        category: cat,
        reason: randomFrom(DOWNTIME_REASONS),
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        shift: SHIFTS[d % 3],
        start_time: daysAgo(d),
        end_time: daysAgo(d),
        duration_minutes: duration,
        resolved: true,
        notes: '',
        date: dateStr(d),
      });
    }
  }

  // ── Active Downtimes (1-3 ativos) ───
  const activeDowntimes = Array.from({ length: randomBetween(1, 3) }, (_, i) => ({
    machine_code: MACHINE_CODES[8 + i],
    category: randomFrom(DOWNTIME_CATEGORIES),
    reason: randomFrom(DOWNTIME_REASONS),
    operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
    shift: SHIFTS[0],
    start_time: daysAgo(0),
    duration_minutes: null,
    resolved: false,
  }));

  // ── Quality Measurements (últimos 30 dias) ───
  const qualityMeasurements: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    const count = randomBetween(3, 8);
    for (let j = 0; j < count; j++) {
      const nominal = randomFloat(10, 100, 2);
      const tolerance = randomFloat(0.05, 0.5, 2);
      const measured = randomFloat(nominal - tolerance * 1.5, nominal + tolerance * 1.5, 3);
      const approved = Math.abs(measured - nominal) <= tolerance;
      qualityMeasurements.push({
        machine_code: randomFrom(MACHINE_CODES.slice(0, 8)),
        product_code: randomFrom(PRODUCT_CODES),
        order_number: productionOrders[randomBetween(0, productionOrders.length - 1)].order_number,
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        dimension_name: randomFrom(['Diâmetro Ext.', 'Altura', 'Largura', 'Espessura Parede', 'Peso']),
        nominal_value: nominal,
        tolerance_upper: nominal + tolerance,
        tolerance_lower: nominal - tolerance,
        measured_value: measured,
        approved,
        defect_type: approved ? null : randomFrom(['dimensional', 'visual', 'funcional']),
        severity: approved ? null : randomFrom(DEFECT_SEVERITIES),
        shift: SHIFTS[d % 3],
        date: dateStr(d),
        timestamp: daysAgo(d),
      });
    }
  }

  // ── Loss Entries (últimos 30 dias) ───
  const lossEntries: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    const count = randomBetween(1, 4);
    for (let j = 0; j < count; j++) {
      lossEntries.push({
        machine_code: randomFrom(MACHINE_CODES.slice(0, 8)),
        product_code: randomFrom(PRODUCT_CODES),
        order_number: productionOrders[randomBetween(0, productionOrders.length - 1)].order_number,
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        category: randomFrom(LOSS_CATEGORIES),
        reason: randomFrom(LOSS_REASONS),
        quantity: randomBetween(1, 50),
        shift: SHIFTS[d % 3],
        date: dateStr(d),
        timestamp: daysAgo(d),
      });
    }
  }

  // ── Setup Entries (últimos 15 dias) ───
  const setupEntries: Record<string, any>[] = [];
  for (let d = 0; d < 15; d++) {
    const count = randomBetween(1, 3);
    for (let j = 0; j < count; j++) {
      const duration = randomBetween(15, 90);
      setupEntries.push({
        machine_code: randomFrom(MACHINE_CODES),
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        type: randomFrom(SETUP_TYPES),
        status: 'concluido',
        start_time: daysAgo(d),
        end_time: daysAgo(d),
        duration_minutes: duration,
        target_minutes: randomBetween(20, 60),
        notes: '',
        shift: SHIFTS[d % 3],
        date: dateStr(d),
      });
    }
  }

  // ── PMP Entries (últimos 30 dias) ───
  const pmpEntries: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    const count = randomBetween(1, 3);
    for (let j = 0; j < count; j++) {
      pmpEntries.push({
        machine_code: randomFrom(MACHINE_CODES.slice(0, 8)),
        product_code: randomFrom(PRODUCT_CODES),
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        type: randomFrom(PMP_TYPES),
        weight_kg: randomFloat(0.5, 25, 1),
        destination: randomFrom(PMP_DESTINATIONS),
        material: randomFrom(['PP', 'PEAD', 'ABS', 'PA6']),
        shift: SHIFTS[d % 3],
        date: dateStr(d),
        timestamp: daysAgo(d),
      });
    }
  }

  // ── Quality Lots ───
  const qualityLots = Array.from({ length: 20 }, (_, i) => {
    const pi = i % PRODUCT_CODES.length;
    return {
      lot_number: `LOT-${dateStr(i).replace(/-/g, '')}-${String(i + 1).padStart(2, '0')}`,
      machine_code: randomFrom(MACHINE_CODES.slice(0, 8)),
      product_code: PRODUCT_CODES[pi],
      product_name: PRODUCT_NAMES[pi],
      order_number: productionOrders[i % productionOrders.length].order_number,
      operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
      status: randomFrom(QUALITY_LOT_STATUSES),
      total_qty: randomBetween(200, 2000),
      approved_qty: randomBetween(180, 1950),
      rejected_qty: randomBetween(2, 50),
      shift: SHIFTS[i % 3],
      date: dateStr(i),
    };
  });

  // ── Mold Maintenances ───
  const moldMaintenances = MOLD_CODES.slice(0, 5).map((code, i) => ({
    mold_code: code,
    type: randomFrom(MAINT_TYPES),
    status: randomFrom(MAINT_STATUSES),
    description: randomFrom(['Limpeza geral', 'Polimento cavidades', 'Troca pinos guia', 'Solda TIG reparo', 'Revisão sistema ejeção']),
    priority: randomFrom(MAINT_PRIORITIES),
    scheduled_date: dateStr(randomBetween(0, 7)),
    completed_date: i < 3 ? dateStr(i) : null,
    cost: randomFloat(200, 5000, 2),
    technician: randomFrom(['José Técnico', 'Wagner Manutenção', 'Rafael Moldes']),
  }));

  // ── Machine Maintenances ───
  const machineMaintenances = MACHINE_CODES.slice(0, 6).map((code, i) => ({
    machine_code: code,
    type: randomFrom(MAINT_TYPES),
    status: randomFrom(MAINT_STATUSES),
    description: randomFrom(['Troca óleo hidráulico', 'Revisão bomba', 'Calibração sensores', 'Troca resistência', 'Revisão elétrica', 'Lubrificação geral']),
    priority: randomFrom(MAINT_PRIORITIES),
    scheduled_date: dateStr(randomBetween(0, 14)),
    completed_date: i < 4 ? dateStr(i) : null,
    downtime_minutes: randomBetween(30, 480),
    cost: randomFloat(500, 15000, 2),
    technician: randomFrom(['Wagner Manutenção', 'Roberto Elétrica', 'Sérgio Mecânica']),
  }));

  // ── Notifications ───
  const notifications = Array.from({ length: 15 }, (_, i) => ({
    type: randomFrom(NOTIF_TYPES),
    title: randomFrom([
      'OEE abaixo da meta', 'Manutenção programada', 'Parada não planejada',
      'Ordem concluída', 'Qualidade fora do spec', 'Material em baixo estoque',
      'Setup acima do tempo', 'Meta de produção atingida',
    ]),
    message: randomFrom([
      'INJ-03 com OEE 62% — abaixo da meta de 85%',
      'Manutenção preventiva do molde MLD-003 agendada para amanhã',
      'Parada elétrica na INJ-07 — técnico acionado',
      'Ordem OP-20260305-01 concluída com 98.2% de aprovação',
      'Dimensão fora da tolerância na INJ-05 — lote em quarentena',
      'Estoque de PP Homopolímero abaixo do mínimo (45 kg)',
      'Setup na INJ-02 levou 72 min (meta: 45 min)',
      'Turno A atingiu meta de 12.000 peças',
    ]),
    machine_code: i < 8 ? randomFrom(MACHINE_CODES) : null,
    read: i > 8,
    timestamp: daysAgo(randomBetween(0, 7)),
  }));

  // ── PCP Messages ───
  const pcpMessages = [
    { type: 'urgent', message: 'Priorizar OP-20260305-01 — cliente crítico', target_machine: 'INJ-01', active: true },
    { type: 'warning', message: 'Material PP chegando amanhã — ajustar planejamento', target_machine: null, active: true },
    { type: 'info', message: 'Nova ordem de prioridade alta para PN-2001', target_machine: 'INJ-04', active: true },
    { type: 'info', message: 'Reunião de produção às 14h na sala 2', target_machine: null, active: true },
    { type: 'warning', message: 'Molde MLD-005 em manutenção — não programar', target_machine: null, active: true },
  ];

  // ── Operator Schedules (próximos 7 dias) ───
  const operatorSchedules: Record<string, any>[] = [];
  for (let d = -2; d < 7; d++) {
    for (let i = 0; i < 8; i++) {
      operatorSchedules.push({
        operator_registration: operators[i % operators.length].registration,
        operator_name: operators[i % operators.length].name,
        machine_code: MACHINE_CODES[i],
        shift: SHIFTS[i % 3],
        date: dateStr(-d),
        role: i < 3 ? 'lider' : 'operador',
      });
    }
  }

  // ── Absenteeism ───
  const absenteeismEntries: Record<string, any>[] = [];
  for (let d = 0; d < 30; d++) {
    if (Math.random() > 0.4) {
      absenteeismEntries.push({
        operator_registration: operators[randomBetween(0, operators.length - 1)].registration,
        operator_name: operators[randomBetween(0, operators.length - 1)].name,
        reason: randomFrom(ABSENCE_REASONS),
        shift: SHIFTS[d % 3],
        date: dateStr(d),
        justified: Math.random() > 0.3,
        notes: '',
      });
    }
  }

  // ── Planning (próximos 7 dias) ───
  const planning: Record<string, any>[] = [];
  for (let d = -1; d < 7; d++) {
    for (let i = 0; i < 6; i++) {
      const pi = randomBetween(0, PRODUCT_CODES.length - 1);
      planning.push({
        machine_code: MACHINE_CODES[i],
        product_code: PRODUCT_CODES[pi],
        product_name: PRODUCT_NAMES[pi],
        mold_code: MOLD_CODES[pi % MOLD_CODES.length],
        order_number: `OP-${dateStr(-d).replace(/-/g, '')}-${String(i + 1).padStart(2, '0')}`,
        operator_registration: operators[i % operators.length].registration,
        shift: SHIFTS[i % 3],
        quantity_planned: randomBetween(500, 3000),
        status: d < 0 ? 'concluido' : d === 0 ? 'em_andamento' : 'pendente',
        date: dateStr(-d),
      });
    }
  }

  // ── SPC Data ───
  const spcData: Record<string, any>[] = [];
  for (const mc of MACHINE_CODES.slice(0, 4)) {
    const nominal = randomFloat(20, 80, 2);
    const sigma = randomFloat(0.05, 0.2, 3);
    for (let i = 0; i < 25; i++) {
      spcData.push({
        machine_code: mc,
        product_code: randomFrom(PRODUCT_CODES),
        dimension_name: 'Diâmetro Ext.',
        sample_number: i + 1,
        measured_value: randomFloat(nominal - sigma * 4, nominal + sigma * 4, 3),
        nominal_value: nominal,
        ucl: parseFloat((nominal + 3 * sigma).toFixed(3)),
        lcl: parseFloat((nominal - 3 * sigma).toFixed(3)),
        usl: parseFloat((nominal + 4 * sigma).toFixed(3)),
        lsl: parseFloat((nominal - 4 * sigma).toFixed(3)),
        date: dateStr(Math.floor(i / 5)),
        timestamp: daysAgo(Math.floor(i / 5)),
      });
    }
  }

  // ── BOM Lines ───
  const bomLines = PRODUCT_CODES.slice(0, 5).flatMap((pc, pi) => [
    { product_code: pc, material_code: materials[pi % materials.length].code, material_name: materials[pi % materials.length].name, quantity_per_unit: randomFloat(0.01, 0.5, 3), unit: 'kg' },
    { product_code: pc, material_code: materials[(pi + 5) % materials.length].code, material_name: materials[(pi + 5) % materials.length].name, quantity_per_unit: randomFloat(1, 4, 0), unit: 'un' },
  ]);

  // ── Inventory Movements ───
  const inventoryMovements = Array.from({ length: 30 }, (_, i) => ({
    material_code: materials[i % materials.length].code,
    material_name: materials[i % materials.length].name,
    type: randomFrom(['entrada', 'saida', 'consumo']),
    quantity: randomFloat(10, 500, 1),
    unit: 'kg',
    reference: `NF-${randomBetween(10000, 99999)}`,
    date: dateStr(randomBetween(0, 20)),
    timestamp: daysAgo(randomBetween(0, 20)),
  }));

  // ── Process Segments ───
  const processSegments = PRODUCT_CODES.slice(0, 6).map((pc, i) => ({
    product_code: pc,
    machine_type: 'injetora_horizontal',
    cycle_time_s: randomFloat(12, 45, 1),
    setup_time_min: randomBetween(15, 60),
    ideal_cavities: randomFrom([2, 4, 6, 8]),
    scrap_rate_target: randomFloat(0.5, 3.0, 1),
    notes: '',
  }));

  // ── Rework Entries ───
  const reworkEntries = Array.from({ length: 10 }, (_, i) => {
    const pi = i % PRODUCT_CODES.length;
    return {
      machine_code: randomFrom(MACHINE_CODES.slice(0, 8)),
      product_code: PRODUCT_CODES[pi],
      product_name: PRODUCT_NAMES[pi],
      order_number: productionOrders[i % productionOrders.length].order_number,
      operator_registration: operators[i % operators.length].registration,
      quantity: randomBetween(5, 100),
      reason: randomFrom(LOSS_REASONS),
      status: randomFrom(['pendente', 'em_andamento', 'concluido', 'descartado']),
      date: dateStr(randomBetween(0, 15)),
    };
  });

  // ── System Logs ───
  const systemLogs = Array.from({ length: 20 }, (_, i) => ({
    action: randomFrom(['login', 'create_order', 'update_machine', 'start_production', 'register_downtime', 'approve_lot', 'close_order']),
    entity: randomFrom(['user', 'production_order', 'machine', 'downtime', 'quality_lot']),
    entity_id: String(randomBetween(1, 100)),
    user_email: users[i % users.length].email,
    details: randomFrom(['Acesso ao sistema', 'Criou nova OP', 'Atualizou status máquina', 'Registrou parada', 'Aprovou lote de qualidade']),
    ip_address: '192.168.1.' + randomBetween(10, 250),
    timestamp: daysAgo(randomBetween(0, 7)),
  }));

  return {
    sites, areas, workCenters,
    machines, products, molds, operators, users, materials,
    productionOrders, productionEntries, oeeHistory,
    downtimeHistory, activeDowntimes,
    qualityMeasurements, lossEntries, setupEntries, pmpEntries,
    qualityLots, moldMaintenances, machineMaintenances,
    notifications, pcpMessages,
    operatorSchedules, absenteeismEntries,
    planning, spcData, bomLines, inventoryMovements,
    processSegments, reworkEntries, systemLogs,
  };
}

// ── Mapeamento collection → key ─────────────────────────────

const COLLECTION_MAP: [string, string][] = [
  ['sites', 'sites'],
  ['areas', 'areas'],
  ['workCenters', 'workCenters'],
  ['machines', 'machines'],
  ['products', 'products'],
  ['molds', 'molds'],
  ['operators', 'operators'],
  ['users', 'users'],
  ['materials', 'materials'],
  ['productionOrders', 'productionOrders'],
  ['productionEntries', 'productionEntries'],
  ['oeeHistory', 'oeeHistory'],
  ['downtimeHistory', 'downtimeHistory'],
  ['activeDowntimes', 'activeDowntimes'],
  ['qualityMeasurements', 'qualityMeasurements'],
  ['lossEntries', 'lossEntries'],
  ['setupEntries', 'setupEntries'],
  ['pmpEntries', 'pmpEntries'],
  ['qualityLots', 'qualityLots'],
  ['moldMaintenances', 'moldMaintenances'],
  ['machineMaintenances', 'machineMaintenances'],
  ['notifications', 'notifications'],
  ['pcpMessages', 'pcpMessages'],
  ['operatorSchedules', 'operatorSchedules'],
  ['absenteeismEntries', 'absenteeismEntries'],
  ['planning', 'planning'],
  ['spcData', 'spcData'],
  ['bomLines', 'bomLines'],
  ['inventoryMovements', 'inventoryMovements'],
  ['processSegments', 'processSegments'],
  ['reworkEntries', 'reworkEntries'],
  ['systemLogs', 'systemLogs'],
];

// ── Componente Página ───────────────────────────────────────

export default function SeedFirestore() {
  const [log, setLog] = useState<{ msg: string; ok: boolean }[]>([]);
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);

  const appendLog = (msg: string, ok = true) => setLog(prev => [...prev, { msg, ok }]);

  const handleSeed = async () => {
    setRunning(true);
    setLog([]);
    setDone(false);

    try {
      appendLog('Gerando dados fictícios...');
      const data = generateAllData();

      appendLog('Limpando coleções existentes...');
      for (const [colName] of COLLECTION_MAP) {
        const del = await clearCollection(colName);
        if (del > 0) appendLog(`  🗑 ${colName}: ${del} docs removidos`);
      }

      appendLog('Inserindo dados no Firestore...');
      let totalDocs = 0;
      for (const [colName, key] of COLLECTION_MAP) {
        const items = (data as any)[key] as any[];
        if (!items || items.length === 0) continue;
        const written = await batchWrite(colName, items);
        totalDocs += written;
        appendLog(`  ✓ ${colName}: ${written} documentos`);
      }

      appendLog(`✅ Seed concluído — ${totalDocs} documentos inseridos em ${COLLECTION_MAP.length} coleções`);
      setDone(true);
    } catch (err: any) {
      appendLog(`❌ Erro: ${err.message}`, false);
    } finally {
      setRunning(false);
    }
  };

  const handleClear = async () => {
    if (!confirm('Tem certeza que deseja limpar TODOS os dados do Firestore?')) return;
    setRunning(true);
    setLog([]);
    setDone(false);

    try {
      appendLog('Limpando todas as coleções...');
      let total = 0;
      for (const [colName] of COLLECTION_MAP) {
        const del = await clearCollection(colName);
        total += del;
        if (del > 0) appendLog(`  🗑 ${colName}: ${del} docs removidos`);
      }
      appendLog(`✅ Limpeza completa — ${total} documentos removidos`);
      setDone(true);
    } catch (err: any) {
      appendLog(`❌ Erro: ${err.message}`, false);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <Database className="w-6 h-6 inline mr-2 -mt-1" />
          Seed Firestore
        </h1>
        <p className="page-subtitle">Popular banco de dados Firebase com dados fictícios de desenvolvimento</p>
      </div>

      {/* Info */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-blue-800">Projeto Firebase: syncro-mes</p>
            <p className="text-xs text-blue-600 mt-1">
              Este seed insere dados realistas de 30 dias em 32 coleções do Firestore.
              Inclui máquinas, produtos, ordens de produção, OEE, paradas, qualidade, perdas, PMP, operadores e mais.
            </p>
          </div>
        </div>
      </div>

      {/* Ações */}
      <div className="flex gap-3">
        <button onClick={handleSeed} disabled={running}
          className="btn-primary flex items-center gap-2 disabled:opacity-50">
          {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {running ? 'Executando...' : 'Executar Seed'}
        </button>
        <button onClick={handleClear} disabled={running}
          className="btn-outline flex items-center gap-2 text-red-600 border-red-300 hover:bg-red-50 disabled:opacity-50">
          <Trash2 className="w-4 h-4" />
          Limpar Dados
        </button>
      </div>

      {/* Log */}
      {log.length > 0 && (
        <div className="card p-0">
          <div className="px-4 py-3 border-b border-surface-100 flex items-center gap-2">
            {done ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Loader2 className="w-4 h-4 animate-spin text-primary-500" />}
            <h3 className="text-sm font-semibold text-surface-800">Log de Execução</h3>
          </div>
          <div className="p-4 max-h-96 overflow-y-auto bg-surface-950 rounded-b-xl">
            <pre className="text-xs font-mono space-y-0.5">
              {log.map((l, i) => (
                <div key={i} className={l.ok ? 'text-emerald-400' : 'text-red-400'}>{l.msg}</div>
              ))}
            </pre>
          </div>
        </div>
      )}

      {/* Resumo das coleções */}
      <div className="card">
        <h3 className="text-sm font-semibold text-surface-800 mb-3">Coleções do Firestore</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {COLLECTION_MAP.map(([name]) => (
            <div key={name} className="px-3 py-2 bg-surface-50 rounded-lg">
              <p className="text-xs font-mono text-surface-600">{name}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
