<template>
  <div class="map-wrapper">
    <img src="../../assets/worldmap-bg.jpg" class="map-bg" />

    <SearchBar v-model="keyword" @select="goCountry" />

    <!-- 간단한 원들 (더미) -->
    <div class="bubble bubble-us"></div>
    <div class="bubble bubble-eu"></div>
    <div class="bubble bubble-af"></div>

    <!-- AI 아이콘 버튼 -->
    <button class="ai-btn" @click="$router.push('/ai')">
      AI
    </button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import SearchBar from "@/components/common/SearchBar.vue";
import { useRouter } from "vue-router";

const router = useRouter();
const keyword = ref("");

const goCountry = (name) => {
  // 실제로는 name → code 매핑 후 이동
  router.push({ name: "countryDetail", params: { code: "KOR" } });
};
</script>

<style scoped>
.map-wrapper {
  position: relative;
  flex: 1;
  height: calc(100vh - 72px);
  background: #222;
  overflow: hidden;
}
.map-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.bubble {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 220, 100, 0.6), transparent);
}
.bubble-us {
  width: 140px;
  height: 140px;
  left: 25%;
  top: 50%;
}
.bubble-eu {
  width: 180px;
  height: 180px;
  left: 50%;
  top: 35%;
}
.bubble-af {
  width: 180px;
  height: 180px;
  left: 55%;
  top: 65%;
}
.ai-btn {
  position: absolute;
  right: 24px;
  bottom: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: #fff;
  cursor: pointer;
  font-weight: 700;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
</style>
