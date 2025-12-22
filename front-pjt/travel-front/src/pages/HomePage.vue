# homepage.vue
<template>
  <div class="page">
    <HeaderBar 
      @toggle-left-panel="toggleLeftPanel"
      @open-chat="isChatOpen = true"
    />

    <div class="content">
      <div class="left-column" v-if="showLeftPanel">
        <LeftPanel />
      </div>

      <div class="map-and-panel">
        <WorldMapView @country-click="openPanel" />

        <CountryDetailPanel
          v-if="showCountryPanel"
          :key="selectedCountry?.iso"
          :country="selectedCountry"
          @close="showCountryPanel = false"
          class="floating-panel"
        />

        <RealtimeChat 
          v-if="isChatOpen" 
          @close="isChatOpen = false" 
        />
        
        <button v-if="!isChatOpen" class="chat-toggle-btn" @click="isChatOpen = true">
          💬 실시간 채팅방
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import HeaderBar from "@/components/common/HeaderBar.vue";
import LeftPanel from "@/components/home/LeftPanel.vue";
import WorldMapView from "@/components/home/WorldMapView.vue";
import CountryDetailPanel from "@/components/home/CountryDetailPanel.vue";
import RealtimeChat from "@/components/chat/RealtimeChat.vue"; // ✅ 임포트 확인

const showCountryPanel = ref(false);
const selectedCountry = ref(null);
const showLeftPanel = ref(false);
const isChatOpen = ref(false); // 채팅창 상태값

const toggleLeftPanel = () => {
  showLeftPanel.value = !showLeftPanel.value;
};

const openPanel = (country) => {
  selectedCountry.value = country;
  showCountryPanel.value = true;
};
</script>

<style scoped>
/* 기존 스타일 유지 */
.page { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
.content { display: flex; flex: 1; overflow: hidden; }
.left-column { width: 340px; border-right: 1px solid #eee; background: white; }
.map-and-panel { position: relative; flex: 1; }

/* 지도가 꽉 차게 */
.map-and-panel > :first-child { width: 100%; height: 100%; }

.floating-panel { position: absolute; top: 20px; right: 20px; z-index: 10; }

.chat-toggle-btn {
  position: absolute; bottom: 30px; right: 30px; z-index: 15;
  padding: 15px 25px; background: #007bff; color: white;
  border: none; border-radius: 50px; cursor: pointer;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
</style>