<template>
  <div class="page">
    <HeaderBar />
    <div class="center">
      <AiAssistant />
    </div>
  </div>
</template>

<script setup>
import HeaderBar from "@/components/common/HeaderBar.vue";
import AiAssistant from "@/components/ai/AiAssistant.vue";
</script>

<style scoped>
.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
