// src>router>index.js
import { createRouter, createWebHistory } from 'vue-router'

import LandingPage from "@/pages/LandingPage.vue";
import HomePage from "@/pages/HomePage.vue";
import LoginPage from "@/pages/LoginPage.vue";
import RegisterPage from "@/pages/RegisterPage.vue";
// import CountryDetailPage from "@/pages/CountryDetailPage.vue";
// import ChatPage from "@/pages/ChatPage.vue";
import AiChatPage from "@/pages/AiChatPage.vue";
import MyPage from "@/pages/MyPage.vue";

// 전역 저장소
import { useUserStore } from "@/store/user";

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
      component: HomePage,
    },
    // {
    //   path: '/country/:code',
    //   name: 'countryDetail',
    //   component: CountryDetailPage
    // },
    {
      path: '/login',
      name: 'Login',
      component: LoginPage,
      meta: { guestOnly: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterPage,
      meta: { guestOnly: true }
    },
    {
      path: '/chat',
      name: 'Chat',
      component: HomePage
    },
    {
      path: '/ai',
      name: 'Ai',
      component: AiChatPage
    },
    {
      path: '/mypage',
      name: 'MyPage',
      component: MyPage,
      meta : { auth:true } 
    },
    
  ],
})

// 🔥 로그인 여부 체크하는 라우터 가드
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  const isLoggedIn = userStore.isAuth;

  // 1️⃣ 로그인 필요 페이지인데 로그인 안 됨 → /login 이동
  if (to.meta.auth && !isLoggedIn) {
    return next("/login");
  }

  // 2️⃣ guestOnly 페이지(로그인/회원가입)에 로그인 상태로 접근 → /home 이동
  if (to.meta.guestOnly && isLoggedIn) {
    return next("/home");
  }

  return next();
});

export default router
