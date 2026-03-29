# AI Job Agent

AI 求职助手系统（V1），支持简历上传解析、岗位 JD 匹配、结果编辑与导出、模拟面试流式对话、历史记录追溯。

## 功能概览

- 简历上传：支持 `PDF / DOC / DOCX`
- 任务处理：JD 匹配、项目改写、自我介绍生成
- 结果中心：结构化编辑、JSON 编辑、版本管理、TXT 导出
- 模拟面试：流式输出，思考过程可折叠
- 历史记录：任务详情、简历文本、聊天记录

## 技术栈（关键）

- 前端：`Vue 3` + `Vite` + `TypeScript` + `Pinia` + `Element Plus`
- 后端：`FastAPI` + `Pydantic` + `OpenAI Compatible API`
- 数据库：`MySQL`
- 文档解析：`pdfplumber` + `python-docx` + `LibreOffice`（用于 DOC 转换）

## 项目结构

- `ai_job_agent_front/` 前端工程
- `ai_job_agent_backend/` 后端工程
- `docs/architecture/` 架构文档

## 启动（已安装依赖）

### 后端

```powershell
cd C:\Users\13113\Desktop\codex_project\ai_job_agent_backend
Set-ExecutionPolicy -Scope Process Bypass
.\start_backend.ps1
```

### 前端

```powershell
cd C:\Users\13113\Desktop\codex_project\ai_job_agent_front
npm run dev
```

## 首次安装（新机器）

### 后端

```powershell
cd C:\Users\13113\Desktop\codex_project\ai_job_agent_backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 前端

```powershell
cd C:\Users\13113\Desktop\codex_project\ai_job_agent_front
npm install
```

## 环境变量配置

后端使用 `ai_job_agent_backend/.env`（可从 `.env.example` 复制）。

最少需要配置：

```env
# 大模型
DASHSCOPE_API_KEY=your_api_key_here
BAILIAN_COMPAT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
BAILIAN_CHAT_MODEL=qwen3.5-plus
BAILIAN_ENABLE_THINKING=true

# MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=ai_job_agent
DB_CHARSET=utf8mb4

# DOC 解析（可选）
LIBREOFFICE_SOFFICE=C:\Program Files\LibreOffice\program\soffice.exe
```

前端开发环境：

```env
VITE_BASE_URL=http://127.0.0.1:8010
```

## 默认访问地址

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8010`
- 健康检查：`http://127.0.0.1:8010/health/full`

## 主要接口

- `POST /upload`
- `POST /process`
- `GET /result/{task_id}`
- `GET /export/{task_id}`
- `POST /agent/chat`
- `POST /agent/chat/stream`
- `GET /history/tasks`

## 安全说明

- 仓库中不要提交任何真实 API Key 或数据库密码
- `.env` 已在 `.gitignore` 中忽略，请仅在本机保存
- 若历史上出现过密钥泄露，请立即在云平台重置该密钥
