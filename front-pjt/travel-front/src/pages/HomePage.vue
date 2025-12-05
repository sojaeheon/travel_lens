<template>
  <div class="page">
    <HeaderBar />

    <div class="content">
      <div class="left-column">
        <PopularList />
        <ExchangeList />
      </div>

      <WorldMapView />

      <CountryDetailPanel
        v-if="showCountryPanel"
        @close="showCountryPanel = false"
      />
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

const showCountryPanel = ref(true); // 일단 항상 열어둠 (나중에 지도 클릭 시 토글)
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.content {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.left-column {
  width: 340px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
