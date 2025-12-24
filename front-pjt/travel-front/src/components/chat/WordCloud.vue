<template>
  <div class="wordcloud-container">
    <svg :width="width" :height="height" v-if="words.length > 0">
      <g :transform="`translate(${width / 2},${height / 2})`">
        <text
          v-for="(word, idx) in words"
          :key="idx"
          :font-size="word.size + 'px'"
          :fill="word.color"
          text-anchor="middle"
          :transform="`translate(${word.x},${word.y}) rotate(${word.rotate})`"
          class="word-item"
        >
          {{ word.text }}
        </text>
      </g>
    </svg>
    <div v-else class="no-data">데이터를 분석 중입니다...</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import cloud from 'd3-cloud';
import { scaleLog } from 'd3-scale'; // ⭐ 선형 대신 로그 스케일 사용 (빈도 차이를 극대화)

const props = defineProps({
  messageList: { type: Array, default: () => [] }
});

const width = 450;
const height = 400;
const words = ref([]);

// 더 선명하고 다양한 색상 팔레트
const colors = ['#FF5A5F', '#FFB400', '#007A87', '#8CE071', '#7B0051', '#45B7D1', '#FE5F55'];

const generateWordCloud = () => {
  const wordCount = {};
  
  props.messageList.forEach(msg => {
    const text = msg.content || msg.message || '';
    // 1. 조사 제거를 위한 최소한의 처리 (공백 기준 분리 후 2글자 이상)
    text.split(/\s+/).forEach(word => {
      const clean = word.replace(/[^가-힣a-zA-Z]/g, '');
      if (clean.length >= 2) {
        wordCount[clean] = (wordCount[clean] || 0) + 1;
      }
    });
  });

  const entries = Object.entries(wordCount)
    .map(([text, count]) => ({ text, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 60); // ⭐ 더 많은 단어를 노출시켜 빽빽하게 만듦

  if (!entries.length) return;

  const minCount = entries[entries.length - 1].count;
  const maxCount = entries[0].count;

  // 2. ⭐ 로그 스케일 적용: 빈도가 조금만 높아도 크기가 확 커지게 함
  const sizeScale = scaleLog()
    .domain([minCount, maxCount])
    .range([16, 90]); // 최소 16px ~ 최대 90px

  const layout = cloud()
    .size([width, height])
    .words(entries.map(d => ({ 
      text: d.text, 
      size: sizeScale(d.count),
      color: colors[Math.floor(Math.random() * colors.length)]
    })))
    .padding(2) // ⭐ 간격을 줄여서 더 빽빽하게 붙임
    .rotate(() => 0) // ⭐ 모두 가로로 정렬 (참고 이미지 스타일)
    .font('Pretendard, sans-serif') // ⭐ 무조건 굵은 폰트 사용
    .fontSize(d => d.size)
    .spiral('archimedean') // 원형 배치
    .on('end', (data) => {
      words.value = data;
    });

  layout.start();
};

watch(() => props.messageList, generateWordCloud, { deep: true });
onMounted(generateWordCloud);
</script>

<style scoped>
.wordcloud-container {
  width: 100%;
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}
.word-item {
  font-weight: 900; /* ⭐ 최대한 굵게 */
  transition: all 0.3s;
  cursor: default;
  paint-order: stroke;
}
.no-data { color: #ccc; }
</style>