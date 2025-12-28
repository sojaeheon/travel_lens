<template>
  <div class="landing">
    <div class="landing-bg"></div>
    <div class="landing-overlay"></div>

    <div class="landing-center">
      <div class="logo-row">
        <img src="../assets/logo.png" class="logo-img" alt="Travel Lens" />
        <span class="logo-text">Travel Lens</span>
      </div>
      <button class="start-btn" @click="$router.push('/home')">START</button>
    </div>
  </div>
</template>


<script setup>
</script>


<style scoped>
.landing {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

/* ⭐ 움직이는 배경 */
.landing-bg {
  position: absolute;
  inset: 0;

  /* ✔ 배경을 가로로 반복되도록 설정 */
  background-image: url("../assets/worldmap-bg.jpg");
  background-size: cover;
  background-repeat: repeat-x;

  /* ✔ 자연스럽게 무한 이동 */
  animation: slide-seamless 40s linear infinite;
}

@keyframes slide-seamless {
  from {
    background-position-x: 0;
  }
  to {
    background-position-x: -100%;
  }
}

.landing-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
}

.landing-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #fff;
}

.logo-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.logo-img {
  width: 70px;
  height: 70px;
}

.logo-text {
  color: black;
  font-size: 40px;
  font-weight: 700;
}

.start-btn {
  margin-top: 8px;
  padding: 12px 40px;
  border-radius: 4px;
  border: none;
  background: #222;
  color: #fff;
  font-size: 16px;
  letter-spacing: 0.2em;
  cursor: pointer;
}
</style>
