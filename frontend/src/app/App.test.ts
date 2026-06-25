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
})
