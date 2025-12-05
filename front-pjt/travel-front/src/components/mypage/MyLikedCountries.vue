<template>
  <div class="wrap">
    <h2>내가 찜한 나라</h2>

    <div class="grid">
      <div v-for="c in cards" :key="c.name" class="card">
        <img src="/src/assets/sample-city.jpg" alt="" />
        <div class="text-top">{{ c.en }}</div>
        <div class="text-bottom">{{ c.name }}</div>
        <button class="heart">♥</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const cards = [
  { name: "파리", en: "FRANCE" },
  { name: "도쿄", en: "JAPAN" },
  { name: "뉴욕", en: "USA" },
  { name: "바르셀로나", en: "SPAIN" },
];
</script>

<style scoped>
.wrap {
  padding: 40px 60px;
}
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
}
.card img {
  width: 100%;
  height: 160px;
  object-fit: cover;
}
.text-top {
  position: absolute;
  top: 12px;
  left: 16px;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}
.text-bottom {
  position: absolute;
  top: 32px;
  left: 16px;
  font-size: 13px;
  color: #fff;
}
.heart {
  position: absolute;
  top: 10px;
  right: 10px;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(0, 0, 0, 0.4);
  color: #fff;
  cursor: pointer;
}
</style>
