<template>
  <section class="panel">
    <h3 class="title">인기 여행지 TOP 10</h3>

    <div v-if="loading" class="empty">불러오는 중...</div>
    <div v-else-if="popular.length === 0" class="empty">데이터가 없습니다</div>

    <div
      v-else
      v-for="(item, idx) in popular"
      :key="item.iso2"
      class="card"
      @click="handleSelect(item)"
    >
      <div class="rank">#{{ idx + 1 }}</div>
      <div class="info">
        <div class="country">
          {{ item.name_ko }}
          <span class="iso">({{ item.iso2 }})</span>
        </div>
        <div class="meta">인기 점수: {{ formatScore(item.score) }}</div>
        <div class="meta">
          좋아요 {{ formatCount(item.favorite_count) }} · 조회 {{ formatCount(item.view_count) }}
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { fetchPopularCountries } from "@/api/popular";

const emit = defineEmits(["select-country"]);

const popular = ref([]);
const loading = ref(true);

const formatScore = (value) => {
  if (typeof value !== "number") return "-";
  return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 1 }).format(value);
};

const formatCount = (value) => {
  if (typeof value !== "number") return "-";
  return new Intl.NumberFormat("ko-KR").format(value);
};

const loadPopular = async () => {
  loading.value = true;
  try {
    const res = await fetchPopularCountries(10);
    popular.value = res.data?.results || [];
  } catch {
    popular.value = [];
  } finally {
    loading.value = false;
  }
};

const handleSelect = (item) => {
  emit("select-country", {
    iso2: item.iso2,
    name_ko: item.name_ko,
    name_en: item.name_en,
  });
};

onMounted(loadPopular);
</script>

<style scoped>
.panel {
  background: #fff;
  border-radius: 16px;
  padding: 18px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  margin-bottom: 16px;
}
.title {
  font-size: 15px;
  margin-bottom: 10px;
}
.card {
  display: flex;
  gap: 10px;
  padding: 8px 6px;
  border-radius: 12px;
  background: #fafafa;
  margin-bottom: 6px;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s, box-shadow 0.15s;
}
.card:hover {
  background: #f2f2f2;
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.06);
}
.rank {
  font-size: 14px;
  font-weight: 600;
}
.info {
  flex: 1;
}
.country {
  font-weight: 600;
}
.iso {
  margin-left: 4px;
  font-size: 12px;
  color: #777;
}
.meta {
  font-size: 12px;
  color: #666;
}
.empty {
  font-size: 12px;
  color: #777;
  padding: 8px 4px;
}
</style>
