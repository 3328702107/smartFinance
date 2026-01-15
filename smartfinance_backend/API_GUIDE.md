# SmartFinance 后端接口手册

> 说明：所有接口均为 REST，默认返回 JSON。基础 URL：`http://127.0.0.1:5000`
> 认证：目前只有 `/api/auth/me` 需要携带登录获得的 Bearer Token，其余接口未强制鉴权（可按需加权限拦截）。

## 健康检查
- **GET** `/api/health`
  - 用途：服务存活检查 + 基础运行状态概览
  - 200 响应示例：
    ```json
    {
      "status": "ok",          // ok / degraded
      "db": "ok",              // ok / error
      "model_status": "正常",   // 目前为占位
      "data_status": "正常",    // 基于 data_sources 推断
      "timestamp": "2026-01-15T10:00:00.000000"
    }
    ```

## 认证（注册/登录）
- **POST** `/api/auth/register`
  - Body(JSON)：`{"username":"test_user1","password":"Passw0rd!","phone":"13800000010","email":"t1@example.com"}`
  - 返回：`{user_id, username, token}`
- **POST** `/api/auth/login`
  - Body(JSON)：`{"username":"test_user1","password":"Passw0rd!","device_id":"d_test_001","ip_address":"1.2.3.4","client_type":"WEB","login_location":"武汉"}`
  - 返回：`{user_id, username, token}`，并写入登录日志
- **GET** `/api/auth/me`
  - Headers：`Authorization: Bearer <token>`（或 query 参数 `token`）
  - 返回：当前用户基础信息

## 风险事件
- **GET** `/api/risk_events`
  - Query：`page` `size` `status`(`待处理/处理中/已解决/已忽略`) `risk_level`(`高/中/低`)
  - 返回：分页事件列表
- **GET** `/api/risk_events/{event_id}`
  - 返回：事件详情（基础信息、用户、设备、最近交易、时间线、告警、处理记录、关联用户）
- **PATCH** `/api/risk_events/{event_id}/status`
  - Body(JSON)：`{"status":"处理中"}`（或 `已解决/已忽略/待处理`）
- **GET** `/api/risk_events/{event_id}/graph`
  - 返回：关系图数据 `{nodes:[...], edges:[...]}`，包含事件-用户-设备-关联用户
- **GET** `/api/risk_events/stats`
  - 用途：风险事件总览与趋势统计（实时监控页）
  - 返回字段：
    - `total`：事件总数
    - `by_level`：按风险级别统计（高/中/低）
    - `by_status`：按处理状态统计（待处理/处理中/已解决/已忽略）
    - `trend_24h`：最近 24 小时按小时聚合的趋势数组，每项包含 `timestamp/high/medium/low/total`

## 告警
- **GET** `/api/alerts`
  - Query：
    - `page` `size`
    - `status`：可传中文枚举（`待处理/处理中/已解决/已忽略`）或英文别名（`pending/processing/resolved/ignored`）
    - `category`：事件类别，用于按关联风险事件类型筛选（`account/transaction/identity/device/behavior`）
  - 返回：告警列表
- **PATCH** `/api/alerts/{alert_id}/status`
  - Body(JSON)：`{"status":"已解决"}`（也可用英文 `resolved/pending/processing/ignored`）
- **GET** `/api/alerts/stats`
  - 用途：风险告警总览和图表统计（告警管理页）
  - 返回字段：
    - `total`：告警总数
    - `status_counts`：按处理状态统计
    - `level_counts`：按告警级别统计（高/中/低）
    - `high_risk_count`：高风险告警数量
    - `recent_trend`：最近 7 天的趋势数据，每天包含各类别（account/transaction/identity/device/behavior/other）计数

## 交易 & 规则风控
- **POST** `/api/transactions`
  - 用途：提交一笔交易，规则引擎自动评估并生成风险事件/告警
  - Body(JSON)：
    ```json
    {
      "user_id": "u_test_001",
      "device_id": "d_test_001",
      "amount": 15000,
      "currency": "CNY",
      "category": "转账",
      "ip_address": "1.2.3.4",
      "status": "成功"
    }
    ```
  - 返回：`{tx_id, event_id, risk_score, risk_level, reasons}`

## 用户 & 登录日志
- **GET** `/api/users`
  - Query：`page` `size` `q`(按用户名模糊搜索)
  - 返回：用户列表
- **GET** `/api/users/{user_id}/login_logs`
  - 返回：该用户近期登录日志（含时间/IP/终端/位置）

## 数据源 & 数据质量
- **GET** `/api/data_sources`
  - 返回：数据源列表（状态、同步进度、错误次数等）
- **GET** `/api/data_sources/quality_issues`
  - 返回：数据质量问题列表
- **GET** `/api/data_sources/stats`
  - 用途：数据采集监控页顶部统计卡片
  - 返回字段：
    - `total_sources`：数据源总数
    - `normal_sources`：状态为“正常”的数据源数
    - `abnormal_sources`：状态非“正常”的数据源数（异常/中断等）
    - `open_quality_issues`：未解决的数据质量问题数量

## 模型占位（未接入大模型）
- **POST** `/api/model/risk_score`
  - Body(JSON)：`{"user_id":"u_test_001","tx_id":"tx_test_002"}`
  - 返回固定示例：`{"score":65,"risk_level":"中","explanations":["占位：当前未接入大模型"]}`




