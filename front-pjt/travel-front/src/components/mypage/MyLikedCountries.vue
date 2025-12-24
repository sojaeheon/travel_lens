<template>
  <div class="wrap">
    <h2>내가 찜한 나라</h2>

    <div v-if="loading" class="loading-state">
      데이터를 불러오는 중입니다...
    </div>

    <div v-else-if="favoriteCards.length > 0" class="grid">
      <transition-group name="list">
        <div v-for="c in favoriteCards" :key="c.iso2" class="card">
          <img 
            :src="c.imageUrl || '/assets/sample-city.jpg'" 
            :alt="c.name_en" 
          />
          <div class="text-top">{{ c.name_en?.toUpperCase() }}</div>
          <div class="text-bottom">{{ c.name_ko }}</div>
          
          <button 
            class="heart active" 
            @click="handleRemoveFavorite(c.iso2)"
            title="찜 해제"
          >
            ♥
          </button>
        </div>
      </transition-group>
    </div>

    <div v-else class="empty-msg">
      아직 찜한 나라가 없습니다. 여행지를 탐색해 보세요!
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/api/axios'; // 기존 설정된 axios 인스턴스 사용

const PEXELS_KEY = import.meta.env.VITE_PEXELS_API_KEY;
const favoriteCards = ref([]);
const loading = ref(true);

/**
 * 1. Django 백엔드에서 찜 목록 가져오기
 */
const fetchMyFavorites = async () => {
  try {
    loading.value = true;
    // 우리가 urls.py에 새로 만든 엔드포인트
    const response = await axios.get('/api/interaction/favorites/');
    const data = response.data; // [{iso2, name_en, name_ko}, ...]

    // 2. Pexels 이미지 결합
    favoriteCards.value = await enrichWithImages(data);
  } catch (error) {
    console.error("찜 목록 로드 실패:", error);
  } finally {
    loading.value = false;
  }
};

/**
 * 2. Pexels API를 사용하여 국가별 랜드마크 이미지 매핑
 */
const enrichWithImages = async (countries) => {
  const promises = countries.map(async (country) => {
    try {
      const pexelsRes = await axios.get('https://api.pexels.com/v1/search', {
        params: { query: `${country.name_en} landmark`, per_page: 1, orientation: 'landscape' },
        headers: { Authorization: PEXELS_KEY }
      });
      return {
        ...country,
        imageUrl: pexelsRes.data.photos[0]?.src.large || ''
      };
    } catch (err) {
      console.warn(`${country.name_en} 이미지 로드 실패`, err);
      return { ...country, imageUrl: '' };
    }
  });
  return await Promise.all(promises);
};

/**
 * 3. 찜 해제 처리 (백엔드 로그 전송 및 UI 업데이트)
 */
const handleRemoveFavorite = async (iso2) => {
  if (!confirm("찜 목록에서 삭제하시겠습니까?")) return;

  try {
    // 기존 UserEventCreateView 로직 활용 (toggle 방식)
    await axios.post('/api/interaction/logs/', {
      event_type: 'country_like_toggle',
      country_code: iso2
    });

    // 성공 시 화면에서 즉시 제거 (반응성 유지)
    favoriteCards.value = favoriteCards.value.filter(c => c.iso2 !== iso2);
  } catch (error) {
    alert("삭제 처리에 실패했습니다.");
    console.error(error);
  }
};

onMounted(() => {
  fetchMyFavorites();
});
</script>

<style scoped>
.wrap { padding: 40px 60px; }
.grid { 
  margin-top: 18px; 
  display: grid; 
  grid-template-columns: repeat(2, 1fr); 
  gap: 18px; 
}

.card { 
  position: relative; 
  border-radius: 18px; 
  overflow: hidden; 
  height: 160px; 
  background: #f0f0f0;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.card img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.card:hover img { transform: scale(1.05); }

.text-top { 
  position: absolute; top: 12px; left: 16px; 
  font-size: 14px; font-weight: 700; color: #fff; 
  text-shadow: 0 2px 4px rgba(0,0,0,0.6); 
}
.text-bottom { 
  position: absolute; top: 32px; left: 16px; 
  font-size: 13px; color: #fff; 
  text-shadow: 0 2px 4px rgba(0,0,0,0.6); 
}

.heart { 
  position: absolute; top: 10px; right: 10px; 
  border-radius: 50%; width: 32px; height: 32px; 
  border: none; background: rgba(255, 255, 255, 0.9); 
  color: #ff4d4f; cursor: pointer; 
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

/* 애니메이션 */
.list-leave-active { transition: all 0.4s ease; }
.list-leave-to { opacity: 0; transform: scale(0.8); }

.empty-msg, .loading-state { 
  text-align: center; margin-top: 100px; color: #999; font-size: 1.1rem; 
}
</style>