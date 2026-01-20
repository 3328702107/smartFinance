# SmartFinance 智能风控系统

一个基于 Flask + SQLAlchemy 的金融风险控制系统，提供实时风险检测、事件分析、告警管理和数据监控等功能。

---

## 项目简介

SmartFinance 是一套完整的金融风控解决方案，通过规则引擎和数据分析，实时检测异常交易、账户盗用、设备异常等风险行为，并提供完善的事件处理流程和数据分析能力。

### 核心功能

| 模块 | 功能描述 |
|------|----------|
| **用户认证** | 注册、登录、JWT 认证、密码管理 |
| **用户管理** | 用户列表、详情、状态管理 |
| **交易监控** | 交易接入、实时风险评分、规则检测 |
| **风险事件** | 事件管理、时间线追踪、处理流程 |
| **告警系统** | 告警触发、等级分类、处理记录 |
| **监控看板** | 风险趋势、系统状态、数据统计 |
| **数据管理** | 数据源配置、质量监控、异常检测 |
| **事件分析** | 关联分析、风险画像、处理建议 |

### 技术栈

- **后端框架**: Flask 3.0
- **数据库**: MySQL 5.7+ / 8.0+
- **ORM**: SQLAlchemy
- **认证**: JWT (PyJWT)
- **密码加密**: Werkzeug Security
- **数据库驱动**: PyMySQL

---

## 快速开始

### 前置要求

- Python 3.8+
- MySQL 5.7+ / 8.0+

### 第一步：创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE smartfinance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sf_app'@'localhost' IDENTIFIED BY 'YourStrongPass!123';
GRANT ALL PRIVILEGES ON smartfinance.* TO 'sf_app'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 第二步：配置环境

```bash
cd smartfinance_backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Mac / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 第三步：配置数据库连接

编辑 `smartfinance_backend/config.py`，修改数据库连接信息：

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://用户名:密码@localhost:3306/smartfinance?charset=utf8mb4"
```

或使用环境变量：

```bash
# Windows PowerShell
$env:DATABASE_URL = "mysql+pymysql://sf_app:YourStrongPass!123@localhost:3306/smartfinance?charset=utf8mb4"

# Mac / Linux
export DATABASE_URL="mysql+pymysql://sf_app:YourStrongPass!123@localhost:3306/smartfinance?charset=utf8mb4"
```

### 第四步：初始化数据库

```bash
cd smartfinance_backend
python init_test_data.py
```

### 第五步：启动服务

```bash
python run.py
```

服务启动后访问：http://localhost:5000

---

## 测试账号

初始化后会创建以下测试账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| alice | 123456 | 普通用户 |
| bob | 123456 | VIP 用户 |

---

## API 接口

### 认证模块 `/api/auth`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/register` | POST | 用户注册 |
| `/login` | POST | 用户登录 |
| `/me` | GET | 获取当前用户信息 |
| `/logout` | POST | 用户登出 |
| `/refresh` | POST | 刷新 Token |
| `/change-password` | POST | 修改密码 |

### 用户管理 `/api/users`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 获取用户列表 |
| `/<user_id>` | GET | 获取用户详情 |
| `/<user_id>/status` | PUT | 更新用户状态 |
| `/<user_id>/devices` | GET | 获取用户设备 |

### 交易监控 `/api/transactions`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | POST | 提交交易并触发风险检测 |
| `/` | GET | 获取交易列表 |
| `/<tx_id>` | GET | 获取交易详情 |

### 风险事件 `/api/risk_events`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 获取风险事件列表 |
| `/<event_id>` | GET | 获取事件详情 |
| `/<event_id>/timeline` | GET | 获取事件时间线 |
| `/<event_id>/handle` | POST | 处理风险事件 |

### 告警管理 `/api/alerts`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 获取告警列表 |
| `/<alert_id>` | GET | 获取告警详情 |
| `/<alert_id>/handle` | POST | 处理告警 |

### 监控看板 `/api/monitor`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/risk-events` | GET | 风险事件统计 |
| `/risk-trend` | GET | 风险趋势数据 |
| `/system-status` | GET | 系统运行状态 |

---

## 项目结构

```
smartfinance/
├── smartfinance_backend/     # 后端目录
│   ├── app.py                # 应用工厂
│   ├── run.py                # 启动脚本
│   ├── config.py             # 配置文件
│   ├── init_test_data.py     # 测试数据初始化
│   ├── requirements.txt      # Python 依赖
│   ├── core/                 # 核心模块
│   │   ├── database.py       # SQLAlchemy 实例
│   │   └── exceptions.py     # 自定义异常
│   ├── models/               # 数据模型
│   │   ├── user.py           # 用户、认证账户、登录日志
│   │   ├── device.py         # 设备信息
│   │   ├── risk.py           # 风险事件、告警、时间线
│   │   ├── transaction.py    # 交易记录
│   │   ├── analysis.py       # 处理记录、关联用户、分析建议
│   │   └── data.py           # 数据源、数据质量
│   ├── routes/               # API 路由
│   ├── services/             # 业务逻辑层
│   └── utils/                # 工具函数
├── .gitignore
└── README.md
```

---

## 风险检测规则

系统内置以下风险检测规则：

| 规则 | 触发条件 | 风险分 |
|------|----------|--------|
| 大额交易 | 单笔金额 ≥ 10,000 | +50 |
| 短时间多笔交易 | 10分钟内 ≥ 5笔 | +30 |
| 异常设备 | 使用已标记异常的设备 | +20 |
| 异地登录 | 短时间内异地登录 | +40 |

风险等级划分：
- **低风险**: 0-39 分
- **中风险**: 40-79 分
- **高风险**: 80+ 分

---

## 常见问题

### 数据库连接失败

检查 MySQL 服务是否启动，确认用户名密码正确：

```bash
# Windows
net start mysql

# Mac / Linux
sudo systemctl start mysql
```

### 端口被占用

```bash
# Windows
netstat -ano | findstr :5000

# Mac / Linux
lsof -ti:5000 | xargs kill -9
```

### 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

---

## 生产环境部署

1. 修改 `SECRET_KEY` 为随机强密码
2. 使用环境变量管理敏感配置
3. 设置 `DEBUG = False`
4. 使用 Gunicorn / uWSGI 等 WSGI 服务器
5. 配置 Nginx 反向代理
6. 使用 HTTPS

---

## 许可证

MIT License
