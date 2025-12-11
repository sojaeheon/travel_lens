<template>
  <div class="page">
    <HeaderBar />

    <div class="content">
      <div class="left-column">
        <PopularList />
        <ExchangeList />
      </div>

      <!-- 지도와 패널을 나란히 배치하는 래퍼 -->
      <div class="map-and-panel">
        <WorldMapView @country-click="openPanel" />

        <!-- absolute로 지도 위에 떠 있는 패널 -->
        <CountryDetailPanel
          v-if="showCountryPanel"
          :country="selectedCountry"
          @close="showCountryPanel = false"
          class="floating-panel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import HeaderBar from "@/components/common/HeaderBar.vue";
import PopularList from "@/components/home/PopularList.vue";
import ExchangeList from "@/components/home/ExchangeList.vue";
import WorldMapView from "@/components/home/WorldMapView.vue";
import CountryDetailPanel from "@/components/home/CountryDetailPanel.vue";

const showCountryPanel = ref(false);
const selectedCountry = ref(null);

const openPanel = (country) => {
  selectedCountry.value = country;
  showCountryPanel.value = true;
};
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* 전체 레이아웃 */
.content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 왼쪽 영역 */
.left-column {
  width: 340px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ⭐ 지도 + 패널을 오른쪽 열로 묶기 위한 wrapper */
.map-and-panel {
  position: relative;
  flex: 1;
}

/* 지도는 전체 오른쪽 영역을 항상 차지 */
.map-and-panel > :first-child {
  flex: 1;
}

/* ⭐ 지도 위에 떠 있는 CountryDetailPanel */
.floating-panel {
  position: absolute;
  top: 20px;
  right: 20px;     /* ← 오른쪽 여백 → 지도 보임 */
  bottom: 20px;
  z-index: 10;
}

/* CountryDetailPanel은 width가 고정이라 그대로 오른쪽에 붙음 */
</style>
