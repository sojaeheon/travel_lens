<template>
  <div class="recommend-card">
    <h3 class="title">✨ AI 추천 여행지</h3>

    <ul class="country-list">
      <li
        v-for="country in recommendedCountries"
        :key="country.code"
        class="country-item"
        @click="selectCountry(country)"
      >
        <div class="left">
          <span class="rank">#{{ country.rank }}</span>
          <span class="name">{{ country.name }}</span>
        </div>

        <div class="right">
          <span class="reason">{{ country.reason }}</span>
          <span class="score">{{ country.score }}점</span>
        </div>
      </li>
    </ul>

    <p class="hint">
      · 추천 기준: 관심도 · 환율 · 항공료 · 안전도
    </p>
  </div>
</template>

<script setup>
import { ref } from "vue";

/**
 * ✅ 더미 추천 데이터
 * 나중에 API 연결 시 이 부분만 교체하면 됨
 */
const recommendedCountries = ref([
  {
    rank: 1,
    code: "JPN",
    name: "일본",
    score: 92,
    reason: "엔저 · 짧은 비행시간",
  },
  {
    rank: 2,
    code: "VNM",
    name: "베트남",
    score: 88,
    reason: "저렴한 물가 · 높은 만족도",
  },
  {
    rank: 3,
    code: "ESP",
    name: "스페인",
    score: 85,
    reason: "관광 수요 급증",
  },
  {
    rank: 4,
    code: "CAN",
    name: "캐나다",
    score: 82,
    reason: "자연 관광 · 안전 국가",
  },
]);

/**
 * 👉 지도 연동용 이벤트
 * (부모에서 WorldMapView 이동 처리 가능)
 */
const emit = defineEmits(["country-select"]);

const selectCountry = (country) => {
  emit("country-select", country);
};
</script>

<style scoped>
.recommend-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
}

.title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 12px;
}

.country-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.country-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  background: #f7f7f7;
  cursor: pointer;
  transition: all 0.2s ease;
}

.country-item:hover {
  background: #111;
  color: #fff;
}

.left {
  display: flex;
  gap: 8px;
  align-items: center;
}

.rank {
  font-weight: 700;
  font-size: 13px;
}

.name {
  font-size: 14px;
  font-weight: 600;
}

.right {
  text-align: right;
  font-size: 12px;
}

.reason {
  display: block;
  opacity: 0.8;
}

.score {
  font-weight: 700;
}

.hint {
  margin-top: 12px;
  font-size: 11px;
  color: #888;
}
</style>
