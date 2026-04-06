import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    host: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(String(64))
    credential_profile: Mapped[str] = mapped_column(String(64), default="default")
    location: Mapped[dict] = mapped_column(JSON, default=dict)
    network: Mapped[dict] = mapped_column(JSON, default=dict)
    ssh_config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
