import pytest
import time
from app.services.masking_service import MaskingService
import re

@pytest.mark.asyncio
async def test_masking_performance():
    # 1. 模拟大规模数据 (1000行，每行10个字段，包含敏感字段)
    sample_data = []
    for i in range(1000):
        sample_data.append({
            "id": i,
            "user_name": f"user_{i}",
            "user_phone": "13800138000",
            "email_address": "test@example.com",
            "password": "secret_password",
            "remark": "Normal text field",
            "created_at": "2025-01-01 12:00:00",
            "status": 1,
            "nested": {"secret_token": "token_val"},
            "tags": ["tag1", "tag2"]
        })

    # 2. 模拟规则
    mock_rules = [
        {"pattern": re.compile(r"^.*phone.*$", re.IGNORECASE), "mask_type": "PARTIAL_3_4"},
        {"pattern": re.compile(r"^.*email.*$", re.IGNORECASE), "mask_type": "EMAIL"},
        {"pattern": re.compile(r"^.*password.*$", re.IGNORECASE), "mask_type": "FULL"},
        {"pattern": re.compile(r"^.*token.*$", re.IGNORECASE), "mask_type": "FULL"},
    ]

    # 3. 测试处理耗时
    start_time = time.time()
    masked_result = await MaskingService.mask_recursive(sample_data, mock_rules)
    duration_ms = (time.time() - start_time) * 1000

    print(f"\n[Performance] Processed 1000 rows in {duration_ms:.2f}ms")
    
    # 4. 断言与验证
    assert duration_ms < 50, f"Performance too slow: {duration_ms}ms"
    assert masked_result[0]["user_phone"] == "138****8000"
    assert masked_result[0]["email_address"] == "t***@example.com"
    assert masked_result[0]["password"] == "******"
    assert masked_result[0]["nested"]["secret_token"] == "******"
    assert masked_result[0]["user_name"] == "user_0" # 非敏感字段保持不变

@pytest.mark.asyncio
async def test_strategy_logic():
    # 验证三级策略优先级
    # 1. 用户级 DISABLE 覆盖一切
    user_context = {"role": "user", "masking_strategy": "DISABLE", "role_masking_strategy": "ENABLE"}
    assert await MaskingService.should_mask(user_context) is False

    # 2. 用户级ENABLE 覆盖一切
    user_context = {"role": "user", "masking_strategy": "ENABLE", "role_masking_strategy": "DISABLE"}
    assert await MaskingService.should_mask(user_context) is True

    # 3. 用户级 ROLE -> 看角色级 ENABLE
    user_context = {"role": "user", "masking_strategy": "ROLE", "role_masking_strategy": "ENABLE"}
    assert await MaskingService.should_mask(user_context) is True

    # 4. Admin + unmask=true
    user_context = {"role": "admin", "masking_strategy": "ROLE", "role_masking_strategy": "GLOBAL"}
    assert await MaskingService.should_mask(user_context, unmask_param=True) is False
