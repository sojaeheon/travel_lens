<template>
  <div class="chat-overlay" @click.self="$emit('close')">
    <div class="chat-card">
      <div class="chat-header">
        <div class="header-info">
          <h3>실시간 채팅방</h3>
          <p>현재 24명 접속 중</p>
        </div>
        <button class="x-btn" @click="$emit('close')">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="chat-body" ref="scrollBox">
        <div v-for="(msg, idx) in messageList" :key="idx" 
             :class="['msg-group', msg.sender_email === currentUserEmail ? 'my' : 'other']">
          <span class="sender-name">{{ msg.sender_nickname }}</span>
          <div class="bubble-row">
            <div class="bubble">{{ msg.content }}</div>
            <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="chat-footer">
        <input v-model="newMsg" @keyup.enter="sendMessage" placeholder="메시지를 입력하세요..." />
        <button class="send-btn" @click="sendMessage" :disabled="!newMsg.trim()">
          <svg viewBox="0 0 24 24" width="22" height="22"><path fill="white" d="M2,21L23,12L2,3V10L17,12L2,14V21Z" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import axios from 'axios';

const emit = defineEmits(['close']);
const messageList = ref([]);
const newMsg = ref('');
const scrollBox = ref(null);
const currentUserEmail = ref(localStorage.getItem('user_email'));
let socket = null;

const connectSocket = () => {
  const token = localStorage.getItem('access_token');
  socket = new WebSocket(`ws://localhost:8000/ws/chat/global/?token=${token}`);
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    messageList.value.push({
      content: data.message,
      sender_nickname: data.user,
      sender_email: data.email,
      created_at: new Date().toISOString()
    });
    scrollToBottom();
  };
};

const sendMessage = () => {
  if (socket && newMsg.value.trim()) {
    socket.send(JSON.stringify({ 'message': newMsg.value }));
    newMsg.value = '';
  }
};

const scrollToBottom = () => {
  nextTick(() => { if (scrollBox.value) scrollBox.value.scrollTop = scrollBox.value.scrollHeight; });
};

const formatTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/chat/history/');
    messageList.value = res.data.results ? res.data.results.reverse() : res.data.reverse();
  } catch (err) { console.error("History Load Error:", err); }
  connectSocket();
  scrollToBottom();
});

onUnmounted(() => { if (socket) socket.close(); });
</script>

<style scoped>
.chat-overlay {
  position: fixed; /* 뷰포트 전체 고정 */
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.3); /* 배경 어둡게 & 지도 비침 */
  display: flex; justify-content: center; align-items: center;
  z-index: 9999; /* 모든 요소보다 위에 표시 */
}

.chat-card {
  width: 480px; height: 650px; background: white; border-radius: 28px;
  display: flex; flex-direction: column; box-shadow: 0 15px 50px rgba(0,0,0,0.3);
  overflow: hidden;
}

.chat-header { padding: 20px 25px; display: flex; justify-content: space-between; border-bottom: 1px solid #eee; }
.header-info h3 { margin: 0; font-size: 18px; color: #333; }
.header-info p { margin: 4px 0 0; font-size: 12px; color: #888; }

.x-btn {
  background: #f1f3f5; border: none; width: 36px; height: 36px; border-radius: 50%;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}

.chat-body { flex: 1; overflow-y: auto; padding: 20px; background: #fff; display: flex; flex-direction: column; }
.msg-group { margin-bottom: 15px; display: flex; flex-direction: column; }
.my { align-items: flex-end; }
.other { align-items: flex-start; }

.sender-name { font-size: 12px; color: #777; margin-bottom: 4px; }
.bubble-row { display: flex; align-items: flex-end; gap: 8px; max-width: 80%; }
.my .bubble-row { flex-direction: row-reverse; }

.bubble { padding: 10px 16px; border-radius: 18px; font-size: 14px; line-height: 1.5; }
.my .bubble { background: #007bff; color: white; border-bottom-right-radius: 4px; }
.other .bubble { background: #f1f3f5; color: #333; border-bottom-left-radius: 4px; }

.msg-time { font-size: 10px; color: #bbb; white-space: nowrap; }

.chat-footer { padding: 15px 20px; display: flex; gap: 10px; align-items: center; border-top: 1px solid #eee; }
.chat-footer input { flex: 1; background: #f1f3f5; border: none; padding: 12px 18px; border-radius: 25px; outline: none; }
.send-btn { background: #007bff; border: none; width: 44px; height: 44px; border-radius: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
</style>