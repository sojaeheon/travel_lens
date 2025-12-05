<template>
  <div class="input-wrap">
    <input
      v-model="textLocal"
      type="text"
      placeholder="메시지를 입력하세요..."
      @keyup.enter="submit"
    />
    <button @click="submit">📨</button>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({ modelValue: String });
const emit = defineEmits(["update:modelValue", "send"]);

const textLocal = ref(props.modelValue || "");
watch(
  () => props.modelValue,
  (v) => (textLocal.value = v || "")
);

const submit = () => {
  if (!textLocal.value.trim()) return;
  emit("send", textLocal.value);
  emit("update:modelValue", "");
  textLocal.value = "";
};
</script>

<style scoped>
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
