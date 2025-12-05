import { createRouter, createWebHistory } from 'vue-router'

import LandingPage from "@/pages/LandingPage.vue";
import HomePage from "@/pages/HomePage.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: LandingPage
    },
    {
      path: '/home',
      name: 'Home',
      component: HomePage
    },
  ],
})

export default router
