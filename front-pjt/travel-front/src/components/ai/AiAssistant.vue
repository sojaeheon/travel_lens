<template>
  <div class="ai-panel">
    <header class="head">
      <div class="title">트레비</div>
      <button class="close" @click="$emit('close')" aria-label="닫기">
        <span aria-hidden="true">×</span>
      </button>
    </header>

    <div class="body">
      <aside class="sidebar">
        <div class="sidebar-title">Conversations</div>
        <div class="sidebar-actions">
          <button class="new-chat" @click="startNewConversation">New</button>
          <button class="clear-chat" @click="clearAllConversations">Clear</button>
        </div>
        <div class="conversation-list">
          <button
            v-for="convo in conversations"
            :key="convo.id"
            :class="['conversation-item', { active: convo.id === conversationId }]"
            @click="selectConversation(convo.id)"
          >
            #{{ convo.id }}
            <span class="conversation-date">{{ formatDate(convo.last_message_at) }}</span>
            <span class="conversation-preview">{{ convo.preview }}</span>
            <span
              class="conversation-delete"
              role="button"
              aria-label="대화 삭제"
              @click.stop="deleteConversation(convo.id)"
            >
              ×
            </span>
          </button>
        </div>
      </aside>

      <section class="chat">
        <div class="chat-messages">
          <div class="msg bot">
            안녕하세요! 여행지, 가격, 안전, 트렌드를 물어보세요.
          </div>
          <div
            v-for="(m, i) in messages"
            :key="i"
            :class="['msg', m.role]"
          >
            <div class="msg-text">{{ m.content }}</div>
            <div v-if="m.role === 'bot' && m.context" class="context">
            <div v-if="m.context.alert" class="context-block">
              <div class="context-title">Travel Alert</div>
              <div class="context-item">
                Level: {{ m.context.alert.alarm_level }}
              </div>
              <div class="context-item">
                Region: {{ m.context.alert.region }}
              </div>
            </div>

            <div v-if="m.context.fx" class="context-block">
              <div class="context-title">Exchange Rate</div>
              <div class="context-item">
                {{ m.context.fx.currency_code }} / KRW: {{ m.context.fx.rate }}
              </div>
              <div class="context-item">
                Change: {{ formatChange(m.context.fx.change) }}
              </div>
              <div class="context-item">
                Date: {{ m.context.fx.recorded_date }}
              </div>
            </div>

            <div v-if="m.context.flight" class="context-block">
              <div class="context-title">Flight Price</div>
              <div class="context-item">
                {{ m.context.flight.airport_name_ko }} ({{ m.context.flight.airport_code_iata }})
              </div>
              <div class="context-item">
                Price: {{ m.context.flight.price }} KRW
              </div>
              <div class="context-item">
                Change: {{ formatChange(m.context.flight.change, ' KRW') }}
              </div>
              <div class="context-item">
                Date: {{ m.context.flight.recorded_date }}
              </div>
            </div>

            <div v-if="m.context.news && m.context.news.length" class="context-block">
              <div class="context-title">News</div>
              <a
                v-for="news in m.context.news"
                :key="news.id || news.url"
                class="context-link"
                :href="news.url"
                target="_blank"
                rel="noreferrer"
              >
                {{ news.title }}
              </a>
            </div>

            <div v-if="m.context.blogs && m.context.blogs.length" class="context-block">
              <div class="context-title">Blogs</div>
              <a
                v-for="blog in m.context.blogs"
                :key="blog.id || blog.url"
                class="context-link"
                :href="blog.url"
                target="_blank"
                rel="noreferrer"
              >
                {{ blog.title }}
              </a>
            </div>
          </div>
        </div>
        </div>
      </section>
    </div>

    <div class="input-wrap">
      <input
        v-model="question"
        type="text"
        placeholder="여행지나 여행 계획을 물어보세요..."
        @keyup.enter="ask"
        :disabled="isLoading"
      />
      <button @click="ask" :disabled="isLoading">전송</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import {
  clearChatConversations,
  deleteChatConversation,
  fetchChatConversations,
  fetchChatHistory,
  queryChatbot,
} from "@/api/chatbot";

const messages = ref([]);
const question = ref("");
const conversationId = ref(null);
const isLoading = ref(false);
const conversations = ref([]);

const formatChange = (value, suffix = "") => {
  if (value === null || value === undefined) return "N/A";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value}${suffix}`;
};

const formatDate = (value) => {
  if (!value) return "";
  return new Date(value).toLocaleString();
};

const ask = async () => {
  if (!question.value.trim() || isLoading.value) return;
  const q = question.value.trim();
  question.value = "";
  messages.value.push({ role: "user", content: q });
  isLoading.value = true;

  try {
    const response = await queryChatbot({
      message: q,
      conversationId: conversationId.value,
    });
    const data = response.data || {};
    if (data.conversation_id) {
      conversationId.value = data.conversation_id;
    }
    messages.value.push({
      role: "bot",
      content: data.answer || "No response available.",
      context: data.context || null,
    });
    await loadConversations();
  } catch (error) {
    messages.value.push({
      role: "bot",
      content: "Request failed. Please try again.",
    });
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const loadHistory = async (id) => {
  try {
    const response = await fetchChatHistory({
      conversationId: id,
    });
    const data = response.data || {};
    if (data.conversation_id) {
      conversationId.value = data.conversation_id;
    }
    if (Array.isArray(data.messages) && data.messages.length) {
      messages.value = data.messages.map((msg) => ({
        role: msg.role === "assistant" ? "bot" : msg.role,
        content: msg.content,
        context: msg.context || null,
      }));
    }
  } catch (error) {
    console.error(error);
  }
};

const loadConversations = async () => {
  try {
    const response = await fetchChatConversations();
    const data = response.data || {};
    conversations.value = Array.isArray(data.results) ? data.results : [];
  } catch (error) {
    conversations.value = [];
    console.error(error);
  }
};

const selectConversation = async (id) => {
  await loadHistory(id);
};

const startNewConversation = () => {
  conversationId.value = null;
  messages.value = [];
};

const deleteConversation = async (id) => {
  try {
    await deleteChatConversation(id);
    if (conversationId.value === id) {
      conversationId.value = null;
      messages.value = [];
    }
    await loadConversations();
  } catch (error) {
    console.error(error);
  }
};

const clearAllConversations = async () => {
  try {
    await clearChatConversations();
    conversationId.value = null;
    messages.value = [];
    await loadConversations();
  } catch (error) {
    console.error(error);
  }
};

onMounted(() => {
  loadConversations();
  loadHistory();
});
</script>

<style scoped>
.ai-panel {
  width: 640px;
  height: 560px;
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
  font-size: 16px;
}
.close {
  border: 1px solid #d1d5db;
  background: #ffffff;
  border-radius: 999px;
  width: 28px;
  height: 28px;
  padding: 0;
  font-size: 18px;
  line-height: 1;
  color: #111827;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.close:hover {
  background: #f3f4f6;
}
.body {
  flex: 1;
  padding: 12px 16px;
  background: #f5f5f7;
  font-size: 14px;
  display: flex;
  gap: 16px;
  overflow: hidden;
}
.sidebar {
  width: 200px;
  border-right: 1px solid #dbe6f3;
  padding-right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}
.sidebar-actions {
  display: flex;
  gap: 8px;
}
.sidebar-title {
  font-weight: 600;
  color: #2b4c7e;
}
.new-chat {
  border: none;
  background: linear-gradient(135deg, #1a5fb4, #5aa0ff);
  color: #fff;
  border-radius: 8px;
  padding: 6px 8px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(26, 95, 180, 0.25);
}
.new-chat:hover {
  filter: brightness(1.05);
}
.clear-chat {
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #374151;
  border-radius: 8px;
  padding: 6px 8px;
  cursor: pointer;
  font-weight: 600;
}
.clear-chat:hover {
  background: #f3f4f6;
}
.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  padding-right: 4px;
}
.conversation-item {
  display: flex;
  flex-direction: column;
  border: 1px solid #dbe6f3;
  background: #fff;
  border-radius: 8px;
  padding: 6px 8px;
  text-align: left;
  cursor: pointer;
  font-size: 12px;
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
  position: relative;
}
.conversation-item.active {
  border-color: #1a5fb4;
  background: #eaf2ff;
  box-shadow: 0 6px 14px rgba(26, 95, 180, 0.18);
}
.conversation-item:hover {
  border-color: #9cc4ff;
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(15, 23, 42, 0.08);
}
.conversation-date {
  color: #4b5563;
  font-size: 11px;
}
.conversation-preview {
  color: #6b7280;
  font-size: 11px;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.conversation-delete {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #6b7280;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}
.conversation-delete:hover {
  background: #fee2e2;
  color: #b91c1c;
  border-color: #fca5a5;
}
.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}
.msg {
  margin-bottom: 8px;
  padding: 8px 10px;
  border-radius: 12px;
  max-width: 80%;
}
.msg-text {
  white-space: pre-line;
}
.msg.bot {
  background: #e5f2ff;
  border: 1px solid #cfe5ff;
}
.msg.user {
  margin-left: auto;
  background: #fff;
  border: 1px solid #e5e7eb;
}
.context {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #dbe6f3;
  display: grid;
  gap: 8px;
  font-size: 12px;
}
.context-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.context-title {
  font-weight: 600;
  color: #2b4c7e;
}
.context-item {
  color: #1f2937;
}
.context-link {
  color: #1a5fb4;
  text-decoration: none;
  padding: 4px 6px;
  border-radius: 6px;
  background: rgba(26, 95, 180, 0.08);
  transition: background 0.12s ease, color 0.12s ease;
}
.context-link:hover {
  background: rgba(26, 95, 180, 0.16);
  color: #123b7a;
}
.input-wrap {
  display: flex;
  border-top: 1px solid #e5e5ea;
}
input {
  flex: 1;
  border: none;
  padding: 10px 12px;
  font-size: 14px;
}
.input-wrap button {
  width: 88px;
  border: none;
  background: linear-gradient(135deg, #007aff, #5aa0ff);
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}
.input-wrap button:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
