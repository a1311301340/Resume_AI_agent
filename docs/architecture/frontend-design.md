# Frontend Design

## Refactor Strategy

- 使用 `app/pages/features/shared` 分层替代原“按类型堆叠”结构
- 页面只依赖 store，store 统一调用 API
- API 层兼容 `BaseResponse` 包裹与扁平对象两种返回

## Key Flows

1. 上传简历：`/upload`
2. 处理任务：`/process`
3. 查看结果：`/result/{task_id}`
4. 导出结果：`/export/{task_id}`
5. 模拟问答：`/agent/chat`
6. 任务轮询兼容：`/task/create` + `/task/{task_id}`

