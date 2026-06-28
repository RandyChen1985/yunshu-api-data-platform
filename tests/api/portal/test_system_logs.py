import pytest
from httpx import AsyncClient
from app.main import app
from app.core.database import get_db_connection

@pytest.mark.asyncio
async def test_system_config_lifecycle(client: AsyncClient, admin_api_key: str):
    """
    Test 1: Get Default Config -> Update Config -> Verify Persistence
    """
    headers = {"X-API-Key": admin_api_key}
    
    # 1. Get Default Config
    resp = await client.get("/api/portal/system/config", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "log.retention.raw_days" in data
    assert "log.retention.stats_days" in data
    
    original_raw_days = data["log.retention.raw_days"]

    # 2. Update Config
    new_config = {
        "log.retention.raw_days": "15",
        "log.retention.stats_days": "180"
    }
    resp = await client.post("/api/portal/system/config", json=new_config, headers=headers)
    assert resp.status_code == 200
    
    # 3. Verify Persistence
    resp = await client.get("/api/portal/system/config", headers=headers)
    data = resp.json()
    assert data["log.retention.raw_days"] == "15"
    assert data["log.retention.stats_days"] == "180"
    
    # Restore config (cleanup)
    await client.post("/api/portal/system/config", json={
        "log.retention.raw_days": original_raw_days,
        "log.retention.stats_days": "90"
    }, headers=headers)

@pytest.mark.asyncio
async def test_trigger_manual_purge(client: AsyncClient, admin_api_key: str):
    """
    Test 2: Trigger Manual Purge -> Check Maintenance Log
    """
    headers = {"X-API-Key": admin_api_key}
    
    # 1. Trigger Purge
    payload = {"days": 30}
    resp = await client.post("/api/portal/system/logs/purge", json=payload, headers=headers)
    assert resp.status_code == 200
    assert "Cleaning task started" in resp.json()["message"]
    
    # 2. Check Maintenance Log (Immediate check might show RUNNING)
    # Give it a slight delay for the background task to at least start/insert the record
    import asyncio
    await asyncio.sleep(0.5)
    
    resp = await client.get("/api/portal/system/logs/maintenance?limit=1", headers=headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) > 0
    latest_log = logs[0]
    
    assert "log_purge" in latest_log["task_name"]
    assert latest_log["status"] in ["RUNNING", "SUCCESS", "FAILED"]
    # We check operator is not None, assuming user_name is populated
    assert latest_log["operator"] is not None



