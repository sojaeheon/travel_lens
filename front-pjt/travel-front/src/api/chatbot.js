import api from "@/api/axios";

export const queryChatbot = ({ message, countryIso2, conversationId } = {}) => {
  return api.post("/chatbot/query/", {
    message,
    country_iso2: countryIso2 || null,
    conversation_id: conversationId || null,
  });
};

export const fetchChatHistory = ({ conversationId } = {}) => {
  return api.get("/chatbot/history/", {
    params: {
      conversation_id: conversationId || null,
    },
  });
};

export const fetchChatConversations = () => {
  return api.get("/chatbot/conversations/");
};

export const deleteChatConversation = (conversationId) => {
  return api.delete(`/chatbot/conversations/${conversationId}/`);
};

export const clearChatConversations = () => {
  return api.delete("/chatbot/conversations/clear/");
};
