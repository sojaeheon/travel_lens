# 🎨 TravelLens Frontend (Vue.js)

> Vue.js 3.5 + Vite를 활용한 반응형 웹 애플리케이션  
> MapLibre GL JS를 통한 인터랙티브 지도 구현

---

## 📋 목차

- [프로젝트 구조](#-프로젝트-구조)
- [기술 스택](#-기술-스택)
- [주요 컴포넌트](#-주요-컴포넌트)
- [상태 관리](#-상태-관리)
- [설치 및 실행](#-설치-및-실행)
- [개발 가이드](#-개발-가이드)

---

## 📁 프로젝트 구조

```
front-pjt/travel-front/
├── index.html                    # HTML 진입점
├── package.json                  # Node.js 의존성
├── vite.config.js               # Vite 설정
├── Dockerfile                   # Docker 이미지
│
├── src/
│   ├── App.vue                  # 루트 컴포넌트
│   ├── main.js                  # 엔트리 포인트
│   │
│   ├── components/              # 🧩 재사용 가능한 컴포넌트
│   │   ├── Map.vue              # MapLibre 지도
│   │   ├── CountryPanel.vue     # 국가 상세 정보 패널
│   │   ├── Chat.vue             # 실시간 채팅
│   │   ├── WordCloud.vue        # d3-cloud 워드 클라우드
│   │   ├── SearchBar.vue        # 검색 바 (자동완성)
│   │   ├── TopPopular.vue       # TOP 10 추천 리스트
│   │   ├── NavigationBar.vue    # 상단 네비게이션
│   │   └── LoadingSpinner.vue   # 로딩 표시기
│   │
│   ├── pages/                   # 📄 페이지 뷰
│   │   ├── Home.vue             # 홈 페이지 (지도 + 대시보드)
│   │   ├── Login.vue            # 로그인 페이지
│   │   ├── SignUp.vue           # 회원가입 페이지
│   │   ├── MyPage.vue           # 마이페이지
│   │   ├── ChatRoom.vue         # 채팅방 페이지
│   │   └── NotFound.vue         # 404 페이지
│   │
│   ├── stores/                  # 🗂️ Pinia 상태 관리
│   │   ├── auth.js              # 인증 상태
│   │   ├── countries.js         # 국가 데이터
│   │   ├── search.js            # 검색 상태
│   │   ├── chat.js              # 채팅 상태
│   │   └── ui.js                # UI 상태 (모달, 패널 등)
│   │
│   ├── router/                  # 🛣️ Vue Router 설정
│   │   └── index.js             # 라우트 정의
│   │
│   ├── api/                     # 🔌 API 클라이언트
│   │   ├── axios.js             # Axios 인스턴스 & 인터셉터
│   │   ├── auth.js              # 인증 API
│   │   ├── travel.js            # 여행 데이터 API
│   │   ├── search.js            # 검색 API
│   │   ├── interaction.js       # 사용자 행동 API
│   │   └── chat.js              # 채팅 API
│   │
│   ├── composables/             # 🎣 Vue Composable (로직 재사용)
│   │   ├── useAuth.js           # 인증 로직
│   │   ├── useChat.js           # WebSocket 채팅 로직
│   │   ├── useMap.js            # 지도 조작 로직
│   │   └── useSearch.js         # 검색 로직
│   │
│   ├── utils/                   # 🔧 유틸리티 함수
│   │   ├── format.js            # 포맷팅 (환율, 날짜 등)
│   │   ├── constants.js         # 상수 정의
│   │   └── localStorage.js      # 로컬 스토리지 관리
│   │
│   ├── assets/                  # 정적 자원
│   │   ├── styles/
│   │   │   ├── main.css         # 전역 스타일
│   │   │   ├── variables.css    # CSS 변수 (색상, 폰트 등)
│   │   │   └── components.css   # 컴포넌트 스타일
│   │   │
│   │   ├── images/              # 이미지 파일
│   │   │
│   │   └── data/
│   │       ├── geojson/         # GeoJSON 데이터 (지도 경계)
│   │       └── styles/
│   │           └── maplibre-style.json  # MapLibre 지도 스타일
│   │
│   └── layouts/                 # 🎯 레이아웃 컴포넌트
│       ├── DefaultLayout.vue
│       └── AuthLayout.vue
│
└── public/                      # 공개 정적 파일
    └── travel-lens-style.json   # MapLibre 스타일 정의
```

---

## 🛠️ 기술 스택

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| Vue.js | 3.5 | 반응형 UI 프레임워크 |
| Vite | 7.1 | 빠른 빌드 도구 |
| Vue Router | 4.6 | SPA 라우팅 |
| Pinia | 3.0 | 상태 관리 스토어 |
| Axios | 1.13 | HTTP 클라이언트 |
| **MapLibre GL JS** | 5.14 | 인터랙티브 지도 |
| **d3-cloud** | 1.2 | 워드 클라우드 시각화 |
| **d3-scale** | 4.0 | 데이터 스케일 변환 |

---

## 🧩 주요 컴포넌트

### Map.vue (지도)

**특징:**
- 198개국을 MapLibre GL JS로 시각화
- 클릭 시 국가 상세 정보 표시
- 인기도에 따라 색상/크기 변경
- 검색어 필터링

**구현 예시:**
```vue
<template>
  <div id="map"></div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import maplibregl from 'maplibre-gl'

const map = ref(null)

onMounted(() => {
  map.value = new maplibregl.Map({
    container: 'map',
    style: '/travel-lens-style.json',
    center: [0, 20],
    zoom: 2
  })
  
  map.value.on('click', 'country-fill', (e) => {
    const country = e.features[0].properties
    console.log('Selected:', country)
  })
})
</script>
```

### CountryPanel.vue (국가 상세)

**표시 정보:**
- 국가 기본 정보 (이름, 위치 등)
- 환율 정보
- 항공권 가격
- 여행 안전경보
- 최신 블로그/뉴스
- 찜하기 버튼

```vue
<template>
  <div class="country-panel" v-if="country">
    <h2>{{ country.name_ko }}</h2>
    <div class="info-grid">
      <div class="info-item">
        <span class="label">환율</span>
        <span class="value">{{ currency?.currency_krw_unit }}</span>
      </div>
      <div class="info-item">
        <span class="label">항공권</span>
        <span class="value">{{ airport?.flight_price }}</span>
      </div>
      <div class="info-item">
        <span class="label">경보</span>
        <span class="alert-badge" :class="'level-' + alert?.alarm_level">
          {{ getAlertLabel(alert?.alarm_level) }}
        </span>
      </div>
    </div>
    <button @click="toggleFavorite" class="btn-favorite">
      {{ isFavorited ? '💔 찜 취소' : '❤️ 찜하기' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useTravelApi } from '@/api/travel'

const props = defineProps({
  countryCode: String
})

const { getCountryDetail, getCurrency, getAlert } = useTravelApi()
const country = ref(null)
const currency = ref(null)
const airport = ref(null)
const alert = ref(null)
const isFavorited = ref(false)

const toggleFavorite = async () => {
  isFavorited.value = !isFavorited.value
}

// 데이터 로드
const loadCountryData = async () => {
  country.value = await getCountryDetail(props.countryCode)
  currency.value = await getCurrency(props.countryCode)
  alert.value = await getAlert(props.countryCode)
}
</script>
```

### Chat.vue (실시간 채팅)

**특징:**
- WebSocket을 통한 실시간 메시지 전송/수신
- JWT 기반 인증
- 메시지 히스토리 표시
- 사용자 닉네임 표시

```vue
<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="msg in messages" :key="msg.id" class="message">
        <span class="sender">{{ msg.sender_nickname }}</span>
        <span class="text">{{ msg.message }}</span>
        <span class="time">{{ formatTime(msg.created_at) }}</span>
      </div>
    </div>
    <div class="input-area">
      <input 
        v-model="inputMessage" 
        @keyup.enter="sendMessage"
        placeholder="메시지 입력..."
      />
      <button @click="sendMessage">전송</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const messages = ref([])
const inputMessage = ref('')
let ws = null

const connectWebSocket = () => {
  const token = authStore.accessToken
  ws = new WebSocket(
    `ws://localhost:8000/ws/chat/global/?token=${token}`
  )
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    messages.value.push(data)
  }
}

const sendMessage = () => {
  if (!inputMessage.value.trim()) return
  
  ws.send(JSON.stringify({
    message: inputMessage.value
  }))
  
  inputMessage.value = ''
}

onMounted(() => {
  connectWebSocket()
})
</script>
```

### SearchBar.vue (검색)

**특징:**
- Elasticsearch 기반 자동완성
- 키보드 네비게이션 지원
- 검색 결과 클릭 시 국가 상세 표시

```vue
<template>
  <div class="search-bar">
    <input 
      v-model="query"
      @input="onInput"
      @keydown="onKeyDown"
      placeholder="국가명 검색..."
    />
    
    <ul v-if="suggestions.length > 0" class="suggestions">
      <li 
        v-for="(suggestion, index) in suggestions"
        :key="suggestion.iso2"
        @click="selectCountry(suggestion)"
        :class="{ active: index === highlightedIndex }"
      >
        {{ suggestion.name_ko }} ({{ suggestion.iso2 }})
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { searchApi } from '@/api/search'

const query = ref('')
const suggestions = ref([])
const highlightedIndex = ref(-1)

const onInput = async () => {
  if (!query.value) {
    suggestions.value = []
    return
  }
  
  const results = await searchApi.suggest(query.value)
  suggestions.value = results
}

const selectCountry = (country) => {
  // 지도에 국가 선택 이벤트 발송
  const event = new CustomEvent('country-selected', {
    detail: country
  })
  window.dispatchEvent(event)
  
  query.value = ''
  suggestions.value = []
}

const onKeyDown = (e) => {
  if (e.key === 'ArrowDown') {
    highlightedIndex.value = Math.min(
      highlightedIndex.value + 1,
      suggestions.value.length - 1
    )
  } else if (e.key === 'ArrowUp') {
    highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
  } else if (e.key === 'Enter') {
    if (highlightedIndex.value >= 0) {
      selectCountry(suggestions.value[highlightedIndex.value])
    }
  }
}
</script>
```

---

## 🗂️ 상태 관리 (Pinia)

### auth.js (인증 상태)

```javascript
// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)
  
  const login = async (email, password) => {
    const response = await authApi.login(email, password)
    accessToken.value = response.access
    user.value = response.user
    localStorage.setItem('access_token', response.access)
  }
  
  const logout = () => {
    user.value = null
    accessToken.value = null
    localStorage.removeItem('access_token')
  }
  
  const register = async (email, name, password) => {
    await authApi.register(email, name, password)
  }
  
  return {
    user,
    accessToken,
    isAuthenticated,
    login,
    logout,
    register
  }
})
```

### countries.js (국가 데이터)

```javascript
// stores/countries.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { travelApi } from '@/api/travel'

export const useCountriesStore = defineStore('countries', () => {
  const countries = ref([])
  const selectedCountry = ref(null)
  const favorites = ref([])
  
  const fetchCountries = async () => {
    countries.value = await travelApi.getCountries()
  }
  
  const selectCountry = (country) => {
    selectedCountry.value = country
  }
  
  const toggleFavorite = (countryCode) => {
    const index = favorites.value.indexOf(countryCode)
    if (index > -1) {
      favorites.value.splice(index, 1)
    } else {
      favorites.value.push(countryCode)
    }
  }
  
  return {
    countries,
    selectedCountry,
    favorites,
    fetchCountries,
    selectCountry,
    toggleFavorite
  }
})
```

### chat.js (채팅 상태)

```javascript
// stores/chat.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const wordCloud = ref({})  // 단어 빈도
  
  const addMessage = (message) => {
    messages.value.push(message)
    
    // 워드 클라우드 업데이트
    const words = message.message.split(/\s+/)
    words.forEach(word => {
      wordCloud.value[word] = (wordCloud.value[word] || 0) + 1
    })
  }
  
  const getTopWords = (limit = 20) => {
    return Object.entries(wordCloud.value)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([word, freq]) => ({ word, freq }))
  }
  
  return {
    messages,
    wordCloud,
    addMessage,
    getTopWords
  }
})
```

---

## 🔌 API 클라이언트

### axios.js (Axios 설정)

```javascript
// api/axios.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const instance = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

// 요청 인터셉터 (토큰 추가)
instance.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 응답 인터셉터 (에러 처리)
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 → 로그인 페이지로 리다이렉트
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default instance
```

### travel.js (여행 데이터 API)

```javascript
// api/travel.js
import instance from './axios'

export const travelApi = {
  getCountries: async (page = 1) => {
    const response = await instance.get('/travel/countries/', {
      params: { page, page_size: 20 }
    })
    return response.data
  },
  
  getCountryDetail: async (iso2) => {
    const response = await instance.get(`/travel/countries/${iso2}/`)
    return response.data
  },
  
  getCurrency: async (iso2) => {
    const response = await instance.get(
      `/travel/countries/${iso2}/currency/`
    )
    return response.data
  },
  
  getAlert: async (iso2) => {
    const response = await instance.get(
      `/travel/countries/${iso2}/alert/`
    )
    return response.data
  }
}
```

---

## 🚀 설치 및 실행

### Docker를 통한 설치

```bash
# 프론트엔드 컨테이너 빌드
docker-compose build frontend

# 서비스 시작
docker-compose up -d frontend

# 로그 확인
docker-compose logs -f frontend
```

### 로컬 개발 환경

```bash
# 1. Node.js 버전 확인
node --version  # v20.19.0 이상 필요

# 2. 의존성 설치
npm install

# 3. 개발 서버 실행
npm run dev

# 브라우저에서 접속
# http://localhost:5173
```

### 프로덕션 빌드

```bash
# 빌드
npm run build

# 결과물 확인 (dist 폴더)
ls dist/

# 빌드 결과물 미리보기
npm run preview
```

---

## 🛣️ 라우팅 설정

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: () => import('@/pages/SignUp.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/mypage',
    name: 'MyPage',
    component: () => import('@/pages/MyPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'ChatRoom',
    component: () => import('@/pages/ChatRoom.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 네비게이션 가드 (인증 확인)
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

---

## 📱 반응형 디자인

```css
/* assets/styles/main.css */

/* 모바일 (< 768px) */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }
  
  #map {
    height: 60vh;
  }
  
  .country-panel {
    height: 40vh;
    overflow-y: auto;
  }
}

/* 태블릿 (768px ~ 1024px) */
@media (768px < width < 1024px) {
  .container {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}

/* 데스크톱 (> 1024px) */
@media (min-width: 1024px) {
  .container {
    display: grid;
    grid-template-columns: 2fr 1fr;
  }
}
```

---

## 🔧 개발 팁

### Vite 환경 변수

```javascript
// vite.config.js
export default {
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __API_URL__: JSON.stringify(process.env.VITE_API_URL || 'http://localhost:8000')
  }
}
```

### 디버깅

```javascript
// main.js에서 Vue DevTools 활성화
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)

if (process.env.NODE_ENV === 'development') {
  app.config.devtools = true
}

app.mount('#app')
```

---

## 📚 유용한 패턴

### Composable로 로직 재사용

```javascript
// composables/useAsync.js
import { ref } from 'vue'

export const useAsync = (asyncFunction) => {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  const execute = async () => {
    loading.value = true
    error.value = null
    try {
      data.value = await asyncFunction()
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }
  
  return { data, loading, error, execute }
}

// 사용
const { data: countries, loading, execute } = useAsync(() => 
  travelApi.getCountries()
)

onMounted(() => execute())
```

---

**🎨 TravelLens Frontend - 사용자 경험을 디자인하다**
