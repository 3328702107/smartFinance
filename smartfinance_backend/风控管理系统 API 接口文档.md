# 风控管理系统 API 接口文档

## 1. 基础信息

### 1.1 基础URL
```
开发环境: http://localhost:8080/api
生产环境: https://api.example.com/api
```

### 1.2 通用请求头
```
Content-Type: application/json
Authorization: Bearer {token}
```

### 1.3 通用响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": 1697123456789
}
```

### 1.4 状态码说明
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权，需要登录
- `403`: 无权限访问
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 2. 认证相关接口

### 2.1 用户登录
**接口地址:** `POST /auth/login`

**请求参数:**
```json
{
  "username": "string",      // 用户名或邮箱
  "password": "string",       // 密码
  "remember": false           // 是否记住我
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "refresh_token_string",
    "userInfo": {
      "id": 1,
      "username": "zhang_manager",
      "name": "张经理",
      "email": "zhang@example.com",
      "phone": "138****8888",
      "avatar": "https://example.com/avatar.jpg",
      "role": "manager",
      "department": "风险管理部",
      "employeeId": "EMP-2023001"
    },
    "expiresIn": 7200
  }
}
```

### 2.2 用户登出
**接口地址:** `POST /auth/logout`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "登出成功"
}
```

### 2.3 刷新Token
**接口地址:** `POST /auth/refresh`

**请求参数:**
```json
{
  "refreshToken": "string"
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "new_token_string",
    "expiresIn": 7200
  }
}
```

### 2.4 发送验证码（忘记密码）
**接口地址:** `POST /auth/send-verification-code`

**请求参数:**
```json
{
  "contact": "string"  // 邮箱或手机号
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "expiresIn": 600  // 有效期（秒）
  }
}
```

### 2.5 验证验证码并重置密码
**接口地址:** `POST /auth/reset-password`

**请求参数:**
```json
{
  "contact": "string",           // 邮箱或手机号
  "verificationCode": "string",   // 验证码
  "newPassword": "string"         // 新密码
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "密码重置成功"
}
```

### 2.6 修改密码
**接口地址:** `POST /auth/change-password`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "oldPassword": "string",    // 原密码
  "newPassword": "string"     // 新密码
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "密码修改成功"
}
```

---

## 3. 用户信息接口

### 3.1 获取当前用户信息
**接口地址:** `GET /user/profile`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhang_manager",
    "name": "张经理",
    "email": "zhang@example.com",
    "phone": "138****8888",
    "avatar": "https://example.com/avatar.jpg",
    "gender": "男",
    "birthday": "1990-05-15",
    "bio": "负责公司风险控制与管理工作",
    "role": "manager",
    "department": "风险管理部",
    "employeeId": "EMP-2023001",
    "joinDate": "2023-01-15"
  }
}
```

### 3.2 更新用户信息
**接口地址:** `PUT /user/profile`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "gender": "string",      // 男/女
  "birthday": "string",     // YYYY-MM-DD
  "bio": "string"
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "name": "张经理",
    "email": "zhang@example.com",
    // ... 其他字段
  }
}
```

### 3.3 上传头像
**接口地址:** `POST /user/avatar`

**请求头:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求参数:**
```
file: File  // 图片文件
```

**响应示例:**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "avatar": "https://example.com/avatar/new.jpg"
  }
}
```

---

## 4. 实时监控接口

### 4.1 获取风险事件列表
**接口地址:** `GET /monitor/risk-events`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
page: int = 1              // 页码
pageSize: int = 10         // 每页数量
type: string = "all"      // 事件类型: all/fraud/fake/abnormal/other
status: string = "all"    // 状态: all/pending/resolved
keyword: string           // 搜索关键词
startTime: string         // 开始时间 YYYY-MM-DD HH:mm:ss
endTime: string           // 结束时间 YYYY-MM-DD HH:mm:ss
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "RISK-20230615-001",
        "type": "account_theft",
        "typeName": "疑似账户盗用",
        "level": "high",
        "levelName": "高风险",
        "status": "pending",
        "statusName": "待处理",
        "riskScore": 92,
        "detectTime": "2023-06-15 10:24:35",
        "description": "检测到异地异常登录行为，IP地址与常用地址不符",
        "userId": "USER-789456",
        "username": "wangxiaoming",
        "userName": "王小明"
      }
    ],
    "total": 24,
    "page": 1,
    "pageSize": 10
  }
}
```

### 4.2 获取风险趋势数据
**接口地址:** `GET /monitor/risk-trend`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
period: string = "today"  // today/week/month
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "labels": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
    "datasets": [
      {
        "label": "高风险",
        "data": [2, 1, 0, 3, 5, 4, 3, 4]
      },
      {
        "label": "中风险",
        "data": [3, 2, 4, 5, 6, 5, 7, 6]
      },
      {
        "label": "低风险",
        "data": [5, 7, 6, 8, 10, 9, 8, 10]
      }
    ]
  }
}
```

### 4.3 获取系统状态
**接口地址:** `GET /monitor/system-status`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "modelStatus": "normal",
    "modelStatusName": "正常",
    "dataStatus": "normal",
    "dataStatusName": "正常"
  }
}
```

### 4.4 获取风险事件详情
**接口地址:** `GET /monitor/risk-events/{eventId}`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "RISK-20230615-001",
    "type": "account_theft",
    "typeName": "疑似账户盗用",
    "level": "high",
    "levelName": "高风险",
    "status": "pending",
    "statusName": "待处理",
    "riskScore": 92,
    "detectTime": "2023-06-15 10:24:35",
    "description": "检测到异地异常登录行为，IP地址与常用地址不符",
    "eventDetails": {
      "loginIp": "185.173.89.xxx",
      "loginLocation": "俄罗斯 莫斯科",
      "commonLocation": "中国 上海",
      "device": "Windows 10 / Chrome 112.0.5615.138",
      "commonDevice": "iPhone 13 / Safari"
    },
    "userInfo": {
      "userId": "USER-789456",
      "username": "wangxiaoming",
      "name": "王小明",
      "registerTime": "2022-03-15",
      "level": "VIP会员",
      "lastLogin": "2023-06-14 20:15:32 (上海)"
    },
    "riskAssessment": "该用户账户在异地IP地址登录，与常用登录地差异较大，且登录设备为新设备。历史上该用户无类似异常行为记录，存在账户盗用风险。"
  }
}
```

### 4.5 处理风险事件
**接口地址:** `POST /monitor/risk-events/{eventId}/handle`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "action": "string",      // freeze/send_verification/mark_resolved/ignore
  "note": "string"         // 处理备注（可选）
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "处理成功"
}
```

---

## 5. 风险告警接口

### 5.1 获取告警列表
**接口地址:** `GET /alerts`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
page: int = 1
pageSize: int = 10
eventType: string = "all"      // all/account/transaction/identity/device/behavior
level: string = "all"          // all/high/medium/low
status: string = "all"         // all/pending/processing/resolved/ignored
timeRange: string = "today"    // today/yesterday/7days/30days/custom
startTime: string              // 自定义开始时间
endTime: string                // 自定义结束时间
keyword: string                // 搜索关键词
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "ALERT-20230615-001",
        "eventType": "account",
        "eventTypeName": "账户盗用风险",
        "level": "high",
        "levelName": "高",
        "status": "pending",
        "statusName": "待处理",
        "triggerTime": "2023-06-15 10:24:35",
        "handler": null,
        "handlerName": null
      }
    ],
    "total": 147,
    "page": 1,
    "pageSize": 10
  }
}
```

### 5.2 获取告警统计
**接口地址:** `GET /alerts/statistics`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
timeRange: string = "today"
```

**响应示例:**
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
  }
}
```

### 5.3 获取告警级别分布
**接口地址:** `GET /alerts/level-distribution`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
timeRange: string = "today"
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "high": 13,
    "medium": 56,
    "low": 78
  }
}
```

### 5.4 获取告警类型趋势
**接口地址:** `GET /alerts/type-trend`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
days: int = 6  // 最近N天
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "labels": ["6/10", "6/11", "6/12", "6/13", "6/14", "6/15"],
    "datasets": [
      {
        "label": "账户风险",
        "data": [8, 12, 9, 15, 11, 7]
      },
      {
        "label": "交易风险",
        "data": [15, 18, 12, 20, 17, 9]
      },
      {
        "label": "身份验证",
        "data": [5, 7, 9, 6, 8, 4]
      },
      {
        "label": "设备异常",
        "data": [3, 5, 4, 6, 5, 3]
      },
      {
        "label": "行为异常",
        "data": [7, 6, 9, 8, 10, 5]
      }
    ]
  }
}
```

### 5.5 获取告警详情
**接口地址:** `GET /alerts/{alertId}`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "ALERT-20230615-001",
    "eventType": "account",
    "eventTypeName": "账户盗用风险",
    "level": "high",
    "levelName": "高",
    "status": "pending",
    "statusName": "待处理",
    "triggerTime": "2023-06-15 10:24:35",
    "rule": "异地异常登录检测规则 v2.3",
    "riskScore": 92,
    "basicInfo": {
      "alertId": "ALERT-20230615-001",
      "eventType": "账户盗用风险",
      "level": "高",
      "triggerTime": "2023-06-15 10:24:35",
      "status": "待处理",
      "rule": "异地异常登录检测规则 v2.3",
      "riskScore": 92
    },
    "userInfo": {
      "userId": "USER-789456",
      "username": "wangxiaoming",
      "name": "王小明",
      "registerTime": "2022-03-15",
      "level": "VIP会员",
      "phone": "138****5678",
      "lastLogin": "2023-06-14 20:15:32 (上海)"
    },
    "eventDetails": {
      "description": "该用户账户在异地IP地址登录，与常用登录地差异较大，且登录设备为新设备。登录IP地址为185.173.89.xxx，地理位置显示为俄罗斯莫斯科，而用户常用登录地为中国上海。",
      "abnormalLogin": {
        "ip": "185.173.89.xxx",
        "location": "俄罗斯 莫斯科",
        "device": "Windows 10 / Chrome 112.0.5615.138",
        "loginMethod": "密码登录"
      },
      "normalPattern": {
        "commonIp": "101.89.*.* / 116.23.*.*",
        "commonLocation": "中国 上海",
        "commonDevice": "iPhone 13 / Safari",
        "commonTime": "19:00 - 22:00"
      }
    },
    "riskAssessment": "该用户账户在异地IP地址登录，与常用登录地差异较大，且登录设备为新设备。历史上该用户无类似异常行为记录，存在账户盗用风险，建议立即采取验证措施。",
    "suggestions": [
      "向用户注册手机发送验证码，要求二次验证",
      "暂时冻结账户敏感操作权限",
      "联系用户确认是否为本人操作",
      "如确认非本人操作，立即锁定账户并引导用户修改密码"
    ],
    "processingRecords": [
      {
        "type": "system",
        "typeName": "系统创建",
        "handler": "系统",
        "handlerName": "系统自动生成告警",
        "time": "2023-06-15 10:24:35",
        "note": "系统检测到异常登录行为，自动创建高风险告警"
      }
    ]
  }
}
```

### 5.6 更新告警状态
**接口地址:** `PUT /alerts/{alertId}/status`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "status": "string"  // pending/processing/resolved/ignored
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "状态更新成功"
}
```

### 5.7 批量操作告警
**接口地址:** `POST /alerts/batch-operation`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "alertIds": ["string"],  // 告警ID数组
  "action": "string"        // resolve/ignore/process/delete
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "批量操作成功",
  "data": {
    "successCount": 5,
    "failCount": 0
  }
}
```

### 5.8 添加告警处理记录
**接口地址:** `POST /alerts/{alertId}/processing-record`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "note": "string",         // 处理记录
  "action": "string"        // 处理动作（可选）
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "处理记录添加成功"
}
```

---

## 6. 数据采集接口

### 6.1 获取数据源列表
**接口地址:** `GET /data-collection/data-sources`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
page: int = 1
pageSize: int = 10
status: string = "all"      // all/normal/warning/error/stopped
keyword: string              // 搜索关键词
```

**响应示例:**
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
  }
}
```

### 6.2 获取数据源统计
**接口地址:** `GET /data-collection/statistics`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 12,
    "normal": 9,
    "abnormal": 2,
    "qualityIssues": 56
  }
}
```

### 6.3 获取数据源状态分布
**接口地址:** `GET /data-collection/status-distribution`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "normal": 9,
    "warning": 1,
    "error": 1,
    "stopped": 1
  }
}
```

### 6.4 获取数据采集趋势
**接口地址:** `GET /data-collection/collection-trend`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
period: string = "today"  // today/week/month
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "labels": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"],
    "datasets": [
      {
        "label": "交易数据",
        "data": [15000, 32000, 45000, 68000, 89000, 105000, 148000, 148562]
      },
      {
        "label": "用户行为",
        "data": [25000, 68000, 125000, 189000, 235000, 278000, 310000, 326891]
      },
      {
        "label": "设备数据",
        "data": [5000, 12000, 22000, 35000, 45000, 52000, 61000, 67321]
      }
    ]
  }
}
```

### 6.5 获取数据质量问题
**接口地址:** `GET /data-collection/data-sources/{sourceId}/quality-issues`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
page: int = 1
pageSize: int = 10
type: string = "all"  // all/missing/format/abnormal/inconsistent
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "REC-87654",
        "type": "missing",
        "typeName": "缺失值",
        "field": "交易地点",
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
  }
}
```

### 6.6 获取数据预览
**接口地址:** `GET /data-collection/data-sources/{sourceId}/preview`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
type: string = "trade"  // trade/user/image/device
limit: int = 10
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "transactionId": "TX2023061500123",
        "userId": "USER789456",
        "amount": 2560.00,
        "time": "14:32:15",
        "status": "success"
      }
    ],
    "total": 148562
  }
}
```

### 6.7 获取数据质量评分
**接口地址:** `GET /data-collection/data-sources/{sourceId}/quality-score`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "score": 82,
    "maxScore": 100,
    "dimensions": {
      "completeness": 85,
      "accuracy": 90,
      "consistency": 75,
      "timeliness": 80
    }
  }
}
```

### 6.8 重新连接数据源
**接口地址:** `POST /data-collection/data-sources/{sourceId}/reconnect`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "重新连接成功"
}
```

### 6.9 导出数据质量问题列表
**接口地址:** `GET /data-collection/data-sources/{sourceId}/quality-issues/export`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
type: string = "all"
format: string = "csv"  // csv/excel
```

**响应:** 文件下载

---

## 7. 事件分析接口

### 7.1 获取事件详情
**接口地址:** `GET /event-analysis/events/{eventId}`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
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
    "impactScopeName": "中",
    "priority": "high",
    "priorityName": "高",
    "duration": "2h 15m"
  }
}
```

### 7.2 获取事件时间线
**接口地址:** `GET /event-analysis/events/{eventId}/timeline`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "timeline": [
      {
        "id": 1,
        "type": "normal",
        "typeName": "正常登录",
        "time": "2023-06-14 20:15:32",
        "description": "用户在常用设备（iPhone 13）上登录账户，地点：上海",
        "icon": "user"
      },
      {
        "id": 2,
        "type": "logout",
        "typeName": "用户登出",
        "time": "2023-06-14 22:30:15",
        "description": "用户主动登出账户",
        "icon": "sign-out"
      },
      {
        "id": 3,
        "type": "warning",
        "typeName": "异常登录尝试",
        "time": "2023-06-15 10:20:18",
        "description": "新设备（Windows 10）尝试登录，IP地址：185.173.89.xxx，地点：俄罗斯莫斯科",
        "icon": "user-secret"
      },
      {
        "id": 4,
        "type": "danger",
        "typeName": "风险事件触发",
        "time": "2023-06-15 10:24:35",
        "description": "系统检测到异地异常登录行为，触发高风险告警",
        "icon": "exclamation-triangle"
      }
    ]
  }
}
```

### 7.3 获取事件溯源路径
**接口地址:** `GET /event-analysis/events/{eventId}/trace-path`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [
      {
        "id": 1,
        "label": "正常登录",
        "group": 1,
        "type": "event",
        "time": "2023-06-14 20:15:32",
        "location": "上海",
        "device": "iPhone 13"
      },
      {
        "id": 8,
        "label": "王小明",
        "group": 4,
        "type": "user",
        "userId": "USER-789456"
      }
    ],
    "edges": [
      {
        "from": 8,
        "to": 1,
        "type": "login"
      }
    ]
  }
}
```

### 7.4 获取关联账户信息
**接口地址:** `GET /event-analysis/events/{eventId}/related-accounts`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
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
        "role": "victim",
        "roleName": "受害者",
        "registerTime": "2022-03-15",
        "level": "VIP会员",
        "phone": "138****5678",
        "email": "wang***@example.com",
        "riskScore": null,
        "status": "normal"
      },
      {
        "id": "USER-123456",
        "name": "李**",
        "username": "li_xxx",
        "role": "recipient",
        "roleName": "收款账户",
        "registerTime": "2023-05-20",
        "level": "普通会员",
        "phone": "139****1234",
        "email": "li***@example.com",
        "riskScore": 85,
        "status": "frozen",
        "statusName": "已冻结",
        "transactionCount": 12
      },
      {
        "id": "USER-654321",
        "name": "张**",
        "username": "zhang_xxx",
        "role": "suspicious",
        "roleName": "可疑关联",
        "registerTime": "2023-01-05",
        "level": "普通会员",
        "phone": "137****5678",
        "email": "zhang***@example.com",
        "riskScore": 62,
        "status": "normal",
        "relationship": "无明显关系"
      }
    ]
  }
}
```

### 7.5 获取关联设备和IP信息
**接口地址:** `GET /event-analysis/events/{eventId}/devices-ips`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "commonDevices": [
      {
        "id": 1,
        "name": "iPhone 13",
        "os": "iOS 16.5",
        "browser": "Safari 16.5",
        "ip": "101.89.xxx.xxx",
        "location": "中国 上海",
        "type": "mobile",
        "isCommon": true
      }
    ],
    "abnormalDevices": [
      {
        "id": 2,
        "name": "未知Windows设备",
        "os": "Windows 10",
        "browser": "Chrome 112.0.5615.138",
        "ip": "185.173.89.xxx",
        "location": "俄罗斯 莫斯科",
        "type": "desktop",
        "isCommon": false,
        "loginTime": "2023-06-15 10:20:18"
      }
    ],
    "ipAnalysis": [
      {
        "ip": "185.173.89.xxx",
        "riskLevel": "high",
        "riskScore": 92,
        "location": "俄罗斯 莫斯科",
        "historyCount": 3,
        "historyType": "可疑登录",
        "description": "历史记录: 3次可疑登录 | 归属地: 俄罗斯 莫斯科"
      },
      {
        "ip": "101.89.xxx.xxx",
        "riskLevel": "low",
        "riskScore": 15,
        "location": "中国 上海",
        "historyCount": 128,
        "historyType": "正常登录",
        "description": "历史记录: 128次正常登录 | 归属地: 中国 上海"
      }
    ]
  }
}
```

### 7.6 获取关联交易记录
**接口地址:** `GET /event-analysis/events/{eventId}/transactions`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
page: int = 1
pageSize: int = 10
type: string = "all"  // all/in/out/abnormal
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "TX2023061501234",
        "type": "out",
        "typeName": "资金转出",
        "amount": 50000.00,
        "currency": "CNY",
        "fromAccount": "USER-789456",
        "fromAccountName": "王小明",
        "toAccount": "USER-123456",
        "toAccountName": "李**",
        "status": "processing",
        "statusName": "处理中",
        "time": "2023-06-15 10:30:22",
        "isAbnormal": true,
        "abnormalReason": "可疑交易 - 已拦截"
      },
      {
        "id": "TX2023061008765",
        "type": "in",
        "typeName": "资金转入",
        "amount": 18500.00,
        "currency": "CNY",
        "fromAccount": "公司工资账户",
        "toAccount": "USER-789456",
        "toAccountName": "王小明",
        "status": "success",
        "statusName": "成功",
        "time": "2023-06-10 09:30:00",
        "isAbnormal": false
      }
    ],
    "total": 15,
    "page": 1,
    "pageSize": 10
  }
}
```

### 7.7 获取责任追溯信息
**接口地址:** `GET /event-analysis/events/{eventId}/responsibility`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [
      {
        "id": 1,
        "label": "黑客攻击",
        "type": "attacker",
        "level": "high"
      },
      {
        "id": 2,
        "label": "用户操作",
        "type": "user",
        "level": "medium"
      },
      {
        "id": 3,
        "label": "系统防护",
        "type": "system",
        "level": "low"
      }
    ],
    "edges": [
      {
        "from": 1,
        "to": 4,
        "value": 5,
        "label": "导致"
      }
    ],
    "analysis": [
      {
        "type": "attacker",
        "typeName": "主要责任主体",
        "description": "疑似黑客攻击，通过非法手段获取用户信息并进行登录操作"
      },
      {
        "type": "user",
        "typeName": "用户责任",
        "description": "可能在其他平台使用相同密码，导致信息泄露；未开启二次验证"
      },
      {
        "type": "system",
        "typeName": "系统防护",
        "description": "异地登录检测及时，但密码重置流程可进一步加强安全验证"
      }
    ]
  }
}
```

### 7.8 获取风险分析和处理建议
**接口地址:** `GET /event-analysis/events/{eventId}/risk-analysis`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "riskAssessment": "该事件属于典型的账户盗用案例，攻击者通过未知手段获取了用户的基本信息，并成功重置密码登录账户。从攻击路径来看，攻击者可能利用了用户在其他平台的信息泄露，使用相同的用户名和密码尝试登录。事件风险等级高，已造成潜在的资金损失风险。",
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
        "description": "暂时冻结账户所有操作权限，防止进一步损失"
      },
      {
        "order": 2,
        "title": "联系用户核实",
        "description": "通过注册手机和邮箱联系用户，确认是否为本人操作"
      },
      {
        "order": 3,
        "title": "强制密码重置",
        "description": "引导用户进行安全的密码重置，并建议开启二次验证"
      },
      {
        "order": 4,
        "title": "调查收款账户",
        "description": "对李**账户进行风险评估，必要时冻结并上报可疑交易"
      },
      {
        "order": 5,
        "title": "加强异常检测",
        "description": "针对此类攻击模式优化风控模型，加强密码重置环节的安全验证"
      }
    ]
  }
}
```

### 7.9 获取处理记录
**接口地址:** `GET /event-analysis/events/{eventId}/processing-records`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "type": "system",
        "typeName": "系统自动处理",
        "handler": "系统",
        "handlerName": "系统自动处理",
        "handlerAvatar": null,
        "time": "2023-06-15 10:25:10",
        "note": "检测到高风险事件，已自动拦截资金转移操作"
      },
      {
        "id": 2,
        "type": "manual",
        "typeName": "人工处理",
        "handler": "张经理",
        "handlerName": "张经理",
        "handlerAvatar": "https://example.com/avatar.jpg",
        "time": "2023-06-15 10:35:42",
        "note": "已冻结用户账户和可疑收款账户，正在联系用户核实情况"
      }
    ]
  }
}
```

### 7.10 添加处理记录
**接口地址:** `POST /event-analysis/events/{eventId}/processing-records`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "note": "string"  // 处理记录内容
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "处理记录添加成功",
  "data": {
    "id": 3,
    "type": "manual",
    "handler": "张经理",
    "time": "2023-06-15 11:00:00",
    "note": "已联系用户，确认为本人操作，已解冻账户"
  }
}
```

### 7.11 更新事件状态
**接口地址:** `PUT /event-analysis/events/{eventId}/status`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "status": "string"  // pending/processing/resolved
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "状态更新成功"
}
```

### 7.12 编辑事件信息
**接口地址:** `PUT /event-analysis/events/{eventId}`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```json
{
  "title": "string",
  "level": "string",
  "priority": "string",
  "note": "string"
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "更新成功"
}
```

### 7.13 导出事件分析报告
**接口地址:** `GET /event-analysis/events/{eventId}/export`

**请求头:**
```
Authorization: Bearer {token}
```

**请求参数:**
```
format: string = "pdf"  // pdf/excel/word
```

**响应:** 文件下载

---

## 8. 通用接口

### 8.1 文件上传
**接口地址:** `POST /common/upload`

**请求头:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求参数:**
```
file: File
type: string = "image"  // image/document/other
```

**响应示例:**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "https://example.com/files/xxx.jpg",
    "filename": "xxx.jpg",
    "size": 102400
  }
}
```

### 8.2 获取系统配置
**接口地址:** `GET /common/config`

**请求头:**
```
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "systemName": "风控管理系统",
    "version": "1.0.0",
    "maxUploadSize": 10485760,
    "supportedImageFormats": ["jpg", "png", "gif"],
    "refreshIntervals": [5, 10, 30, 60]
  }
}
```

---

## 9. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权，需要登录 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如用户名已存在） |
| 422 | 请求参数验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## 10. 数据字典

### 10.1 风险级别
- `high`: 高风险
- `medium`: 中风险
- `low`: 低风险

### 10.2 事件状态
- `pending`: 待处理
- `processing`: 处理中
- `resolved`: 已解决
- `ignored`: 已忽略

### 10.3 事件类型
- `account_theft`: 账户盗用
- `transaction_abnormal`: 异常交易
- `identity_fake`: 伪造身份
- `device_abnormal`: 设备异常
- `behavior_abnormal`: 行为异常
- `batch_registration`: 批量注册

### 10.4 告警类型
- `account`: 账户风险
- `transaction`: 交易风险
- `identity`: 身份验证
- `device`: 设备异常
- `behavior`: 行为异常

### 10.5 数据源状态
- `normal`: 正常
- `warning`: 警告
- `error`: 异常
- `stopped`: 已停止

### 10.6 数据源类型
- `database`: 数据库
- `api`: API接口
- `file`: 文件
- `stream`: 数据流

### 10.7 数据质量问题类型
- `missing`: 缺失值
- `format`: 格式错误
- `abnormal`: 值异常
- `inconsistent`: 数据不一致

### 10.8 账户角色
- `victim`: 受害者
- `recipient`: 收款账户
- `suspicious`: 可疑关联
- `normal`: 正常关联

### 10.9 交易类型
- `in`: 资金转入
- `out`: 资金转出
- `consume`: 消费
- `refund`: 退款

### 10.10 交易状态
- `success`: 成功
- `processing`: 处理中
- `failed`: 失败
- `cancelled`: 已取消

---

## 11. 接口调用示例

### 11.1 登录示例
```javascript
// 使用 axios
const response = await axios.post('/api/auth/login', {
  username: 'zhang_manager',
  password: 'password123',
  remember: true
});

// 保存 token
localStorage.setItem('token', response.data.data.token);
```

### 11.2 获取风险事件列表示例
```javascript
const response = await axios.get('/api/monitor/risk-events', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  params: {
    page: 1,
    pageSize: 10,
    type: 'all',
    status: 'pending'
  }
});
```

### 11.3 处理风险事件示例
```javascript
const response = await axios.post(
  `/api/monitor/risk-events/${eventId}/handle`,
  {
    action: 'freeze',
    note: '检测到异常登录，已冻结账户'
  },
  {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  }
);
```

### 11.4 文件上传示例
```javascript
const formData = new FormData();
formData.append('file', file);
formData.append('type', 'image');

const response = await axios.post('/api/common/upload', formData, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'multipart/form-data'
  }
});
```

---

## 12. 注意事项

### 12.1 认证
- 所有需要认证的接口都需要在请求头中携带 `Authorization: Bearer {token}`
- Token 有效期通常为 2 小时，过期后需要使用 refreshToken 刷新
- 如果 refreshToken 也过期，需要重新登录

### 12.2 分页
- 所有列表接口都支持分页，默认 `page=1`, `pageSize=10`
- 最大 `pageSize` 为 100
- 响应中包含 `total` 字段表示总记录数

### 12.3 时间格式
- 所有时间字段统一使用格式：`YYYY-MM-DD HH:mm:ss`
- 日期字段使用格式：`YYYY-MM-DD`
- 时区统一使用 UTC+8（北京时间）

### 12.4 错误处理
- 所有接口错误都会返回统一的错误格式
- 客户端需要根据 `code` 字段判断请求是否成功
- 建议统一处理 401 错误，自动跳转到登录页

### 12.5 请求频率限制
- 为防止接口被恶意调用，部分接口有请求频率限制
- 超过限制会返回 429 错误码
- 建议客户端实现请求去重和重试机制

### 12.6 数据安全
- 敏感数据（如密码）在传输过程中必须加密
- 建议使用 HTTPS 协议
- 不要在客户端存储敏感信息

---