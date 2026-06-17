# 基于AI问诊的医疗管理系统

## 项目简介
基于AI问诊的医疗管理系统，采用前后端分离架构，集成AI智能问诊功能，支持患者在线挂号、AI预问诊、医生诊疗管理、病历管理等功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + Ant Design 5 + Vite |
| 后端 | Python 3.9+ / FastAPI |
| 数据库 | MySQL 8.0 (严格3NF) |
| AI服务 | OpenAI GPT API / 规则引擎回退 |
| 认证 | JWT + RBAC |

## 项目结构
```
├── backend/                    # 后端 FastAPI
│   ├── app/
│   │   ├── models/            # SQLAlchemy 模型 (11个)
│   │   ├── schemas/           # Pydantic 数据验证
│   │   ├── routers/           # API 路由 (10个模块)
│   │   ├── services/          # 业务服务层
│   │   ├── utils/             # 工具类 (JWT, 密码)
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 入口
│   ├── run.py
│   └── requirements.txt
├── frontend/                   # 前端 React
│   ├── src/
│   │   ├── api/               # API 请求层
│   │   ├── components/        # 通用组件
│   │   ├── context/           # Auth 上下文
│   │   ├── pages/             # 页面
│   │   │   ├── Login/         # 登录
│   │   │   ├── Register/      # 注册
│   │   │   ├── Admin/         # 管理端
│   │   │   ├── Doctor/        # 医生端
│   │   │   ├── Patient/       # 患者端
│   │   │   └── AIDiagnosis/   # AI问诊
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── database/
    └── init.sql               # 数据库初始化 (11张表)
```

## 快速开始

### 1. 启动数据库
```bash
# 创建数据库
mysql -u root -p < database/init.sql
```

### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
python run.py
# 服务运行在 http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 3. 启动前端
```bash
cd frontend
npm install
npm run dev
# 服务运行在 http://localhost:5173
```

### 4. 访问系统
- 打开浏览器访问 http://localhost:5173
- 管理员账号: admin / admin123 (需先在数据库执行init.sql)

## 功能模块
1. **用户管理** — 登录/注册/角色权限/基本信息管理
2. **患者管理** — 患者信息注册/完善/病历查看
3. **医生管理** — 医师注册/审核/排班/职称管理
4. **科室管理** — 科室层级管理/科室导航
5. **预约挂号** — 在线挂号/号源管理/排队叫号/预约查询
6. **AI问诊** — 症状采集/AI智能诊断/科室推荐/风险评估
7. **诊疗管理** — 病历创建/诊断录入/治疗方案/复诊提醒
8. **处方管理** — 药品处方/用法用量/库存管理
9. **通知管理** — 消息推送/未读提醒

## 数据库设计 (11张表, 3NF)
users, patients, doctors, departments, appointments,
ai_consultations, diagnosis_records, prescriptions,
medicines, operation_logs, notifications

## 开发人员分工
| 人员 | 角色 | 职责 |
|------|------|------|
| 组员1 | 项目经理/后端 | AI问诊模块/病历管理/数据库设计 |
| 组员2 | 前端组长 | 前端框架/用户管理/患者端/AI问诊前端 |
| 组员3 | 后端开发 | 用户认证/预约挂号/挂号管理 |
| 组员4 | 前端/测试 | 医生端/挂号管理前端/系统测试部署 |
