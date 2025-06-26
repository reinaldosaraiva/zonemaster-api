import httpx
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.crud.dns_check import dns_check_crud
from app.crud.dns_result import dns_result_crud
from app.schemas.dns_check import DNSCheckCreate, DNSCheckResponse
from app.models.dns_check import DNSCheck

class ZonemasterService:
    def __init__(self):
        self.api_url = settings.ZONEMASTER_API_URL
        self.timeout = settings.ZONEMASTER_API_TIMEOUT
    
    async def _call_zonemaster_api(self, domain: str) -> List[Dict[str, Any]]:
        """Call Zonemaster API via JSON-RPC 2.0"""
        payload = {
            "jsonrpc": "2.0",
            "method": "start_domain_test",
            "params": {
                "domain": domain,
                "profile": "default"
            },
            "id": 1
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Check for JSON-RPC error
            if "error" in result:
                raise Exception(f"Zonemaster API error: {result['error']}")
            
            # Return the results array from the response
            return result.get("result", [])
    
    def _parse_zonemaster_results(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Parse raw Zonemaster results into our format"""
        parsed_results = []
        
        for result in raw_results:
            # Extract fields from Zonemaster result format
            # This is a simplified parser - real implementation would need
            # to handle the actual Zonemaster result structure
            parsed_result = {
                "level": result.get("level", "INFO"),
                "module": result.get("module", "UNKNOWN"),
                "tag": result.get("tag", "UNKNOWN"),
                "message": result.get("message", str(result))
            }
            parsed_results.append(parsed_result)
        
        return parsed_results
    
    async def run_check_and_save(
        self, 
        db: AsyncSession, 
        domain: str
    ) -> DNSCheckResponse:
        """Run DNS check via Zonemaster API and save results to database"""
        try:
            # Create DNS check record
            dns_check_create = DNSCheckCreate(domain=domain)
            dns_check = await dns_check_crud.create(db, dns_check_create)
            
            # Call Zonemaster API
            raw_results = await self._call_zonemaster_api(domain)
            
            # Parse results
            parsed_results = self._parse_zonemaster_results(raw_results)
            
            # Save results to database
            if parsed_results:
                await dns_result_crud.create_bulk(
                    db, 
                    dns_check.id, 
                    parsed_results
                )
            
            # Refresh DNS check to get results
            dns_check_with_results = await dns_check_crud.get(db, dns_check.id)
            
            return DNSCheckResponse.model_validate(dns_check_with_results)
            
        except httpx.HTTPError as e:
            # Handle HTTP errors from Zonemaster API
            raise Exception(f"Failed to connect to Zonemaster API: {str(e)}")
        except Exception as e:
            # Handle other errors
            raise Exception(f"DNS check failed: {str(e)}")

zonemaster_service = ZonemasterService()