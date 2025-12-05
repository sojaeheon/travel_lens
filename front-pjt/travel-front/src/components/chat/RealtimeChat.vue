<template>
  <div class="chat-panel">
    <header class="head">
      <div>
        <div class="title">실시간 채팅방</div>
        <div class="sub">현재 24명 접속 중</div>
      </div>
    </header>

    <div class="body">
      <ChatMessage
        v-for="(msg, i) in messages"
        :key="i"
        :message="msg"
        :isMine="msg.sender === '나'"
      />
    </div>

    <ChatInput v-model="text" @send="sendMessage" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import ChatMessage from "./ChatMessage.vue";
import ChatInput from "./ChatInput.vue";

const messages = ref([
  { sender: "여행러버", text: "다음 주에 일본 가는데 추천 장소 있나요?", time: "오후 02:51" },
  { sender: "새벽항공", text: "도쿄 아사쿠사 추천해요! 센소지 절이 정말 멋져요", time: "오후 02:52" },
  { sender: "배낭여행", text: "유럽 여행 계획 중인데 환율이 걱정되네요", time: "오후 02:53" },
]);

const text = ref("");

const sendMessage = (value) => {
  messages.value.push({
    sender: "나",
    text: value,
    time: "오후 03:00",
  });
};
</script>

<style scoped>
.chat-panel {
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
}
.title {
  font-weight: 600;
}
.sub {
  font-size: 11px;
  color: #777;
}
.body {
  flex: 1;
  padding: 10px 12px;
  overflow-y: auto;
  background: #f5f5f7;
}
</style>
