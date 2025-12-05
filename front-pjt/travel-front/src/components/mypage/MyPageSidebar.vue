<template>
  <aside class="sidebar">
    <div class="logo">MY PAGE</div>
    <nav>
      <div
        class="item"
        :class="{ active: current === 'edit' }"
        @click="$emit('change', 'edit')"
      >
        회원정보 수정
      </div>
      <div
        class="item"
        :class="{ active: current === 'liked' }"
        @click="$emit('change', 'liked')"
      >
        내가 찜한 나라
      </div>
    </nav>
  </aside>
</template>

<script setup>
defineProps({ current: String });
</script>

<style scoped>
.sidebar {
  width: 220px;
  background: #fafafa;
  border-right: 1px solid #e5e5ea;
  padding: 24px 18px;
}
.logo {
  font-weight: 700;
  margin-bottom: 20px;
}
.item {
  padding: 10px 4px;
  cursor: pointer;
  font-size: 14px;
}
.item.active {
  font-weight: 600;
}
</style>
