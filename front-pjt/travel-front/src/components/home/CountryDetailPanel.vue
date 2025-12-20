<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import likeIcon from "@/assets/like_btn.png";
import unlikeIcon from "@/assets/unlike_btn.png";
import { sendLog } from "@/api/log";
import { fetchFavoriteStatus as fetchFavoriteStatusApi } from "@/api/favorite";

const props = defineProps({
  country: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close"]);

const tabs = ["뉴스", "블로그", "출입국"];
const currentTab = ref("뉴스");

// ==================================================
// ⭐ 로그인 여부 (SimpleJWT 기준)
// ==================================================
const isAuthenticated = computed(() => {
  return !!localStorage.getItem("access"); // 🔥 핵심 수정
});

// ==================================================
// ⭐ ISO2 코드 계산
// ==================================================
const iso2 = computed(() => {
  const code = props.country.iso || "";
  return code.length === 2
    ? code.toUpperCase()
    : code.slice(0, 2).toUpperCase();
});

// ==================================================
// ❤️ 좋아요 상태 (서버 기준)
// ==================================================
const isLiked = ref(false);
const loadingLike = ref(false);

// 👉 찜 상태 조회 API
const fetchFavoriteStatus = async () => {
  if (!isAuthenticated.value) {
    isLiked.value = false;
    return;
  }

  try {
    const res = await fetchFavoriteStatusApi(iso2.value);
    isLiked.value = res.data.is_favorited;
  } catch {
    isLiked.value = false;
  }
};

// ==================================================
// ⏱ 체류 시간 측정
// ==================================================
let enterTime = 0;

// ==================================================
// 라이프사이클
// ==================================================
onMounted(async () => {
  enterTime = Date.now();

  // 상세 열림 로그 (비로그인도 수집)
  sendLog({
    event_type: "country_detail_open",
    country_code: iso2.value,
  });

  await fetchFavoriteStatus();
});

onBeforeUnmount(() => {
  const durationSec = (Date.now() - enterTime) / 1000;

  sendLog({
    event_type: "country_detail_stay",
    country_code: iso2.value,
    value: Number(durationSec.toFixed(2)),
  });
});

// ==================================================
// ❤️ 좋아요 토글 (서버 기준)
// ==================================================
const toggleLike = async () => {
  if (!isAuthenticated.value) {
    alert("로그인 후 찜할 수 있습니다.");
    return;
  }

  if (loadingLike.value) return;
  loadingLike.value = true;

  try {
    await sendLog({
      event_type: "country_like_toggle",
      country_code: iso2.value,
    });

    await fetchFavoriteStatus();
  } finally {
    loadingLike.value = false;
  }
};

// ==================================================
// 국가 변경 시 상태 재조회
// ==================================================
watch(
  () => iso2.value,
  async () => {
    await fetchFavoriteStatus();
  }
);
</script>

<template>
  <aside class="panel">
    <header class="head">
      <div class="title-group">
        <div class="country-row">
          <div class="country">{{ props.country.name_ko }}</div>

          <!-- ❤️ 좋아요 버튼 (로그인 사용자만) -->
          <button
            v-if="isAuthenticated"
            class="like-btn"
            :class="{ liked: isLiked }"
            :disabled="loadingLike"
            @click="toggleLike"
          >
            <img
              :src="isLiked ? likeIcon : unlikeIcon"
              class="like-img"
            />
          </button>
        </div>

        <div class="en">{{ props.country.name_en }}</div>
      </div>

      <button class="close-btn" @click="emit('close')">✕</button>
    </header>

    <!-- 탭 -->
    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['tab', { active: tab === currentTab }]"
        @click="currentTab = tab"
      >
        {{ tab }}
      </button>
    </nav>

    <!-- 뉴스 -->
    <div class="news-list" v-if="currentTab === '뉴스'">
      <div v-for="n in 4" :key="n" class="news-card">
        <div class="title">
          [안전] {{ props.country.name_ko }} 관련 최신 뉴스 {{ n }}
        </div>
        <div class="meta">2025-12-01 · 한국관광공사</div>
      </div>

      <div class="pagination">
        <span v-for="n in 6" :key="n" class="page">{{ n }}</span>
      </div>
    </div>

    <!-- 항공료 -->
    <section class="block">
      <h4>항공료</h4>
      <div class="line-between">
        <span>{{ props.country.name_ko }}</span>
        <span class="price">450,000 원</span>
      </div>
      <div class="change up">+5%</div>
    </section>

    <!-- 환율 -->
    <section class="block">
      <h4>환율</h4>
      <div class="line-between">
        <span>USD / KRW</span>
        <span class="price">1,350</span>
      </div>
      <div class="change up">+5%</div>
    </section>
  </aside>
</template>


<style scoped>
/* 패널 전체 */
.panel {
  width: 320px;
  background: #ffffff;
  box-shadow: -2px 0 20px rgba(0, 0, 0, 0.08);
  padding: 18px 24px 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-radius: 20px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

/* 헤더 */
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.country-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.country {
  font-weight: 700;
  font-size: 16px;
}

.en {
  font-size: 12px;
  color: #777;
}

/* ----------------------------------------------------- */
/* ❤️ 좋아요 이미지 버튼 */
/* ----------------------------------------------------- */
.like-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: #f2f2f7;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.2s, background 0.2s;
}

.like-btn:hover {
  transform: scale(1.1);
}

.like-btn.liked {
  background: #ffe3e8;
}

.like-img {
  width: 18px;
  height: 18px;
  pointer-events: none;
}

/* ----------------------------------------------------- */

.close-btn {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 20px;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background 0.2s;
}
.close-btn:hover {
  background: #f2f2f7;
}

/* 탭 */
.tabs {
  display: flex;
  gap: 8px;
}

.tab {
  flex: 1;
  padding: 8px 0;
  border-radius: 999px;
  border: none;
  background: #f2f2f7;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.25s, color 0.25s;
}

.tab.active {
  background: #333;
  color: #fff;
}

/* 뉴스 */
.news-list {
  flex: 1;
  overflow-y: auto;
}

.news-card {
  border-radius: 14px;
  background: #f8f8fa;
  padding: 10px 12px;
  margin-bottom: 10px;
  transition: transform 0.15s;
}
.news-card:hover {
  transform: translateY(-2px);
}

.news-card .title {
  font-size: 13px;
}

.meta {
  margin-top: 4px;
  font-size: 11px;
  color: #777;
}

/* 페이지 버튼 */
.pagination {
  text-align: center;
  margin-top: 8px;
}

.page {
  display: inline-block;
  margin: 0 3px;
  font-size: 11px;
  padding: 3px 6px;
  border-radius: 6px;
  transition: background 0.2s;
}
.page:hover {
  background: #eee;
}

/* 박스 */
.block {
  background: #f8f8fa;
  border-radius: 18px;
  padding: 12px 14px;
}

.block h4 {
  margin: 0 0 6px;
  font-size: 14px;
}

.line-between {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.price {
  font-weight: 600;
}

.change {
  font-size: 12px;
  margin-top: 2px;
}

.change.up {
  color: #1bbf4b;
}
</style>
