# 🔧 TravelLens Backend (Django)

> Django 5.2 기반 RESTful API 서버  
> Django Channels를 활용한 실시간 WebSocket 통신

---

## 📋 목차

- [프로젝트 구조](#-프로젝트-구조)
- [주요 앱 설명](#-주요-앱-설명)
- [데이터베이스 스키마](#-데이터베이스-스키마)
- [설치 및 실행](#-설치-및-실행)
- [API 엔드포인트](#-api-엔드포인트)
- [개발 가이드](#-개발-가이드)

---

## 📁 프로젝트 구조

```
backend-pjt/
├── manage.py
├── requirements.txt          # Python 의존성
├── Dockerfile               # Docker 이미지
├── .env                     # 환경 변수 (git ignore)
│
├── travel_back/             # 메인 Django 프로젝트
│   ├── settings.py          # Django 설정
│   ├── urls.py              # 전체 라우팅
│   ├── asgi.py              # ASGI 설정 (Channels)
│   └── wsgi.py              # WSGI 설정
│
├── accounts/                # 👤 사용자 인증
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── authentication.py    # JWT 인증
│   └── migrations/
│
├── travel/                  # 🌍 여행 데이터
│   ├── models.py            # Country, Currency, Airport, TravelAlert
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── management/
│   │   └── commands/
│   │       └── load_travel_seed.py
│   └── migrations/
│
├── content/                 # 📰 블로그/뉴스
│   ├── models.py            # DestinationBlog, DestinationNews
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── management/
│   │   └── commands/
│   │       └── load_content_seed.py
│   └── migrations/
│
├── search/                  # 🔍 검색 엔진
│   ├── models.py
│   ├── views.py             # 검색 API
│   ├── serializers.py
│   ├── urls.py
│   ├── elastic/             # Elasticsearch 연동
│   │   ├── load_country.py
│   │   ├── elastic_utils.py
│   │   └── mappings.py
│   ├── services/
│   │   └── search_service.py
│   └── migrations/
│
├── interaction/             # 📊 사용자 행동 로깅
│   ├── models.py            # UserEvent, UserFavorite
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── kafka/
│   │   └── kafka_producer.py
│   └── migrations/
│
├── chat/                    # 💬 실시간 채팅
│   ├── models.py            # ChatMessage
│   ├── views.py
│   ├── consumers.py         # WebSocket Consumer
│   ├── serializers.py
│   ├── routing.py           # WebSocket 라우팅
│   └── migrations/
│
├── chatbot/                 # 🤖 AI 챗봇
│   ├── models.py
│   ├── views.py
│   ├── services/
│   │   └── llm_service.py
│   ├── serializers.py
│   ├── urls.py
│   └── migrations/
│
├── analytics/               # 📈 분석
│   ├── models.py            # CountryPopularity
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── migrations/
│
└── dummy_data/              # 📁 초기 시드 데이터 (CSV)
    ├── countries.csv
    ├── currencies.csv
    ├── airports.csv
    └── travel_alerts.csv
```

---

## 🎯 주요 앱 설명

### 1. accounts (사용자 인증)

**모델:**
- `User`: 커스텀 사용자 모델 (이메일 기반 인증)

**API 엔드포인트:**
```http
POST   /api/accounts/register/          # 회원가입
POST   /api/accounts/login/             # 로그인
POST   /api/accounts/logout/            # 로그아웃
GET    /api/accounts/profile/           # 프로필 조회
PUT    /api/accounts/profile/           # 프로필 수정 (비밀번호 변경)
POST   /api/accounts/token/refresh/     # 토큰 갱신
```

**예시:**
```bash
# 회원가입
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "홍길동",
    "password": "password123"
  }'

# 로그인
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

---

### 2. travel (여행 데이터)

**모델:**
- `Country`: 국가 기본 정보 (198개국)
- `Currency`: 환율 데이터 (77개국)
- `Airport`: 항공권 가격 (11개국)
- `TravelAlert`: 여행 안전경보 (1~4 단계)

**API 엔드포인트:**
```http
GET    /api/travel/countries/           # 국가 목록
GET    /api/travel/countries/{iso2}/    # 국가 상세
GET    /api/travel/countries/{iso2}/currency/    # 환율
GET    /api/travel/countries/{iso2}/airport/     # 항공권
GET    /api/travel/countries/{iso2}/alert/       # 경보
```

**데이터 로드:**
```bash
# 초기 국가 데이터 로드
docker-compose exec backend python manage.py load_travel_seed
```

---

### 3. content (블로그/뉴스)

**모델:**
- `DestinationBlog`: 네이버 블로그 글
- `DestinationNews`: Google News RSS

**API 엔드포인트:**
```http
GET    /api/content/blogs/              # 블로그 목록
GET    /api/content/blogs/{id}/         # 블로그 상세
GET    /api/content/news/               # 뉴스 목록
GET    /api/content/news/{id}/          # 뉴스 상세
```

**특징:**
- 5분마다 자동 수집 (Kafka Producer)
- Logstash를 통해 3분마다 Elasticsearch 동기화
- 최대 1년 이전 데이터는 주기적으로 아카이브 (Spark/HDFS)

---

### 4. search (검색 엔진)

**Elasticsearch 인덱스:**
- `country_index`: 국가 검색 + 자동완성
- `blog_index`: 블로그 검색 (한글 형태소 분석)
- `news_index`: 뉴스 검색

**API 엔드포인트:**
```http
GET    /api/search/countries?q=일본                # 국가 검색
GET    /api/search/countries/suggest?q=일         # 자동완성
GET    /api/search/blogs?q=여행&iso2=JP          # 블로그 검색
GET    /api/search/news?q=한류&iso2=KR           # 뉴스 검색
```

**검색 설정:**
```python
# settings.py의 Elasticsearch 설정
ELASTICSEARCH_HOST = 'elasticsearch'
ELASTICSEARCH_PORT = 9200

# Nori 토크나이저를 통한 한글 형태소 분석
# "일본 여행" → "일본", "여행" 분리
# "일" 입력 시 → "일본", "필리핀" 등 자동완성
```

**Elasticsearch 인덱스 생성:**
```bash
docker-compose exec backend python manage.py shell
>>> from search.elastic.load_country import load_countries_to_es
>>> load_countries_to_es()
```

---

### 5. interaction (사용자 행동 로깅)

**모델:**
- `UserEvent`: 사용자 행동 로그 (클릭, 조회, 찜, 체류)
- `UserFavorite`: 찜한 국가 목록

**API 엔드포인트:**
```http
POST   /api/interaction/logs/           # 행동 로그 기록
GET    /api/interaction/favorites/      # 찜한 국가 목록
GET    /api/interaction/countries/{iso2}/favorite/  # 찜 상태 조회
```

**Kafka 연동:**
행동 로그는 자동으로 Kafka `user_events` 토픽으로 전송됨:
```python
# interaction/kafka/kafka_producer.py
def send_event(event_data):
    producer.send('user_events', event_data)
```

**Flink에서 처리:**
- 1시간 윈도우로 집계
- 가중치 계산: 클릭(1) + 조회(3) + 찜하기(10) + 체류시간(0.2/초)
- `country_popularity` 테이블에 저장

---

### 6. chat (실시간 채팅)

**모델:**
- `ChatMessage`: 채팅 메시지

**WebSocket 엔드포인트:**
```javascript
ws://localhost:8000/ws/chat/global/?token=<access_token>
```

**특징:**
- Django Channels + Redis 채널 레이어
- JWT 인증을 통한 보안
- 다중 인스턴스 지원 (Redis 레이어)
- 채팅 메시지 히스토리 PostgreSQL 저장

**구현 상세:**
```python
# chat/consumers.py
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # JWT 검증
        # 채널 그룹에 가입
        
    async def receive(self, text_data):
        # 메시지 저장 및 브로드캐스트
        
    async def chat_message(self, event):
        # 모든 클라이언트에게 메시지 전송
```

---

### 7. chatbot (AI 챗봇)

**API 엔드포인트:**
```http
POST   /api/chatbot/query/              # AI 쿼리 처리
```

**요청 예시:**
```json
{
  "query": "12월에 따뜻하고 저렴한 곳 추천해줘"
}
```

**응답 예시:**
```json
{
  "response": "12월에는 태국과 베트남을 추천드립니다...",
  "countries": ["TH", "VN"],
  "recommendation_scores": {
    "TH": 95.5,
    "VN": 92.3
  }
}
```

---

### 8. analytics (분석)

**모델:**
- `CountryPopularity`: 국가별 인기도 (Flink에서 1시간마다 갱신)

**API 엔드포인트:**
```http
GET    /api/analytics/popular/          # TOP 10 여행지
GET    /api/analytics/popular/?window_type=daily   # 일간 통계
GET    /api/analytics/popular/?window_type=monthly # 월간 통계
```

**데이터 흐름:**
```
UserEvent (매초 기록)
→ Kafka (user_events)
→ Flink (1시간 윈도우 집계)
→ PostgreSQL (country_popularity)
→ /api/analytics/popular/ (조회)
```

---

## 🗄️ 데이터베이스 스키마

### 주요 테이블

#### Country (국가)
```sql
CREATE TABLE travel_country (
    id INTEGER PRIMARY KEY,
    iso2 VARCHAR(2) UNIQUE,           -- 국가 코드 (JP, KR, etc)
    iso3 VARCHAR(3),
    name_ko VARCHAR(100),              -- 한글 국가명
    name_en VARCHAR(100),              -- 영문 국가명
    continent_name_ko VARCHAR(50),
    continent_name_en VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMP
);
```

#### UserEvent (사용자 행동)
```sql
CREATE TABLE interaction_userevent (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    event_type VARCHAR(50),            -- click, view, favorite, stay
    country_iso2 VARCHAR(2),
    stay_duration INTEGER,             -- 초 단위
    created_at TIMESTAMP
);
```

#### CountryPopularity (인기도)
```sql
CREATE TABLE analytics_countrypopularity (
    id INTEGER PRIMARY KEY,
    country_iso2 VARCHAR(2),
    popularity_score FLOAT,            -- 가중치 합계
    ranking INTEGER,
    calculated_at TIMESTAMP            -- 1시간 단위
);
```

#### ChatMessage
```sql
CREATE TABLE chat_chatmessage (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    message TEXT,
    created_at TIMESTAMP
);
```

---

## 🚀 설치 및 실행

### Docker를 통한 설치

```bash
# 1. 백엔드 컨테이너 빌드
docker-compose build backend

# 2. 서비스 시작
docker-compose up -d

# 3. 마이그레이션 실행
docker-compose exec backend python manage.py migrate

# 4. 초기 데이터 로드
docker-compose exec backend python manage.py load_travel_seed
```

### 로컬 개발 환경 설정

```bash
# 1. Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cat > .env << 'EOF'
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=travellens
POSTGRES_USER=travellens
POSTGRES_PASSWORD=2049
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
ELASTICSEARCH_HOST=127.0.0.1
ELASTICSEARCH_PORT=9200
EOF

# 4. 마이그레이션
python manage.py migrate

# 5. 개발 서버 실행
python manage.py runserver
```

---

## 📡 API 엔드포인트 상세

### 인증

```http
# 회원가입
POST /api/accounts/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "홍길동",
  "password": "securepass123"
}

# 로그인
POST /api/accounts/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}

# 응답
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "홍길동"
  }
}

# 로그아웃
POST /api/accounts/logout/
Authorization: Bearer <access_token>
```

### 여행 데이터

```http
# 국가 목록
GET /api/travel/countries/?page=1&page_size=20
Authorization: Bearer <access_token>

# 응답
{
  "count": 198,
  "next": "http://localhost:8000/api/travel/countries/?page=2",
  "previous": null,
  "results": [...]
}

# 국가 상세
GET /api/travel/countries/JP/
{
  "iso2": "JP",
  "name_ko": "일본",
  "name_en": "Japan",
  "latitude": 36.2048,
  "longitude": 138.2529
}

# 환율
GET /api/travel/countries/JP/currency/
{
  "iso2": "JP",
  "currency_code": "JPY",
  "currency_krw_unit": "962.81",
  "recorded_date": "2024-12-26"
}

# 항공권 가격
GET /api/travel/countries/JP/airport/
{
  "iso2": "JP",
  "airport_name_ko": "나리타 국제공항",
  "flight_price": "450000.00",
  "recorded_date": "2024-12-26"
}

# 안전경보
GET /api/travel/countries/JP/alert/
{
  "iso2": "JP",
  "alarm_level": "1",  # 1=유의, 2=자제, 3=권고, 4=금지
  "region": "전 지역",
  "updated_at": "2024-12-26T02:00:00Z"
}
```

### 검색

```http
# 국가 검색
GET /api/search/countries?q=일본&size=10

# 자동완성
GET /api/search/countries/suggest?q=일&size=5
{
  "count": 2,
  "results": [
    {"iso2": "JP", "name_ko": "일본"},
    {"iso2": "IL", "name_ko": "이스라엘"}
  ]
}

# 블로그 검색
GET /api/search/blogs?q=여행&iso2=JP&size=10

# 뉴스 검색
GET /api/search/news?q=한류&iso2=KR&size=10
```

### 사용자 인터랙션

```http
# 행동 로그 기록
POST /api/interaction/logs/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "event_type": "country_click",
  "country_code": "JP",
  "value": null
}

# 찜한 국가 목록
GET /api/interaction/favorites/
Authorization: Bearer <access_token>

# 찜 상태 조회
GET /api/interaction/countries/JP/favorite/
Authorization: Bearer <access_token>
```

### 분석

```http
# 인기 여행지 TOP 10
GET /api/analytics/popular/
{
  "results": [
    {
      "country_iso2": "JP",
      "country_name": "일본",
      "popularity_score": 150.5,
      "ranking": 1
    },
    ...
  ]
}
```

---

## 🛠️ 개발 가이드

### 새로운 API 엔드포인트 추가

1. **앱 생성**
```bash
python manage.py startapp myapp
```

2. **models.py에서 모델 정의**
```python
from django.db import models
from accounts.models import User

class MyModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'myapp_mymodel'
```

3. **serializers.py에서 DRF 직렬화 정의**
```python
from rest_framework import serializers
from .models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'user', 'name', 'created_at']
        read_only_fields = ['created_at']
```

4. **views.py에서 ViewSet 정의**
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MyModel.objects.filter(user=self.request.user)
```

5. **urls.py에서 라우팅**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyModelViewSet

router = DefaultRouter()
router.register(r'my-models', MyModelViewSet, basename='mymodel')

urlpatterns = [
    path('', include(router.urls)),
]
```

6. **travel_back/urls.py에 포함**
```python
urlpatterns = [
    # ... 다른 경로들 ...
    path('api/myapp/', include('myapp.urls')),
]
```

### Kafka를 통한 비동기 처리

```python
# myapp/tasks.py (또는 내부)
from interaction.kafka.kafka_producer import send_event

def process_user_action(user, country_code):
    # 액션 저장
    action = UserAction.objects.create(
        user=user,
        country_code=country_code
    )
    
    # Kafka로 전송
    send_event({
        'user_id': user.id,
        'country_code': country_code,
        'timestamp': int(time.time())
    })
```

---

## 📚 유용한 명령어

```bash
# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# Django 셸 실행
python manage.py shell

# 관리자 계정 생성
python manage.py createsuperuser

# 정적 파일 수집
python manage.py collectstatic --noinput

# 데이터베이스 리셋
python manage.py migrate zero  # 모든 마이그레이션 되돌리기
python manage.py migrate  # 다시 적용

# 개발 서버 실행 (로컬)
python manage.py runserver

# Daphne 서버 실행 (WebSocket 지원)
daphne -b 0.0.0.0 -p 8000 travel_back.asgi:application
```

---

## 🔧 Elasticsearch 설정

### 인덱스 매핑 예시

```json
{
  "mappings": {
    "properties": {
      "name_ko": {
        "type": "text",
        "analyzer": "nori"
      },
      "name_en": {
        "type": "text",
        "analyzer": "standard"
      },
      "iso2": {
        "type": "keyword"
      }
    }
  }
}
```

### 인덱스 생성

```bash
curl -X PUT http://localhost:9200/country_index \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "analysis": {
        "analyzer": {
          "nori": {
            "type": "nori"
          }
        }
      }
    },
    "mappings": { ... }
  }'
```

---

**🔧 TravelLens Backend - 데이터 기반 여행 플랫폼의 핵심**
