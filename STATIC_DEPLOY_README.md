# 静态发布版使用说明

## 每天更新数据

1. 在本地更新 `data/source/用户承接表.xlsx`、`data/source/用户订单表.xlsx`、`data/source/明细表.xlsx`。
2. 双击 `build_static_site.bat`，或运行 `python build_static_site.py`。
3. 将生成后的 `dist/` 提交到 GitHub。
4. GitHub Pages 会部署 `dist/`，外部访问链接保持不变。

## 安全边界

- 不需要上传原始 Excel。
- 不需要上传 `data/dashboard.sqlite3`。
- 发布版会上传 `dist/data/*.json`，这些 JSON 是页面展示所需数据。
- 当前发布版为公开脱敏版：`union_id`、`wxid`、`user_id`、`order_id` 会替换为 `public_*` 编号。
- 客户标签明细不会公开，只保留是否包含 `螳螂到课`，用于到课预测。
- 订单号 `order_no` 会保留，用于昨日复盘点击追溯订单号。
- 订单号仍属于可追溯业务信息。若后续要给更大范围外部人员看，应再做“无订单号汇总版”。
