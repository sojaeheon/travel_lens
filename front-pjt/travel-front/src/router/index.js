import { createRouter, createWebHistory } from 'vue-router'

import LandingPage from "@/pages/LandingPage.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: LandingPage
    },
    // {
    //   path: '/main',
    //   name: 'Main',
    //   component: () => import('../components/MainView.vue')
    // },
  ],
})

export default router
