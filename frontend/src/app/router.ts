import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/modules/chat/pages/ChatWorkspacePage.vue'),
    },
    {
      path: '/knowledge',
      name: 'knowledge-workbench',
      component: () => import('@/modules/chat/pages/KnowledgeWorkbenchPage.vue'),
    },
  ],
})
