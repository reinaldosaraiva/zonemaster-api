from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.dns_check import DNSCheck
from app.schemas.dns_check import DNSCheckCreate

class DNSCheckCRUD:
    async def create(self, db: AsyncSession, obj_in: DNSCheckCreate) -> DNSCheck:
        db_obj = DNSCheck(domain=obj_in.domain)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: int) -> Optional[DNSCheck]:
        stmt = select(DNSCheck).options(selectinload(DNSCheck.results)).where(DNSCheck.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DNSCheck]:
        stmt = (
            select(DNSCheck)
            .options(selectinload(DNSCheck.results))
            .offset(skip)
            .limit(limit)
            .order_by(DNSCheck.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_multi_with_count(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        stmt = (
            select(
                DNSCheck.id,
                DNSCheck.domain,
                DNSCheck.created_at,
                func.count(DNSCheck.results).label("results_count")
            )
            .outerjoin(DNSCheck.results)
            .group_by(DNSCheck.id, DNSCheck.domain, DNSCheck.created_at)
            .offset(skip)
            .limit(limit)
            .order_by(DNSCheck.created_at.desc())
        )
        result = await db.execute(stmt)
        return [
            {
                "id": row.id,
                "domain": row.domain,
                "created_at": row.created_at,
                "results_count": row.results_count
            }
            for row in result.all()
        ]

dns_check_crud = DNSCheckCRUD()