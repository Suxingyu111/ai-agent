# 配置管理规则落地状态

## 已完成范围

- 新增根目录 `.gitignore`，明确禁止提交真实 `.env` 配置文件。
- 新增后端本地开发配置模板：`backend/.env.example`。
- 新增后端生产部署配置模板：`backend/.env.prod.example`。
- 新增前端本地开发配置模板：`frontend/.env.example`。
- 新增前端生产部署配置模板：`frontend/.env.prod.example`。
- 所有配置模板均按类别分组，并为每个配置项补充中文注释说明。
- 项目级规则 `AGENTS.md` 已补充配置管理长期规则。
- 架构设计文档已补充配置管理设计章节。

## 重要约束

- 后端真实配置必须从 `backend/.env` 读取。
- 前端真实配置必须从 `frontend/.env` 读取。
- 真实 `.env` 文件包含密钥、数据库密码、API Token、本地服务地址等信息，禁止提交到 Git。
- 示例配置文件只提供配置项说明和占位值，可以提交到 Git。
- 前端配置只能使用 `VITE_` 前缀变量，不能放任何私密密钥。
- 新增配置项时，必须同步更新本地和生产示例配置文件，并添加中文注释。

## 验证方式

- 已执行 `git diff --check` 检查 Markdown 和配置模板空白格式。
- 已通过 `git status --short` 核对新增文件范围。

## 后续建议

- 实现后端 `Settings` 配置类时，按当前模板分类映射配置项。
- 实现前端配置读取时，集中封装 `src/shared/config/`，避免业务页面直接散落读取 `import.meta.env`。
- 后续接入部署时，用平台密钥管理或 CI/CD Secret 注入生产 `.env`。
