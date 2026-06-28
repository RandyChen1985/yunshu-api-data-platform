# 任务: Dashboard 24小时趋势可视化

## 1. 后端开发 [x]
- [x] 在 `app/api/portal/endpoints/dashboard.py` 中实现 `get_api_trends_24h` 接口
  - [x] 编写聚合 SQL 查询
  - [x] 实现 24 小时时间序列补全逻辑
- [x] 接口验证
  - [x] 使用 curl 验证返回数据格式

## 2. 前端开发 [x]
- [x] 集成 ECharts
  - [x] 安装依赖: `npm install echarts vue-echarts`
- [x] 开发趋势图组件
  - [x] 在 `Overview.vue` 中引入并配置 ECharts
  - [x] 实现从 API 获取数据并更新图表
- [x] 视觉美化
  - [x] 调整颜色、网格、提示框等，使其符合系统风格

## 3. 验收验证 [x]
- [x] 冒烟测试: 确保 Dashboad 页面不报错且图表显示正常
- [x] 性能测试: 确认大数据量下的数据聚合耗时在可接受范围内
