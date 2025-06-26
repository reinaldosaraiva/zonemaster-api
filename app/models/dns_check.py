from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from .dns_result import DNSResult

class DNSCheck(Base):
    __tablename__ = "dns_checks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship
    results: Mapped[List["DNSResult"]] = relationship(
        "DNSResult",
        back_populates="dns_check",
        cascade="all, delete-orphan"
    )