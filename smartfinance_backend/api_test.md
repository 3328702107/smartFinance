# API 测试说明（api_test）

本文件用于快速联调 / 测试，基于当前后端代码中已实现的接口，总结常用调用方式和**请求参数示例**。

- 基础地址（本地开发）：`http://localhost:5000`
- 统一前缀：多数接口为 `/api/...`，也有少数为 `/data-collection/...`、`/event-analysis/...`
- 返回格式：部分接口返回“裸 JSON”，部分接口通过统一壳：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": 1700000000000
}
```

> 以下示例默认使用 `curl`，你也可以在 Postman / Apifox 中按相同结构配置。

---

## 1. 健康检查

### 1.1 GET /api/health

- 描述：检查服务、数据库、数据源、模型状态。
- 请求参数：无
- 示例：

```bash
curl -X GET "http://localhost:5000/api/health"
```

---

## 2. 认证与账户（/api/auth）

### 2.1 注册：POST /api/auth/register

- 请求头：`Content-Type: application/json`
- 请求体参数：
  - `username` (string, 必填)
  - `password` (string, 必填)
  - `phone` (string, 可选)
  - `email` (string, 可选)
- 示例：

```bash
curl -X POST "http://localhost:5000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "123456",
    "phone": "13800000000",
    "email": "test@example.com"
  }'
```

### 2.2 登录：POST /api/auth/login

- 请求头：`Content-Type: application/json`
- 请求体参数：
  - `username` (string, 必填)
  - `password` (string, 必填)
  - `device_id` (string, 可选)
  - `ip_address` (string, 可选)
  - `client_type` (string, 可选，默认 `WEB`)
  - `login_location` (string, 可选)
- 示例：

```bash
curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "123456",
    "device_id": "device-001",
    "ip_address": "1.2.3.4",
    "client_type": "WEB",
    "login_location": "上海"
  }'
```

登录成功后，响应中会返回 `data.token`，后续接口可通过 `Authorization: Bearer <token>` 传入。

### 2.3 获取当前用户：GET /api/auth/me

- 请求头：
  - `Authorization: Bearer <token>`（推荐）
- 或查询参数：
  - `token`（不推荐，仅方便调试）
- 示例：

```bash
curl -X GET "http://localhost:5000/api/auth/me" \
  -H "Authorization: Bearer {{token}}"
```

或：

```bash
curl -X GET "http://localhost:5000/api/auth/me?token={{token}}"
```

### 2.4 刷新 token：POST /api/auth/refresh

- 请求体参数：
  - `refreshToken` (string, 必填；当前与登录返回的 token 相同)
- 示例：

```bash
curl -X POST "http://localhost:5000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "{{old_token}}"
  }'
```

### 2.5 修改密码：POST /api/auth/change-password

- 请求头：`Authorization: Bearer <token>`
- 请求体参数：
  - `oldPassword` (string, 必填)
  - `newPassword` (string, 必填)
- 示例：

```bash
curl -X POST "http://localhost:5000/api/auth/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{token}}" \
  -d '{
    "oldPassword": "123456",
    "newPassword": "654321"
  }'
```

---

## 3. 用户与登录日志（/api/users）

### 3.1 用户列表：GET /api/users/

- 查询参数：
  - `page` (int, 默认 1)
  - `size` (int, 默认 20)
  - `q` (string，可选，用户名模糊搜索)
- 示例：

```bash
curl -X GET "http://localhost:5000/api/users/?page=1&size=10&q=test"
```

### 3.2 用户登录日志：GET /api/users/<user_id>/login_logs

- 路径参数：
  - `user_id` 用户 ID
- 示例：

```bash
curl -X GET "http://localhost:5000/api/users/USER123/login_logs"
```

---

## 4. 交易接入与规则检测（/api/transactions）

### 4.1 新交易接入：POST /api/transactions/

- 请求头：`Content-Type: application/json`
- 请求体参数（关键字段）：
  - `user_id` (string, 必填)
  - `amount` (number, 必填)
  - `device_id` (string, 可选)
  - `currency` (string, 可选，默认 `CNY`)
  - `category` (string, 可选，例如 `转账`)
  - `ip_address` (string, 可选)
  - `status` (string, 可选，默认 `成功`)
  - `tx_id` (string，可选，不传则后端生成)
- 示例：

```bash
curl -X POST "http://localhost:5000/api/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER123",
    "device_id": "device-001",
    "amount": 1200.5,
    "currency": "CNY",
    "category": "转账",
    "ip_address": "1.2.3.4",
    "status": "成功"
  }'
```

---

## 5. 风险事件基础接口（/api/risk_events）

### 5.1 事件列表：GET /api/risk_events/

- 查询参数：
  - `page` (int, 默认 1)
  - `size` (int, 默认 20)
  - `status` (string，可选：`待处理/处理中/已解决/已忽略`)
  - `risk_level` (string，可选：`高/中/低`)
- 示例：

```bash
curl -X GET "http://localhost:5000/api/risk_events/?page=1&size=10&status=待处理&risk_level=高"
```

### 5.2 事件详情：GET /api/risk_events/<event_id>

- 路径参数：
  - `event_id` 事件 ID
- 示例：

```bash
curl -X GET "http://localhost:5000/api/risk_events/EVENT123"
```

### 5.3 更新事件状态：PATCH /api/risk_events/<event_id>/status

- 路径参数：`event_id`
- 请求体参数：
  - `status` (string, 必填：`待处理` / `处理中` / `已解决` / `已忽略`)
- 示例：

```bash
curl -X PATCH "http://localhost:5000/api/risk_events/EVENT123/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "已解决"
  }'
```

---

## 6. 实时监控（/api/monitor）

### 6.1 风险事件列表（监控视角）：GET /api/monitor/risk-events

- 查询参数：
  - `page` (int, 默认 1)
  - `pageSize` (int, 默认 10)
  - `type` (string，可选：`all`/`fraud`/`fake`/`abnormal`/`other`)
  - `status` (string，可选：`all`/`pending`/`processing`/`resolved`/`ignored`)
  - `keyword` (string，可选，描述模糊搜索)
- 示例：

```bash
curl -X GET "http://localhost:5000/api/monitor/risk-events?page=1&pageSize=10&type=abnormal&status=pending&keyword=交易"
```

### 6.2 风险趋势：GET /api/monitor/risk-trend

- 查询参数：
  - `period` (string，可选，当前仅占位，可传 `today`)
- 示例：

```bash
curl -X GET "http://localhost:5000/api/monitor/risk-trend?period=today"
```

### 6.3 系统状态：GET /api/monitor/system-status

- 请求参数：无
- 示例：

```bash
curl -X GET "http://localhost:5000/api/monitor/system-status"
```

---

## 7. 告警管理（/api/alerts）

### 7.1 告警列表：GET /api/alerts/

- 查询参数：
  - `page` (int, 默认 1)
  - `pageSize` (int, 默认 10)
  - `status` (string，`all`/`pending`/`processing`/`resolved`/`ignored`)
  - `level` (string，`all`/`high`/`medium`/`low`)
  - `eventType` (string，`all`/`account`/`transaction`/`identity`/`device`)
  - `timeRange` (string，`today`/`yesterday`/`7days`/`30days`/`all`/`custom`)
  - `startTime` / `endTime` (ISO 时间字符串，`timeRange=custom` 时使用)
  - `keyword` (string，可选，按告警 ID 或类型模糊搜索)
- 示例：

```bash
curl -X GET "http://localhost:5000/api/alerts/?page=1&pageSize=10&status=pending&level=high&eventType=transaction&timeRange=7days"
```

### 7.2 更新告警状态：PATCH /api/alerts/<alert_id>/status

- 路径参数：`alert_id`
- 请求体参数：
  - `status` (string, 必填：`pending`/`processing`/`resolved`/`ignored`，自动映射到中文状态)
- 示例：

```bash
curl -X PATCH "http://localhost:5000/api/alerts/ALERT123/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved"
  }'
```

### 7.3 告警详情：GET /api/alerts/<alert_id>

```bash
curl -X GET "http://localhost:5000/api/alerts/ALERT123"
```

---

## 8. 数据源基础接口（/api/data_sources）

### 8.1 数据源列表：GET /api/data_sources/

- 请求参数：无
- 示例：

```bash
curl -X GET "http://localhost:5000/api/data_sources/"
```

### 8.2 数据质量问题列表：GET /api/data_sources/quality_issues

```bash
curl -X GET "http://localhost:5000/api/data_sources/quality_issues"
```

### 8.3 数据源统计：GET /api/data_sources/stats

```bash
curl -X GET "http://localhost:5000/api/data_sources/stats"
```

---

## 9. 数据采集模块（/data-collection）

### 9.1 数据源监控列表：GET /data-collection/data-sources

- 查询参数：
  - `page` (int, 默认 1)
  - `pageSize` (int, 默认 10)
  - `status` (string，`all`/`normal`/`warning`/`error`/`stopped`)
  - `keyword` (string，可选，按名称模糊搜索)
- 示例：

```bash
curl -X GET "http://localhost:5000/data-collection/data-sources?page=1&pageSize=10&status=normal"
```

### 9.2 单数据源质量问题：GET /data-collection/data-sources/<source_id>/quality-issues

- 查询参数：
  - `page` (int, 默认 1)
  - `pageSize` (int, 默认 10)
  - `type` (string，`all`/`missing`/`format`/`abnormal`/`inconsistent`)
- 示例：

```bash
curl -X GET "http://localhost:5000/data-collection/data-sources/SRC001/quality-issues?page=1&pageSize=10&type=missing"
```

### 9.3 数据预览：GET /data-collection/data-sources/<source_id>/preview

- 查询参数：
  - `type` (string，`trade`/`user`/`device`)
  - `limit` (int，可选)
- 示例：

```bash
curl -X GET "http://localhost:5000/data-collection/data-sources/SRC001/preview?type=trade&limit=10"
```

### 9.4 数据质量评分：GET /data-collection/data-sources/<source_id>/quality-score

```bash
curl -X GET "http://localhost:5000/data-collection/data-sources/SRC001/quality-score"
```

### 9.5 重新连接数据源：POST /data-collection/data-sources/<source_id>/reconnect

```bash
curl -X POST "http://localhost:5000/data-collection/data-sources/SRC001/reconnect"
```

---

## 10. 事件分析模块（/event-analysis）

以单个 `event_id` 的分析为例：

### 10.1 事件概览：GET /event-analysis/events/<event_id>

```bash
curl -X GET "http://localhost:5000/event-analysis/events/EVENT123"
```

### 10.2 时间线：GET /event-analysis/events/<event_id>/timeline

```bash
curl -X GET "http://localhost:5000/event-analysis/events/EVENT123/timeline"
```

### 10.3 关联账户：GET /event-analysis/events/<event_id>/related-accounts

```bash
curl -X GET "http://localhost:5000/event-analysis/events/EVENT123/related-accounts"
```

### 10.4 处理记录：GET /event-analysis/events/<event_id>/processing-records

```bash
curl -X GET "http://localhost:5000/event-analysis/events/EVENT123/processing-records"
```

### 10.5 新增处理记录：POST /event-analysis/events/<event_id>/processing-records

- 请求头：`Content-Type: application/json`
- 请求体参数：
  - `note` (string, 必填)
  - `action` (string, 可选，默认 `标记已处理`)
  - `operator` (string, 可选，默认 `系统`)
- 示例：

```bash
curl -X POST "http://localhost:5000/event-analysis/events/EVENT123/processing-records" \
  -H "Content-Type: application/json" \
  -d '{
    "note": "人工确认无风险，关闭事件",
    "action": "关闭事件",
    "operator": "admin"
  }'
```

### 10.6 更新事件状态：PUT /event-analysis/events/<event_id>/status

- 请求体参数：
  - `status` (string, 必填：`pending` / `processing` / `resolved` / `ignored`)
- 示例：

```bash
curl -X PUT "http://localhost:5000/event-analysis/events/EVENT123/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved"
  }'
```

---

## 11. 模型占位接口（/api/model）

### 11.1 风控评分：POST /api/model/risk_score

- 请求体参数：任意 JSON（当前不会实际使用）
- 示例：

```bash
curl -X POST "http://localhost:5000/api/model/risk_score" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER123",
    "amount": 5000
  }'
```

---

> 如果你在实际测试过程中需要新增某个接口的详细示例，可以直接在本文件相应模块下追加一小节，保持同样结构（接口路径 + 参数说明 + curl 示例）。
