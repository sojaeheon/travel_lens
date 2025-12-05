<template>
  <section class="panel">
    <h3 class="title">환율</h3>

    <div v-for="(item, idx) in rates" :key="item.country" class="card">
      <div class="rank">#{{ idx + 1 }}</div>
      <div class="info">
        <div class="country">{{ item.country }}</div>
        <div class="line">
          <span class="code">{{ item.code }}</span>
          <span class="value">{{ item.value }}</span>
          <span class="change" :class="{ up: item.diff > 0 }">
            {{ item.diff > 0 ? "+" : "" }}{{ item.diff }}%
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const rates = [
  { country: "미국", code: "KRW", value: 1350, diff: 5 },
  { country: "일본", code: "KRW", value: 890, diff: 3 },
  { country: "유럽연합", code: "KRW", value: 1450, diff: 2 },
];
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
}
.rank {
  font-size: 14px;
  font-weight: 600;
}
.country {
  font-weight: 600;
}
.line {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.code {
  color: #777;
}
.change.up {
  color: #1bbf4b;
}
</style>
