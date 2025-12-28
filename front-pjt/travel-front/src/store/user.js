import { defineStore } from "pinia";
import api from "@/api/axios";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("access_token") || null,  // ✅ 수정
    profile: JSON.parse(localStorage.getItem("user")) || null,
  }),

  getters: {
    isAuth: (state) => !!state.token,
  },

  actions: {
    // ⭐ 실제 로그인 (JWT 연동)
    async login(email, password) {
      const res = await api.post("/accounts/login/", {
        email,
        password,
      });

      const access = res.data.access;
      const refresh = res.data.refresh;
      const user = res.data.user;

      // 저장 - 키 이름 통일
      localStorage.setItem("access_token", access);  // ✅ 수정
      localStorage.setItem("refresh_token", refresh);  // ✅ 수정
      localStorage.setItem("user", JSON.stringify(user));
      localStorage.setItem("user_email", user.email);  // ✅ 추가
      localStorage.setItem("user_nickname", user.nickname || user.email.split('@')[0]);  // ✅ 추가

      this.token = access;
      this.profile = user;
    },

    // ⭐ 실제 회원가입
    async register(email, name, password) {
      await api.post("/accounts/register/", {
        email,
        name,
        password,
      });
    },

    // ⭐ 로그아웃
    logout() {
      localStorage.removeItem("access_token");  // ✅ 수정
      localStorage.removeItem("refresh_token");  // ✅ 수정
      localStorage.removeItem("user");
      localStorage.removeItem("user_email");  // ✅ 추가
      localStorage.removeItem("user_nickname");  // ✅ 추가

      this.token = null;
      this.profile = null;
    },
  },
});