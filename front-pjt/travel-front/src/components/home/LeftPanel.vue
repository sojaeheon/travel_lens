<template>
  <div class="left-panel">
    <!-- 버튼 탭 -->
    <div class="tab-buttons">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 콘텐츠 영역 -->
    <div class="tab-content">
      <PopularList
        v-if="activeTab === 'popular'"
        @select-country="handleSelectCountry"
      />
      <ExchangeList
        v-if="activeTab === 'exchange'"
        @select-country="handleSelectCountry"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import PopularList from "./PopularList.vue";
import ExchangeList from "./ExchangeList.vue";

const emit = defineEmits(["country-select"]);

const activeTab = ref("popular");

const tabs = [
  { key: "popular", label: "인기 여행지" },
  { key: "exchange", label: "주요 환율" },
];

const handleSelectCountry = (country) => {
  emit("country-select", country);
};
</script>

<style scoped>
.left-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.tab-buttons {
  display: flex;
  gap: 8px;
}

.tab-buttons button {
  flex: 1;
  padding: 10px 0;
  border-radius: 10px;
  border: none;
  background: #f2f2f2;
  font-size: 14px;
  cursor: pointer;
}

.tab-buttons button.active {
  background: #111;
  color: #fff;
  font-weight: 600;
}

.tab-content {
  margin-top: 12px;
  flex: 1;
  overflow-y: auto;
}
</style>
