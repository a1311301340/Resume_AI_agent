# Backend Design

## Migration Check

已核对文档中的核心接口、字段与内容：

- 保留 `task_id`、`jd_text`、`mode`、`reply` 等关键字段
- 保留 `BaseResponse(code, message, data)` 返回格式
- 保留 `/upload -> /process -> /result -> /export` 主链路

## Compatibility

- 为第二版前端补充 `POST /task/create` 和 `GET /task/{task_id}`
- 为结果导出补充 `GET /result/{task_id}/export`
- `task` 兼容接口返回扁平对象，适配轮询 store

