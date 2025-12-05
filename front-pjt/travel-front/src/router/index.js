import { createRouter, createWebHistory } from 'vue-router'

import LandingPage from "@/pages/LandingPage.vue";
import HomePage from "@/pages/HomePage.vue";
import LoginPage from "@/pages/LoginPage.vue";
import RegisterPage from "@/pages/RegisterPage.vue";

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
    {
      path: '/login',
      name: 'ㅣogin',
      component: LoginPage
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterPage
    },
  ],
})

export default router
