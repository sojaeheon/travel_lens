<template>
  <div class="search-wrap">
    <input
      v-model="keywordLocal"
      class="search-input"
      type="text"
      placeholder="어디로 떠나고 싶으신가요?"
      @input="onInput"
      @keyup.enter="onSearch"
    />

    <!-- 검색 아이콘 -->
    <button class="search-btn" @click="onSearch"></button>

    <!-- 자동완성 dropdown -->
    <div v-if="showDropdown && suggestions.length" class="dropdown">
      <div
        v-for="item in suggestions"
        :key="item.iso2"
        class="item"
        @click="select(item)"
      >
        {{ item.name_ko }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { fetchCountrySuggestions, fetchCountries } from "@/api/search";

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

const showDropdown = ref(false);
const suggestions = ref([]);
let debounceId = null;

const onInput = () => {
  emit("update:modelValue", keywordLocal.value);
  const keyword = keywordLocal.value.trim();

  if (!keyword) {
    suggestions.value = [];
    showDropdown.value = false;
    return;
  }

  if (debounceId) {
    clearTimeout(debounceId);
  }

  debounceId = setTimeout(async () => {
    try {
      const res = await fetchCountrySuggestions(keyword, 6);
      suggestions.value = res.data?.results || [];
      showDropdown.value = true;
    } catch {
      suggestions.value = [];
      showDropdown.value = false;
    }
  }, 250);
};

const select = (val) => {
  keywordLocal.value = val.name_ko || "";
  emit("update:modelValue", keywordLocal.value);
  emit("select", val);
  showDropdown.value = false;
};

const onSearch = async () => {
  const keyword = keywordLocal.value.trim();
  if (!keyword) return;

  try {
    const res = await fetchCountries(keyword, 1);
    const first = res.data?.results?.[0];
    if (first) {
      select(first);
    }
  } catch {
    // ignore
  }
};
</script>

<style scoped>
/* =============================== */
/* 기존 스타일 유지 */
/* =============================== */
.search-wrap {
  position: relative;
  width: 70%;
  margin: 20px auto 0;
}

.search-input {
  width: 100%;
  border-radius: 999px;
  border: none;
  padding: 14px 52px 14px 20px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.15);
}

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
  background-image: url("@/assets/search_btn.png");
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.dropdown {
  position: absolute;
  top: 110%;
  left: 0;
  right: 0;
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
