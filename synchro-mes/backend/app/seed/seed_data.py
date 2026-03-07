"""
Seed — Popula o banco com dados fictícios para demonstração.

Fase 1 ISA-95: Todas as entidades usam FK integer IDs.
Entidades-pai são inseridas primeiro, flush para obter IDs,
e então entidades-filhas recebem os IDs via lookup dicts.
"""
import random
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.machine import Machine, Mold
from app.models.product import Product
from app.models.operator import Operator
from app.models.production import ProductionOrder, Planning, ProductionEntry
from app.models.downtime import ActiveDowntime, DowntimeHistory
from app.models.oee import OeeHistory
from app.models.quality import QualityMeasurement
from app.models.notification import Notification
from app.models.loss import LossEntry
from app.models.setup import SetupEntry
from app.models.pmp import PmpEntry
from app.models.quality_lot import QualityLot
from app.models.mold_maintenance import MoldMaintenance
from app.models.pcp import PcpMessage
from app.models.leadership import OperatorSchedule, AbsenteeismEntry
from app.models.hierarchy import Site, Area, WorkCenter
from app.models.material import Material, BomLine, InventoryMovement
from app.models.machine_maintenance import MachineMaintenance
from app.models.process_segment import ProcessSegment
from app.services.auth_service import AuthService


async def seed_all(db: AsyncSession):
    """Executa todo o seed — idempotente (verifica se já existe)."""
    existing = await db.execute(select(func.count(User.id)))
    if existing.scalar() > 0:
        print("[SEED] Banco já contém dados. Pulando seed.")
        return

    print("[SEED] Populando banco com dados fictícios...")

    # ── Fase 0: ISA-95 Equipment Hierarchy ───────────────────
    wc_ids = await _seed_hierarchy(db)

    # ── Fase 1: entidades-pai (sem dependências FK) ──────────
    await _seed_users(db)
    machine_ids = await _seed_machines(db, wc_ids)
    product_ids = await _seed_products(db)
    op_by_name, op_by_reg = await _seed_operators(db)

    # ── Fase 2: dependem de Fase 1 ──────────────────────────
    mold_ids = await _seed_molds(db, product_ids)
    material_ids = await _seed_materials(db)
    await _seed_bom(db, product_ids, material_ids)
    await _seed_process_segments(db, product_ids)

    # ── Fase 3: orders (dependem de products, machines) ─────
    order_ids = await _seed_production_orders(db, product_ids, machine_ids)

    # ── Fase 4: todas as demais entidades ────────────────────
    await _seed_planning(db, machine_ids, product_ids)
    await _seed_production_entries(db, machine_ids, product_ids, op_by_name)
    await _seed_downtimes(db, machine_ids, op_by_name)
    await _seed_oee_history(db, machine_ids)
    await _seed_quality(db, machine_ids, product_ids)
    await _seed_notifications(db, machine_ids)
    await _seed_losses(db, machine_ids, product_ids, order_ids)
    await _seed_setups(db, machine_ids, op_by_name)
    await _seed_pmp(db, machine_ids, op_by_name)
    await _seed_quality_lots(db, machine_ids, product_ids, order_ids)
    await _seed_mold_maintenance(db, mold_ids)
    await _seed_machine_maintenance(db, machine_ids)
    await _seed_pcp_messages(db, machine_ids)
    await _seed_leadership(db, op_by_reg, op_by_name, machine_ids)

    await db.commit()
    print("[SEED] Concluído — dados fictícios inseridos.")


# ── ISA-95 Equipment Hierarchy ────────────────────────────────
async def _seed_hierarchy(db: AsyncSession) -> dict[str, int]:
    """Cria Site → Area → WorkCenter. Retorna {wc_code: id}."""
    site = Site(code="SITE-01", name="Planta Industrial Principal",
                address="Rua Industrial, 500", city="São Paulo", state="SP")
    db.add(site)
    await db.flush()

    areas_data = [
        ("AREA-INJ", "Área de Injeção", site.id),
        ("AREA-MON", "Área de Montagem", site.id),
        ("AREA-ALM", "Almoxarifado", site.id),
    ]
    areas = {}
    for code, name, sid in areas_data:
        a = Area(code=code, name=name, site_id=sid)
        db.add(a)
        areas[code] = a
    await db.flush()

    wcs_data = [
        ("WC-INJ-A", "Centro de Trabalho Injeção A", areas["AREA-INJ"].id, 5),
        ("WC-INJ-B", "Centro de Trabalho Injeção B", areas["AREA-INJ"].id, 5),
        ("WC-MON-1", "Centro de Montagem 1", areas["AREA-MON"].id, 3),
    ]
    wcs = {}
    for code, name, aid, cap in wcs_data:
        wc = WorkCenter(code=code, name=name, area_id=aid, capacity=cap)
        db.add(wc)
        wcs[code] = wc
    await db.flush()
    return {code: wc.id for code, wc in wcs.items()}


# ── Users ─────────────────────────────────────────────────────
async def _seed_users(db: AsyncSession):
    users = [
        {"email": "admin@demo-mes.app", "name": "Administrador Demo", "role": "admin", "initials": "AD"},
        {"email": "supervisor@demo-mes.app", "name": "Carlos Supervisor", "role": "supervisor", "initials": "CS"},
        {"email": "operador@demo-mes.app", "name": "Roberto Operador", "role": "operador", "initials": "RO"},
        {"email": "qualidade@demo-mes.app", "name": "Ana Qualidade", "role": "qualidade", "initials": "AQ"},
        {"email": "pcp@demo-mes.app", "name": "Marcos PCP", "role": "pcp", "initials": "MP"},
    ]
    pwd = AuthService.hash_password("demo1234")
    perms_map = {
        "admin": ["dashboard", "producao", "qualidade", "paradas", "planejamento", "relatorios", "admin", "usuarios", "configuracoes", "lideranca", "pcp", "ferramentaria", "setup", "pmp", "historico"],
        "supervisor": ["dashboard", "producao", "qualidade", "paradas", "planejamento", "relatorios", "lideranca", "setup", "pmp", "ferramentaria"],
        "operador": ["dashboard", "producao", "paradas", "setup", "pmp"],
        "qualidade": ["dashboard", "qualidade", "relatorios", "ferramentaria"],
        "pcp": ["dashboard", "planejamento", "relatorios", "pcp", "producao"],
    }
    for u in users:
        db.add(User(
            email=u["email"], name=u["name"], hashed_password=pwd,
            role=u["role"], avatar_initials=u["initials"],
            custom_claims={"role": u["role"], "permissions": perms_map[u["role"]]},
        ))
    await db.flush()


# ── Machines ──────────────────────────────────────────────────
async def _seed_machines(db: AsyncSession, wc_ids: dict[str, int]) -> dict[str, int]:
    """Retorna {code: id}."""
    statuses = ["running", "running", "running", "running", "stopped",
                "running", "maintenance", "running", "stopped", "running"]
    products = ["TFT-28", "FR-500", "PF-22G", "CV-110", None,
                "BR-45", None, "TFT-28", None, "PL-80"]
    operators = ["Roberto Silva", "Ana Costa", "Pedro Santos", "Maria Oliveira",
                 None, "João Lima", None, "Carlos Ferreira", None, "Luiza Souza"]
    # Map machines to work centers
    wc_assignments = [
        "WC-INJ-A", "WC-INJ-A", "WC-INJ-A", "WC-INJ-A", "WC-INJ-A",
        "WC-INJ-B", "WC-INJ-B", "WC-INJ-B", "WC-INJ-B", "WC-INJ-B",
    ]
    machines = []
    for i in range(1, 11):
        m = Machine(
            code=f"INJ-{i:02d}", name=f"Injetora {i:02d}", type="injetora",
            tonnage=random.choice([150, 250, 350, 450, 550, 650]),
            status=statuses[i - 1], current_product=products[i - 1],
            current_operator=operators[i - 1],
            cycle_time_seconds=random.uniform(18, 45),
            cavities=random.choice([1, 2, 4, 6, 8]),
            efficiency=random.uniform(65, 95),
            work_center_id=wc_ids.get(wc_assignments[i - 1]),
        )
        db.add(m)
        machines.append(m)
    await db.flush()
    return {m.code: m.id for m in machines}


# ── Products ──────────────────────────────────────────────────
async def _seed_products(db: AsyncSession) -> dict[str, int]:
    """Retorna {code: id}."""
    prods = [
        ("TFT-28", "Tampa Flip-Top 28mm", 4.2, "PP", "branco"),
        ("FR-500", "Frasco 500ml", 32.5, "PET", "transparente"),
        ("PF-22G", "Preforma 22g", 22.0, "PET", "transparente"),
        ("CV-110", "Conector Veicular 110", 8.7, "PA6.6", "preto"),
        ("BR-45", "Bucha Redonda 45mm", 15.3, "PP", "cinza"),
        ("PL-80", "Pallet Liso 80x80", 1200.0, "PEAD", "preto"),
        ("CX-200", "Caixa Organizadora 200L", 850.0, "PP", "azul"),
        ("TB-12", "Tubete 12mm", 3.8, "PS", "branco"),
        ("RG-30", "Rótulo Garra 30mm", 1.2, "PP", "branco"),
        ("FD-60", "Flange Diâmetro 60", 45.0, "POM", "natural"),
        ("GR-25", "Grade Retangular 25L", 380.0, "PEAD", "verde"),
        ("TP-500", "Tampa Press-On 500", 12.0, "PP", "vermelho"),
    ]
    products = []
    for code, name, weight, material, color in prods:
        p = Product(
            code=code, name=name, weight_grams=weight,
            material=material, color=color,
            cycle_time_ideal=random.uniform(15, 40),
            cavities=random.choice([1, 2, 4]),
        )
        db.add(p)
        products.append(p)
    await db.flush()
    return {p.code: p.id for p in products}


# ── Molds ─────────────────────────────────────────────────────
async def _seed_molds(db: AsyncSession, product_ids: dict[str, int]) -> dict[str, int]:
    """Retorna {code: id}."""
    molds_data = [
        ("MLD-001", "Molde Tampa FT 28", 4, "TFT-28", 18.5),
        ("MLD-002", "Molde Frasco 500", 1, "FR-500", 35.0),
        ("MLD-003", "Molde Preforma 22g", 8, "PF-22G", 12.0),
        ("MLD-004", "Molde Conector V110", 2, "CV-110", 28.0),
        ("MLD-005", "Molde Bucha R45", 2, "BR-45", 22.0),
        ("MLD-006", "Molde Pallet 80", 1, "PL-80", 90.0),
    ]
    molds = []
    for code, name, cav, prod_code, cycle in molds_data:
        m = Mold(
            code=code, name=name, cavities=cav,
            product_id=product_ids[prod_code],
            cycle_time_ideal=cycle,
            total_cycles=random.randint(10000, 500000),
            status=random.choice(["disponivel", "em_uso"]),
        )
        db.add(m)
        molds.append(m)
    await db.flush()
    return {m.code: m.id for m in molds}


# ── Operators ────────────────────────────────────────────────
async def _seed_operators(db: AsyncSession) -> tuple[dict[str, int], dict[str, int]]:
    """Retorna (name->id, registration->id)."""
    names = [
        ("OP-001", "Roberto Silva", "A"), ("OP-002", "Ana Costa", "A"),
        ("OP-003", "Pedro Santos", "A"), ("OP-004", "Maria Oliveira", "B"),
        ("OP-005", "João Lima", "B"), ("OP-006", "Carlos Ferreira", "B"),
        ("OP-007", "Luiza Souza", "C"), ("OP-008", "Fernando Alves", "C"),
        ("OP-009", "Patricia Ramos", "C"), ("OP-010", "Ricardo Mendes", "A"),
        ("OP-011", "Claudia Nunes", "B"), ("OP-012", "Diego Torres", "C"),
        ("OP-013", "Juliana Pires", "A"), ("OP-014", "Marcos Ribeiro", "B"),
        ("OP-015", "Vanessa Lima", "C"),
    ]
    ops = []
    for reg, name, shift in names:
        o = Operator(
            registration=reg, name=name, shift=shift,
            skills=[f"INJ-{random.randint(1, 10):02d}" for _ in range(random.randint(2, 5))],
        )
        db.add(o)
        ops.append(o)
    await db.flush()
    by_name = {o.name: o.id for o in ops}
    by_reg = {o.registration: o.id for o in ops}
    return by_name, by_reg


# ── Production Orders ────────────────────────────────────────
async def _seed_production_orders(
    db: AsyncSession, product_ids: dict[str, int], machine_ids: dict[str, int]
) -> dict[str, int]:
    """Retorna {order_number: id}."""
    statuses = ["in_progress", "in_progress", "planned", "planned", "completed",
                "in_progress", "planned", "completed", "in_progress", "planned",
                "planned", "completed"]
    product_codes = ["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45", "PL-80",
                     "CX-200", "TB-12", "RG-30", "FD-60", "GR-25", "TP-500"]
    names = ["Tampa Flip-Top 28mm", "Frasco 500ml", "Preforma 22g",
             "Conector Veicular 110", "Bucha Redonda 45mm", "Pallet Liso 80x80",
             "Caixa Organizadora 200L", "Tubete 12mm", "Rótulo Garra 30mm",
             "Flange Diâmetro 60", "Grade Retangular 25L", "Tampa Press-On 500"]
    clients = ["AutoParts Ltda", "Embala Tudo", "PetBrasil S.A.", "VeiculTech",
               "Plásticos Unidos", "LogPack", "CasaOrg", "TuboFlex",
               "RotuloPro", "TechFlange", "AgriPlast", "TampaBrasil"]

    today = date.today()
    orders = []
    for i in range(12):
        qty = random.randint(5000, 50000)
        produced = random.randint(0, qty) if statuses[i] != "planned" else 0
        good = int(produced * random.uniform(0.92, 0.99))
        machine_code = f"INJ-{(i % 10) + 1:02d}"
        o = ProductionOrder(
            order_number=f"OP-2025-{i + 1:03d}",
            product_id=product_ids[product_codes[i]],
            product_name=names[i],
            quantity_planned=qty, quantity_produced=produced,
            quantity_good=good, quantity_rejected=produced - good,
            status=statuses[i],
            priority=random.choice(["normal", "high", "urgent"]),
            machine_id=machine_ids[machine_code],
            client=clients[i],
            due_date=today + timedelta(days=random.randint(1, 14)),
        )
        db.add(o)
        orders.append(o)
    await db.flush()
    return {o.order_number: o.id for o in orders}


# ── Planning ─────────────────────────────────────────────────
async def _seed_planning(
    db: AsyncSession, machine_ids: dict[str, int], product_ids: dict[str, int]
):
    today = date.today()
    product_codes = ["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45", "PL-80"]
    names = ["Tampa Flip-Top 28mm", "Frasco 500ml", "Preforma 22g",
             "Conector Veicular 110", "Bucha Redonda 45mm", "Pallet Liso 80x80"]
    for day_offset in range(7):
        d = today + timedelta(days=day_offset)
        for machine_idx in range(1, 11):
            prod_idx = random.randint(0, len(product_codes) - 1)
            machine_code = f"INJ-{machine_idx:02d}"
            db.add(Planning(
                machine_id=machine_ids[machine_code],
                product_id=product_ids[product_codes[prod_idx]],
                product_name=names[prod_idx],
                quantity_planned=random.randint(2000, 20000),
                date=d, shift=random.choice(["A", "B", "C"]),
                cycle_time_seconds=random.uniform(15, 45),
                cavities=random.choice([1, 2, 4]),
                weight_grams=random.uniform(2, 50),
                material=random.choice(["PP", "PET", "PEAD", "PA6.6"]),
                sequence=1,
                status="pendente" if day_offset > 0 else "em_andamento",
            ))


# ── Production Entries ────────────────────────────────────────
async def _seed_production_entries(
    db: AsyncSession, machine_ids: dict[str, int],
    product_ids: dict[str, int], op_by_name: dict[str, int]
):
    today = datetime.now(timezone.utc)
    operator_names = ["Roberto Silva", "Ana Costa", "Pedro Santos", "Maria Oliveira"]
    product_codes = ["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45", "PL-80"]
    for day_offset in range(30):
        ts = today - timedelta(days=day_offset)
        for machine_idx in range(1, 11):
            machine_code = f"INJ-{machine_idx:02d}"
            for _ in range(random.randint(2, 6)):
                good = random.randint(100, 2000)
                rej = random.randint(0, int(good * 0.08))
                prod_code = random.choice(product_codes)
                op_name = random.choice(operator_names)
                db.add(ProductionEntry(
                    machine_id=machine_ids[machine_code],
                    product_id=product_ids[prod_code],
                    operator_id=op_by_name[op_name],
                    shift=random.choice(["A", "B", "C"]),
                    quantity_good=good, quantity_rejected=rej,
                    cycle_time_actual=random.uniform(15, 50),
                    timestamp=ts - timedelta(hours=random.randint(0, 8)),
                ))


# ── Downtimes ─────────────────────────────────────────────────
async def _seed_downtimes(
    db: AsyncSession, machine_ids: dict[str, int], op_by_name: dict[str, int]
):
    categories = ["mecanica", "eletrica", "setup", "processo",
                  "qualidade", "falta_material", "programada"]
    reasons = [
        "Troca de molde", "Falha no bico injetor", "Aquecimento irregular",
        "Falta de matéria-prima", "Manutenção preventiva", "Ajuste de parâmetros",
        "Defeito no produto", "Problema elétrico", "Troca de cor",
        "Limpeza de molde", "Quebra de extrator", "Setup de máquina",
    ]
    today = datetime.now(timezone.utc)
    operator_names = ["Roberto Silva", "Ana Costa", "Pedro Santos"]

    # Paradas ativas (2 máquinas paradas)
    db.add(ActiveDowntime(
        machine_id=machine_ids["INJ-05"],
        reason="Troca de molde", category="setup",
        operator_id=op_by_name["Roberto Silva"],
        shift="A", start_time=today - timedelta(minutes=45),
    ))
    db.add(ActiveDowntime(
        machine_id=machine_ids["INJ-09"],
        reason="Falta de matéria-prima", category="falta_material",
        operator_id=op_by_name["Pedro Santos"],
        shift="A", start_time=today - timedelta(minutes=120),
    ))

    # Histórico (30 dias)
    for day_offset in range(30):
        for _ in range(random.randint(3, 8)):
            start = today - timedelta(days=day_offset, hours=random.randint(0, 20))
            dur = random.uniform(5, 120)
            machine_code = f"INJ-{random.randint(1, 10):02d}"
            op_name = random.choice(operator_names)
            db.add(DowntimeHistory(
                machine_id=machine_ids[machine_code],
                reason=random.choice(reasons),
                category=random.choice(categories),
                operator_id=op_by_name[op_name],
                shift=random.choice(["A", "B", "C"]),
                start_time=start,
                end_time=start + timedelta(minutes=dur),
                duration_minutes=round(dur, 1),
                is_planned=random.random() < 0.2,
            ))


# ── OEE History ───────────────────────────────────────────────
async def _seed_oee_history(db: AsyncSession, machine_ids: dict[str, int]):
    today = date.today()
    for day_offset in range(30):
        d = today - timedelta(days=day_offset)
        for machine_idx in range(1, 11):
            avail = random.uniform(75, 98)
            perf = random.uniform(70, 99)
            qual = random.uniform(90, 99.5)
            oee = (avail * perf * qual) / 10000
            total = random.randint(500, 5000)
            good = int(total * qual / 100)
            planned = 480.0
            running = planned * avail / 100
            machine_code = f"INJ-{machine_idx:02d}"
            db.add(OeeHistory(
                machine_id=machine_ids[machine_code],
                date=d, shift=random.choice(["A", "B", "C"]),
                availability=round(avail, 1), performance=round(perf, 1),
                quality_rate=round(qual, 1), oee=round(oee, 1),
                planned_time_minutes=planned,
                running_time_minutes=round(running, 1),
                downtime_minutes=round(planned - running, 1),
                total_produced=total, good_produced=good,
                rejected=total - good,
                ideal_cycle_seconds=random.uniform(15, 40),
            ))


# ── Quality Measurements ─────────────────────────────────────
async def _seed_quality(
    db: AsyncSession, machine_ids: dict[str, int], product_ids: dict[str, int]
):
    today = datetime.now(timezone.utc)
    dimensions = ["Diâmetro externo", "Altura", "Espessura parede",
                  "Peso", "Diâmetro interno"]
    defects = ["rebarba", "bolha", "mancha", "dimensional", "deformação"]
    product_codes = ["TFT-28", "FR-500", "PF-22G", "CV-110"]

    for day_offset in range(15):
        for _ in range(random.randint(5, 15)):
            nominal = random.uniform(10, 100)
            tolerance = nominal * 0.02
            measured = nominal + random.uniform(-tolerance * 1.5, tolerance * 1.5)
            approved = abs(measured - nominal) <= tolerance
            machine_code = f"INJ-{random.randint(1, 10):02d}"
            prod_code = random.choice(product_codes)
            db.add(QualityMeasurement(
                machine_id=machine_ids[machine_code],
                product_id=product_ids[prod_code],
                inspector=random.choice(["Ana Qualidade", "Paulo Inspetor"]),
                dimension_name=random.choice(dimensions),
                nominal_value=round(nominal, 2),
                measured_value=round(measured, 2),
                tolerance_upper=round(nominal + tolerance, 2),
                tolerance_lower=round(nominal - tolerance, 2),
                is_approved=approved,
                defect_type=random.choice(defects) if not approved else None,
                defect_severity=random.choice(["minor", "major", "critical"]) if not approved else None,
                timestamp=today - timedelta(days=day_offset, hours=random.randint(0, 8)),
            ))


# ── Notifications ─────────────────────────────────────────────
async def _seed_notifications(db: AsyncSession, machine_ids: dict[str, int]):
    db.add(Notification(
        title="Máquina INJ-05 parada",
        message="Parada há mais de 30 minutos — troca de molde",
        type="warning", machine_id=machine_ids["INJ-05"],
    ))
    db.add(Notification(
        title="OEE abaixo da meta",
        message="INJ-03 com OEE de 62% — abaixo da meta de 75%",
        type="error", machine_id=machine_ids["INJ-03"],
    ))
    db.add(Notification(
        title="Ordem OP-2025-001 completa",
        message="100% da quantidade planejada atingida",
        type="success",
    ))
    db.add(Notification(
        title="Manutenção preventiva",
        message="INJ-07 tem manutenção programada para amanhã",
        type="info", machine_id=machine_ids["INJ-07"],
    ))


# ── Losses ────────────────────────────────────────────────────
async def _seed_losses(
    db: AsyncSession, machine_ids: dict[str, int],
    product_ids: dict[str, int], order_ids: dict[str, int]
):
    categories = ["refugo", "rebarba", "dimensional", "cor", "contaminacao"]
    materials = ["PP", "PET", "PEAD", "PA6.6", "PS", "POM"]
    product_codes = ["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45"]
    today = datetime.now(timezone.utc)
    order_numbers = list(order_ids.keys())

    for day_offset in range(15):
        for _ in range(random.randint(2, 6)):
            machine_code = f"INJ-{random.randint(1, 10):02d}"
            prod_code = random.choice(product_codes)
            order_num = random.choice(order_numbers)
            db.add(LossEntry(
                machine_id=machine_ids[machine_code],
                product_id=product_ids[prod_code],
                order_id=order_ids[order_num],
                quantity=random.randint(5, 200),
                weight_kg=round(random.uniform(0.1, 15.0), 2),
                reason=random.choice([
                    "Rebarba excessiva", "Fora de dimensional",
                    "Contaminação", "Cor irregular", "Bolha",
                ]),
                category=random.choice(categories),
                material=random.choice(materials),
                is_manual=random.random() < 0.3,
                timestamp=today - timedelta(days=day_offset, hours=random.randint(0, 8)),
            ))


# ── Setup Entries ─────────────────────────────────────────────
async def _seed_setups(
    db: AsyncSession, machine_ids: dict[str, int], op_by_name: dict[str, int]
):
    setup_types = ["troca_molde", "troca_cor", "troca_material", "ajuste"]
    mold_codes = ["MLD-001", "MLD-002", "MLD-003", "MLD-004", "MLD-005", "MLD-006"]
    operator_names = ["Roberto Silva", "Ana Costa", "Pedro Santos"]
    today = datetime.now(timezone.utc)
    for day_offset in range(10):
        for _ in range(random.randint(1, 4)):
            start = today - timedelta(days=day_offset, hours=random.randint(1, 20))
            dur = random.uniform(10, 90)
            machine_code = f"INJ-{random.randint(1, 10):02d}"
            op_name = random.choice(operator_names)
            db.add(SetupEntry(
                machine_id=machine_ids[machine_code],
                setup_type=random.choice(setup_types),
                mold_from=random.choice(mold_codes),
                mold_to=random.choice(mold_codes),
                product_from=random.choice(["TFT-28", "FR-500", "PF-22G"]),
                product_to=random.choice(["CV-110", "BR-45", "PL-80"]),
                start_time=start,
                end_time=start + timedelta(minutes=dur),
                duration_minutes=round(dur, 1),
                status="concluido",
                operator_id=op_by_name[op_name],
            ))


# ── PMP (Moído/Borra/Sucata) ─────────────────────────────────
async def _seed_pmp(
    db: AsyncSession, machine_ids: dict[str, int], op_by_name: dict[str, int]
):
    pmp_types = ["moido", "borra", "sucata"]
    destinations = ["reprocesso", "descarte", "venda"]
    operator_names = ["Roberto Silva", "Ana Costa", "Pedro Santos"]
    today = datetime.now(timezone.utc)
    for day_offset in range(15):
        for _ in range(random.randint(1, 5)):
            machine_code = f"INJ-{random.randint(1, 10):02d}"
            op_name = random.choice(operator_names)
            db.add(PmpEntry(
                type=random.choice(pmp_types),
                machine_id=machine_ids[machine_code],
                weight_kg=round(random.uniform(0.5, 50.0), 2),
                destination=random.choice(destinations),
                material=random.choice(["PP", "PET", "PEAD", "PA6.6"]),
                operator_id=op_by_name[op_name],
                notes=random.choice(["", "Lote contaminado", "Reprocesso programado", ""]),
                timestamp=today - timedelta(days=day_offset, hours=random.randint(0, 8)),
            ))


# ── Quality Lots ──────────────────────────────────────────────
async def _seed_quality_lots(
    db: AsyncSession, machine_ids: dict[str, int],
    product_ids: dict[str, int], order_ids: dict[str, int]
):
    statuses = ["quarentena", "em_triagem", "concluida"]
    product_codes = ["TFT-28", "FR-500", "PF-22G", "CV-110"]
    today = datetime.now(timezone.utc)
    order_numbers = list(order_ids.keys())

    for i in range(15):
        status = random.choice(statuses)
        approved = random.randint(500, 5000) if status == "concluida" else 0
        rejected = random.randint(10, 200) if status == "concluida" else 0
        machine_code = f"INJ-{random.randint(1, 10):02d}"
        prod_code = random.choice(product_codes)
        order_num = random.choice(order_numbers)
        db.add(QualityLot(
            lot_number=f"LOT-2025-{i + 1:04d}",
            product_id=product_ids[prod_code],
            machine_id=machine_ids[machine_code],
            order_id=order_ids[order_num],
            quantity=random.randint(1000, 10000),
            reason=random.choice([
                "Variação dimensional", "Contaminação",
                "Cor fora do padrão", "Rebarbas excessivas",
                "Inspeção de lote",
            ]),
            status=status,
            approved_qty=approved,
            rejected_qty=rejected,
            returned_to_production=random.choice([True, False]) if status == "concluida" else False,
            inspector=random.choice(["Ana Qualidade", "Paulo Inspetor"]),
            concluded_at=today - timedelta(days=i) if status == "concluida" else None,
        ))


# ── Mold Maintenance ─────────────────────────────────────────
async def _seed_mold_maintenance(db: AsyncSession, mold_ids: dict[str, int]):
    mold_codes = list(mold_ids.keys())
    maint_types = ["preventiva", "corretiva", "limpeza"]
    statuses = ["concluida", "concluida", "pendente", "em_andamento"]
    today = datetime.now(timezone.utc)
    for i in range(10):
        status = random.choice(statuses)
        start = today - timedelta(days=i * 3, hours=random.randint(1, 12))
        dur_h = round(random.uniform(0.5, 8.0), 1)
        end = start + timedelta(hours=dur_h) if status == "concluida" else None
        mold_code = random.choice(mold_codes)
        db.add(MoldMaintenance(
            mold_id=mold_ids[mold_code],
            maintenance_type=random.choice(maint_types),
            technician=random.choice(["Técnico A", "Técnico B", "Técnico C"]),
            description=random.choice([
                "Troca de pinos extratores", "Polimento cavidade",
                "Limpeza geral", "Reparo canal quente", "Troca anel O-Ring",
            ]),
            start_time=start,
            end_time=end,
            duration_hours=dur_h if status == "concluida" else None,
            cost=round(random.uniform(100, 5000), 2) if status == "concluida" else None,
            parts_replaced=random.choice(["Pinos, Molas", "Anel O-Ring", "Bico injetor", None]),
            status=status,
        ))


# ── PCP Messages ─────────────────────────────────────────────
async def _seed_pcp_messages(db: AsyncSession, machine_ids: dict[str, int]):
    messages = [
        ("Priorizar OP-2025-001 — cliente urgente", 5, "urgent", "INJ-01"),
        ("Troca de produto INJ-03 às 14h", 3, "info", "INJ-03"),
        ("Material PP azul em falta — previsão amanhã", 4, "warning", None),
        ("Meta turno A: 15.000 peças", 2, "info", None),
        ("INJ-07 liberada após manutenção", 3, "info", "INJ-07"),
        ("Auditor externo amanhã — preparar documentação", 4, "warning", None),
    ]
    for msg, priority, msg_type, machine_code in messages:
        db.add(PcpMessage(
            message=msg, priority=priority, type=msg_type,
            target_machine_id=machine_ids[machine_code] if machine_code else None,
            is_active=True,
        ))


# ── Leadership (Escala + Absenteísmo) ────────────────────────
async def _seed_leadership(
    db: AsyncSession, op_by_reg: dict[str, int],
    op_by_name: dict[str, int], machine_ids: dict[str, int]
):
    operators = [
        ("OP-001", "Roberto Silva"), ("OP-002", "Ana Costa"),
        ("OP-003", "Pedro Santos"), ("OP-004", "Maria Oliveira"),
        ("OP-005", "João Lima"), ("OP-006", "Carlos Ferreira"),
        ("OP-007", "Luiza Souza"), ("OP-008", "Fernando Alves"),
        ("OP-009", "Patricia Ramos"),
    ]
    today = date.today()
    for day_offset in range(7):
        d = today + timedelta(days=day_offset)
        for reg, name in operators[:6]:
            machine_code = f"INJ-{random.randint(1, 10):02d}"
            db.add(OperatorSchedule(
                operator_id=op_by_reg[reg],
                operator_name=name,
                date=d,
                shift=random.choice(["A", "B", "C"]),
                machine_id=machine_ids[machine_code],
                position=random.choice(["operador", "lider", "auxiliar"]),
            ))

    # Absenteísmo
    reasons = ["falta", "atestado", "atraso", "ferias", "folga"]
    for _ in range(12):
        reg, name = random.choice(operators)
        d = today - timedelta(days=random.randint(1, 30))
        db.add(AbsenteeismEntry(
            operator_id=op_by_reg[reg],
            operator_name=name,
            date=d,
            shift=random.choice(["A", "B", "C"]),
            reason=random.choice(reasons),
            hours_absent=random.randint(1, 8),
            justified=random.random() < 0.6,
            notes=random.choice(["", "Atestado médico", "Atraso transporte", ""]),
        ))


# ── Materials ─────────────────────────────────────────────────
async def _seed_materials(db: AsyncSession) -> dict[str, int]:
    """Retorna {code: id}."""
    materials_data = [
        ("MAT-PP", "Polipropileno (PP)", "resina", "kg", 0.91, "BrasilPlas", 500),
        ("MAT-PET", "PET Grau Garrafa", "resina", "kg", 1.38, "PetroMat", 300),
        ("MAT-PA66", "Poliamida 6.6", "resina", "kg", 1.14, "EngPlast", 100),
        ("MAT-PEAD", "PEAD Alta Densidade", "resina", "kg", 0.95, "PoliVerde", 400),
        ("MAT-PS", "Poliestireno (PS)", "resina", "kg", 1.04, "EstirenoBR", 200),
        ("MAT-POM", "Poliacetal (POM)", "resina", "kg", 1.41, "TechPoly", 50),
        ("MAT-MB-BR", "Masterbatch Branco TiO2", "masterbatch", "kg", None, "ColorMix", 50),
        ("MAT-MB-PT", "Masterbatch Preto Carbon", "masterbatch", "kg", None, "ColorMix", 50),
        ("MAT-MB-AZ", "Masterbatch Azul 2040", "masterbatch", "kg", None, "ColorMix", 30),
        ("MAT-MB-VM", "Masterbatch Vermelho 1020", "masterbatch", "kg", None, "ColorMix", 20),
        ("MAT-MB-VD", "Masterbatch Verde 3060", "masterbatch", "kg", None, "ColorMix", 20),
        ("MAT-AD-UV", "Aditivo UV Estabilizante", "aditivo", "kg", None, "AddChem", 25),
        ("MAT-AD-AO", "Antioxidante Primário", "aditivo", "kg", None, "AddChem", 25),
        ("EMB-CX-01", "Caixa Papelão 60x40x30", "embalagem", "un", None, "EmbalPack", 500),
        ("EMB-SC-01", "Saco PE 80x120cm", "embalagem", "un", None, "EmbalPack", 1000),
    ]
    mats = []
    for code, name, mat_type, unit, density, supplier, min_stock in materials_data:
        m = Material(
            code=code, name=name, type=mat_type, unit=unit,
            density=density, supplier=supplier, min_stock=min_stock,
            current_stock=round(random.uniform(min_stock * 0.3, min_stock * 2.0), 1),
            cost_per_unit=round(random.uniform(5, 80), 2),
        )
        db.add(m)
        mats.append(m)
    await db.flush()
    return {m.code: m.id for m in mats}


# ── BOM ───────────────────────────────────────────────────────
async def _seed_bom(db: AsyncSession, product_ids: dict[str, int], material_ids: dict[str, int]):
    bom_data = [
        ("TFT-28", "MAT-PP", 0.0042, True), ("TFT-28", "MAT-MB-BR", 0.00012, False),
        ("FR-500", "MAT-PET", 0.0325, True),
        ("PF-22G", "MAT-PET", 0.0220, True),
        ("CV-110", "MAT-PA66", 0.0087, True), ("CV-110", "MAT-MB-PT", 0.00026, False),
        ("BR-45", "MAT-PP", 0.0153, True), ("BR-45", "MAT-MB-BR", 0.0005, False),
        ("PL-80", "MAT-PEAD", 1.2000, True), ("PL-80", "MAT-MB-PT", 0.036, False),
        ("CX-200", "MAT-PP", 0.8500, True), ("CX-200", "MAT-MB-AZ", 0.025, False),
        ("TB-12", "MAT-PS", 0.0038, True),
        ("RG-30", "MAT-PP", 0.0012, True),
        ("FD-60", "MAT-POM", 0.0450, True),
        ("GR-25", "MAT-PEAD", 0.3800, True), ("GR-25", "MAT-MB-VD", 0.011, False),
        ("TP-500", "MAT-PP", 0.0120, True), ("TP-500", "MAT-MB-VM", 0.0004, False),
    ]
    for prod_code, mat_code, qty, is_primary in bom_data:
        db.add(BomLine(
            product_id=product_ids[prod_code],
            material_id=material_ids[mat_code],
            quantity_per_unit=qty,
            is_primary=is_primary,
        ))
    await db.flush()


# ── Process Segments ─────────────────────────────────────────
async def _seed_process_segments(db: AsyncSession, product_ids: dict[str, int]):
    segments = [
        ("TFT-28", 18.5, 800, 400, 220, 45, 6.0, 120, 80, 8, 150),
        ("FR-500", 35.0, 1200, 600, 270, 25, 12.0, 80, 120, 12, 250),
        ("PF-22G", 12.0, 1500, 700, 280, 20, 4.0, 150, 100, 6, 200),
        ("CV-110", 28.0, 900, 500, 290, 80, 8.0, 100, 60, 10, 350),
        ("BR-45", 22.0, 700, 350, 210, 40, 7.0, 90, 70, 8, 200),
        ("PL-80", 90.0, 600, 300, 200, 60, 30.0, 60, 150, 15, 550),
    ]
    for code, cycle, inj_p, hold_p, melt_t, mold_t, cool, inj_s, screw, back_p, clamp in segments:
        db.add(ProcessSegment(
            product_id=product_ids[code],
            cycle_time_ideal=cycle,
            injection_pressure=inj_p,
            holding_pressure=hold_p,
            melt_temperature=melt_t,
            mold_temperature=mold_t,
            cooling_time=cool,
            injection_speed=inj_s,
            screw_rpm=screw,
            back_pressure=back_p,
            clamping_force=clamp,
        ))
    await db.flush()


# ── Machine Maintenance ──────────────────────────────────────
async def _seed_machine_maintenance(db: AsyncSession, machine_ids: dict[str, int]):
    machine_codes = list(machine_ids.keys())
    today = datetime.now(timezone.utc)
    for i in range(15):
        status = random.choice(["concluida", "concluida", "pendente", "em_andamento"])
        start = today - timedelta(days=i * 5, hours=random.randint(1, 12))
        dur_h = round(random.uniform(0.5, 12.0), 1)
        end = start + timedelta(hours=dur_h) if status == "concluida" else None
        code = random.choice(machine_codes)
        db.add(MachineMaintenance(
            machine_id=machine_ids[code],
            maintenance_type=random.choice(["preventiva", "corretiva", "limpeza"]),
            priority=random.choice(["baixa", "media", "alta", "critica"]),
            description=random.choice([
                "Troca de óleo hidráulico", "Alinhamento platô",
                "Limpeza geral cilindro", "Substituição resistências",
                "Calibração sensores pressão", "Revisão unidade injeção",
                "Troca filtro hidráulico", "Ajuste paralelo platôs",
            ]),
            technician=random.choice(["Manutentor A", "Manutentor B", "Manutentor C"]),
            scheduled_date=(today + timedelta(days=random.randint(-10, 10))).date(),
            start_time=start if status != "pendente" else None,
            end_time=end,
            duration_hours=dur_h if status == "concluida" else None,
            cost=round(random.uniform(200, 15000), 2) if status == "concluida" else 0,
            parts_replaced=random.choice([
                "Filtro hidráulico, O-Ring", "Resistência cilindro",
                "Sensor pressão SPX-2", "Mangueira hidráulica", None,
            ]),
            status=status,
        ))
