# 风控管理系统 API 接口文档（实现版）

> 本文档根据当前后端代码实际实现自动梳理，格式与原始《风控管理系统 API 接口文档》保持尽量一致，但字段、URL、状态码等以本文件为准。

---

## 1. 基础信息

### 1.1 基础 URL

```
开发环境（Flask 默认）: http://localhost:5000/api
前端示例使用:       http://localhost:8080/api （通过代理转发到后端）
```

### 1.2 通用请求头

大部分业务接口建议统一使用：

```
Content-Type: application/json
Authorization: Bearer {token}
```

说明：
- 部分接口目前代码中未强制校验 token（未做装饰器统一认证），但推荐前端仍统一带上 Authorization 头，后续方便统一接入鉴权。
- 认证与用户信息相关接口会真实解析并校验 `Authorization: Bearer {token}`。

### 1.3 通用响应格式

除极个别返回原始 `jsonify` 的接口外，大部分接口通过 `utils.response.api_response` 或 `paginated_response` 统一返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": 1697123456789
}
```

分页接口（使用 `paginated_response`）：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [],
    "total": 0,
    "page": 1,
    "pageSize": 10
  },
  "timestamp": 1697123456789
}
```

### 1.4 状态码说明（code 字段）

- `200`: 成功
- `400`: 请求参数错误 / 业务校验失败
- `401`: 未授权或 token 非法
- `403`: 被禁止（如账户冻结）
- `404`: 资源不存在
- `409`: 资源冲突（如注册用户名重复）
- `500`: 服务器内部错误（部分地方会被归为 400 文本错误）

---

## 2. 认证相关接口

路由前缀：`/api/auth`

### 2.1 用户注册

**接口地址:** `POST /api/auth/register`

**请求体（JSON）:**
```json
{
  "username": "string",
  "password": "string",
  "phone": "string，可选",
  "email": "string，可选"
}
```

**说明：**
- `username` 与 `password` 必填，否则返回 `code=400`，`message="username and password required"`。
- 注册成功时由服务层生成用户并返回 token；若用户名已存在等冲突，返回 `code=409`，`message` 为具体错误信息。

**响应示例（成功）：**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user_id": "U20230101001",
    "username": "zhang_manager",
    "token": "jwt_token_string"
  },
  "timestamp": 1697123456789
}
```

---

### 2.2 用户登录

**接口地址:** `POST /api/auth/login`

**请求体（JSON）：**
```json
{
  "username": "string",        // 必填
  "password": "string",        // 必填
  "device_id": "string 可选",  // 设备 ID
  "ip_address": "string 可选",  // 登录 IP
  "client_type": "string 可选，默认 WEB",
  "login_location": "string 可选" // 登录地描述
}
```

**响应示例（成功）：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "jwt_token_string",
    "refreshToken": "与 token 相同（当前实现）",
    "userInfo": {
      "id": "USER-001",
      "username": "zhang_manager",
      "name": "zhang_manager",         // 当前实现使用 username 作为 name
      "email": "zhang@example.com",
      "phone": "138****8888",
      "avatar": "头像地址，可为空",
      "role": "manager/user/vip_user", // 由 user.role 或 account_level 推导
      "department": "部门，可为空",
      "employeeId": "EMP-2023001 可为空"
    },
    "expiresIn": 43200                  // 秒，大约 12 小时
  },
  "timestamp": 1697123456789
}
```

**错误情况：**
- 账号被冻结：`code=403`，`message` 包含 `frozen` 文本。
- 用户不存在/密码错误：`code=401`。
- 其他校验错误：`code=400`，`message` 为具体错误信息。

---

### 2.3 获取当前登录信息

**接口地址:** `GET /api/auth/me`

**请求头：**
```
Authorization: Bearer {token}
```
或查询参数：`?token=xxx`（不推荐，仅兼容）

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": "USER-001",
    "username": "zhang_manager",
    "phone": "138****8888",
    "email": "zhang@example.com",
    "status": "正常/冻结",
    "account_level": "普通/黄金/VIP 等"
  },
  "timestamp": 1697123456789
}
```

**错误：**
- 未提供 token：`code=401`，`message="token required"`
- token 非法或过期：`code=401`，`message` 为错误原因
- 用户不存在：`code=404`，`message="user not found"`

---

### 2.4 用户登出

**接口地址:** `POST /api/auth/logout`

**说明：**
- 当前实现为无状态登出，仅返回成功，不做 token 黑名单等处理。

**响应示例：**
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null,
  "timestamp": 1697123456789
}
```

---

### 2.5 刷新 Token

**接口地址:** `POST /api/auth/refresh`

**请求体（JSON）：**
```json
{
  "refreshToken": "string"  // 必填
}
```

**响应示例（成功）：**
```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "new_jwt_token_string",
    "expiresIn": 43200
  },
  "timestamp": 1697123456789
}
```

**错误：**
- 缺少 refreshToken：`code=400`
- refreshToken 非法或过期：`code=401`，`message="invalid refreshToken"`

---

### 2.6 修改密码

**接口地址:** `POST /api/auth/change-password`

**请求头：**
```
Authorization: Bearer {token}
```

**请求体（JSON）：**
```json
{
  "oldPassword": "string",   // 必填
  "newPassword": "string"    // 必填
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null,
  "timestamp": 1697123456789
}
```

**错误：**
- 缺少字段：`code=400`，`message="oldPassword and newPassword required"`
- token 非法或业务校验失败：`code=400`，`message` 为具体原因

---

### 2.7 发送验证码（忘记密码）

**接口地址:** `POST /api/auth/send-verification-code`

**请求体：**
```json
{
  "contact": "string"  // 邮箱或手机号，必填
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "expiresIn": 600
  },
  "timestamp": 1697123456789
}
```

**错误：**
- 缺少 contact：`code=400`, `message="contact required"`

---

### 2.8 验证验证码并重置密码

**接口地址:** `POST /api/auth/reset-password`

**请求体：**
```json
{
  "contact": "string",            // 必填
  "verificationCode": "string",   // 必填
  "newPassword": "string"         // 必填
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "密码重置成功",
  "data": null,
  "timestamp": 1697123456789
}
```

---

## 3. 用户信息接口

路由前缀：`/api/user`

### 3.1 获取当前用户信息

**接口地址:** `GET /api/user/profile`

**请求头：**
```
Authorization: Bearer {token}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "USER-001",
    "username": "zhang_manager",
    "name": "张三",
    "email": "zhang@example.com",
    "phone": "138****8888",
    "avatar": "/static/avatars/USER-001.png",
    "gender": "男/女/未知",
    "birthday": "1990-05-15",
    "bio": "个人简介",
    "role": "manager",
    "department": "风险管理部",
    "employeeId": "EMP-2023001",
    "joinDate": "2023-01-15"
  },
  "timestamp": 1697123456789
}
```

**错误：**
- token 无效或未登录：`code=401`, `message="unauthorized"`

---

### 3.2 更新用户信息

**接口地址:** `PUT /api/user/profile`

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**请求体（JSON）：**
```json
{
  "name": "string 可选",
  "email": "string 可选",
  "phone": "string 可选",
  "gender": "string 可选",      // 男/女/其他
  "birthday": "string 可选",    // YYYY-MM-DD
  "bio": "string 可选"
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": "USER-001",
    "name": "张三",
    "email": "zhang@example.com",
    "phone": "138****8888",
    "gender": "男",
    "birthday": "1990-05-15",
    "bio": "负责公司风险控制与管理工作"
  },
  "timestamp": 1697123456789
}
```

---

### 3.3 上传头像

**接口地址:** `POST /api/user/avatar`

**请求头：**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求参数（表单）：**
- `file`: 图片文件，必填

**说明：**
- 头像文件会保存到后端 `static/avatars` 目录，文件名为 `{user_id}{原扩展名}`。

**响应示例：**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "avatar": "/static/avatars/USER-001.png"
  },
  "timestamp": 1697123456789
}
```

---

## 4. 实时监控接口

路由前缀：`/api/monitor`

### 4.1 获取风险事件列表

**接口地址:** `GET /api/monitor/risk-events`

**请求参数（query）：**

- `page`: int，默认 1
- `pageSize`: int，默认 10
- `type`: string，默认 `all`
  - `all`
  - `fraud` （账户盗用）
  - `fake` （证件伪造）
  - `abnormal`（异常交易/设备异常）
  - `other`（批量注册等其他）
- `status`: string，默认 `all`
  - `pending/processing/resolved/ignored`
- `keyword`: string，可选，在描述中模糊搜索

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "EVT-20230615-001",
        "type": "account_theft",          
        "typeName": "账户盗用",            
        "level": "high",                  
        "levelName": "高",                
        "status": "pending",              
        "statusName": "待处理",            
        "riskScore": 92,
        "detectTime": "2023-06-15 10:24:35",
        "description": "规则检测描述",
        "userId": "USER-789456",
        "username": "wangxiaoming",
        "userName": "wangxiaoming"
      }
    ],
    "total": 24,
    "page": 1,
    "pageSize": 10
  },
  "timestamp": 1697123456789
}
```

---

### 4.2 获取风险趋势数据

**接口地址:** `GET /api/monitor/risk-trend`

**请求参数：**
- `period`: string，默认 `today`（当前实现仅用于占位，不影响返回逻辑）

**响应说明：**
- 按最近 24 小时聚合为 8 个时间点，每 3 小时一个点，统计不同风险等级数量。

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "labels": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
    "datasets": [
      {"label": "高风险", "data": [2, 1, 0, 3, 5, 4, 3, 4]},
      {"label": "中风险", "data": [3, 2, 4, 5, 6, 5, 7, 6]},
      {"label": "低风险", "data": [5, 7, 6, 8, 10, 9, 8, 10]}
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 4.3 获取系统状态

**接口地址:** `GET /api/monitor/system-status`

**响应说明：**
- `modelStatus` 当前固定为 `normal` / "正常"。
- `dataStatus` 根据数据源表中是否存在非“正常”的数据源来判断 `normal/abnormal`。

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "modelStatus": "normal",
    "modelStatusName": "正常",
    "dataStatus": "normal",
    "dataStatusName": "正常"
  },
  "timestamp": 1697123456789
}
```

---

### 4.4 获取风险事件详情

**接口地址:** `GET /api/monitor/risk-events/{eventId}`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "EVT-20230615-001",
    "type": "account_theft",
    "typeName": "账户盗用",
    "level": "high",
    "levelName": "高",
    "status": "pending",
    "statusName": "待处理",
    "riskScore": 92,
    "detectTime": "2023-06-15 10:24:35",
    "description": "事件描述",
    "eventDetails": {
      "loginIp": "1.2.3.4",
      "loginLocation": "上海",
      "commonLocation": "上海",
      "device": "iPhone 13",
      "commonDevice": "iPhone 13"
    },
    "userInfo": {
      "userId": "USER-789456",
      "username": "wangxiaoming",
      "name": "wangxiaoming",
      "registerTime": "2022-03-15",
      "level": "VIP会员",
      "lastLogin": null
    },
    "riskAssessment": "当前复用 description 字段"
  },
  "timestamp": 1697123456789
}
```

---

### 4.5 处理风险事件

**接口地址:** `POST /api/monitor/risk-events/{eventId}/handle`

**请求体：**
```json
{
  "action": "string", // 必填，自定义动作编码，由服务内部解释
  "note": "string 可选" // 处理备注
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "处理成功",
  "data": null,
  "timestamp": 1697123456789
}
```

**错误：**
- 未传 action：`code=400`, `message="action required"`

---

## 5. 风险告警接口

路由前缀：`/api/alerts`

### 5.1 获取告警列表

**接口地址:** `GET /api/alerts`

**请求参数（query）：**

- `page`: int，默认 1
- `pageSize`: int，默认 10
- `eventType`: string，默认 `all` （按内部映射到 RiskEvent.event_type）
- `level`: string，`all/high/medium/low`
- `status`: string，`all/pending/processing/resolved/ignored`
- `timeRange`: string，`today/yesterday/7days/30days/custom/all`
- `startTime`, `endTime`: string，自定义时间范围，`timeRange=custom` 时生效，格式为 ISO8601 或 `YYYY-MM-DDTHH:MM:SS`
- `keyword`: string，在告警 ID/类型上模糊匹配

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "ALERT-001",
        "eventType": "account",      
        "eventTypeName": "账户盗用告警", 
        "level": "high",
        "levelName": "高",
        "status": "pending",
        "statusName": "待处理",
        "triggerTime": "2023-06-15 10:24:35",
        "handler": "张经理",
        "handlerName": "张经理"
      }
    ],
    "total": 147,
    "page": 1,
    "pageSize": 10
  },
  "timestamp": 1697123456789
}
```

---

### 5.2 获取告警统计

**接口地址:** `GET /api/alerts/statistics`

**请求参数：**
- `timeRange` 参数在当前实现中未使用，接口返回全量统计。

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 147,
    "pending": 36,
    "resolved": 98,
    "highRisk": 13,
    "mediumRisk": 56,
    "lowRisk": 78
  },
  "timestamp": 1697123456789
}
```

---

### 5.3 获取告警级别分布

**接口地址:** `GET /api/alerts/level-distribution`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "high": 13,
    "medium": 56,
    "low": 78
  },
  "timestamp": 1697123456789
}
```

---

### 5.4 获取告警类型趋势

**接口地址:** `GET /api/alerts/type-trend`

**请求参数：**
- `days`: int，默认 6

**响应示例（与示例文档结构一致）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "labels": ["6/10", "6/11", "6/12", "6/13", "6/14", "6/15"],
    "datasets": [
      {"label": "账户风险", "data": [8, 12, 9, 15, 11, 7]},
      {"label": "交易风险", "data": [15, 18, 12, 20, 17, 9]},
      {"label": "身份验证", "data": [5, 7, 9, 6, 8, 4]},
      {"label": "设备异常", "data": [3, 5, 4, 6, 5, 3]},
      {"label": "行为异常", "data": [7, 6, 9, 8, 10, 5]}
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 5.5 获取告警详情

**接口地址:** `GET /api/alerts/{alertId}`

**响应结构与原文档类似，但部分字段由事件/用户实际数据推导：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "ALERT-001",
    "eventType": "account",
    "eventTypeName": "账户盗用告警",
    "level": "high",
    "levelName": "高",
    "status": "pending",
    "statusName": "待处理",
    "triggerTime": "2023-06-15 10:24:35",
    "rule": "触发规则名称",
    "riskScore": 92,
    "basicInfo": { ... },
    "userInfo": { ... },
    "eventDetails": { ... },
    "riskAssessment": "当前基于事件描述",
    "processingRecords": [
      {
        "type": "system/manual",
        "typeName": "系统创建/人工处理",
        "handler": "操作人",
        "handlerName": "操作人",
        "time": "2023-06-15 10:24:35",
        "note": "处理说明"
      }
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 5.6 更新告警状态

**接口地址（两种，等价）:**
- `PATCH /api/alerts/{alertId}/status`
- `PUT /api/alerts/{alertId}/status`  // 兼容文档

**请求体：**

```json
{
  "status": "pending/processing/resolved/ignored"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null,
  "timestamp": 1697123456789
}
```

---

### 5.7 批量操作告警

**接口地址:** `POST /api/alerts/batch-operation`

**请求体：**
```json
{
  "alertIds": ["string"],   // 必填
  "action": "resolve/ignore/process/delete"  // 必填
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "批量操作成功",
  "data": {
    "successCount": 5,
    "failCount": 0
  },
  "timestamp": 1697123456789
}
```

---

### 5.8 添加告警处理记录

**接口地址:** `POST /api/alerts/{alertId}/processing-record`

**请求体：**
```json
{
  "note": "string",          // 必填
  "action": "string 可选"     // freeze/send_verification/mark_resolved/ignore/contact_user
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "处理记录添加成功",
  "data": null,
  "timestamp": 1697123456789
}
```

---

## 6. 数据采集接口

注意：此部分实现的路由前缀为 `/data-collection`（无 `/api`），前端通常通过网关映射到 `/api/data-collection`。

### 6.1 获取数据源列表

**接口地址:** `GET /data-collection/data-sources`

**请求参数：**
- `page`: int，默认 1
- `pageSize`: int，默认 10
- `status`: string，`all/normal/warning/error/stopped`
- `keyword`: string，按数据源名称模糊搜索

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "交易数据中心",
        "type": "database",
        "connection": "db-trade-01.internal",
        "status": "normal",           
        "statusName": "正常",          
        "collectionStatus": "running",
        "collectionStatusName": "采集进行中",
        "lastSyncTime": "2023-06-15 14:32:18",
        "progress": 78,
        "todayCollected": 148562,
        "estimatedCompletion": "14:45",
        "qualityIssuesCount": 12,
        "errorMessage": null
      }
    ],
    "total": 12,
    "page": 1,
    "pageSize": 10
  },
  "timestamp": 1697123456789
}
```

---

### 6.2 获取数据源统计

**接口地址:** `GET /data-collection/statistics`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 12,
    "normal": 9,
    "abnormal": 2,
    "qualityIssues": 56
  },
  "timestamp": 1697123456789
}
```

---

### 6.3 获取数据源状态分布

**接口地址:** `GET /data-collection/status-distribution`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "normal": 9,
    "warning": 1,
    "error": 1,
    "stopped": 1
  },
  "timestamp": 1697123456789
}
```

---

### 6.4 获取数据采集趋势

**接口地址:** `GET /data-collection/collection-trend`

**请求参数：**
- `period`: string，默认 `today`，当前实现仅作占位

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "labels": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"],
    "datasets": [
      {"label": "交易数据", "data": [15000, 32000, 45000, 68000, 89000, 105000, 148000, 148562]},
      {"label": "用户行为", "data": [25000, 68000, 125000, 189000, 235000, 278000, 310000, 326891]},
      {"label": "设备数据", "data": [5000, 12000, 22000, 35000, 45000, 52000, 61000, 67321]}
    ]
  },
  "timestamp": 1697123456789
}
```

（实际实现中，这些数据是按数据库中交易、登录日志、设备的真实记录统计）

---

### 6.5 获取数据质量问题

**接口地址:** `GET /data-collection/data-sources/{sourceId}/quality-issues`

**请求参数：**
- `page`: int，默认 1
- `pageSize`: int，默认 10
- `type`: string，`all/missing/format/abnormal/inconsistent`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "ISSUE-87654",
        "type": "missing",
        "typeName": "缺失值",
        "field": null,
        "description": "交易记录中缺少交易地点信息",
        "time": "2023-06-15 14:28:15"
      }
    ],
    "statistics": {
      "missing": 8,
      "formatError": 3,
      "abnormal": 1
    },
    "total": 12,
    "page": 1,
    "pageSize": 10
  },
  "timestamp": 1697123456789
}
```

---

### 6.6 获取数据预览

**接口地址:** `GET /data-collection/data-sources/{sourceId}/preview`

**请求参数：**
- `type`: string = `trade/user/image/device`，默认 `trade`
- `limit`: int = 10

**当前实现说明：**
- 目前数据库中未真实存储原始业务明细，此接口返回预置的示例数据结构，用于前端联调。

**示例（type=trade）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "transactionId": "TX2023061500123",
        "userId": "USER789456",
        "amount": 2560.0,
        "time": "14:32:15",
        "status": "success"
      }
    ],
    "total": 148562
  },
  "timestamp": 1697123456789
}
```

---

### 6.7 获取数据质量评分

**接口地址:** `GET /data-collection/data-sources/{sourceId}/quality-score`

**说明：**
- 根据该数据源下质量问题的数量及严重程度，简单从 100 扣分得出 `score`，并同步赋值到各维度。

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "score": 82,
    "maxScore": 100,
    "dimensions": {
      "completeness": 82,
      "accuracy": 82,
      "consistency": 82,
      "timeliness": 82
    }
  },
  "timestamp": 1697123456789
}
```

---

### 6.8 重新连接数据源

**接口地址:** `POST /data-collection/data-sources/{sourceId}/reconnect`

**说明：**
- 将数据源状态重置为“正常”，清空最近错误信息并更新时间。

**响应示例：**
```json
{
  "code": 200,
  "message": "重新连接成功",
  "data": null,
  "timestamp": 1697123456789
}
```

---

### 6.9 导出数据质量问题列表

**接口地址:** `GET /data-collection/data-sources/{sourceId}/quality-issues/export`

**请求参数：**
- `type`: string = `all/missing/format/abnormal/inconsistent`
- `format`: string，目前仅支持 `csv`，其他值会返回错误

**响应：**
- 成功时返回 `text/csv` 文件流，带 Content-Disposition 头；
- 若 `format` 非 `csv`，返回：`code=400`, `message="only csv export is supported currently"`。

---

## 7. 事件分析接口

路由前缀：`/event-analysis`

> 本模块基于 `RiskEvent` 及一系列关联表，整体结构与原始示例文档 7.x 基本一致，但部分字段值由数据库实际内容推导。

### 7.1 获取事件详情

**接口地址:** `GET /event-analysis/events/{eventId}`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "EVT-20230615-001",
    "title": "疑似账户盗用事件分析",
    "type": "account_theft",
    "typeName": "账户盗用",
    "level": "high",
    "levelName": "高风险",
    "status": "pending",
    "statusName": "待处理",
    "detectTime": "2023-06-15 10:24:35",
    "riskScore": 92,
    "relatedAccounts": 3,
    "relatedDevices": 2,
    "impactScope": "medium",
    "impactScopeName": "个人/多用户",
    "priority": "high",
    "priorityName": "高",
    "duration": "2h 15m"
  },
  "timestamp": 1697123456789
}
```

---

### 7.2 获取事件时间线

**接口地址:** `GET /event-analysis/events/{eventId}/timeline`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "timeline": [
      {
        "id": 1,
        "type": "normal/warning/danger/info",
        "typeName": "步骤标题",
        "time": "2023-06-14 20:15:32",
        "description": "步骤描述",
        "icon": "user/exclamation-triangle"
      }
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 7.3 获取事件溯源路径

**接口地址:** `GET /event-analysis/events/{eventId}/trace-path`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [
      {
        "id": 1,
        "label": "账户盗用",
        "group": 1,
        "type": "event",
        "time": "2023-06-14 20:15:32",
        "location": null,
        "device": null
      }
    ],
    "edges": [
      {"from": 2, "to": 1, "type": "related"}
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 7.4 获取关联账户信息

**接口地址:** `GET /event-analysis/events/{eventId}/related-accounts`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "USER-789456",
        "name": "王小明",
        "username": "wangxiaoming",
        "role": "victim/suspicious",
        "roleName": "受害者/可疑关联等",
        "registerTime": "2022-03-15",
        "level": "VIP会员",
        "phone": "138****5678",
        "email": "wang***@example.com",
        "riskScore": 85,
        "status": "normal"
      }
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 7.5 获取关联设备和 IP 信息

**接口地址:** `GET /event-analysis/events/{eventId}/devices-ips`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "commonDevices": [ ... ],
    "abnormalDevices": [ ... ],
    "ipAnalysis": [
      {
        "ip": "185.173.89.xxx",
        "riskLevel": "high/medium/low",
        "riskScore": 92,
        "location": null,
        "historyCount": 1,
        "historyType": "相关登录",
        "description": "风险等级: high"
      }
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 7.6 获取关联交易记录

**接口地址:** `GET /event-analysis/events/{eventId}/transactions`

**请求参数：**
- `page`: int，默认 1
- `pageSize`: int，默认 10

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "TX2023061501234",
        "type": "in/out/consume/refund",
        "typeName": "资金转出/资金转入/退款等",
        "amount": 50000.0,
        "currency": "CNY",
        "fromAccount": "USER-789456",
        "fromAccountName": "王小明",
        "toAccount": "USER-123456",
        "toAccountName": "李**",
        "status": "success/processing/failed/cancelled",
        "statusName": "成功/处理中/失败/已取消",
        "time": "2023-06-15 10:30:22",
        "isAbnormal": true,
        "abnormalReason": "大额交易"
      }
    ],
    "total": 15,
    "page": 1,
    "pageSize": 10
  },
  "timestamp": 1697123456789
}
```

---

### 7.7 获取责任追溯信息

**接口地址:** `GET /event-analysis/events/{eventId}/responsibility`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [ ... ],
    "edges": [ ... ],
    "analysis": [
      {
        "type": "attacker/user/system",
        "typeName": "主要责任主体/用户责任/系统防护",
        "description": "描述文本"
      }
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 7.8 获取风险分析和处理建议

**接口地址:** `GET /event-analysis/events/{eventId}/risk-analysis`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "riskAssessment": "事件风险评估文本",
    "riskScores": {
      "accountSecurity": 95,
      "accountSecurityLevel": "极高",
      "fundLoss": 85,
      "fundLossLevel": "高",
      "infoLeak": 65,
      "infoLeakLevel": "中"
    },
    "suggestions": [
      {
        "order": 1,
        "title": "立即冻结账户",
        "description": "立即冻结账户，防止进一步损失。"
      }
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 7.9 获取处理记录

**接口地址:** `GET /event-analysis/events/{eventId}/processing-records`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "type": "system/manual",
        "typeName": "系统自动处理/人工处理",
        "handler": "张经理",
        "handlerName": "张经理",
        "handlerAvatar": null,
        "time": "2023-06-15 10:35:42",
        "note": "已冻结用户账户和可疑收款账户"
      }
    ]
  },
  "timestamp": 1697123456789
}
```

---

### 7.10 添加处理记录

**接口地址:** `POST /event-analysis/events/{eventId}/processing-records`

**请求体：**
```json
{
  "note": "string",          // 必填
  "action": "string 可选",   // 动作名称
  "operator": "string 可选"  // 操作人，默认 "系统"
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "处理记录添加成功",
  "data": {
    "id": 3,
    "type": "manual",
    "handler": "张经理",
    "handlerName": "张经理",
    "handlerAvatar": null,
    "time": "2023-06-15 11:00:00",
    "note": "已联系用户，确认为本人操作，已解冻账户"
  },
  "timestamp": 1697123456789
}
```

---

### 7.11 更新事件状态

**接口地址:** `PUT /event-analysis/events/{eventId}/status`

**请求体：**
```json
{
  "status": "pending/processing/resolved/ignored"
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null,
  "timestamp": 1697123456789
}
```

---

### 7.12 编辑事件信息

**接口地址:** `PUT /event-analysis/events/{eventId}`

**请求体：**
```json
{
  "level": "high/medium/low 可选",
  "note": "string 可选",          // 优先用于更新描述
  "description": "string 可选"   // 当 note 未提供时，作为描述
}
```

**响应：**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null,
  "timestamp": 1697123456789
}
```

---

### 7.13 导出事件分析报告

**接口地址:** `GET /event-analysis/events/{eventId}/export`

**响应：**
- 返回 `text/plain` 的简单文本报告，带下载文件名 `event_{eventId}_report.txt`。

---

## 8. 通用接口

路由前缀：`/api/common`

### 8.1 文件上传

**接口地址:** `POST /common/upload`

**请求头：**
```
Authorization: Bearer {token} （目前未强制校验）
Content-Type: multipart/form-data
```

**表单字段：**
- `file`: File，必填
- `type`: string，可选，`image/document/other`，默认 `image`

**说明：**
- 允许的图片扩展名：`png, jpg, jpeg, gif, webp`
- 允许的文档扩展名：`pdf, doc, docx, xls, xlsx, ppt, pptx, txt, csv`
- 文件将保存到后端配置的 `UPLOAD_FOLDER` 目录，默认为应用根目录下 `uploads`。

**响应示例：**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "http://localhost:5000/api/common/files/xxx.jpg",
    "filename": "xxx.jpg",            // 实际为 UUID+扩展名
    "originalName": "原始文件名.jpg",
    "size": 102400
  },
  "timestamp": 1697123456789
}
```

---

### 8.1.1 访问已上传文件

**接口地址:** `GET /common/files/{filename}`

**说明：**
- 直接返回文件内容。
- 与上传响应中的 `url` 字段保持一致。

---

### 8.2 获取系统配置

**接口地址:** `GET /common/config`

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "systemName": "风控管理系统",
    "version": "1.0.0",
    "maxUploadSize": 10485760,
    "supportedImageFormats": ["png", "jpg", "jpeg", "gif", "webp"],
    "supportedDocFormats": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"],
    "refreshIntervals": [5, 10, 30, 60]
  },
  "timestamp": 1697123456789
}
```

---

## 9. 交易与风控联动接口（扩展）

路由前缀：`/api/transactions`

### 9.1 上报交易并触发风控

**接口地址:** `POST /transactions`

**请求体：**
```json
{
  "tx_id": "string 可选",   // 不传则后端生成
  "user_id": "string",      // 必填
  "device_id": "string 可选",
  "amount": 1200.5,          // 必填
  "currency": "CNY",        // 可选，默认 CNY
  "category": "转账/消费等",
  "ip_address": "1.2.3.4",
  "status": "成功/失败/处理中等"
}
```

**说明：**
- 若 `user_id` 不存在，则返回 `code=400`, `message="user not found"`。
- 若 `device_id` 存在但设备不存在，会自动创建该设备并关联用户。
- 系统会基于金额、短时间内交易次数、设备是否异常等规则打分，并自动生成 `RiskEvent` 和 `Alert`。

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "tx_id": "自动或传入的交易 ID",
    "event_id": "关联风险事件 ID",
    "risk_score": 80,
    "risk_level": "高/中/低",
    "reasons": ["大额交易", "短时间内多笔交易"]
  },
  "timestamp": 1697123456789
}
```

---

## 10. 其他接口

### 10.1 用户列表与登录日志（内部管理用）

路由前缀：`/api/users`

- `GET /users/`：分页返回用户列表（返回字段为 `items + page + size + total`，与统一 `data` 包装略有不同）。
- `GET /users/{userId}/login_logs`：返回最近 50 条登录日志。

### 10.2 模型评分占位接口

路由前缀：`/api/model`

- `POST /model/risk_score`
  - 当前为占位实现，返回固定：
  ```json
  {
    "score": 65,
    "risk_level": "中",
    "explanations": ["占位：基于规则+模型的综合评分接口，当前未接入大模型"]
  }
  ```

---

