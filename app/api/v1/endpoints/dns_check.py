from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.dns_check import (
    DNSCheckCreate, 
    DNSCheckResponse, 
    DNSCheckListResponse
)
from app.crud.dns_check import dns_check_crud
from app.services.zonemaster_service import zonemaster_service

router = APIRouter()

@router.post("/", response_model=DNSCheckResponse, status_code=status.HTTP_201_CREATED)
async def create_dns_check(
    dns_check: DNSCheckCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new DNS check by running Zonemaster analysis on the provided domain.
    
    This endpoint will:
    1. Create a DNS check record
    2. Call Zonemaster API to analyze the domain
    3. Parse and store the results
    4. Return the complete check with results
    """
    try:
        result = await zonemaster_service.run_check_and_save(db, dns_check.domain)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"DNS check failed: {str(e)}"
        )

@router.get("/{check_id}", response_model=DNSCheckResponse)
async def get_dns_check(
    check_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific DNS check by ID, including all its results.
    """
    dns_check = await dns_check_crud.get(db, check_id)
    if not dns_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS check not found"
        )
    return DNSCheckResponse.model_validate(dns_check)

@router.get("/", response_model=List[DNSCheckListResponse])
async def list_dns_checks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of DNS checks with result counts.
    
    This endpoint returns a summary view of checks without the full results
    to improve performance when listing many checks.
    """
    checks = await dns_check_crud.get_multi_with_count(db, skip=skip, limit=limit)
    return [DNSCheckListResponse(**check) for check in checks]