<template>
  <div class="chat-overlay" @click.self="$emit('close')">
    <div class="chat-card">
      <div class="chat-header">
        <div class="header-info">
          <h3>실시간 채팅방</h3>
          <p>현재 접속 중</p>
        </div>
        <button class="x-btn" @click="$emit('close')">X</button>
      </div>

      <div class="chat-tabs">
        <button :class="{ active: activeTab==='chat' }" @click="activeTab='chat'">💬 채팅</button>
        <button :class="{ active: activeTab==='wordcloud' }" @click="activeTab='wordcloud'">🔤 인기 키워드</button>
      </div>

      <div v-if="activeTab==='chat'" class="chat-body" ref="scrollBox">
        <template v-for="(msg, idx) in messageList" :key="idx">
          <div v-if="shouldShowDateDivider(idx)" class="date-divider">
            <span>{{ formatDate(msg.created_at) }}</span>
          </div>

          <div :class="['msg-group', msg.sender_email === currentUserEmail ? 'my' : 'other']">
            <span class="sender-name">{{ extractUsername(msg.sender_email) }}</span>
            <div class="bubble-row">
              <div class="bubble">{{ msg.content || msg.message }}</div>
              <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
            </div>
          </div>
        </template>
      </div>
      <div v-else class="wordcloud-body">
        <WordCloud :messageList="messageList" />
      </div>

      <div class="chat-footer">
        <template v-if="isLoggedIn">
          <input v-model="newMsg" @keyup.enter="sendMessage" placeholder="메시지를 입력하세요..." />
          <button class="send-btn" @click="sendMessage" :disabled="!newMsg.trim()">
            <svg viewBox="0 0 24 24" width="22" height="22">
              <path fill="white" d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
            </svg>
          </button>
        </template>
        
        <div v-else class="login-prompt">
          <span>채팅을 하려면 로그인이 필요합니다.</span>
          <button @click="goToLogin" class="login-redirect-btn">로그인하러 가기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// ... 기존 import 생략 ...
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import WordCloud from './WordCloud.vue';

const router = useRouter();
const emit = defineEmits(['close']);
const messageList = ref([]);
const newMsg = ref('');
const scrollBox = ref(null);
const activeTab = ref('chat');

// ... 기존 로직 유지 ...

// 2. 날짜 구분선 로직 추가
const shouldShowDateDivider = (idx) => {
  if (idx === 0) return true; // 첫 번째 메시지는 무조건 표시
  const prevDate = new Date(messageList.value[idx - 1].created_at).toDateString();
  const currDate = new Date(messageList.value[idx].created_at).toDateString();
  return prevDate !== currDate;
};

const formatDate = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleDateString('ko-KR', { 
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' 
  });
};

const formatTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  // 오전/오후 형식을 유지하면서 시간 표시
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: true });
};

// ... 기존 loadChatHistory, connectSocket, sendMessage 등 유지 ...
const isLoggedIn = computed(() => {
  const token = localStorage.getItem('access_token');
  return token && token !== 'null';
});

const currentUserEmail = ref(localStorage.getItem('user_email'));
let socket = null;

const extractUsername = (email) => email?.split('@')[0] || '익명 사용자';

const goToLogin = () => {
  emit('close');
  router.push('/login');
};

const loadChatHistory = async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/chat/history/');
    const messages = res.data.results || res.data || [];
    // API 데이터가 보통 최신순(역순)으로 오므로, 시간순 정렬이 필요할 수 있습니다.
    messageList.value = messages.reverse().map(msg => ({
      id: msg.id,
      content: msg.content || msg.message,
      sender_nickname: msg.sender_nickname || msg.user || '익명',
      sender_email: msg.sender_email || msg.email || 'anonymous',
      created_at: msg.created_at
    })).reverse(); // 데이터가 최신순으로 온다면 reverse()로 시간순 정렬
  } catch (err) {
    console.error("히스토리 로드 실패:", err);
  }
};

const connectSocket = () => {
  const token = localStorage.getItem('access_token');
  socket = new WebSocket(`ws://localhost:8000/ws/chat/global/?token=${token}`);
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    messageList.value.push({
      content: data.message || data.content,
      sender_nickname: data.user || data.sender_nickname || '익명',
      sender_email: data.sender_email || data.email || 'anonymous',
      created_at: data.created_at || new Date().toISOString()
    });
    scrollToBottom();
  };
};

const sendMessage = () => {
  if (socket && newMsg.value.trim()) {
    socket.send(JSON.stringify({ message: newMsg.value }));
    newMsg.value = '';
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollBox.value) scrollBox.value.scrollTop = scrollBox.value.scrollHeight;
  });
};

onMounted(async () => {
  await loadChatHistory();
  connectSocket();
  scrollToBottom();
});

onUnmounted(() => {
  if (socket) socket.close();
});
</script>

<style scoped>
/* ... 기존 스타일 유지 ... */
.chat-overlay { position: fixed; top:0; left:0; width:100vw; height:100vh; background: rgba(0,0,0,0.3); display:flex; justify-content:center; align-items:center; z-index:9999; }
.chat-card { width:480px; height:650px; background:white; border-radius:28px; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 15px 50px rgba(0,0,0,0.3); }
.chat-header { padding:20px 25px; display:flex; justify-content:space-between; border-bottom:1px solid #eee; }
.header-info h3 { margin:0; font-size:18px; color:#333; }
.header-info p { margin:4px 0 0; font-size:12px; color:#888; }
.x-btn { background:#f1f3f5; border:none; width:36px; height:36px; border-radius:50%; cursor:pointer; display:flex; justify-content:center; align-items:center; }
.chat-tabs { display:flex; border-bottom:1px solid #eee; }
.chat-tabs button { flex:1; padding:10px; border:none; cursor:pointer; background:#f9f9f9; border-bottom: 2px solid transparent; }
.chat-tabs button.active { font-weight:bold; background:#fff; border-bottom: 2px solid #007bff; }
.chat-body { flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; }
.msg-group { margin-bottom:15px; display:flex; flex-direction:column; }
.my { align-items:flex-end; }
.other { align-items:flex-start; }
.sender-name { font-size:12px; color:#777; margin-bottom:4px; }
.bubble-row { display:flex; align-items:flex-end; gap:8px; max-width:80%; }
.my .bubble-row { flex-direction:row-reverse; }
.bubble { padding:10px 16px; border-radius:18px; font-size:14px; line-height:1.5; }
.my .bubble { background:#007bff; color:white; border-bottom-right-radius:4px; }
.other .bubble { background:#f1f3f5; color:#333; border-bottom-left-radius:4px; }
.msg-time { font-size:10px; color:#bbb; white-space:nowrap; }
.chat-footer { padding:15px 20px; display:flex; gap:10px; align-items:center; border-top:1px solid #eee; min-height: 80px; }
.chat-footer input { flex:1; background:#f1f3f5; border:none; padding:12px 18px; border-radius:25px; outline:none; }
.send-btn { background:#007bff; border:none; width:44px; height:44px; border-radius:14px; cursor:pointer; display:flex; justify-content:center; align-items:center; color:white; }
.wordcloud-body { flex:1; display:flex; justify-content:center; align-items:center; padding:20px; }

/* 3. 날짜 구분선 스타일 추가 */
.date-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
  position: relative;
}
.date-divider::before {
  content: "";
  position: absolute;
  width: 100%;
  height: 1px;
  background-color: #eee;
  z-index: 1;
}
.date-divider span {
  background: white;
  padding: 0 15px;
  font-size: 11px;
  color: #999;
  z-index: 2;
  border-radius: 10px;
}

.login-prompt { flex:1; display:flex; justify-content:space-between; align-items:center; }
.login-prompt span { font-size: 13px; color: #666; }
.login-redirect-btn { background:#007bff; color:white; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-weight:bold; }
</style>