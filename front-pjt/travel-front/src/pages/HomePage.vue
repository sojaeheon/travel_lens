<template>
  <div class="page">
    <HeaderBar 
      @toggle-left-panel="toggleLeftPanel"
      @open-chat="handleOpenChat" 
    />

    <div class="content">
      <div class="left-column" v-if="showLeftPanel">
        <LeftPanel @country-select="handlePopularSelect" />
      </div>

      <div class="map-and-panel">
        <WorldMapView
          ref="mapView"
          @country-click="openPanel"
          @open-ai="openAiAssistant"
        />

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

        <div v-if="isAiOpen" class="ai-overlay">
          <AiAssistant @close="isAiOpen = false" />
        </div>
        

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
import AiAssistant from "@/components/ai/AiAssistant.vue";
// ✅ [추가] 로그에서 로그인 상태를 확인하기 위해 userStore를 임포트합니다.
import { useUserStore } from "@/store/user";

const userStore = useUserStore(); // ✅ [추가] store 인스턴스 생성

const showCountryPanel = ref(false);
const selectedCountry = ref(null);

const showLeftPanel = ref(false);
const isChatOpen = ref(false);
const isAiOpen = ref(false);
const mapView = ref(null);

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

const openAiAssistant = () => {
  isAiOpen.value = true;
};

const toggleLeftPanel = () => {
  showLeftPanel.value = !showLeftPanel.value;
};

const openPanel = (country) => {
  selectedCountry.value = country;
  showCountryPanel.value = true;
};

const handlePopularSelect = (country) => {
  if (!country?.iso2) return;
  mapView.value?.focusCountry({
    iso2: country.iso2,
    name_ko: country.name_ko,
    name_en: country.name_en,
  });
  openPanel({
    iso: country.iso2,
    name_ko: country.name_ko,
    name_en: country.name_en,
  });
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

.ai-overlay {
  position: absolute;
  left: 24px;
  bottom: 90px;
  z-index: 12;
}

</style>
