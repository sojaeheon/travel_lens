<template>
  <div class="page">
    <HeaderBar />
    <div class="body">
      <MyPageSidebar :current="current" @change="current = $event" />

      <EditProfile v-if="current === 'edit'" />
      <MyLikedCountries v-else />
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import HeaderBar from "@/components/common/HeaderBar.vue";
import MyPageSidebar from "@/components/mypage/MyPageSidebar.vue";
import EditProfile from "@/components/mypage/EditProfile.vue";
import MyLikedCountries from "@/components/mypage/MyLikedCountries.vue";

const current = ref("edit");
</script>

<style scoped>
.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.body {
  flex: 1;
  display: flex;
}
</style>
