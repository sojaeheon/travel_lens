<template>
  <aside class="panel">
    <header class="head">
      <div>
        <div class="country">대한민국 ♡</div>
        <div class="en">KOREA</div>
      </div>
      <button class="close-btn" @click="$emit('close')">✕</button>
    </header>

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

    <!-- 뉴스 리스트 -->
    <div class="news-list" v-if="currentTab === '뉴스'">
      <div v-for="n in 4" :key="n" class="news-card">
        <div class="title">[안전] 한국 여행 관련 최신 뉴스 제목 {{ n }}</div>
        <div class="meta">2025-12-01 · 한국관광공사</div>
      </div>
      <div class="pagination">
        <span v-for="n in 6" :key="n" class="page">{{ n }}</span>
      </div>
    </div>

    <!-- 항공료 / 환율 블록 -->
    <section class="block">
      <h4>항공료</h4>
      <div class="line-between">
        <span>대한민국</span>
        <span class="price">450,000 원</span>
      </div>
      <div class="change up">+5%</div>
    </section>

    <section class="block">
      <h4>환율</h4>
      <div class="line-between">
        <span>미국 / KRW</span>
        <span class="price">1,350</span>
      </div>
      <div class="change up">+5%</div>
    </section>
  </aside>
</template>

<script setup>
import { ref } from "vue";

const tabs = ["뉴스", "블로그", "출입국"];
const currentTab = ref("뉴스");
</script>

<style scoped>
.panel {
  width: 320px;
  background: #ffffff;
  height: calc(100vh - 72px);
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.country {
  font-weight: 700;
}
.en {
  font-size: 12px;
  color: #777;
}
.close-btn {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 18px;
}
.tabs {
  display: flex;
  gap: 8px;
}
.tab {
  flex: 1;
  padding: 6px 0;
  border-radius: 999px;
  border: none;
  background: #f2f2f7;
  font-size: 13px;
  cursor: pointer;
}
.tab.active {
  background: #333;
  color: #fff;
}
.news-list {
  flex: 1;
  overflow-y: auto;
}
.news-card {
  border-radius: 10px;
  background: #f8f8fa;
  padding: 8px 10px;
  margin-bottom: 8px;
}
.news-card .title {
  font-size: 13px;
}
.meta {
  margin-top: 4px;
  font-size: 11px;
  color: #777;
}
.pagination {
  text-align: center;
  margin-top: 8px;
}
.page {
  display: inline-block;
  margin: 0 3px;
  font-size: 11px;
}
.block {
  background: #f8f8fa;
  border-radius: 16px;
  padding: 10px 12px;
}
.block h4 {
  margin: 0 0 6px;
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
