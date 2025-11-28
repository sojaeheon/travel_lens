<template>
  <div class="landing-container">
    <div class="overlay"></div>

    <div class="content">
      <div class="logo-wrap">
        <img src="./image/travel_lens_rogo1.png" alt="logo" class="logo" />
      </div>

      <button class="start-btn" @click="goMain">
        START
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const goMain = () => {
  router.push('/main')
}
</script>

<style scoped>
.landing-container {
  width: 100vw;
  height: 100vh;
  background-image: url('@/assets/bg.png');
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
}

.content {
  position: relative;
  text-align: center;
  color: white;
}

.logo-wrap {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}

.logo {
  width: 900px;
  margin-right: 1px;
}

.title {
  font-size: 64px;
  font-weight: 700;
  text-align: left;
  line-height: 1.2;
}

.start-btn {
  margin-top: 30px;
  padding: 12px 40px;
  font-size: 20px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid #fff;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  backdrop-filter: blur(2px);
  transition: 0.2s;
}

.start-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}
</style>
