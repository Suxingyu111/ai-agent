<script setup lang="ts">
import { appConfig } from '@/shared/config/appConfig'
</script>

<template>
  <main class="app-shell">
    <section class="workspace">
      <div class="workspace__header">
        <p class="workspace__eyebrow">Multi-Agent Platform</p>
        <h1>{{ appConfig.appName }}</h1>
        <p class="workspace__description">
          独立智能体、工具网关、知识库、记忆和工作流会在这里逐步展开。
        </p>
      </div>

      <div class="status-grid" aria-label="平台初始化状态">
        <article class="status-card">
          <span class="status-card__label">运行环境</span>
          <strong>{{ appConfig.appEnv }}</strong>
        </article>
        <article class="status-card">
          <span class="status-card__label">API 地址</span>
          <strong>{{ appConfig.api.baseUrl }}</strong>
        </article>
        <article class="status-card">
          <span class="status-card__label">智能体构建器</span>
          <strong>{{ appConfig.features.enableAgentBuilder ? '已启用' : '未启用' }}</strong>
        </article>
        <article class="status-card">
          <span class="status-card__label">Workflow 编排</span>
          <strong>{{ appConfig.features.enableWorkflowBuilder ? '已启用' : '未启用' }}</strong>
        </article>
      </div>
    </section>
  </main>
</template>
