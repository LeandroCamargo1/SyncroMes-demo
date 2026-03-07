// ══════════════════════════════════════════════════════════════
// Firestore Service — CRUD genérico + serviços por coleção
// Projeto Firebase: syncro-mes (independente)
// ══════════════════════════════════════════════════════════════
import {
  collection, doc, getDocs, getDoc, addDoc, updateDoc, deleteDoc,
  query, where, orderBy, limit, writeBatch, serverTimestamp,
  type QueryConstraint, type DocumentData,
} from 'firebase/firestore';
import { db } from '../lib/firebase';

// ── Helpers ─────────────────────────────────────────────────

/** Converte doc snapshot em objeto com id */
function docToObj<T = DocumentData>(snap: any): T & { id: string } {
  return { id: snap.id, ...snap.data() } as T & { id: string };
}

/** CRUD genérico para qualquer coleção */
export function createService<T = DocumentData>(collectionName: string) {
  const colRef = () => collection(db, collectionName);

  return {
    async getAll(...constraints: QueryConstraint[]): Promise<(T & { id: string })[]> {
      const q = constraints.length ? query(colRef(), ...constraints) : query(colRef());
      const snap = await getDocs(q);
      return snap.docs.map(d => docToObj<T>(d));
    },

    async getById(id: string): Promise<(T & { id: string }) | null> {
      const snap = await getDoc(doc(db, collectionName, id));
      return snap.exists() ? docToObj<T>(snap) : null;
    },

    async create(data: Partial<T>): Promise<string> {
      const ref = await addDoc(colRef(), { ...data, created_at: serverTimestamp(), updated_at: serverTimestamp() });
      return ref.id;
    },

    async update(id: string, data: Partial<T>): Promise<void> {
      await updateDoc(doc(db, collectionName, id), { ...data, updated_at: serverTimestamp() } as any);
    },

    async delete(id: string): Promise<void> {
      await deleteDoc(doc(db, collectionName, id));
    },

    /** Busca com filtros */
    async find(field: string, op: any, value: any, ...extra: QueryConstraint[]): Promise<(T & { id: string })[]> {
      const q = query(colRef(), where(field, op, value), ...extra);
      const snap = await getDocs(q);
      return snap.docs.map(d => docToObj<T>(d));
    },
  };
}

// ── Serviços por coleção ────────────────────────────────────

export const machinesService = createService('machines');
export const productsService = createService('products');
export const operatorsService = createService('operators');
export const usersService = createService('users');
export const productionOrdersService = createService('productionOrders');
export const productionEntriesService = createService('productionEntries');
export const activeDowntimesService = createService('activeDowntimes');
export const downtimeHistoryService = createService('downtimeHistory');
export const qualityMeasurementsService = createService('qualityMeasurements');
export const oeeHistoryService = createService('oeeHistory');
export const lossEntriesService = createService('lossEntries');
export const setupEntriesService = createService('setupEntries');
export const pmpEntriesService = createService('pmpEntries');
export const qualityLotsService = createService('qualityLots');
export const moldMaintenancesService = createService('moldMaintenances');
export const machineMaintenancesService = createService('machineMaintenances');
export const notificationsService = createService('notifications');
export const pcpMessagesService = createService('pcpMessages');
export const systemLogsService = createService('systemLogs');
export const operatorSchedulesService = createService('operatorSchedules');
export const absenteeismEntriesService = createService('absenteeismEntries');
export const sitesService = createService('sites');
export const areasService = createService('areas');
export const workCentersService = createService('workCenters');
export const moldsService = createService('molds');
export const materialsService = createService('materials');
export const bomLinesService = createService('bomLines');
export const inventoryMovementsService = createService('inventoryMovements');
export const planningService = createService('planning');
export const reworkEntriesService = createService('reworkEntries');
export const spcDataService = createService('spcData');
export const processSegmentsService = createService('processSegments');

// ── Batch write helper ──────────────────────────────────────

/** Escreve múltiplos documentos em uma coleção via batch (máx 500 por batch) */
export async function batchWrite(collectionName: string, items: Record<string, any>[]): Promise<number> {
  let written = 0;
  for (let i = 0; i < items.length; i += 400) {
    const batch = writeBatch(db);
    const chunk = items.slice(i, i + 400);
    for (const item of chunk) {
      const ref = doc(collection(db, collectionName));
      batch.set(ref, { ...item, created_at: serverTimestamp(), updated_at: serverTimestamp() });
    }
    await batch.commit();
    written += chunk.length;
  }
  return written;
}

/** Limpa uma coleção inteira (para reset de seed) */
export async function clearCollection(collectionName: string): Promise<number> {
  const snap = await getDocs(collection(db, collectionName));
  if (snap.empty) return 0;
  let deleted = 0;
  for (let i = 0; i < snap.docs.length; i += 400) {
    const batch = writeBatch(db);
    snap.docs.slice(i, i + 400).forEach(d => batch.delete(d.ref));
    await batch.commit();
    deleted += Math.min(400, snap.docs.length - i);
  }
  return deleted;
}
