# 🛡️ SmartFinance 智能风控系统

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Flask](https://img.shields.io/badge/Flask-3.0-orange)
![Vue](https://img.shields.io/badge/Vue.js-3.0-brightgreen)

SmartFinance 是一套现代化的金融风险控制系统，基于规则引擎和数据分析技术，提供实时的风险检测、事件分析、告警管理和全方位的数据监控功能。

---

## ✨ 核心功能

1.  **📊 实时监控看板**
    *   风险事件实时统计与趋势图表
    *   系统健康状态监控（数据库、模型、采集器）

2.  **🕵️ 风险检测与分析**
    *   **多维度规则引擎**：大额交易、高频操作、异地登录、设备异常等内置规则
    *   **事件图谱**：可视化展示事件、用户、设备、IP 之间的关联关系（基于 G6/ECharts）
    *   **溯源分析**：支持对风险事件进行深度溯源和归因分析

3.  **🚨 告警管理中心**
    *   告警分级（高/中/低）与状态流转（待处理/处理中/已解决）
    *   支持批量操作与人工处理记录

4.  **💾 智能数据采集**
    *   多源数据接入监控
    *   数据质量实时评估（完整性、准确性、一致性）

5.  **🔐 安全认证体系**
    *   完善的 JWT 认证与 RBAC 权限控制
    *   支持密码加密、二次验证流程

---

## 🛠️ 技术架构

### 后端 (Backend) - `smartfinance_backend/`
*   **框架**: Flask 3.0 (Python)
*   **数据库**: MySQL 8.0 (ORM: SQLAlchemy)
*   **认证**: PyJWT + Werkzeug Security
*   **工具**: Pandas (数据处理), PyTest (测试)

### 前端 (Frontend) - `front/vue_front/`
*   **框架**: Vue 3 + Vite
*   **UI 组件**: Element Plus
*   **图表**: ECharts + AntV G6 (关联图谱)
*   **样式**: SCSS / TailwindCSS

---

## 🚀 快速开始

### 1. 环境准备
*   Python 3.8+
*   Node.js 16+
*   MySQL 5.7+

### 2. 后端启动
```bash
cd smartfinance_backend

# 创建并激活虚拟环境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 修改 config.py 或设置环境变量 DATABASE_URL

# 初始化数据
python init_test_data.py

# 启动服务
python run.py
```
> 后端服务默认运行在 `http://localhost:5000`

### 3. 前端启动
```bash
cd front/vue_front

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```
> 前端服务通常运行在 `http://localhost:5173`

---

## 🔌 API 接口概览

| 模块 | 基础路径 | 主要功能 |
| :--- | :--- | :--- |
| **认证** | `/api/auth` | 登录、注册、刷新 Token、修改密码 |
| **用户** | `/api/users` | 用户管理、画像查询、头像上传 |
| **交易** | `/api/transactions` | 交易录入、通过规则引擎检测风险 |
| **监控** | `/api/monitor` | 实时风险事件、趋势图、系统状态 |
| **告警** | `/api/alerts` | 告警列表、详情、状态更新 |
| **事件** | `/api/risk_events` | 风险事件详情、关联分析图谱数据 |
| **数据** | `/api/data_sources` | 数据源监控、质量问题统计 |
| **通用** | `/api/common` | 文件上传、全局配置获取 |

---

## 🧪 风险规则配置

系统默认内置以下风险规则（可根据业务需求扩展）：

| 规则名称 | 触发条件 | 风险值 |
| :--- | :--- | :--- |
| **大额交易** | 单笔 > 10,000 | +50 |
| **高频交易** | 10分钟内 > 5笔 | +30 |
| **设备异常** | 命中已知异常设备库 | +20 |
| **异地登录** | IP 地理位置发生突变 | +40 |

> 风险判定：0-39 (低), 40-79 (中), ≥80 (高)

---

## 👥 贡献者

@3328702107

## 📄 许可证

MIT License
