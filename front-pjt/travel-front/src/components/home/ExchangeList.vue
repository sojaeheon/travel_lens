<template>
  <section class="panel">
    <h3 class="title">주요 환율</h3>

    <div v-if="loading" class="empty">불러오는 중...</div>
    <div v-else-if="rates.length === 0" class="empty">데이터가 없습니다</div>

    <div
      v-else
      v-for="(item, idx) in rates"
      :key="item.iso2"
      class="card"
      @click="handleSelect(item)"
    >
      <div class="rank">#{{ idx + 1 }}</div>
      <div class="info">
        <div class="country">
          {{ item.name_ko }}
          <span class="code">{{ item.currency_code }}</span>
        </div>
        <div class="line">
          <span class="value">{{ formatRate(item.rate) }} KRW</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { fetchExchangeRates } from "@/api/exchange";

const emit = defineEmits(["select-country"]);

const rates = ref([]);
const loading = ref(true);

const formatRate = (value) => {
  if (typeof value !== "number") return "-";
  return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 4 }).format(value);
};

const loadRates = async () => {
  loading.value = true;
  try {
    const res = await fetchExchangeRates(10);
    rates.value = res.data?.results || [];
  } catch {
    rates.value = [];
  } finally {
    loading.value = false;
  }
};

const handleSelect = (item) => {
  emit("select-country", {
    iso2: item.iso2,
    name_ko: item.name_ko,
  });
};

onMounted(loadRates);
</script>

<style scoped>
.panel {
  background: #fff;
  border-radius: 16px;
  padding: 18px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
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
.code {
  margin-left: 6px;
  font-size: 12px;
  color: #777;
}
.line {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.value {
  font-weight: 600;
}
.empty {
  font-size: 12px;
  color: #777;
  padding: 8px 4px;
}
</style>
