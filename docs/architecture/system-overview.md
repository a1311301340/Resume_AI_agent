# System Overview

## Refactor Goals

1. 保留原有接口路径和核心返回结构（`BaseResponse`）。
2. 支持新前端任务中心接口（`/task/*`）的兼容访问。
3. 引入清晰分层，后续可替换内存仓储为数据库仓储。

## Backend Layers

- `api`: HTTP 路由和协议转换
- `application`: 用例编排
- `domain`: 业务规则与实体
- `infrastructure`: 仓储、解析器、存储等外部实现

## Frontend Layers

- `app`: 路由、布局、应用级初始化
- `pages`: 页面编排
- `features`: 业务动作（上传、处理、结果、聊天）
- `shared`: 请求层与类型定义

