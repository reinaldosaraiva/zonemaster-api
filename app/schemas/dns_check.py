from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict

class DNSResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    level: str
    module: str
    tag: str
    message: str

class DNSCheckCreate(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255, description="Domain to check")

class DNSCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    domain: str
    created_at: datetime
    results: List[DNSResultResponse] = []

class DNSCheckListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    domain: str
    created_at: datetime
    results_count: int = Field(default=0, description="Number of results for this check")