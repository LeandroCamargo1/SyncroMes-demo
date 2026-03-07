"""
Enums centralizados — Status e categorias tipados para o MES.
Nomes dos membros em lowercase para que SQLAlchemy armazene
os valores corretos (SQLAlchemy usa .name por padrão).
"""
import enum


class MachineStatus(str, enum.Enum):
    running = "running"
    stopped = "stopped"
    maintenance = "maintenance"
    setup = "setup"


class MoldStatus(str, enum.Enum):
    disponivel = "disponivel"
    em_uso = "em_uso"
    manutencao = "manutencao"


class OrderStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class OrderPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class PlanningStatus(str, enum.Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluido = "concluido"


class Shift(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class DowntimeCategory(str, enum.Enum):
    mecanica = "mecanica"
    eletrica = "eletrica"
    setup = "setup"
    processo = "processo"
    qualidade = "qualidade"
    falta_material = "falta_material"
    programada = "programada"


class QualityLotStatus(str, enum.Enum):
    quarentena = "quarentena"
    em_triagem = "em_triagem"
    concluida = "concluida"


class ReworkStatus(str, enum.Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluido = "concluido"
    descartado = "descartado"


class SetupType(str, enum.Enum):
    troca_molde = "troca_molde"
    troca_cor = "troca_cor"
    troca_material = "troca_material"
    ajuste = "ajuste"


class SetupStatus(str, enum.Enum):
    em_andamento = "em_andamento"
    concluido = "concluido"


class PmpType(str, enum.Enum):
    moido = "moido"
    borra = "borra"
    sucata = "sucata"


class PmpDestination(str, enum.Enum):
    reprocesso = "reprocesso"
    descarte = "descarte"
    venda = "venda"


class MaintenanceType(str, enum.Enum):
    preventiva = "preventiva"
    corretiva = "corretiva"
    limpeza = "limpeza"


class MaintenanceStatus(str, enum.Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluida = "concluida"


class NotificationType(str, enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"
    success = "success"


class PcpMessageType(str, enum.Enum):
    info = "info"
    warning = "warning"
    urgent = "urgent"


class UserRole(str, enum.Enum):
    admin = "admin"
    supervisor = "supervisor"
    operador = "operador"
    qualidade = "qualidade"
    pcp = "pcp"


class DefectSeverity(str, enum.Enum):
    minor = "minor"
    major = "major"
    critical = "critical"


class LossCategory(str, enum.Enum):
    refugo = "refugo"
    rebarba = "rebarba"
    dimensional = "dimensional"
    cor = "cor"
    contaminacao = "contaminacao"


class AbsenteeismReason(str, enum.Enum):
    falta = "falta"
    atestado = "atestado"
    atraso = "atraso"
    ferias = "ferias"
    folga = "folga"
