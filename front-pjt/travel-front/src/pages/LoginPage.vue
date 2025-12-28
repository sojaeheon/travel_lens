<template>
  <div class="auth-layout">
    <HeaderBar />

    <div class="auth-center">
      <div class="auth-box">
        <h2 class="title">Sign In</h2>

        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" autocomplete="email" />
        </label>

        <label class="field">
          <span>Password</span>
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>

        <button class="submit-btn" @click="onSubmit">Sign In</button>

        <p class="helper">
          아직 계정이 없나요?
          <a @click.prevent="$router.push('/register')">회원가입</a>
        </p>

        <!-- 에러 메시지 -->
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import HeaderBar from "@/components/common/HeaderBar.vue";
import { useUserStore } from "@/store/user";

const email = ref("");
const password = ref("");
const errorMessage = ref("");

const userStore = useUserStore();
const router = useRouter();

// 로그인 실행
const onSubmit = async () => {
  errorMessage.value = "";

  try {
    await userStore.login(email.value, password.value);

    // 로그인 성공 → 홈 화면 이동
    router.push("/home");
  } catch (err) {
    errorMessage.value = "로그인에 실패했습니다. 이메일 또는 비밀번호를 확인해주세요.";
    console.error(err);
  }
};
</script>

<style scoped>
@import "@/styles/auth.css";

.error-text {
  color: #ff4d4f;
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
}
</style>
