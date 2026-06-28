import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.api.v1.endpoints.universal import query_resource_data, ResourceQueryRequest
from app.api.v1.schemas.data import BaseResponse
from app.services.data_adapter.models import ResultSet

# Mock data
MOCK_RESOURCE_KEY = "test_resource"
MOCK_USER = {"user_id": 1, "role": "admin"}
MOCK_CONFIG = MagicMock()
MOCK_CONFIG.data_source = "mock_source"

@pytest.mark.asyncio
async def test_post_resource_success():
    """Test happy path for POST resource query"""
    
    # Mock mocks
    mock_verify_access = AsyncMock(return_value=True)
    mock_get_config = AsyncMock(return_value=MOCK_CONFIG)
    
    mock_adapter = AsyncMock()
    mock_adapter.execute.return_value = ResultSet(
        items=[{"id": 1, "name": "test"}],
        total=1,
        page=1,
        size=20, 
        pages=1
    )
    mock_get_adapter = AsyncMock(return_value=mock_adapter)

    # Patch dependencies
    # MetaService is imported mostly inside functions, so we patch where it is defined
    with patch("app.api.v1.endpoints.universal.verify_resource_access", mock_verify_access), \
         patch("app.services.meta_service.MetaService.get_config", mock_get_config), \
         patch("app.api.v1.endpoints.universal.get_adapter", mock_get_adapter):

        # Input data
        request_data = ResourceQueryRequest(
            filters=[["status", "=", "active"], ["type", "IN", ["A", "B"]]],
            page=1,
            size=10
        )

        # Call endpoint (direct function call to avoid full app/client setup overhead for unit test)
        response = await query_resource_data(
            resource_key=MOCK_RESOURCE_KEY,
            query_in=request_data,
            user=MOCK_USER
        )

        # Assertions
        assert response.code == 200
        assert response.data.total == 1
        assert response.data.items[0]["name"] == "test"
        
        # Verify adapter called with correct LogicalQuery
        args, _ = mock_adapter.execute.call_args
        logical_query = args[0]
        assert logical_query.resource == MOCK_RESOURCE_KEY
        assert logical_query.filters == [("status", "=", "active"), ("type", "IN", ["A", "B"])]
        assert logical_query.page == 1
        assert logical_query.size == 10

@pytest.mark.asyncio
async def test_post_resource_invalid_filter_format():
    """Test invalid filter format raises 400"""
    
    mock_verify_access = AsyncMock(return_value=True)
    
    with patch("app.api.v1.endpoints.universal.verify_resource_access", mock_verify_access):
        # Invalid filter - not a list of 3
        request_data = ResourceQueryRequest(
            filters=[["status", "="]] # Missing value
        )

        with pytest.raises(HTTPException) as excinfo:
            await query_resource_data(
                resource_key=MOCK_RESOURCE_KEY,
                query_in=request_data,
                user=MOCK_USER
            )
        
        assert excinfo.value.status_code == 400
        assert "must be a list of 3 elements" in excinfo.value.detail

@pytest.mark.asyncio
async def test_post_resource_not_found():
    """Test resource not found raises 404"""
    
    mock_verify_access = AsyncMock(return_value=True)
    mock_get_config = AsyncMock(return_value=None) # Config not found

    with patch("app.api.v1.endpoints.universal.verify_resource_access", mock_verify_access), \
         patch("app.services.meta_service.MetaService.get_config", mock_get_config):

        request_data = ResourceQueryRequest()

        with pytest.raises(HTTPException) as excinfo:
            await query_resource_data(
                resource_key="unknown_resource",
                query_in=request_data,
                user=MOCK_USER
            )
        
        assert excinfo.value.status_code == 404
        assert "not found" in excinfo.value.detail
