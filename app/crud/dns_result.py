from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dns_result import DNSResult

class DNSResultCRUD:
    async def create_bulk(
        self, 
        db: AsyncSession, 
        dns_check_id: int,
        results_data: List[dict]
    ) -> List[DNSResult]:
        db_objects = []
        for result_data in results_data:
            db_obj = DNSResult(
                dns_check_id=dns_check_id,
                level=result_data["level"],
                module=result_data["module"],
                tag=result_data["tag"],
                message=result_data["message"]
            )
            db_objects.append(db_obj)
            db.add(db_obj)
        
        await db.commit()
        for obj in db_objects:
            await db.refresh(obj)
        return db_objects

dns_result_crud = DNSResultCRUD()