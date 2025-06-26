from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from .dns_check import DNSCheck

class DNSResult(Base):
    __tablename__ = "dns_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dns_check_id: Mapped[int] = mapped_column(
        ForeignKey("dns_checks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tag: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationship
    dns_check: Mapped["DNSCheck"] = relationship(
        "DNSCheck",
        back_populates="results"
    )