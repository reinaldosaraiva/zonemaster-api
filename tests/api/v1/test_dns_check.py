import pytest
import httpx
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import get_db, Base
from app.core.config import settings

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test async engine
test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

# Create test session factory
TestAsyncSessionLocal = async_sessionmaker(
    test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def override_get_db():
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def setup_database():
    """Setup test database before each test"""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_dns_check_success(async_client: AsyncClient, setup_database, httpx_mock):
    """Test successful DNS check creation with mocked Zonemaster API"""
    # Mock successful Zonemaster API response
    mock_response = {
        "jsonrpc": "2.0",
        "result": [
            {
                "level": "INFO",
                "module": "NAMESERVER",
                "tag": "N01",
                "message": "Nameserver NS1.EXAMPLE.COM responds to queries."
            },
            {
                "level": "WARNING", 
                "module": "DELEGATION",
                "tag": "D01",
                "message": "Warning about delegation setup."
            }
        ],
        "id": 1
    }
    
    httpx_mock.add_response(
        method="POST",
        url=settings.ZONEMASTER_API_URL,
        json=mock_response,
        status_code=200
    )
    
    # Test data
    test_domain = "example.com"
    
    # Make request to our API
    response = await async_client.post(
        "/api/v1/checks/",
        json={"domain": test_domain}
    )
    
    # Assertions
    assert response.status_code == 201
    response_data = response.json()
    
    assert response_data["domain"] == test_domain
    assert "id" in response_data
    assert "created_at" in response_data
    assert len(response_data["results"]) == 2
    
    # Check first result
    result1 = response_data["results"][0]
    assert result1["level"] == "INFO"
    assert result1["module"] == "NAMESERVER"
    assert result1["tag"] == "N01"
    assert result1["message"] == "Nameserver NS1.EXAMPLE.COM responds to queries."
    
    # Check second result
    result2 = response_data["results"][1]
    assert result2["level"] == "WARNING"
    assert result2["module"] == "DELEGATION"
    assert result2["tag"] == "D01"

@pytest.mark.asyncio
async def test_create_dns_check_zonemaster_api_error(async_client: AsyncClient, setup_database, httpx_mock):
    """Test DNS check creation when Zonemaster API returns error"""
    # Mock Zonemaster API error response
    mock_response = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32602,
            "message": "Invalid domain name"
        },
        "id": 1
    }
    
    httpx_mock.add_response(
        method="POST",
        url=settings.ZONEMASTER_API_URL,
        json=mock_response,
        status_code=200
    )
    
    # Make request to our API
    response = await async_client.post(
        "/api/v1/checks/",
        json={"domain": "invalid..domain"}
    )
    
    # Should return service unavailable
    assert response.status_code == 503
    assert "DNS check failed" in response.json()["detail"]

@pytest.mark.asyncio  
async def test_create_dns_check_zonemaster_api_unavailable(async_client: AsyncClient, setup_database, httpx_mock):
    """Test DNS check creation when Zonemaster API is unavailable"""
    # Mock connection error
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))
    
    # Make request to our API
    response = await async_client.post(
        "/api/v1/checks/",
        json={"domain": "example.com"}
    )
    
    # Should return service unavailable
    assert response.status_code == 503
    assert "DNS check failed" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_dns_check_success(async_client: AsyncClient, setup_database, httpx_mock):
    """Test getting a DNS check by ID"""
    # First create a DNS check
    mock_response = {
        "jsonrpc": "2.0",
        "result": [
            {
                "level": "INFO",
                "module": "NAMESERVER", 
                "tag": "N01",
                "message": "Test message."
            }
        ],
        "id": 1
    }
    
    httpx_mock.add_response(
        method="POST",
        url=settings.ZONEMASTER_API_URL,
        json=mock_response,
        status_code=200
    )
    
    # Create DNS check
    create_response = await async_client.post(
        "/api/v1/checks/",
        json={"domain": "example.com"}
    )
    
    check_id = create_response.json()["id"]
    
    # Get the DNS check
    get_response = await async_client.get(f"/api/v1/checks/{check_id}")
    
    assert get_response.status_code == 200
    response_data = get_response.json()
    assert response_data["id"] == check_id
    assert response_data["domain"] == "example.com"
    assert len(response_data["results"]) == 1

@pytest.mark.asyncio
async def test_get_dns_check_not_found(async_client: AsyncClient, setup_database):
    """Test getting a non-existent DNS check"""
    response = await async_client.get("/api/v1/checks/99999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "DNS check not found"

@pytest.mark.asyncio
async def test_list_dns_checks(async_client: AsyncClient, setup_database, httpx_mock):
    """Test listing DNS checks"""
    # Mock Zonemaster API response
    mock_response = {
        "jsonrpc": "2.0",
        "result": [
            {
                "level": "INFO",
                "module": "TEST",
                "tag": "T01", 
                "message": "Test message."
            }
        ],
        "id": 1
    }
    
    httpx_mock.add_response(
        method="POST",
        url=settings.ZONEMASTER_API_URL,
        json=mock_response,
        status_code=200
    )
    
    # Create a few DNS checks
    domains = ["example1.com", "example2.com"]
    for domain in domains:
        await async_client.post(
            "/api/v1/checks/",
            json={"domain": domain}
        )
    
    # List DNS checks
    response = await async_client.get("/api/v1/checks/")
    
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    
    # Check that results_count is included
    for check in response_data:
        assert "results_count" in check
        assert check["results_count"] == 1  # Each check has 1 result from mock

@pytest.mark.asyncio
async def test_list_dns_checks_pagination(async_client: AsyncClient, setup_database, httpx_mock):
    """Test DNS checks pagination"""
    # Mock Zonemaster API response
    mock_response = {
        "jsonrpc": "2.0",
        "result": [],
        "id": 1
    }
    
    httpx_mock.add_response(
        method="POST",
        url=settings.ZONEMASTER_API_URL,
        json=mock_response,
        status_code=200
    )
    
    # Create multiple DNS checks
    for i in range(5):
        await async_client.post(
            "/api/v1/checks/",
            json={"domain": f"example{i}.com"}
        )
    
    # Test pagination
    response = await async_client.get("/api/v1/checks/?skip=2&limit=2")
    
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2

@pytest.mark.asyncio
async def test_create_dns_check_invalid_domain(async_client: AsyncClient, setup_database):
    """Test creating DNS check with invalid domain"""
    response = await async_client.post(
        "/api/v1/checks/",
        json={"domain": ""}
    )
    
    # Should return validation error
    assert response.status_code == 422