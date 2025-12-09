import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/",   // Django 서버 주소
  withCredentials: false                  // JWT는 localStorage 보관
});

// 저장된 토큰을 헤더에 자동 포함
api.interceptors.request.use(
  config => {
    const access = localStorage.getItem("access");
    if (access) {
      config.headers.Authorization = `Bearer ${access}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

export default api;
