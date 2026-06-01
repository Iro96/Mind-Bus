---
name: backend-api
description: "Use when: adding FastAPI routes and endpoints, creating Pydantic schemas, implementing services, adding middleware, handling authentication, or building API features"
keywords: ["fastapi", "endpoint", "route", "schema", "pydantic", "service", "middleware", "jwt", "authentication", "api"]
---

# Backend API Skills

Patterns for building FastAPI endpoints and services in Mind-Bus.

## Quick Start: Adding an Endpoint

### 1. Define Schema (Pydantic)
```python
# apps/api/schemas/my_schema.py
from pydantic import BaseModel
from typing import Optional

class MyRequest(BaseModel):
    """Request model."""
    name: str
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Test",
                "description": "Test description"
            }
        }

class MyResponse(BaseModel):
    """Response model."""
    id: UUID
    name: str
    created_at: datetime
```

### 2. Create Service
```python
# apps/api/services/my_service.py
from typing import List
from uuid import UUID

class MyService:
    """Business logic layer."""
    
    def __init__(self, db):
        self.db = db
    
    async def create_item(self, request: MyRequest, user_id: UUID):
        """Create new item."""
        item = await self.db.create(
            table="items",
            data={
                "name": request.name,
                "description": request.description,
                "user_id": user_id,
                "created_at": datetime.now()
            }
        )
        return item
    
    async def get_items(self, user_id: UUID) -> List:
        """Get user's items."""
        items = await self.db.query(
            "SELECT * FROM items WHERE user_id = ?",
            [user_id]
        )
        return items
```

### 3. Add Route
```python
# apps/api/routes/my_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from apps.api.security import get_current_user
from apps.api.services.my_service import MyService
from apps.api.schemas.my_schema import MyRequest, MyResponse

router = APIRouter(prefix="/api/my", tags=["my"])

@router.post("/items", response_model=MyResponse)
async def create_item(
    request: MyRequest,
    current_user: User = Depends(get_current_user),
    service: MyService = Depends(get_service)
):
    """Create new item."""
    try:
        item = await service.create_item(request, current_user.id)
        return MyResponse(**item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/items", response_model=List[MyResponse])
async def get_items(
    current_user: User = Depends(get_current_user),
    service: MyService = Depends(get_service)
):
    """Get user's items."""
    items = await service.get_items(current_user.id)
    return [MyResponse(**item) for item in items]

@router.get("/items/{item_id}", response_model=MyResponse)
async def get_item(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    service: MyService = Depends(get_service)
):
    """Get specific item."""
    item = await service.get_item(item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return MyResponse(**item)
```

### 4. Register Route in Main
```python
# apps/api/main.py
from apps.api.routes.my_routes import router as my_router

app.include_router(my_router)
```

## API Patterns

### Error Handling
```python
from fastapi import HTTPException, status

@router.post("/endpoint")
async def my_endpoint(request: MyRequest):
    """Endpoint with error handling."""
    try:
        # Validate input
        if not request.name:
            raise ValueError("Name is required")
        
        # Process
        result = await process(request)
        
        return {"success": True, "data": result}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### Dependency Injection
```python
from fastapi import Depends
from apps.api.security import get_current_user

async def get_service(db: Database = Depends(get_db)) -> MyService:
    """Service dependency."""
    return MyService(db)

@router.get("/items")
async def get_items(
    current_user: User = Depends(get_current_user),
    service: MyService = Depends(get_service)
):
    """Endpoint with dependencies."""
    return await service.get_items(current_user.id)
```

### Pagination
```python
from typing import Optional

class PaginatedResponse(BaseModel):
    """Paginated response."""
    items: List[Item]
    total: int
    page: int
    page_size: int
    pages: int

@router.get("/items", response_model=PaginatedResponse)
async def get_items_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get paginated items."""
    offset = (page - 1) * page_size
    
    items = await db.query(
        "SELECT * FROM items WHERE user_id = ? LIMIT ? OFFSET ?",
        [current_user.id, page_size, offset]
    )
    
    total = await db.scalar(
        "SELECT COUNT(*) FROM items WHERE user_id = ?",
        [current_user.id]
    )
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )
```

### Request/Response Logging
```python
from fastapi import Request
import logging
import json
from uuid import uuid4

logger = logging.getLogger(__name__)

async def log_request_middleware(request: Request, call_next):
    """Log all requests."""
    request_id = str(uuid4())
    request.scope["request_id"] = request_id
    
    body = await request.body()
    logger.info(
        f"Request: {request_id}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "body": body.decode() if body else None
        }
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Response: {request_id}",
        extra={
            "status": response.status_code,
            "content_type": response.headers.get("content-type")
        }
    )
    
    return response

# Add to app
app.add_middleware(middleware_class=type("LoggingMiddleware", 
                                        (), 
                                        {"dispatch": log_request_middleware}))
```

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "X-Content-Range"]
)
```

### Authentication Patterns
```python
# apps/api/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> User:
    """Validate JWT and return current user."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token")
        
        user = await db.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        return user
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
```

### Background Tasks
```python
from fastapi import BackgroundTasks

@router.post("/process")
async def process_data(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Process data in background."""
    
    # Queue task
    background_tasks.add_task(
        long_running_task,
        request.data,
        current_user.id
    )
    
    return {"message": "Processing started"}

async def long_running_task(data: str, user_id: UUID):
    """Long running task."""
    result = await expensive_operation(data)
    await notify_user(user_id, result)
```

## Testing Patterns

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)

def test_create_item(client, mock_service):
    """Test item creation."""
    response = client.post(
        "/api/my/items",
        json={"name": "Test Item"},
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"

def test_get_items(client):
    """Test item retrieval."""
    response = client.get(
        "/api/my/items",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unauthorized(client):
    """Test unauthorized access."""
    response = client.get("/api/my/items")
    assert response.status_code == 401
```

## Common Mistakes

1. **Not Validating Input**: Always use Pydantic schemas
   ```python
   # ✅ CORRECT
   @router.post("/items")
   async def create(request: MyRequest):
       # request is validated
   ```

2. **Blocking Operations**: Always use async
   ```python
   # ❌ WRONG
   items = db.query(...)  # Blocks event loop
   
   # ✅ CORRECT
   items = await db.query(...)
   ```

3. **SQL Injection**: Use parameterized queries
   ```python
   # ✅ CORRECT
   await db.query("SELECT * FROM items WHERE id = ?", [id])
   ```

## Performance Tips

1. **Use Dependency Injection**: Reuse dependencies
2. **Cache Responses**: Use Redis for frequently accessed data
3. **Async All The Way**: No blocking calls in routes
4. **Connection Pooling**: Reuse DB connections
5. **Pagination**: Always paginate large result sets

## References

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **API Routes**: `apps/api/routes/`
- **Services**: `apps/api/services/`
- **Schemas**: `apps/api/schemas/`
- **Security**: `apps/api/security.py`
