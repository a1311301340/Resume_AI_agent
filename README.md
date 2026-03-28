# 后端（不安装依赖版）
cd C:\Users\13113\Desktop\codex_project\ai_job_agent_backend
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\python.exe run.py

# 前端（不安装依赖版）
cd C:\Users\13113\Desktop\codex_project\ai_job_agent_front
npm run dev




# AI Job Agent

基于你提供的 3 份文档重构的项目骨架，目标是：

- 稳定性优先：保留原接口与返回内容语义
- 可扩展优先：后端分层（api/application/domain/infrastructure），前端分层（app/pages/features/shared）
- 向后兼容：同时兼容文档中的两套前端接口调用习惯

## 目录

- `ai_job_agent_backend/` FastAPI 后端
- `ai_job_agent_front/` Vue3 前端
- `docs/architecture/` 架构与迁移说明

## 快速启动（Windows）

后端（自动创建虚拟环境并安装依赖）：

- `cd ai_job_agent_backend`
- `.\start_backend.ps1`

百炼应用 API 配置（`.env`）：

- `BAILIAN_API_KEY=...`
- `BAILIAN_APP_ID=...`
- `BAILIAN_BASE_URL=https://dashscope.aliyuncs.com`

前端：

- `cd ai_job_agent_front`
- `npm install`
- `npm run dev`

## 兼容接口

原接口（保持）：

- `POST /upload`
- `POST /process`
- `GET /result/{task_id}`
- `GET /export/{task_id}`
- `POST /agent/chat`

兼容接口（新增）：

- `POST /task/create`
- `GET /task/{task_id}`
- `GET /result/{task_id}/export`
