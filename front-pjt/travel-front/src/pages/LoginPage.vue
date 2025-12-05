<template>
  <div class="auth-layout">
    <HeaderBar />

    <div class="auth-center">
      <div class="auth-box">
        <h2 class="title">Sign In</h2>

        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" />
        </label>

        <label class="field">
          <span>Password</span>
          <input v-model="password" type="password" />
        </label>

        <button class="submit-btn" @click="onSubmit">Sign In</button>

        <p class="helper">
          아직 계정이 없나요?
          <a @click.prevent="$router.push('/register')">회원가입</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import HeaderBar from "@/components/common/HeaderBar.vue";
import { useUserStore } from "@/store/user";

const email = ref("");
const password = ref("");
const userStore = useUserStore();

const onSubmit = async () => {
  await userStore.login(email.value, password.value);
};
</script>

<style scoped>
@import "@/styles/auth.css";
</style>
