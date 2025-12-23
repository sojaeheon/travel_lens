<template>
  <div class="page">
    <HeaderBar 
      @toggle-left-panel="toggleLeftPanel"
      @open-chat="handleOpenChat" 
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
          @close="handleCloseChat" 
        />
        
        <button v-if="!isChatOpen" class="chat-toggle-btn" @click="handleOpenChat">
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
import RealtimeChat from "@/components/chat/RealtimeChat.vue";
// ✅ [추가] 로그에서 로그인 상태를 확인하기 위해 userStore를 임포트합니다.
import { useUserStore } from "@/store/user";

const userStore = useUserStore(); // ✅ [추가] store 인스턴스 생성
const showCountryPanel = ref(false);
const selectedCountry = ref(null);
const showLeftPanel = ref(false);
const isChatOpen = ref(false);

// ✅ [추가/수정] 채팅창 제어 및 디버깅 로그 함수
const handleOpenChat = () => {
  console.log("--- 채팅창 열기 프로세스 시작 ---");
  console.log("1. 클릭 신호 수신됨");
  console.log("2. 현재 유저 인증 상태:", userStore.isAuth); 
  
  isChatOpen.value = true;
  
  console.log("3. isChatOpen 상태값:", isChatOpen.value);
  console.log("------------------------------");
};

const handleCloseChat = () => {
  console.log("--- 채팅창 닫기 프로세스 시작 ---");
  isChatOpen.value = false;
  console.log("결과: 채팅창이 닫혔습니다.");
};

const toggleLeftPanel = () => {
  showLeftPanel.value = !showLeftPanel.value;
};

const openPanel = (country) => {
  selectedCountry.value = country;
  showCountryPanel.value = true;
};
</script>

<style scoped>
/* 기존 스타일은 동일하게 유지됩니다. */
.page { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
.content { display: flex; flex: 1; overflow: hidden; }
.left-column { width: 340px; border-right: 1px solid #eee; background: white; }
.map-and-panel { position: relative; flex: 1; }
.map-and-panel > :first-child { width: 100%; height: 100%; }
.floating-panel { position: absolute; top: 20px; right: 20px; z-index: 10; }
.chat-toggle-btn {
  position: absolute; bottom: 30px; right: 30px; z-index: 15;
  padding: 15px 25px; background: #007bff; color: white;
  border: none; border-radius: 50px; cursor: pointer;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
</style>