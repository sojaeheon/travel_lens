<template>
  <div class="search-wrap">
    <input
      v-model="keywordLocal"
      class="search-input"
      type="text"
      placeholder="어디로 떠나고 싶으신가요?"
      @input="onInput"
    />

    <!-- 검색 아이콘 버튼 -->
    <button class="search-btn"></button>

    <!-- 자동완성 영역 -->
    <div v-if="showDropdown && suggestions.length" class="dropdown">
      <div
        v-for="item in suggestions"
        :key="item"
        class="item"
        @click="select(item)"
      >
        {{ item }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";

const props = defineProps({
  modelValue: String,
});
const emit = defineEmits(["update:modelValue", "select"]);

const keywordLocal = ref(props.modelValue || "");

watch(
  () => props.modelValue,
  (v) => {
    if (v !== keywordLocal.value) keywordLocal.value = v || "";
  }
);

const all = ["가나", "가야", "가나다라", "가지와", "가라", "가구"];
const showDropdown = ref(false);

const suggestions = computed(() => {
  if (!keywordLocal.value) return [];
  return all.filter((it) => it.startsWith(keywordLocal.value));
});

const onInput = () => {
  emit("update:modelValue", keywordLocal.value);
  showDropdown.value = true;
};

const select = (val) => {
  keywordLocal.value = val;
  emit("update:modelValue", val);
  emit("select", val);
  showDropdown.value = false;
};
</script>

<style scoped>
/* =============================== */
/* 🔍 검색 바 전체 */
/* =============================== */
.search-wrap {
  position: relative;
  width: 70%;
  margin: 20px auto 0;
}

/* =============================== */
/* 🔍 입력창 스타일 (불투명 + 블러) */
/* =============================== */
.search-input {
  width: 100%;
  border-radius: 999px;
  border: none;
  padding: 14px 52px 14px 20px;
  font-size: 14px;

  /* ✔ 반투명 + blur */
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(10px);

  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.15);
}

/* =============================== */
/* 🔍 검색 버튼 (SVG 아이콘 삽입) */
/* =============================== */
.search-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 22px;
  height: 22px;
  border: none;
  background: none;
  cursor: pointer;

  /* 🔄 PNG 아이콘 사용 */
  background-image: url("@/assets/search_btn.png");
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

/* =============================== */
/* 🔽 자동완성 Dropdown */
/* =============================== */
.dropdown {
  position: absolute;
  top: 110%;
  left: 0;
  right: 0;

  /* ✔ 반투명 + blur */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);

  border-radius: 16px;
  padding: 6px 0;
}

.item {
  padding: 8px 16px;
  cursor: pointer;
}
.item:hover {
  background: rgba(0, 0, 0, 0.05);
}
</style>
