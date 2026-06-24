# 健康检查接口

## GET `/api/v1/health`

用于检查后端 API 服务是否已经启动，并返回当前应用名称、运行环境和 API 前缀。

## 权限要求

- 不需要登录。
- 不需要 CSRF。
- 不消耗会员额度。

## 请求参数

无。

## 成功响应

```json
{
  "status": "ok",
  "app_name": "AI 多智能体平台",
  "environment": "test",
  "api_prefix": "/api/v1"
}
```

## 响应字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `status` | `string` | 服务状态，当前固定为 `ok`。 |
| `app_name` | `string` | 当前后端应用名称。 |
| `environment` | `string` | 当前后端运行环境。 |
| `api_prefix` | `string` | 当前 API v1 前缀。 |

## 错误响应

该接口不包含业务错误。服务不可用时由网关或 FastAPI 返回标准 HTTP 错误。

## 前端 TypeScript 类型建议

```ts
export interface HealthResponse {
  status: 'ok'
  app_name: string
  environment: string
  api_prefix: string
}
```
