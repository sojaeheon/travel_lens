import { defineStore } from "pinia";
import api from "@/api/axios";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("access") || null, // ⭐ 로그인 유지
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

      // 저장
      localStorage.setItem("access", access);
      localStorage.setItem("refresh", refresh);
      localStorage.setItem("user", JSON.stringify(user));

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
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("user");

      this.token = null;
      this.profile = null;
    },
  },
});
