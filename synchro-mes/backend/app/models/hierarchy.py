"""
Models: ISA-95 Equipment Hierarchy — Site > Area > WorkCenter
Nível 3 da hierarquia ISA-95 (Enterprise → Site → Area → WorkCenter → Equipment)
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Site(Base):
    __tablename__ = "sites"

    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    timezone = Column(String(50), default="America/Sao_Paulo")
    is_active = Column(Boolean, default=True)

    # ── Relationships ─────────────────────────────────────
    areas = relationship("Area", back_populates="site", lazy="noload")

    def __repr__(self):
        return f"<Site {self.code}>"


class Area(Base):
    __tablename__ = "areas"

    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # ── Relationships ─────────────────────────────────────
    site = relationship("Site", back_populates="areas", lazy="joined")
    work_centers = relationship("WorkCenter", back_populates="area", lazy="noload")

    @property
    def site_code(self) -> str | None:
        return self.site.code if self.site else None

    def __repr__(self):
        return f"<Area {self.code}>"


class WorkCenter(Base):
    __tablename__ = "work_centers"

    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    capacity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    # ── Relationships ─────────────────────────────────────
    area = relationship("Area", back_populates="work_centers", lazy="joined")
    machines = relationship("Machine", back_populates="work_center", lazy="noload")

    @property
    def area_code(self) -> str | None:
        return self.area.code if self.area else None

    @property
    def site_code(self) -> str | None:
        return self.area.site.code if self.area and self.area.site else None

    def __repr__(self):
        return f"<WorkCenter {self.code}>"
