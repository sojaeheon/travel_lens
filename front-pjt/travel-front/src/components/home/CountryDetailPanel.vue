<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import likeIcon from "@/assets/like_btn.png";
import unlikeIcon from "@/assets/unlike_btn.png";
import { sendLog } from "@/api/log";
import { fetchFavoriteStatus as fetchFavoriteStatusApi } from "@/api/favorite";
import { fetchNewsByCountry, fetchBlogsByCountry } from "@/api/search";
import { fetchCountryInsight } from "@/api/insights";

/* ===============================
   props / emit
================================ */
const props = defineProps({
  country: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close"]);

/* ===============================
   탭 / 검색
================================ */
const tabs = ["뉴스", "블로그"];
const currentTab = ref("뉴스");

const searchQuery = ref(""); // 입력 중
const appliedQuery = ref(""); // 실제 검색어(엔터/버튼 시에만 반영)

/* ===============================
   로그인 여부
================================ */
const isAuthenticated = computed(() => !!localStorage.getItem("access_token"));

/* ===============================
   ISO2 코드
================================ */
const iso2 = computed(() => {
  const code = props.country.iso || "";
  return code.length === 2 ? code.toUpperCase() : code.slice(0, 2).toUpperCase();
});

/* ===============================
   ❤️ 좋아요
================================ */
const isLiked = ref(false);
const loadingLike = ref(false);

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

/* ===============================
   ⏱ 체류 시간 로그
================================ */
let enterTime = 0;

onMounted(async () => {
  enterTime = Date.now();

  sendLog({
    event_type: "country_detail_open",
    country_code: iso2.value,
  });

  await fetchFavoriteStatus();
  fetchContents(); // ✅ 첫 진입 시 뉴스/블로그 바로 로드
  fetchInsight(); // ✅ 첫 진입 시 항공/환율 바로 로드
});

onBeforeUnmount(() => {
  const durationSec = (Date.now() - enterTime) / 1000;

  sendLog({
    event_type: "country_detail_stay",
    country_code: iso2.value,
    value: Number(durationSec.toFixed(2)),
  });
});

/* ===============================
   ❤️ 좋아요 토글
================================ */
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
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("favorites-updated"));
    }
  } finally {
    loadingLike.value = false;
  }
};

/* ===============================
   🧭 항공료 / 환율 (DB)
================================ */
const insightLoading = ref(false);

const flightPrice = ref(null); // number | null
const flightChange = ref(null); // number | null  (delta)
const flightAirportName = ref(null); // ✅ 공항명
const flightAirportCode = ref(null); // ✅ IATA 코드

const fxPair = ref(null); // string | null
const fxRate = ref(null); // number | null
const fxChange = ref(null); // number | null  (delta)

const fetchInsight = async () => {
  if (!iso2.value) return;

  insightLoading.value = true;
  try {
    const res = await fetchCountryInsight(iso2.value);
    const data = res.data || {};

    // flight
    flightPrice.value = data?.flight?.price ?? null;
    flightChange.value = data?.flight?.change ?? null; // 없으면 null로 유지
    flightAirportName.value = data?.flight?.airport_name_ko ?? null;
    flightAirportCode.value = data?.flight?.airport_code_iata ?? null;

    // fx
    fxPair.value = data?.fx?.pair ?? null;
    fxRate.value = data?.fx?.rate ?? null;
    fxChange.value = data?.fx?.change ?? null; // 없으면 null로 유지
  } catch {
    flightPrice.value = null;
    flightChange.value = null;
    flightAirportName.value = null;
    flightAirportCode.value = null;

    fxPair.value = null;
    fxRate.value = null;
    fxChange.value = null;
  } finally {
    insightLoading.value = false;
  }
};

const isUp = (v) => typeof v === "number" && v >= 0;
const fmtDeltaKrw = (v) => {
  if (typeof v !== "number") return "-";
  const sign = v > 0 ? "+" : "";
  return `${sign}${new Intl.NumberFormat("ko-KR").format(v)} 원`;
};

const fmtDeltaFx = (v) => {
  if (typeof v !== "number") return "-";
  const sign = v > 0 ? "+" : "";
  return `${sign}${new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 4 }).format(v)}`;
};

const fmtKrw = (v) => {
  if (typeof v !== "number") return "-";
  return new Intl.NumberFormat("ko-KR").format(v) + " 원";
};

const fmtFx = (v) => {
  if (typeof v !== "number") return "-";
  return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 4 }).format(v);
};

/* ===============================
   📰 뉴스 / 블로그 데이터
================================ */
const contents = ref([]);
const loading = ref(false);

/* ===============================
   Pagination (10개 단위 + 번호 10개만 표시)
================================ */
const page = ref(1);
const pageSize = 10; // 한 페이지에 10개
const groupSize = 10; // 아래 번호 10개만 보여주기

const totalCount = ref(0);
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)));

const pageGroupStart = computed(() => Math.floor((page.value - 1) / groupSize) * groupSize + 1);
const pageGroupEnd = computed(() => Math.min(pageGroupStart.value + groupSize - 1, totalPages.value));

const pagesToShow = computed(() => {
  const arr = [];
  for (let p = pageGroupStart.value; p <= pageGroupEnd.value; p++) arr.push(p);
  return arr; // ✅ 최대 10개만
});

const goPage = (p) => {
  if (p < 1 || p > totalPages.value) return;
  page.value = p;
  fetchContents();
};
const goPrev = () => goPage(page.value - 1);
const goNext = () => goPage(page.value + 1);

const goPrevGroup = () => {
  if (pageGroupStart.value === 1) return;
  goPage(pageGroupStart.value - 1);
};
const goNextGroup = () => {
  if (pageGroupEnd.value === totalPages.value) return;
  goPage(pageGroupEnd.value + 1);
};

/* ===============================
   데이터 호출
================================ */
const fetchContents = async () => {
  if (!iso2.value) return;

  loading.value = true;

  try {
    const res =
      currentTab.value === "뉴스"
        ? await fetchNewsByCountry(iso2.value, appliedQuery.value, page.value, pageSize)
        : await fetchBlogsByCountry(iso2.value, appliedQuery.value, page.value, pageSize);

    contents.value = res.data.results || [];
    totalCount.value = res.data.count ?? 0;
  } catch {
    contents.value = [];
    totalCount.value = 0;
  } finally {
    loading.value = false;
  }
};

/* ===============================
   🔍 검색 실행 (엔터 / 버튼)
================================ */
const onSearch = () => {
  appliedQuery.value = searchQuery.value.trim();
  page.value = 1; // ✅ 검색하면 1페이지부터
  fetchContents();
};

/* ===============================
   탭/국가 변경 시: 검색 초기화 + 1페이지 + 바로 조회
================================ */
watch([iso2, currentTab], () => {
  searchQuery.value = "";
  appliedQuery.value = "";
  page.value = 1;
  fetchContents();
});

/* 나라 변경 시 좋아요/인사이트 재조회 */
watch(
  () => iso2.value,
  async () => {
    await fetchFavoriteStatus();
    fetchInsight(); // ✅ 나라 클릭마다 항공/환율 갱신
  }
);

/* ===============================
   카드 클릭 시 링크 이동 + 날짜 포맷
================================ */
const openLink = (url) => {
  if (!url) return;
  window.open(url, "_blank", "noopener,noreferrer");
};

const formatKstDateTime = (value) => {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);

  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`;
};
</script>

<template>
  <aside class="panel">
    <!-- 헤더 -->
    <header class="head">
      <div class="title-group">
        <div class="country-row">
          <div class="country">{{ props.country.name_ko }}</div>

          <button
            v-if="isAuthenticated"
            class="like-btn"
            :class="{ liked: isLiked }"
            :disabled="loadingLike"
            @click="toggleLike"
          >
            <img :src="isLiked ? likeIcon : unlikeIcon" class="like-img" />
          </button>
        </div>

        <div class="en">{{ props.country.name_en }}</div>
      </div>

      <button class="close-btn" @click="emit('close')">✕</button>
    </header>

    <!-- 검색 -->
    <div style="display: flex; gap: 6px">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="뉴스 · 블로그 검색"
        class="search-input"
        @keyup.enter="onSearch"
      />
      <button class="tab" style="flex: 0 0 60px" @click="onSearch">검색</button>
    </div>

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

    <!-- 뉴스 / 블로그 -->
    <div class="news-list">
      <div v-if="loading" class="pagination">불러오는 중...</div>

      <div
        v-for="item in contents"
        :key="item.id ?? item.url"
        class="news-card"
        @click="openLink(item.url)"
        style="cursor: pointer"
      >
        <div class="title">{{ item.title }}</div>
        <div class="meta">
          {{ formatKstDateTime(item.published_at) }}
        </div>
      </div>

      <div v-if="!loading && contents.length === 0" class="pagination">검색 결과가 없습니다</div>
    </div>

    <!-- 페이지네이션 -->
    <div class="pagination" v-if="totalPages > 1">
      <span
        class="page"
        @click="goPrevGroup"
        :style="pageGroupStart === 1 ? 'opacity:.4;pointer-events:none;' : ''"
        >«</span
      >
      <span class="page" @click="goPrev" :style="page === 1 ? 'opacity:.4;pointer-events:none;' : ''">‹</span>

      <span
        v-for="p in pagesToShow"
        :key="p"
        class="page"
        :style="p === page ? 'background:#333;color:#fff;' : ''"
        @click="goPage(p)"
      >
        {{ p }}
      </span>

      <span
        class="page"
        @click="goNext"
        :style="page === totalPages ? 'opacity:.4;pointer-events:none;' : ''"
        >›</span
      >
      <span
        class="page"
        @click="goNextGroup"
        :style="pageGroupEnd === totalPages ? 'opacity:.4;pointer-events:none;' : ''"
        >»</span
      >
    </div>

    <!-- 항공료 -->
    <section class="block">
      <h4>항공료</h4>
      <div class="line-between">
        <span>
          {{ props.country.name_ko }}
          <span v-if="flightAirportName" class="sub">
            · {{ flightAirportName }} ({{ flightAirportCode }})
          </span>
        </span>
        <span class="price"></span>
      </div>
      <div class="change">
        {{ insightLoading ? "" : fmtKrw(flightPrice) }}
      </div>
    </section>

    <!-- 환율 -->
    <section class="block">
      <h4>환율</h4>
      <div class="line-between">
        <span>{{ fxPair || "통화 / KRW" }}</span>
        <span class="price"></span>
      </div>
      <div class="change">
        {{ insightLoading ? "" : fmtFx(fxRate) }}
      </div>
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
  cursor: pointer;
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

/* ✅ 하락일 때 */
.change.down {
  color: #ff4d4f;
}

/* ✅ 공항 정보(작게) */
.sub {
  margin-left: 4px;
  font-size: 11px;
  color: #777;
}

.search-input {
  width: 100%;
  padding: 8px 14px;
  border-radius: 999px;
  border: none;
  background: #f2f2f7;
  font-size: 13px;
  outline: none;
}
.search-input:focus {
  background: #fff;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.08);
}
</style>
