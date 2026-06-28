import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'

import { describe, expect, it } from 'vitest'

describe('App root', () => {
  it('通过 RouterView 渲染当前路由页面', () => {
    const appSource = readFileSync(
      fileURLToPath(new URL('../App.vue', import.meta.url)),
      'utf-8',
    )

    expect(appSource).toContain('<RouterView />')
  })

  it('提供知识库调试工作台路由', () => {
    const routerSource = readFileSync(
      fileURLToPath(new URL('./router.ts', import.meta.url)),
      'utf-8',
    )
    const workbenchSource = readFileSync(
      fileURLToPath(
        new URL('../modules/chat/pages/KnowledgeWorkbenchPage.vue', import.meta.url),
      ),
      'utf-8',
    )

    expect(routerSource).toContain("path: '/knowledge'")
    expect(routerSource).toContain('KnowledgeWorkbenchPage.vue')
    expect(workbenchSource).toContain('getLoveMasterKnowledgeDocuments')
    expect(workbenchSource).toContain('getLoveMasterRetrievalDebug')
    expect(workbenchSource).toContain('runLoveMasterRetrievalEvaluation')
  })
})
