<template>
  <header class="header">
    <!-- ⭐ 좌측 영역 -->
    <div class="left-section">
      <!-- 메뉴 버튼 -->
      <img
        src="@/assets/menu_icon.png"
        alt="menu"
        class="menu-icon"
        :class="{ active: isMenuOpen }"
        @click="toggleMenu"
      />

      <!-- 로고 -->
      <div class="logo-area" @click="$router.push('/home')">
        <img src="/src/assets/logo.png" class="logo-icon" alt="logo" />
        <span class="logo-title">Travel Lens</span>
      </div>
    </div>

    <!-- 우측 네비 -->
    <div class="right-section">
      <button class="chat-btn" @click="$emit('open-chat')">
        🧑‍🤝‍🧑 실시간 채팅방
      </button>

      <template v-if="!isLoggedIn">
        <button class="auth-btn light" @click="$router.push('/login')">
          sign in
        </button>
        <button class="auth-btn dark" @click="$router.push('/register')">
          sign up
        </button>
      </template>

      <template v-else>
        <div class="profile-wrapper" @click="toggleDropdown">
          <div class="profile-icon">👤</div>

          <div v-if="dropdownOpen" class="dropdown">
            <!-- 👤 사용자 정보 -->
            <div class="user-info">
              <div class="nickname">{{ userNickname }}</div>
              <div class="email">{{ userEmail }}</div>
            </div>

            <div class="divider"></div>

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

/* emit 정의 */
const emit = defineEmits(["toggle-left-panel","open-chat"]);

const router = useRouter();
const userStore = useUserStore();
/* 사용자 정보 */
const userNickname = computed(() => {
  return (
    userStore.profile?.nickname ||
    localStorage.getItem("user_nickname") ||
    "사용자"
  );
});

const userEmail = computed(() => {
  return (
    userStore.profile?.email ||
    localStorage.getItem("user_email") ||
    ""
  );
});

/* 로그인 여부 */
const isLoggedIn = computed(() => userStore.isAuth);

/* ⭐ 메뉴 열림 상태 */
const isMenuOpen = ref(true);

/* 메뉴 버튼 클릭 */
const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
  emit("toggle-left-panel");
};

/* 드롭다운 */
const dropdownOpen = ref(false);
const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

const goMyPage = () => {
  dropdownOpen.value = false;
  router.push("/mypage");
};

const logout = () => {
  userStore.logout();
  dropdownOpen.value = false;
  router.push("/home");
  window.location.reload();
};
</script>

<style scoped>
/* 헤더 */
.header {
  height: 72px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  background: #fff;
  border-bottom: 1px solid #e5e5ea;
}

/* 좌측 */
.left-section {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* ❌ 기본 상태 = 회색 */
.menu-icon {
  width: 32px;
  height: 32px;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  background: #e5e5ea;          /* ⭐ 안 눌림 = 회색 */
  transition: background 0.2s ease;
}

/* ✅ 눌린 상태 = 흰색 */
.menu-icon.active {
  background: #ffffff;
}

/* hover */
.menu-icon:hover {
  background: #f0f0f0;
}

/* 로고 */
.logo-area {
  display: flex;
  align-items: center;
  gap: 3px;
  cursor: pointer;
  padding-left : 10px;
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
  z-index: 100;
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

/* 사용자 정보 */
.user-info {
  padding: 12px 14px;
  background: #fafafa;
}

.nickname {
  font-size: 14px;
  font-weight: 600;
}

.email {
  font-size: 12px;
  color: #777;
  margin-top: 2px;
}

.divider {
  height: 1px;
  background: #e5e5ea;
}
</style>
