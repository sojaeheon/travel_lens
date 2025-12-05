<template>
  <div :class="['msg', isMine ? 'mine' : 'other']">
    <div class="name" v-if="!isMine">{{ message.sender }}</div>
    <div class="bubble">{{ message.text }}</div>
    <div class="time">{{ message.time }}</div>
  </div>
</template>

<script setup>
defineProps({
  message: Object,
  isMine: Boolean,
});
</script>

<style scoped>
.msg {
  margin-bottom: 8px;
  font-size: 13px;
}
.msg.mine {
  text-align: right;
}
.name {
  color: #777;
  margin-bottom: 2px;
}
.bubble {
  display: inline-block;
  padding: 8px 10px;
  border-radius: 14px;
  background: #fff;
  max-width: 70%;
}
.msg.mine .bubble {
  background: #007aff;
  color: #fff;
}
.time {
  font-size: 11px;
  color: #aaa;
  margin-top: 2px;
}
</style>
