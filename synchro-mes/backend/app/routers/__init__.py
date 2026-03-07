from app.routers.auth import router as auth_router
from app.routers.machines import router as machines_router
from app.routers.production import router as production_router
from app.routers.downtimes import router as downtimes_router
from app.routers.quality import router as quality_router
from app.routers.dashboard import router as dashboard_router
from app.routers.oee import router as oee_router
from app.routers.losses import router as losses_router
from app.routers.setup import router as setup_router
from app.routers.pmp import router as pmp_router
from app.routers.tooling import router as tooling_router
from app.routers.pcp_router import router as pcp_router
from app.routers.leadership import router as leadership_router
from app.routers.history import router as history_router
from app.routers.admin_data import router as admin_data_router
from app.routers.quality_lots import router as quality_lots_router
from app.routers.hierarchy import router as hierarchy_router
from app.routers.materials import router as materials_router
from app.routers.maintenance import router as maintenance_router
from app.routers.kpis import router as kpis_router

all_routers = [
    (auth_router,          "/api/auth",          ["Auth"]),
    (machines_router,      "/api/machines",      ["Machines"]),
    (production_router,    "/api/production",    ["Production"]),
    (downtimes_router,     "/api/downtimes",     ["Downtimes"]),
    (quality_router,       "/api/quality",       ["Quality"]),
    (dashboard_router,     "/api/dashboard",     ["Dashboard"]),
    (oee_router,           "/api/oee",           ["OEE"]),
    (losses_router,        "/api/losses",        ["Losses"]),
    (setup_router,         "/api/setup",         ["Setup"]),
    (pmp_router,           "/api/pmp",           ["PMP"]),
    (tooling_router,       "/api/tooling",       ["Tooling"]),
    (pcp_router,           "/api/pcp",           ["PCP"]),
    (leadership_router,    "/api/leadership",    ["Leadership"]),
    (history_router,       "/api/history",       ["History"]),
    (admin_data_router,    "/api/admin",         ["Admin"]),
    (quality_lots_router,  "/api/quality-lots",  ["QualityLots"]),
    (hierarchy_router,     "/api/hierarchy",     ["Hierarchy"]),
    (materials_router,     "/api/materials",     ["Materials"]),
    (maintenance_router,   "/api/maintenance",   ["Maintenance"]),
    (kpis_router,          "/api/kpis",          ["KPIs"]),
]
