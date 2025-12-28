<template>
  <div class="auth-layout">
    <HeaderBar />

    <div class="auth-center">
      <div class="auth-box">
        <h2 class="title">Register</h2>

        <label class="field">
          <span>Name</span>
          <input v-model="name" type="text" placeholder="이름 입력" />
        </label>

        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" placeholder="이메일 입력" />
        </label>

        <label class="field">
          <span>Password</span>
          <input
            v-model="password"
            type="password"
            placeholder="비밀번호 입력"
          />
        </label>

        <label class="agree">
          <input type="checkbox" v-model="agree" />
          <div>
            <div>[필수] 서비스 이용약관 동의</div>
            <div class="sub">
              이용약관, 개인정보(이름, 이메일)의 수집 및 이용에 대한 동의
            </div>
          </div>
        </label>

        <button class="submit-btn" @click="onSubmit">Register</button>

        <!-- 에러 메시지 -->
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <!-- 성공 메시지 -->
        <p v-if="successMessage" class="success-text">
          {{ successMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import HeaderBar from "@/components/common/HeaderBar.vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";

const name = ref("");
const email = ref("");
const password = ref("");
const agree = ref(true);

const errorMessage = ref("");
const successMessage = ref("");

const userStore = useUserStore();
const router = useRouter();

const onSubmit = async () => {
  errorMessage.value = "";
  successMessage.value = "";

  if (!agree.value) {
    return (errorMessage.value = "약관에 동의해주세요.");
  }

  if (!name.value || !email.value || !password.value) {
    return (errorMessage.value = "모든 필드를 입력해주세요.");
  }

  try {
    // 📌 회원가입 실행
    await userStore.register(email.value, name.value, password.value);

    successMessage.value = "회원가입 성공! 로그인 페이지로 이동합니다.";

    // 1.5초 후 이동
    setTimeout(() => router.push("/login"), 1500);
  } catch (err) {
    console.error(err);
    errorMessage.value = "회원가입 실패. 입력 정보를 확인해주세요.";
  }
};
</script>

<style scoped>
.auth-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.auth-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
.auth-box {
  width: 460px;
  border-radius: 16px;
  border: 1px solid #e5e5ea;
  padding: 32px 36px;
  background: #fff;
}
.title {
  margin-bottom: 24px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 18px;
  font-size: 14px;
}
.field input {
  border-radius: 8px;
  border: 1px solid #dedede;
  padding: 10px 11px;
  font-size: 14px;
}
.agree {
  display: flex;
  gap: 10px;
  font-size: 13px;
  margin-bottom: 16px;
}
.agree .sub {
  font-size: 12px;
  color: #777;
}
.submit-btn {
  width: 100%;
  border-radius: 8px;
  padding: 10px 0;
  border: none;
  background: #222;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  margin-top: 6px;
}

.error-text {
  margin-top: 12px;
  color: #e63946;
  font-size: 14px;
  text-align: center;
}

.success-text {
  margin-top: 12px;
  color: #2a9d8f;
  font-size: 14px;
  text-align: center;
}
</style>
