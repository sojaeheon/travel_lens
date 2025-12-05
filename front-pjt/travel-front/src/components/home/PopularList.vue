<template>
  <section class="panel">
    <h3 class="title">인기 여행지 리스트</h3>

    <div
      v-for="(item, idx) in popular"
      :key="item.country"
      class="card"
    >
      <div class="rank">#{{ idx + 1 }}</div>
      <div class="info">
        <div class="country">{{ item.country }}</div>
        <div class="city">{{ item.city }}</div>
        <div class="price-row">
          <span class="label">최대항공료</span>
          <span class="price">{{ item.price.toLocaleString() }}원</span>
          <span class="rate" :class="{ up: item.change > 0 }">
            {{ item.change > 0 ? "+" : "" }}{{ item.change }}%
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const popular = [
  { country: "대한민국", city: "서울", price: 450000, change: 5 },
  { country: "일본", city: "도쿄", price: 380000, change: 3 },
  { country: "프랑스", city: "파리", price: 950000, change: 2 },
  { country: "미국", city: "뉴욕", price: 1050000, change: -1 },
];
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
.city {
  font-size: 12px;
  color: #777;
}
.price-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.label {
  color: #999;
}
.price {
  font-weight: 600;
}
.rate.up {
  color: #1bbf4b;
}
</style>
