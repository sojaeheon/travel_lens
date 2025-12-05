<template>
  <div class="ai-panel">
    <header class="head">
      <div class="title">AI 여행 어시스턴트</div>
      <button class="close" @click="$emit('close')">✕</button>
    </header>

    <div class="body">
      <div class="msg bot">
        안녕하세요! 여행지 추천 AI 에이전트입니다. 어떤 여행지를 찾으시나요?
      </div>
      <div
        v-for="(m, i) in messages"
        :key="i"
        :class="['msg', m.role]"
      >
        {{ m.content }}
      </div>
    </div>

    <div class="input-wrap">
      <input
        v-model="question"
        type="text"
        placeholder="여행지를 물어보세요..."
        @keyup.enter="ask"
      />
      <button @click="ask">📤</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const messages = ref([]);
const question = ref("");

const ask = () => {
  if (!question.value.trim()) return;
  const q = question.value;
  messages.value.push({ role: "user", content: q });
  // 실제로는 백엔드/LLM 호출
  messages.value.push({
    role: "bot",
    content: `예시 응답) "${q}"에 어울리는 추천 여행지는 일본 도쿄입니다.`,
  });
  question.value = "";
};
</script>

<style scoped>
.ai-panel {
  width: 480px;
  height: 480px;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}
.head {
  padding: 14px 16px;
  border-bottom: 1px solid #e5e5ea;
  display: flex;
  justify-content: space-between;
}
.title {
  font-weight: 600;
}
.close {
  border: none;
  background: none;
  cursor: pointer;
}
.body {
  flex: 1;
  padding: 10px 12px;
  overflow-y: auto;
  background: #f5f5f7;
  font-size: 13px;
}
.msg {
  margin-bottom: 8px;
  padding: 8px 10px;
  border-radius: 12px;
  max-width: 80%;
}
.msg.bot {
  background: #e5f2ff;
}
.msg.user {
  margin-left: auto;
  background: #fff;
}
.input-wrap {
  display: flex;
  border-top: 1px solid #e5e5ea;
}
input {
  flex: 1;
  border: none;
  padding: 10px 12px;
  font-size: 13px;
}
button {
  width: 48px;
  border: none;
  background: #007aff;
  color: #fff;
  cursor: pointer;
}
</style>
