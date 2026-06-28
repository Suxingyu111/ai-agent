# AI 恋爱大师知识文档沉淀目录

该目录用于沉淀 AI 恋爱大师 RAG 知识库的 Markdown 知识卡片。

默认配置：

```env
KNOWLEDGE_DOCUMENTS_PATH=./knowledge/love_master
```

目录约定：

- `curated/`：人工整理并随项目提交的知识卡片，服务初始化默认知识库时会优先读取。
- `collected/`：URL 采集接口整理出的知识卡片，便于人工审核、编辑和后续提交。

运行 `POST /api/v1/knowledge-bases/love-master-default/sources/collect` 后，服务端会把整理出的 Markdown 文档写入：

```text
backend/knowledge/love_master/collected/
```

这些 Markdown 文件是 RAG 入库前的可审查资料源，后续可以人工审核、编辑、提交到 Git，再重新入库或重建索引。
