import { defineStore } from "pinia";
// import axios from "axios";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: null,
    profile: null,
  }),
  actions: {
    async login(email, password) {
      // 실제 연동 시 axios 사용
      // const res = await axios.post("/api/auth/login", { email, password });
      // this.token = res.data.token;
      // this.profile = res.data.user;

      console.log("login called", email, password);
      this.token = "dummy-token";
      this.profile = { email, name: "더미 사용자" };
    },
    async register(payload) {
      console.log("register called", payload);
      // await axios.post("/api/auth/register", payload);
    },
  },
});
