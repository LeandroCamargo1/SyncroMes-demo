"""
Seed — Popula o banco com dados fictícios para demonstração
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
from app.services.auth_service import AuthService


async def seed_all(db: AsyncSession):
    """Executa todo o seed — idempotente (verifica se já existe)."""
    existing = await db.execute(select(func.count(User.id)))
    if existing.scalar() > 0:
        print("[SEED] Banco já contém dados. Pulando seed.")
        return

    print("[SEED] Populando banco com dados fictícios...")
    await _seed_users(db)
    await _seed_machines(db)
    await _seed_products(db)
    await _seed_molds(db)
    await _seed_operators(db)
    await _seed_production_orders(db)
    await _seed_planning(db)
    await _seed_production_entries(db)
    await _seed_downtimes(db)
    await _seed_oee_history(db)
    await _seed_quality(db)
    await _seed_notifications(db)
    await _seed_losses(db)
    await _seed_setups(db)
    await _seed_pmp(db)
    await _seed_quality_lots(db)
    await _seed_mold_maintenance(db)
    await _seed_pcp_messages(db)
    await _seed_leadership(db)
    await db.commit()
    print("[SEED] Concluído — dados fictícios inseridos.")


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


# ── Machines ──────────────────────────────────────────────────
async def _seed_machines(db: AsyncSession):
    statuses = ["running", "running", "running", "running", "stopped", "running", "maintenance", "running", "stopped", "running"]
    products = ["TFT-28", "FR-500", "PF-22G", "CV-110", None, "BR-45", None, "TFT-28", None, "PL-80"]
    operators = ["Roberto Silva", "Ana Costa", "Pedro Santos", "Maria Oliveira", None, "João Lima", None, "Carlos Ferreira", None, "Luiza Souza"]
    for i in range(1, 11):
        code = f"INJ-{i:02d}"
        db.add(Machine(
            code=code, name=f"Injetora {i:02d}", type="injetora",
            tonnage=random.choice([150, 250, 350, 450, 550, 650]),
            status=statuses[i - 1], current_product=products[i - 1],
            current_operator=operators[i - 1],
            cycle_time_seconds=random.uniform(18, 45),
            cavities=random.choice([1, 2, 4, 6, 8]),
            efficiency=random.uniform(65, 95),
        ))


# ── Products ──────────────────────────────────────────────────
async def _seed_products(db: AsyncSession):
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
    for code, name, weight, material, color in prods:
        db.add(Product(
            code=code, name=name, weight_grams=weight,
            material=material, color=color,
            cycle_time_ideal=random.uniform(15, 40),
            cavities=random.choice([1, 2, 4]),
        ))


# ── Molds ─────────────────────────────────────────────────────
async def _seed_molds(db: AsyncSession):
    molds = [
        ("MLD-001", "Molde Tampa FT 28", 4, "TFT-28", 18.5),
        ("MLD-002", "Molde Frasco 500", 1, "FR-500", 35.0),
        ("MLD-003", "Molde Preforma 22g", 8, "PF-22G", 12.0),
        ("MLD-004", "Molde Conector V110", 2, "CV-110", 28.0),
        ("MLD-005", "Molde Bucha R45", 2, "BR-45", 22.0),
        ("MLD-006", "Molde Pallet 80", 1, "PL-80", 90.0),
    ]
    for code, name, cav, prod, cycle in molds:
        db.add(Mold(
            code=code, name=name, cavities=cav,
            product_code=prod, cycle_time_ideal=cycle,
            total_cycles=random.randint(10000, 500000),
            status=random.choice(["disponivel", "em_uso"]),
        ))


# ── Operators ────────────────────────────────────────────────
async def _seed_operators(db: AsyncSession):
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
    for reg, name, shift in names:
        db.add(Operator(
            registration=reg, name=name, shift=shift,
            skills=[f"INJ-{random.randint(1,10):02d}" for _ in range(random.randint(2, 5))],
        ))


# ── Production Orders ────────────────────────────────────────
async def _seed_production_orders(db: AsyncSession):
    statuses = ["in_progress", "in_progress", "planned", "planned", "completed",
                "in_progress", "planned", "completed", "in_progress", "planned", "planned", "completed"]
    products = ["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45", "PL-80",
                "CX-200", "TB-12", "RG-30", "FD-60", "GR-25", "TP-500"]
    names = ["Tampa Flip-Top 28mm", "Frasco 500ml", "Preforma 22g", "Conector Veicular 110",
             "Bucha Redonda 45mm", "Pallet Liso 80x80", "Caixa Organizadora 200L", "Tubete 12mm",
             "Rótulo Garra 30mm", "Flange Diâmetro 60", "Grade Retangular 25L", "Tampa Press-On 500"]
    clients = ["AutoParts Ltda", "Embala Tudo", "PetBrasil S.A.", "VeiculTech", "Plásticos Unidos",
               "LogPack", "CasaOrg", "TuboFlex", "RotuloPro", "TechFlange", "AgriPlast", "TampaBrasil"]

    today = date.today()
    for i in range(12):
        qty = random.randint(5000, 50000)
        produced = random.randint(0, qty) if statuses[i] != "planned" else 0
        good = int(produced * random.uniform(0.92, 0.99))
        db.add(ProductionOrder(
            order_number=f"OP-2025-{i + 1:03d}",
            product_code=products[i], product_name=names[i],
            quantity_planned=qty, quantity_produced=produced,
            quantity_good=good, quantity_rejected=produced - good,
            status=statuses[i], priority=random.choice(["normal", "high", "urgent"]),
            machine_code=f"INJ-{(i % 10) + 1:02d}",
            client=clients[i],
            due_date=today + timedelta(days=random.randint(1, 14)),
        ))


# ── Planning ─────────────────────────────────────────────────
async def _seed_planning(db: AsyncSession):
    today = date.today()
    products = ["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45", "PL-80"]
    names = ["Tampa Flip-Top 28mm", "Frasco 500ml", "Preforma 22g", "Conector Veicular 110",
             "Bucha Redonda 45mm", "Pallet Liso 80x80"]
    for day_offset in range(7):
        d = today + timedelta(days=day_offset)
        for machine_idx in range(1, 11):
            prod_idx = random.randint(0, len(products) - 1)
            db.add(Planning(
                machine_code=f"INJ-{machine_idx:02d}",
                product_code=products[prod_idx],
                product_name=names[prod_idx],
                quantity_planned=random.randint(2000, 20000),
                date=d, shift=random.choice(["A", "B", "C"]),
                cycle_time_seconds=random.uniform(15, 45),
                cavities=random.choice([1, 2, 4]),
                weight_grams=random.uniform(2, 50),
                material=random.choice(["PP", "PET", "PEAD", "PA6.6"]),
                sequence=1, status="pendente" if day_offset > 0 else "em_andamento",
            ))


# ── Production Entries ────────────────────────────────────────
async def _seed_production_entries(db: AsyncSession):
    today = datetime.now(timezone.utc)
    for day_offset in range(30):
        ts = today - timedelta(days=day_offset)
        for machine_idx in range(1, 11):
            for entry in range(random.randint(2, 6)):
                good = random.randint(100, 2000)
                rej = random.randint(0, int(good * 0.08))
                db.add(ProductionEntry(
                    machine_code=f"INJ-{machine_idx:02d}",
                    product_code=random.choice(["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45", "PL-80"]),
                    operator_name=random.choice(["Roberto Silva", "Ana Costa", "Pedro Santos", "Maria Oliveira"]),
                    shift=random.choice(["A", "B", "C"]),
                    quantity_good=good, quantity_rejected=rej,
                    cycle_time_actual=random.uniform(15, 50),
                    timestamp=ts - timedelta(hours=random.randint(0, 8)),
                ))


# ── Downtimes ─────────────────────────────────────────────────
async def _seed_downtimes(db: AsyncSession):
    categories = ["mecanica", "eletrica", "setup", "processo", "qualidade", "falta_material", "programada"]
    reasons = [
        "Troca de molde", "Falha no bico injetor", "Aquecimento irregular",
        "Falta de matéria-prima", "Manutenção preventiva", "Ajuste de parâmetros",
        "Defeito no produto", "Problema elétrico", "Troca de cor",
        "Limpeza de molde", "Quebra de extrator", "Setup de máquina",
    ]
    today = datetime.now(timezone.utc)

    # Paradas ativas (2 máquinas paradas)
    db.add(ActiveDowntime(
        machine_code="INJ-05", reason="Troca de molde", category="setup",
        operator_name="Roberto Silva", shift="A", start_time=today - timedelta(minutes=45),
    ))
    db.add(ActiveDowntime(
        machine_code="INJ-09", reason="Falta de matéria-prima", category="falta_material",
        operator_name="Pedro Santos", shift="A", start_time=today - timedelta(minutes=120),
    ))

    # Histórico (30 dias)
    for day_offset in range(30):
        for _ in range(random.randint(3, 8)):
            start = today - timedelta(days=day_offset, hours=random.randint(0, 20))
            dur = random.uniform(5, 120)
            db.add(DowntimeHistory(
                machine_code=f"INJ-{random.randint(1, 10):02d}",
                reason=random.choice(reasons), category=random.choice(categories),
                operator_name=random.choice(["Roberto Silva", "Ana Costa", "Pedro Santos"]),
                shift=random.choice(["A", "B", "C"]),
                start_time=start, end_time=start + timedelta(minutes=dur),
                duration_minutes=round(dur, 1), is_planned=random.random() < 0.2,
            ))


# ── OEE History ───────────────────────────────────────────────
async def _seed_oee_history(db: AsyncSession):
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
            db.add(OeeHistory(
                machine_code=f"INJ-{machine_idx:02d}",
                date=d, shift=random.choice(["A", "B", "C"]),
                availability=round(avail, 1), performance=round(perf, 1),
                quality_rate=round(qual, 1), oee=round(oee, 1),
                planned_time_minutes=planned, running_time_minutes=round(running, 1),
                downtime_minutes=round(planned - running, 1),
                total_produced=total, good_produced=good, rejected=total - good,
                ideal_cycle_seconds=random.uniform(15, 40),
            ))


# ── Quality Measurements ─────────────────────────────────────
async def _seed_quality(db: AsyncSession):
    today = datetime.now(timezone.utc)
    dimensions = ["Diâmetro externo", "Altura", "Espessura parede", "Peso", "Diâmetro interno"]
    defects = ["rebarba", "bolha", "mancha", "dimensional", "deformação"]

    for day_offset in range(15):
        for _ in range(random.randint(5, 15)):
            nominal = random.uniform(10, 100)
            tolerance = nominal * 0.02
            measured = nominal + random.uniform(-tolerance * 1.5, tolerance * 1.5)
            approved = abs(measured - nominal) <= tolerance
            db.add(QualityMeasurement(
                machine_code=f"INJ-{random.randint(1, 10):02d}",
                product_code=random.choice(["TFT-28", "FR-500", "PF-22G", "CV-110"]),
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
async def _seed_notifications(db: AsyncSession):
    db.add(Notification(title="Máquina INJ-05 parada", message="Parada há mais de 30 minutos — troca de molde", type="warning", machine_code="INJ-05"))
    db.add(Notification(title="OEE abaixo da meta", message="INJ-03 com OEE de 62% — abaixo da meta de 75%", type="error", machine_code="INJ-03"))
    db.add(Notification(title="Ordem OP-2025-001 completa", message="100% da quantidade planejada atingida", type="success"))
    db.add(Notification(title="Manutenção preventiva", message="INJ-07 tem manutenção programada para amanhã", type="info", machine_code="INJ-07"))


# ── Losses ────────────────────────────────────────────────────
async def _seed_losses(db: AsyncSession):
    categories = ["refugo", "rebarba", "dimensional", "cor", "contaminacao"]
    materials = ["PP", "PET", "PEAD", "PA6.6", "PS", "POM"]
    today = datetime.now(timezone.utc)
    for day_offset in range(15):
        for _ in range(random.randint(2, 6)):
            db.add(LossEntry(
                machine_code=f"INJ-{random.randint(1,10):02d}",
                product_code=random.choice(["TFT-28", "FR-500", "PF-22G", "CV-110", "BR-45"]),
                order_number=f"OP-2025-{random.randint(1,12):03d}",
                quantity=random.randint(5, 200),
                weight_kg=round(random.uniform(0.1, 15.0), 2),
                reason=random.choice(["Rebarba excessiva", "Fora de dimensional", "Contaminação", "Cor irregular", "Bolha"]),
                category=random.choice(categories),
                material=random.choice(materials),
                is_manual=random.random() < 0.3,
                created_at=today - timedelta(days=day_offset, hours=random.randint(0, 8)),
            ))


# ── Setup Entries ─────────────────────────────────────────────
async def _seed_setups(db: AsyncSession):
    setup_types = ["troca_molde", "troca_cor", "troca_material", "ajuste"]
    mold_codes = ["MLD-001", "MLD-002", "MLD-003", "MLD-004", "MLD-005", "MLD-006"]
    today = datetime.now(timezone.utc)
    for day_offset in range(10):
        for _ in range(random.randint(1, 4)):
            start = today - timedelta(days=day_offset, hours=random.randint(1, 20))
            dur = random.uniform(10, 90)
            db.add(SetupEntry(
                machine_code=f"INJ-{random.randint(1,10):02d}",
                setup_type=random.choice(setup_types),
                mold_from=random.choice(mold_codes),
                mold_to=random.choice(mold_codes),
                product_from=random.choice(["TFT-28", "FR-500", "PF-22G"]),
                product_to=random.choice(["CV-110", "BR-45", "PL-80"]),
                start_time=start,
                end_time=start + timedelta(minutes=dur),
                duration_minutes=round(dur, 1),
                status="concluido",
                operator_name=random.choice(["Roberto Silva", "Ana Costa", "Pedro Santos"]),
            ))


# ── PMP (Moído/Borra/Sucata) ─────────────────────────────────
async def _seed_pmp(db: AsyncSession):
    pmp_types = ["moido", "borra", "sucata"]
    destinations = ["reprocesso", "descarte", "venda"]
    today = datetime.now(timezone.utc)
    for day_offset in range(15):
        for _ in range(random.randint(1, 5)):
            db.add(PmpEntry(
                type=random.choice(pmp_types),
                machine_code=f"INJ-{random.randint(1,10):02d}",
                weight_kg=round(random.uniform(0.5, 50.0), 2),
                destination=random.choice(destinations),
                material=random.choice(["PP", "PET", "PEAD", "PA6.6"]),
                operator_name=random.choice(["Roberto Silva", "Ana Costa", "Pedro Santos"]),
                notes=random.choice(["", "Lote contaminado", "Reprocesso programado", ""]),
                created_at=today - timedelta(days=day_offset, hours=random.randint(0, 8)),
            ))


# ── Quality Lots ──────────────────────────────────────────────
async def _seed_quality_lots(db: AsyncSession):
    statuses = ["quarentena", "em_triagem", "concluida"]
    today = datetime.now(timezone.utc)
    for i in range(15):
        status = random.choice(statuses)
        approved = random.randint(500, 5000) if status == "concluida" else 0
        rejected = random.randint(10, 200) if status == "concluida" else 0
        db.add(QualityLot(
            lot_number=f"LOT-2025-{i+1:04d}",
            product_code=random.choice(["TFT-28", "FR-500", "PF-22G", "CV-110"]),
            machine_code=f"INJ-{random.randint(1,10):02d}",
            order_number=f"OP-2025-{random.randint(1,12):03d}",
            quantity=random.randint(1000, 10000),
            reason=random.choice(["Variação dimensional", "Contaminação", "Cor fora do padrão", "Rebarbas excessivas", "Inspeção de lote"]),
            status=status,
            approved_qty=approved,
            rejected_qty=rejected,
            returned_to_production=random.choice([True, False]) if status == "concluida" else False,
            inspector=random.choice(["Ana Qualidade", "Paulo Inspetor"]),
            concluded_at=today - timedelta(days=i) if status == "concluida" else None,
            created_at=today - timedelta(days=i + 1),
        ))


# ── Mold Maintenance ─────────────────────────────────────────
async def _seed_mold_maintenance(db: AsyncSession):
    mold_codes = ["MLD-001", "MLD-002", "MLD-003", "MLD-004", "MLD-005", "MLD-006"]
    maint_types = ["preventiva", "corretiva", "limpeza"]
    statuses = ["concluida", "concluida", "pendente", "em_andamento"]
    today = datetime.now(timezone.utc)
    for i in range(10):
        status = random.choice(statuses)
        start = today - timedelta(days=i * 3, hours=random.randint(1, 12))
        dur_h = round(random.uniform(0.5, 8.0), 1)
        end = start + timedelta(hours=dur_h) if status == "concluida" else None
        db.add(MoldMaintenance(
            mold_code=random.choice(mold_codes),
            maintenance_type=random.choice(maint_types),
            technician=random.choice(["Técnico A", "Técnico B", "Técnico C"]),
            description=random.choice(["Troca de pinos extratores", "Polimento cavidade", "Limpeza geral", "Reparo canal quente", "Troca anel O-Ring"]),
            start_time=start,
            end_time=end,
            duration_hours=dur_h if status == "concluida" else None,
            cost=round(random.uniform(100, 5000), 2) if status == "concluida" else None,
            parts_replaced=random.choice(["Pinos, Molas", "Anel O-Ring", "Bico injetor", None]),
            status=status,
            created_at=start,
        ))


# ── PCP Messages ─────────────────────────────────────────────
async def _seed_pcp_messages(db: AsyncSession):
    messages = [
        ("Priorizar OP-2025-001 — cliente urgente", 5, "urgent", "INJ-01"),
        ("Troca de produto INJ-03 às 14h", 3, "info", "INJ-03"),
        ("Material PP azul em falta — previsão amanhã", 4, "warning", None),
        ("Meta turno A: 15.000 peças", 2, "info", None),
        ("INJ-07 liberada após manutenção", 3, "info", "INJ-07"),
        ("Auditor externo amanhã — preparar documentação", 4, "warning", None),
    ]
    for msg, priority, msg_type, machine in messages:
        db.add(PcpMessage(
            message=msg, priority=priority, type=msg_type,
            target_machine=machine, is_active=True,
        ))


# ── Leadership (Escala + Absenteísmo) ────────────────────────
async def _seed_leadership(db: AsyncSession):
    operators = [
        ("OP-001", "Roberto Silva"), ("OP-002", "Ana Costa"), ("OP-003", "Pedro Santos"),
        ("OP-004", "Maria Oliveira"), ("OP-005", "João Lima"), ("OP-006", "Carlos Ferreira"),
        ("OP-007", "Luiza Souza"), ("OP-008", "Fernando Alves"), ("OP-009", "Patricia Ramos"),
    ]
    today = date.today()
    for day_offset in range(7):
        d = today + timedelta(days=day_offset)
        for reg, name in operators[:6]:
            db.add(OperatorSchedule(
                operator_registration=reg,
                operator_name=name,
                date=d,
                shift=random.choice(["A", "B", "C"]),
                machine_code=f"INJ-{random.randint(1,10):02d}",
                position=random.choice(["operador", "lider", "auxiliar"]),
            ))

    # Absenteísmo
    reasons = ["falta", "atestado", "atraso", "ferias", "folga"]
    for i in range(12):
        reg, name = random.choice(operators)
        d = today - timedelta(days=random.randint(1, 30))
        db.add(AbsenteeismEntry(
            operator_registration=reg,
            operator_name=name,
            date=d,
            shift=random.choice(["A", "B", "C"]),
            reason=random.choice(reasons),
            hours_absent=round(random.uniform(1, 8), 1),
            justified=random.random() < 0.6,
            notes=random.choice(["", "Atestado médico", "Atraso transporte", ""]),
        ))
