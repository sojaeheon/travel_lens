<template>
  <div class="auth-layout">
    <HeaderBar />

    <div class="auth-center">
      <div class="auth-box">
        <h2 class="title">Register</h2>

        <label class="field">
          <span>Name</span>
          <input v-model="name" type="text" />
        </label>

        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" />
        </label>

        <label class="field">
          <span>Password</span>
          <input v-model="password" type="password" />
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import HeaderBar from "@/components/common/HeaderBar.vue";
import { useUserStore } from "@/store/user";

const name = ref("");
const email = ref("");
const password = ref("");
const agree = ref(true);
const userStore = useUserStore();

const onSubmit = async () => {
  if (!agree.value) return alert("약관에 동의해주세요.");
  await userStore.register({ name: name.value, email: email.value, password: password.value });
};
</script>

<style scoped>
@import "@/styles/auth.css"; /* 스타일 공유하고 싶으면 공통 css로 빼도 됨 */
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
</style>
