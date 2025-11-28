import { createRouter, createWebHistory } from 'vue-router'
import StartView from '../components/StartView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: StartView
    },
    // {
    //   path: '/main',
    //   name: 'Main',
    //   component: () => import('../components/MainView.vue')
    // },
  ],
})

export default router
