from fastapi import APIRouter
from app.api.v1.endpoints import dns_check
from app.api import health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(dns_check.router, prefix="/checks", tags=["dns-checks"])