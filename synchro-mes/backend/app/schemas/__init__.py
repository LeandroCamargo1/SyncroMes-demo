from app.schemas.user import UserCreate, UserRead, UserUpdate, Token, TokenData
from app.schemas.machine import MachineRead, MachineUpdate, MoldRead
from app.schemas.production import (
    ProductionOrderCreate, ProductionOrderRead, ProductionOrderUpdate,
    PlanningCreate, PlanningRead,
    ProductionEntryCreate, ProductionEntryRead,
)
from app.schemas.downtime import (
    ActiveDowntimeCreate, ActiveDowntimeRead,
    DowntimeHistoryRead,
)
from app.schemas.quality import QualityMeasurementCreate, QualityMeasurementRead
from app.schemas.oee import OeeHistoryRead, OeeSummary
from app.schemas.dashboard import DashboardSummary, MachineCardData
