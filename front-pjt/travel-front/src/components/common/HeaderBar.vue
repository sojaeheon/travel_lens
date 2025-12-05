<template>
  <header class="header">
    <div class="logo-area" @click="$router.push('/home')">
      <img src="../../assets/logo.png" class="logo-icon" alt="logo" />
      <span class="logo-title">Travel Lens</span>
    </div>

    <div class="header-right">
      <button class="icon-btn" @click="$router.push('/chat')">
        🧑‍🤝‍🧑 실시간 채팅방
      </button>
      <button class="auth-btn light" @click="$router.push('/login')">
        sign in
      </button>
      <button class="auth-btn dark" @click="$router.push('/register')">
        sign up
      </button>
    </div>
  </header>
</template>

<script setup>
</script>

<style scoped>
.header {
  height: 72px;
  background: #ffffff;
  border-bottom: 1px solid #e5e5ea;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
}
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
  font-weight: 700;
  font-size: 22px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.icon-btn {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
}
.auth-btn {
  border-radius: 20px;
  padding: 6px 18px;
  font-size: 14px;
  border: none;
  cursor: pointer;
}
.auth-btn.light {
  background: #e5e5ea;
}
.auth-btn.dark {
  background: #333;
  color: #fff;
}
</style>
