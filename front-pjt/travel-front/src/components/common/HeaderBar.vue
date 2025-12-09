<template>
  <header class="header">
    <!-- 로고 -->
    <div class="logo-area" @click="$router.push('/home')">
      <img src="/src/assets/logo.png" class="logo-icon" alt="logo" />
      <span class="logo-title">Travel Lens</span>
    </div>

    <!-- 우측 네비 -->
    <div class="right-section">

      <!-- 실시간 채팅방 -->
      <button class="chat-btn" @click="$router.push('/chat')">
        🧑‍🤝‍🧑 실시간 채팅방
      </button>

      <!-- ⭐ 비회원 UI -->
      <template v-if="!isLoggedIn">
        <button class="auth-btn light" @click="$router.push('/login')">
          sign in
        </button>
        <button class="auth-btn dark" @click="$router.push('/register')">
          sign up
        </button>
      </template>

      <!-- ⭐ 회원 UI -->
      <template v-else>
        <div class="profile-wrapper" @click="toggleDropdown">
          <div class="profile-icon">👤</div>

          <!-- 드롭다운 -->
          <div v-if="dropdownOpen" class="dropdown">
            <div class="dropdown-item" @click="goMyPage">마이페이지</div>
            <div class="dropdown-item logout" @click="logout">로그아웃</div>
          </div>
        </div>
      </template>

    </div>
  </header>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/store/user";

const router = useRouter();
const userStore = useUserStore();

// ⭐ 로그인 여부 — Pinia 구조대로 수정
const isLoggedIn = computed(() => userStore.isAuth);

// 드롭다운 열기/닫기
const dropdownOpen = ref(false);
const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

// 마이페이지 이동
const goMyPage = () => {
  dropdownOpen.value = false;
  router.push("/mypage");
};

// 로그아웃 처리
const logout = () => {
  userStore.logout();
  dropdownOpen.value = false;
  router.push("/login");
};
</script>

<style scoped>
.header {
  height: 72px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  background: #fff;
  border-bottom: 1px solid #e5e5ea;
}

/* 로고 */
.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
.logo-icon {
  width: 32px;
  height: 32px;
}
.logo-title {
  font-size: 22px;
  font-weight: 700;
}

/* 우측 */
.right-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

/* 비회원 버튼 */
.auth-btn {
  padding: 6px 18px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.auth-btn.light {
  background: #e5e5ea;
}
.auth-btn.dark {
  background: #333;
  color: white;
}

/* 회원 아이콘 */
.profile-wrapper {
  position: relative;
  cursor: pointer;
}
.profile-icon {
  width: 36px;
  height: 36px;
  background: #efefef;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
}

/* 드롭다운 */
.dropdown {
  position: absolute;
  right: 0;
  top: 46px;
  background: white;
  border: 1px solid #e5e5ea;
  border-radius: 10px;
  min-width: 120px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 10;
}

.dropdown-item {
  padding: 10px 14px;
  font-size: 14px;
  cursor: pointer;
}
.dropdown-item:hover {
  background: #f5f5f5;
}

.logout {
  color: #d9534f;
}
</style>
