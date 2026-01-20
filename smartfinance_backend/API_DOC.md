# 智能风控系统 API 文档（基于当前后端代码）

---

## 1. 总体说明

- 技术栈：Flask + SQLAlchemy（MySQL）
- 主要模块：
  - 认证与账户：`/api/auth/...`
  - 用户与登录日志：`/api/users/...`
  - 交易与规则检测：`/api/transactions/...`
  - 模型占位：`/api/model/...`
  - 风险事件基础接口：`/api/risk_events/...`
  - 实时监控：`/api/monitor/...`
  - 告警管理：`/api/alerts/...`
  - 数据源基础接口：`/api/data_sources/...`
  - 数据采集模块：`/data-collection/...`
  - 事件分析模块：`/event-analysis/...`

- 鉴权方式：
  - 登录成功后返回 `token`；后续推荐在请求头中携带：
    
    ```http
    Authorization: Bearer <token>
    ```

  - 当前仅部分接口使用 token 校验（如 `/api/auth/me`、`/api/auth/change-password`），其它接口暂未强制校验。

### 1.1 统一响应格式

大部分新接口通过 `api_utils.api_response` 返回统一结构：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": 1700000000000
}
```

分页接口通过 `paginated_response`，`data` 为：

```json
{
  "list": [ ... ],
  "total": 123,
  "page": 1,
  "pageSize": 10
}
```

> 兼容性提示：旧接口（如 `/api/health`、`/api/risk_events/*`、`/api/users/*`、`/api/transactions/`、`/api/model/risk_score`）直接返回 JSON，而不是包在上述统一壳中，文档中会特别标出。

---

## 2. 健康检查

### 2.1 GET `/api/health`

- 描述：服务健康检查与简单运行状态。
- 请求：无参数。
- 响应（**非统一壳**）：

```json
{
  "status": "ok" | "degraded",
  "db": "ok" | "error",
  "model_status": "正常",
  "data_status": "正常" | "异常" | "unknown",
  "timestamp": "2026-01-20T10:00:00.000000"
}
```

---

## 3. 认证与账户（/api/auth）

> 所有接口均返回统一壳结构。

### 3.1 POST `/api/auth/register`

- 描述：注册新用户。
- 请求体 JSON：
  - `username` (string, 必填)
  - `password` (string, 必填)
  - `phone` (string, 可选)
  - `email` (string, 可选)
- 示例请求：

```json
{
  "username": "alice",
  "password": "123456",
  "phone": "13800000000",
  "email": "alice@example.com"
}
```

- 响应 `data`：

```json
{
  "user_id": "用户ID",
  "username": "alice",
  "token": "访问令牌"
}
```

### 3.2 POST `/api/auth/login`

- 描述：用户名密码登录。
- 请求体 JSON：
  - `username` (string)
  - `password` (string)
  - `device_id` (string，可选)
  - `ip_address` (string，可选)
  - `client_type` (string，可选，默认 `"WEB"`)
  - `login_location` (string，可选)

- 响应 `data`：

```json
{
  "token": "访问令牌",
  "refreshToken": "刷新令牌（当前与 token 相同）",
  "userInfo": {
    "id": 1,
    "username": "zhang_manager",
    "name": "张经理",
    "email": "zhang@example.com",
    "phone": "13800000000",
    "avatar": "https://example.com/avatar.jpg",
    "role": "manager",
    "department": "风险管理部",
    "employeeId": "EMP-2023001"
  },
  "expiresIn": 43200
}
```

### 3.3 GET `/api/auth/me`

- 描述：获取当前登录用户信息。
- 鉴权：
  - 请求头：`Authorization: Bearer <token>`，或
  - 查询参数：`?token=<token>`。
- 响应 `data`：

```json
{
  "user_id": "...",
  "username": "...",
  "phone": "...",
  "email": "...",
  "status": "正常" | "冻结",
  "account_level": "普通" | "VIP" | ...
}
```

### 3.4 POST `/api/auth/logout`

- 描述：登出（当前仅前端态，后端未维护 token 黑名单）。
- 请求体：可为空。
- 响应：

```json
{
  "code": 200,
  "message": "登出成功",
  "data": null,
  "timestamp": 1700000000000
}
```

### 3.5 POST `/api/auth/refresh`

- 描述：刷新访问令牌。
- 请求体 JSON：

```json
{
  "refreshToken": "旧的 refreshToken"
}
```

- 响应 `data`：

```json
{
  "token": "新的访问令牌",
  "expiresIn": 43200
}
```

### 3.6 POST `/api/auth/change-password`

- 描述：修改登录密码。
- 鉴权：`Authorization: Bearer <token>`。
- 请求体 JSON：

```json
{
  "oldPassword": "原密码",
  "newPassword": "新密码"
}
```

- 响应：`message: "密码修改成功"`。

---

## 4. 用户与登录日志（/api/users）

> 注意：本模块接口仍返回“裸 JSON”，**不**使用统一壳。

### 4.1 GET `/api/users/`

- 描述：用户列表。
- 查询参数：
  - `page` (int, 默认 1)
  - `size` (int, 默认 20)
  - `q` (string，可选，用户名模糊搜索)
- 响应：

```json
{
  "items": [
    {
      "user_id": "...",
      "username": "...",
      "status": "正常" | "冻结",
      "account_level": "普通" | "VIP"
    }
  ],
  "page": 1,
  "size": 20,
  "total": 100
}
```

### 4.2 GET `/api/users/<user_id>/login_logs`

- 描述：指定用户最近登录记录（最多 50 条）。
- 响应：

```json
[
  {
    "log_id": 1,
    "login_time": "2026-01-20T10:00:00",
    "ip_address": "1.2.3.4",
    "login_status": "成功" | "失败",
    "login_location": "上海",
    "client_type": "WEB" | "ANDROID" | ...
  }
]
```

---

## 5. 交易接入与规则检测（/api/transactions）

> 返回为“裸 JSON”。

### 5.1 POST `/api/transactions/`

- 描述：接收入账交易，根据简单规则创建风险事件和告警。
- 请求体 JSON（关键字段）：

```json
{
  "tx_id": "可选，不传则后端生成",
  "user_id": "用户ID",
  "device_id": "设备ID，可选",
  "amount": 1200.5,
  "currency": "CNY",
  "category": "转账",
  "ip_address": "1.2.3.4",
  "status": "成功"
}
```

- 响应：

```json
{
  "tx_id": "交易ID",
  "event_id": "关联风险事件ID",
  "risk_score": 0,
  "risk_level": "高" | "中" | "低",
  "reasons": ["大额交易", "短时间内多笔交易", "异常设备"]
}
```

---

## 6. 模型占位接口（/api/model）

> 返回为“裸 JSON”。

### 6.1 POST `/api/model/risk_score`

- 描述：风控模型评分占位接口（当前返回固定值）。
- 请求体：任意 JSON（当前未使用）。
- 响应：

```json
{
  "score": 65,
  "risk_level": "中",
  "explanations": [
    "占位：基于规则+模型的综合评分接口，当前未接入大模型"
  ]
}
```

---

## 7. 风险事件基础接口（/api/risk_events）

> 返回为“裸 JSON”，主要供内部使用；监控与事件分析有专门接口。

### 7.1 GET `/api/risk_events/`

- 描述：风险事件列表。
- 查询参数：
  - `page` (int, 默认 1)
  - `size` (int, 默认 20)
  - `status` (string，可选，中文：`待处理/处理中/已解决/已忽略`)
  - `risk_level` (string，可选，中文：`高/中/低`)

- 响应示例：

```json
{
  "items": [
    {
      "event_id": "...",
      "event_type": "账户盗用/异常交易/证件伪造/批量注册/设备异常",
      "risk_level": "高/中/低",
      "score": 80,
      "status": "待处理",
      "user_id": "...",
      "device_id": "...",
      "ip_address": "...",
      "detection_time": "...",
      "created_at": "..."
    }
  ],
  "page": 1,
  "size": 20,
  "total": 100
}
```

### 7.2 GET `/api/risk_events/stats`

- 描述：风险事件汇总与 24 小时趋势。
- 响应：

```json
{
  "total": 100,
  "by_level": {"高": 10, "中": 50, "低": 40},
  "by_status": {"待处理": 10, "处理中": 5, "已解决": 80, "已忽略": 5},
  "trend_24h": [
    {
      "timestamp": "2026-01-20T10:00:00",
      "high": 1,
      "medium": 2,
      "low": 3,
      "total": 6
    }
  ]
}
```

### 7.3 GET `/api/risk_events/<event_id>`

- 描述：风险事件详情（含用户、设备、交易、时间线、告警、处理记录、关联用户）。
- 响应字段：
  - `event`: 事件基础信息
  - `user`: 用户信息（可为 null）
  - `device`: 设备信息（可为 null）
  - `recent_transactions`: 最近交易列表
  - `timelines`: 事件时间线
  - `alerts`: 关联告警
  - `handling_records`: 处理记录
  - `related_users`: 关联用户

### 7.4 PATCH `/api/risk_events/<event_id>/status`

- 描述：更新事件状态（中文状态）。
- 请求体 JSON：

```json
{ "status": "待处理" | "处理中" | "已解决" | "已忽略" }
```

- 响应：`{"message": "ok"}` 或错误。

### 7.5 GET `/api/risk_events/<event_id>/graph`

- 描述：事件关系图（事件-用户-设备-关联用户）。
- 响应：

```json
{
  "nodes": [{"id": "...", "type": "event/user/device", "label": "..."}],
  "edges": [{"source": "...", "target": "...", "type": "belongs_to/from_device/..."}]
}
```

---

## 8. 实时监控接口（/api/monitor）

> 所有接口均使用统一壳格式。

### 8.1 GET `/api/monitor/risk-events`

- 描述：监控页风险事件列表。
- 查询参数：
  - `page`, `pageSize`
  - `type`: `"all" | "fraud" | "fake" | "abnormal" | "other"`
  - `status`: `"all" | "pending" | "processing" | "resolved" | "ignored"`
  - `keyword`: 描述模糊搜索

- `data.list` 每项主要字段：

```json
{
  "id": "事件ID",
  "type": "account_theft" | "transaction_abnormal",
  "typeName": "账户盗用/异常交易/...",
  "level": "high/medium/low",
  "levelName": "高/中/低",
  "status": "pending/processing/resolved/ignored",
  "statusName": "待处理/处理中/已解决/已忽略",
  "riskScore": 80,
  "detectTime": "2026-01-20 10:00:00",
  "description": "事件描述",
  "userId": "...",
  "username": "...",
  "userName": "..."
}
```

### 8.2 GET `/api/monitor/risk-trend`

- 描述：最近 24 小时风险趋势（聚合为 8 个时间点）。
- 查询参数：
  - `period` (string，可选，当前未实际使用)
- 响应 `data`：

```json
{
  "labels": ["10:00", "13:00", ...],
  "datasets": [
    {"label": "高风险", "data": [1,2,...]},
    {"label": "中风险", "data": [3,4,...]},
    {"label": "低风险", "data": [5,6,...]}
  ]
}
```

### 8.3 GET `/api/monitor/system-status`

- 描述：系统整体运行状态。
- 响应 `data`：

```json
{
  "modelStatus": "normal",
  "modelStatusName": "正常",
  "dataStatus": "normal" | "abnormal",
  "dataStatusName": "正常" | "异常"
}
```

### 8.4 GET `/api/monitor/risk-events/<event_id>`

- 描述：监控视角下的单个事件详情（简化版）。
- 响应 `data` 主要字段：
  - 顶层：`id`, `type`/`typeName`, `level`/`levelName`, `status`/`statusName`,
    `riskScore`, `detectTime`, `description`。
  - `userInfo`: 用户基本信息（注册时间、等级等）。
  - `eventDetails`: 登录 IP、地理位置、设备等。

---

## 9. 告警管理接口（/api/alerts）

> 所有接口均使用统一壳格式。

### 9.1 GET `/api/alerts/`

- 描述：告警列表。
- 查询参数：
  - `page`, `pageSize`
  - `status`: `"all" | "pending" | "processing" | "resolved" | "ignored"`
  - `level`: `"all" | "high" | "medium" | "low"`
  - `eventType`: `"all" | "account" | "transaction" | "identity" | "device"`
  - `timeRange`: `"all" | "today" | "yesterday" | "7days" | "30days" | "custom"`
  - `startTime`, `endTime`（当 `timeRange=custom` 时）
  - `keyword`: 按告警 ID/类型模糊搜索

- `data.list` 每项主要字段：

```json
{
  "id": "告警ID",
  "eventType": "account",
  "eventTypeName": "账户盗用告警",
  "level": "high/medium/low",
  "levelName": "高/中/低",
  "status": "pending/processing/resolved/ignored",
  "statusName": "待处理/处理中/已解决/已忽略",
  "triggerTime": "2026-01-20 10:00:00",
  "handler": "处理人ID/名称",
  "handlerName": "处理人名称"
}
```

### 9.2 PATCH `/api/alerts/<alert_id>/status`

- 描述：更新告警状态（PATCH）。
- 请求体 JSON：

```json
{ "status": "pending" | "processing" | "resolved" | "ignored" }
```

- 响应：`message: "状态更新成功"`。

### 9.3 PUT `/api/alerts/<alert_id>/status`

- 描述：同 9.2，兼容 PUT 方法。

### 9.4 GET `/api/alerts/stats`

- 描述：告警基础统计（内部使用）。
- `data` 字段：

```json
{
  "total": 100,
  "status_counts": {"待处理": 10, "处理中": 5, "已解决": 80, "已忽略": 5},
  "level_counts": {"高": 10, "中": 50, "低": 40},
  "high_risk_count": 10,
  "recent_trend": [
    {
      "date": "2026-01-14",
      "account": 1,
      "transaction": 2,
      "identity": 0,
      "device": 1,
      "behavior": 0,
      "other": 0
    }
  ]
}
```

### 9.5 GET `/api/alerts/statistics`

- 描述：总览统计（对外）。
- 响应 `data`：

```json
{
  "total": 100,
  "pending": 10,
  "resolved": 80,
  "highRisk": 10,
  "mediumRisk": 50,
  "lowRisk": 40
}
```

### 9.6 GET `/api/alerts/level-distribution`

- 描述：告警级别分布。
- 响应 `data`：

```json
{
  "high": 10,
  "medium": 50,
  "low": 40
}
```

### 9.7 GET `/api/alerts/type-trend`

- 描述：告警类型趋势。
- 查询参数：
  - `days` (int, 默认 6，表示近 N 天)
- 响应 `data`：

```json
{
  "labels": ["06/01", "06/02", ...],
  "datasets": [
    {"label": "账户风险", "data": [1,2,...]},
    {"label": "交易风险", "data": [...]},
    {"label": "身份验证", "data": [...]},
    {"label": "设备异常", "data": [...]},
    {"label": "行为异常", "data": [...]}  
  ]
}
```

### 9.8 GET `/api/alerts/<alert_id>`

- 描述：告警详情。
- 响应 `data` 主要结构：

```json
{
  "id": "告警ID",
  "eventType": "account",
  "eventTypeName": "账户盗用告警",
  "level": "high/medium/low",
  "levelName": "高/中/低",
  "status": "pending/processing/resolved/ignored",
  "statusName": "待处理/处理中/已解决/已忽略",
  "triggerTime": "2026-01-20 10:00:00",
  "rule": "触发规则",
  "riskScore": 80,
  "basicInfo": { ... },
  "userInfo": { ... },
  "eventDetails": {
    "description": "事件描述",
    "abnormalLogin": {"ip": "...", "location": "...", ...},
    "normalPattern": {"commonIp": "..."}
  },
  "riskAssessment": "风险评估文本",
  "processingRecords": [
    {
      "type": "system" | "manual",
      "typeName": "系统创建/人工处理",
      "handler": "...",
      "handlerName": "...",
      "time": "2026-01-20 10:05:00",
      "note": "处理说明"
    }
  ]
}
```

### 9.9 POST `/api/alerts/batch-operation`

- 描述：批量操作告警。
- 请求体 JSON：

```json
{
  "alertIds": ["告警ID1", "告警ID2"],
  "action": "resolve" | "ignore" | "process" | "delete"
}
```

- 响应 `data`：

```json
{
  "successCount": 10,
  "failCount": 2
}
```

### 9.10 POST `/api/alerts/<alert_id>/processing-record`

- 描述：为告警添加处理记录。
- 请求体 JSON：

```json
{
  "note": "必填，处理说明",
  "action": "freeze" | "send_verification" | "mark_resolved" | "ignore" | "contact_user"
}
```

- 响应：`message: "处理记录添加成功"`。

---

## 10. 数据源基础接口（/api/data_sources）

> 全部使用统一壳格式，供内部使用或简单监控。

### 10.1 GET `/api/data_sources/`

- 描述：数据源列表。
- 响应 `data`：数组，每项：

```json
{
  "source_id": "...",
  "source_name": "...",
  "source_type": "数据库/API/文件/消息队列",
  "status": "正常/异常/中断",
  "last_sync_time": "...",
  "sync_progress": 80.5,
  "error_count": 0
}
```

### 10.2 GET `/api/data_sources/quality_issues`

- 描述：所有数据质量问题列表。
- 响应 `data`：数组，每项：

```json
{
  "issue_id": "...",
  "source_id": "...",
  "issue_type": "缺失字段/格式错误/值异常/...",
  "severity": "高/中/低",
  "status": "已解决/未解决/...",
  "created_at": "..."
}
```

### 10.3 GET `/api/data_sources/stats`

- 描述：数据源与质量问题汇总。
- 响应 `data`：

```json
{
  "total_sources": 10,
  "normal_sources": 8,
  "abnormal_sources": 2,
  "open_quality_issues": 5
}
```

---

## 11. 数据采集模块（/data-collection）

> 全部使用统一壳格式，专为“数据采集监控”前端设计。

### 11.1 GET `/data-collection/data-sources`

- 描述：数据源分页列表。
- 查询参数：
  - `page`, `pageSize`
  - `status`: `"all" | "normal" | "warning" | "error" | "stopped"`
  - `keyword`: 数据源名称模糊搜索

- 响应 `data`：

```json
{
  "list": [
    {
      "id": "数据源ID",
      "name": "数据源名称",
      "type": "database/api/file/stream",
      "connection": "连接串或 URL",
      "status": "normal/error/stopped",
      "statusName": "正常/异常/中断",
      "collectionStatus": "running/stopped",
      "collectionStatusName": "采集进行中/已停止",
      "lastSyncTime": "2026-01-20 10:00:00",
      "progress": 80,
      "todayCollected": 0,
      "estimatedCompletion": null,
      "qualityIssuesCount": 1,
      "errorMessage": "最近错误信息"
    }
  ],
  "total": 10,
  "page": 1,
  "pageSize": 10
}
```

### 11.2 GET `/data-collection/statistics`

- 描述：数据源统计汇总。
- 响应 `data`：

```json
{
  "total": 10,
  "normal": 8,
  "abnormal": 2,
  "qualityIssues": 5
}
```

### 11.3 GET `/data-collection/status-distribution`

- 描述：数据源状态分布。
- 响应 `data`：

```json
{
  "normal": 8,
  "warning": 1,
  "error": 1,
  "stopped": 0
}
```

### 11.4 GET `/data-collection/collection-trend`

- 描述：数据采集趋势（当前为示例占位数据）。
- 查询参数：`period`（暂未使用）。
- 响应 `data`：

```json
{
  "labels": ["10:00", "11:00", ...],
  "datasets": [
    {"label": "交易数据", "data": [...]},
    {"label": "用户行为", "data": [...]},
    {"label": "设备数据", "data": [...]}  
  ]
}
```

### 11.5 GET `/data-collection/data-sources/<source_id>/quality-issues`

- 描述：单个数据源的质量问题列表。
- 查询参数：
  - `page`, `pageSize`
  - `type`: `"all" | "missing" | "format" | "abnormal" | "inconsistent"`

- 响应 `data`：

```json
{
  "list": [
    {
      "id": "ISSUE-1",
      "type": "missing/format/abnormal",
      "typeName": "缺失字段/格式错误/值异常",
      "field": null,
      "description": "问题描述",
      "time": "2026-01-20 10:00:00"
    }
  ],
  "statistics": {
    "missing": 1,
    "formatError": 0,
    "abnormal": 0
  },
  "total": 1,
  "page": 1,
  "pageSize": 10
}
```

### 11.6 GET `/data-collection/data-sources/<source_id>/preview`

- 描述：数据预览（占位样例）。
- 查询参数：
  - `type`: `"trade" | "user" | "device"`（默认 `trade`）
  - `limit`: 数量（当前未严格使用）

- 响应 `data`：

```json
{
  "list": [ { ... 示例记录 ... } ],
  "total": 1
}
```

### 11.7 GET `/data-collection/data-sources/<source_id>/quality-score`

- 描述：数据质量评分（基于问题严重度估算）。
- 响应 `data`：

```json
{
  "score": 85,
  "maxScore": 100,
  "dimensions": {
    "completeness": 85,
    "accuracy": 85,
    "consistency": 85,
    "timeliness": 85
  }
}
```

### 11.8 POST `/data-collection/data-sources/<source_id>/reconnect`

- 描述：重新连接数据源，将状态改为“正常”。
- 响应：`message: "重新连接成功"`。

### 11.9 GET `/data-collection/data-sources/<source_id>/quality-issues/export`

- 描述：导出数据质量问题列表（CSV）。
- 查询参数：
  - `format`: 目前仅支持 `"csv"`
- 响应：`text/csv` 文件下载。

---

## 12. 事件分析模块（/event-analysis）

> 全部使用统一壳格式，对应完整的事件分析流程。

### 12.1 GET `/event-analysis/events/<event_id>`

- 描述：事件概览。
- 响应 `data`：

```json
{
  "id": "事件ID",
  "title": "事件标题/类型",
  "level": "high/medium/low",
  "levelName": "高/中/低",
  "status": "pending/processing/resolved/ignored",
  "statusName": "待处理/处理中/已解决/已忽略",
  "score": 80,
  "type": "account",
  "typeName": "账户盗用/异常交易/...",
  "createTime": "2026-01-20 10:00:00",
  "updateTime": "2026-01-20 10:05:00",
  "description": "事件描述",
  "user": {
    "userId": "...",
    "username": "...",
    "name": "...",
    "level": "普通/VIP"
  }
}
```

### 12.2 GET `/event-analysis/events/<event_id>/timeline`

- 描述：事件时间线。
- 响应 `data`：数组，每项：

```json
{
  "time": "2026-01-20 10:00:00",
  "type": "normal/warning/danger/processing/info",
  "typeName": "登录/验证/预警/...",
  "description": "步骤描述"
}
```

### 12.3 GET `/event-analysis/events/<event_id>/trace-path`

- 描述：事件行为路径关系图。
- 响应 `data`：

```json
{
  "nodes": [
    {"id": "user-...", "type": "user", "label": "用户名"},
    {"id": "device-...", "type": "device", "label": "设备名称"},
    {"id": "ip-1.2.3.4", "type": "ip", "label": "1.2.3.4"}
  ],
  "edges": [
    {"source": "user-...", "target": "device-...", "relation": "使用设备登录"},
    {"source": "user-...", "target": "ip-1.2.3.4", "relation": "登录 IP"}
  ]
}
```

### 12.4 GET `/event-analysis/events/<event_id>/related-accounts`

- 描述：关联账户列表。
- 响应 `data`：

```json
[
  {
    "userId": "关联用户ID",
    "username": "关联用户名",
    "relationType": "同设备/同IP/同绑卡/...",
    "riskScore": 60
  }
]
```

### 12.5 GET `/event-analysis/events/<event_id>/devices-ips`

- 描述：事件涉及的设备和 IP。
- 响应 `data`：

```json
{
  "devices": [
    {
      "deviceId": "设备ID",
      "deviceName": "设备名称",
      "deviceType": "Android/iOS/PC",
      "location": "上海"
    }
  ],
  "ips": [
    {
      "ip": "1.2.3.4",
      "location": "未知/上海",
      "riskScore": 80
    }
  ]
}
```

### 12.6 GET `/event-analysis/events/<event_id>/transactions`

- 描述：事件关联交易列表（分页）。
- 查询参数：`page`, `pageSize`。
- 响应：统一壳 + `data.list`，每项：

```json
{
  "transactionId": "交易ID",
  "time": "2026-01-20 10:00:00",
  "amount": 1200.5,
  "type": "转账/支付/...",
  "status": "成功/失败/..."
}
```

### 12.7 GET `/event-analysis/events/<event_id>/responsibility`

- 描述：责任追溯（当前为简化占位）。
- 响应 `data`：

```json
{
  "mainParty": {
    "type": "user",
    "id": "用户ID",
    "name": "用户名",
    "responsibility": "待确认"
  },
  "conclusion": "基于当前证据，责任仍在调查中。"
}
```

### 12.8 GET `/event-analysis/events/<event_id>/risk-analysis`

- 描述：风险分析与建议。
- 响应 `data`：

```json
{
  "assessment": "分析内容（优先来自 RiskAnalysisRecommendation）",
  "suggestions": ["建议核实用户身份...", "建议评估近期相关交易..."]
}
```

### 12.9 GET `/event-analysis/events/<event_id>/processing-records`

- 描述：事件处理记录列表。
- 响应 `data`：

```json
[
  {
    "id": 1,
    "operator": "处理人",
    "action": "操作内容",
    "time": "2026-01-20 10:05:00",
    "note": "处理备注"
  }
]
```

### 12.10 POST `/event-analysis/events/<event_id>/processing-records`

- 描述：新增事件处理记录。
- 请求体 JSON：

```json
{
  "note": "必填，处理说明",
  "action": "标记已处理/冻结账户/...",
  "operator": "处理人名称，可选，默认系统"
}
```

- 响应：`message: "处理记录添加成功"`。

### 12.11 PUT `/event-analysis/events/<event_id>/status`

- 描述：更新事件状态（英文枚举）。
- 请求体 JSON：

```json
{ "status": "pending" | "processing" | "resolved" | "ignored" }
```

- 响应：`message: "事件状态更新成功"`。

### 12.12 PUT `/event-analysis/events/<event_id>`

- 描述：编辑事件信息（目前支持修改风险等级与描述）。
- 请求体 JSON：

```json
{
  "level": "high" | "medium" | "low",
  "description": "新的事件描述"
}
```

- 响应：`message: "事件信息更新成功"`。

### 12.13 GET `/event-analysis/events/<event_id>/export`

- 描述：导出事件分析报告。
- 响应：`text/plain` 文本文件下载，内容包含事件 ID、类型、风险等级、评分、状态、检测时间与描述等基本信息。

---

