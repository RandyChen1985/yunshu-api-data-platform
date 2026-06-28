# 任务：验证管理接口 (Verify Admin API)

- [x] 创建 `tests/api/v1/test_keys.py` <!-- id: 0 -->
    - 实现 `test_create_api_key_success` (测试创建成功)
    - 实现 `test_create_api_key_duplicate` (可选/边缘情况：测试重复创建)
- [x] 运行自动化测试以确保通过 <!-- id: 1 -->
    - 命令: `pytest tests/api/v1/test_keys.py`
- [x] 更新 `tests/CHECKLIST.md` 中 `/keys` 的状态 <!-- id: 2 -->
