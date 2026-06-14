<div align="center">

# 🌍 TravelLens

### 데이터 기반 글로벌 여행 인사이트 플랫폼

여행지의 **인기 · 위험도 · 비용 · 최신 트렌드**를 지도 위에서 탐색하고  
실시간 데이터와 AI를 활용해 여행 의사결정을 돕습니다.

[![Vue](https://img.shields.io/badge/Vue.js-3.5-4FC08D?logo=vuedotjs&logoColor=white)](./front-pjt/travel-front)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](./backend-pjt)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](./backend-pjt)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-7.5-231F20?logo=apachekafka&logoColor=white)](./data-pipeline/kafka)
[![Flink](https://img.shields.io/badge/Apache_Flink-1.18-E6526F?logo=apacheflink&logoColor=white)](./data-pipeline/flink)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.17-005571?logo=elasticsearch&logoColor=white)](./elasticsearch)
[![Airflow](https://img.shields.io/badge/Apache_Airflow-2.10-017CEE?logo=apacheairflow&logoColor=white)](./data-pipeline/airflow)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](./docker-compose.yml)

[`🎬 시연 영상`](./travellens%20_video.mp4) · [`📘 API 문서`](#api) · [`🧱 프로젝트 구조`](#structure) · [`▶️ 실행 방법`](#run)

</div>

> [!IMPORTANT]
> **대표 이미지 추가 위치**  
> 권장 파일: `docs/images/travellens-cover.gif`  
> 권장 내용: 세계지도 탐색 → 국가 상세 → AI 챗봇이 이어지는 10~15초 GIF

---

## 🧭 빠른 탐색

| [프로젝트 개요](#overview) | [설계 산출물](#deliverables) | [핵심 기능](#features) | [기술 스택](#stack) |
| --- | --- | --- | --- |
| [데이터 흐름](#data-flow) | [AI 챗봇](#ai-chatbot) | [담당 역할](#contribution) | [트러블슈팅](#troubleshooting) |

<a id="overview"></a>

## 📌 프로젝트 개요

TravelLens는 여행지 선택에 필요한 정보가 여러 플랫폼에 흩어져 있다는 문제에서 시작했습니다. 국가별 여행경보, 환율, 항공권 가격, 뉴스와 블로그를 수집하고 사용자 행동 데이터를 분석하여 하나의 세계지도 UI에서 제공합니다.

사용자는 지도를 탐색하며 국가별 정보를 비교하고, 실시간 인기 여행지를 확인하거나 자연어로 AI 챗봇에 여행 관련 질문을 할 수 있습니다. 서비스 내부에서는 Kafka와 Flink가 사용자 행동을 실시간으로 처리하고, Airflow가 외부 데이터 수집을 자동화하며, Elasticsearch가 국가와 여행 콘텐츠 검색을 담당합니다.

| 구분 | 내용 |
| --- | --- |
| 개발 기간 | 2025.11 ~ 2025.12, 6주 |
| 팀 구성 | 2명 |
| 담당 분야 | 프론트엔드, 백엔드, AI, 데이터 파이프라인 설계 |
| 담당 범위 | 서비스 기획, 데이터 파이프라인 구조 설계, Django API 설계, Elasticsearch 검색 구조 설계, 실시간 데이터 처리 아키텍처 기획 및 구현 |
| 협업 도구 | GitHub, Notion, Figma |
| API 문서 | 로컬 실행 후 `http://localhost:8000/swagger/` |
| 시연 영상 | [`travellens _video.mp4`](./travellens%20_video.mp4) |

### 프로젝트 한눈에 보기

| 🗺️ 지도 탐색 | ⚡ 실시간 분석 | 🔎 통합 검색 | 🤖 AI 추천 |
| --- | --- | --- | --- |
| MapLibre 기반 국가 탐색과 위험도·인기도 시각화 | Kafka와 Flink를 통한 사용자 행동 집계 | Elasticsearch 기반 국가·뉴스·블로그 검색 | 최신 여행 데이터와 사용자 관심사를 반영한 검색 증강 답변 |

<a id="deliverables"></a>

## 📐 설계 산출물

설계 문서는 README에 모두 펼쳐놓기보다 대표 이미지를 미리보기로 제공하고 원본 문서로 연결합니다. 현재 저장소에 존재하는 자료와 추가할 자료를 구분했습니다.

| 구분 | 상태 | README 표시 | 권장 파일 |
| --- | --- | --- | --- |
| 서비스 기획서 | 🔶 정리 필요 | 문제 정의·목표·핵심 기능 요약 | `docs/planning/project-plan.pdf` |
| 사용자 흐름 | 🔴 추가 필요 | 지도 탐색부터 챗봇까지의 User Flow | `docs/design/user-flow.png` |
| 화면 설계 | 🔴 추가 필요 | Figma 핵심 화면 또는 와이어프레임 | `docs/design/wireframe.png` |
| 시스템 아키텍처 | 🔶 초안 존재 | 서비스·저장소·파이프라인 관계 | `docs/architecture/system-architecture.png` |
| 실시간 데이터 흐름 | 🔶 초안 존재 | 행동 이벤트의 Kafka·Flink 처리 | `docs/architecture/realtime-pipeline.png` |
| 검색 색인 흐름 | 🔴 추가 필요 | PostgreSQL → Logstash → Elasticsearch | `docs/architecture/search-pipeline.png` |
| 배치·아카이브 흐름 | 🔶 초안 존재 | Airflow → PySpark → HDFS PoC | `docs/architecture/archive-poc.png` |
| ERD | 🟢 원본 존재 | 주요 모델과 관계 | [`front-pjt/TravleLens_ERD.pdf`](./front-pjt/TravleLens_ERD.pdf) |
| API 명세 | 🟢 구현됨 | Swagger / ReDoc | `/swagger/`, `/redoc/` |

<details>
<summary><strong>현재 저장소의 초기 아키텍처 산출물 보기</strong></summary>

<br>

#### 전체 시스템 구조 초안

![초기 시스템 아키텍처](./assets/image.png)

#### 실시간 데이터 경로 초안

![초기 실시간 데이터 경로](./assets/image-4.png)

> 이 이미지는 초기 설계안입니다. 실제 구현에서 Logstash는 인기도 결과 처리 경로가 아니라 국가·뉴스·블로그를 PostgreSQL에서 Elasticsearch로 색인하는 별도 동기화 계층입니다.

#### 아카이브 경로 PoC

![초기 아카이브 경로](./assets/image-5.png)

> 현재 아카이브 작업은 `spark-submit --master local[*]` 방식의 PySpark PoC입니다. Docker에 Spark Master·Worker가 정의되어 있지만 실제 아카이브 Job은 해당 클러스터를 사용하지 않습니다.

</details>

### 권장 문서 디렉터리

```text
docs/
├─ planning/                    # 프로젝트 기획서와 요구사항
├─ design/                      # 사용자 흐름, 와이어프레임, Figma 캡처
├─ architecture/                # 시스템·실시간·검색·아카이브 구조
├─ database/                    # ERD와 데이터 사전
├─ api/                         # API 명세와 요청·응답 예시
└─ images/                      # README 대표 이미지와 기능 GIF
```

## 💡 기획 배경

해외여행 수요는 지속적으로 증가하고 있지만 사용자는 여행지를 선택하는 과정에서 많은 정보에 노출됩니다. 여행지의 안전성, 인기, 비용, 최신 이슈가 서로 다른 플랫폼에 분산되어 있어 직접 검색하고 비교하는 데 많은 시간이 필요합니다.

기존 여행 플랫폼은 후기와 상품 검색 중심인 경우가 많아 여러 국가를 객관적인 데이터로 비교하거나 최근 트렌드를 한눈에 파악하기 어렵습니다. TravelLens는 이러한 탐색 피로를 줄이기 위해 다양한 여행 데이터를 수집·분석하고, 세계지도 기반 UI와 AI 챗봇을 통해 데이터 기반 여행 의사결정을 지원하도록 기획했습니다.

## 🔍 문제 정의

### 👥 대상 사용자

- 목적지를 정하지 못한 해외여행 계획 초기 단계 사용자
- 후기뿐 아니라 비용·안전·트렌드 같은 객관적 데이터를 함께 확인하려는 사용자
- 최근 인기 여행지와 현지 이슈에 민감한 사용자

### ⚠️ 현재 문제

- 여행 정보가 뉴스, 블로그, 항공권, 환율, 공공기관 등 여러 채널에 분산되어 있습니다.
- 국가별 인기와 안전도를 동일한 기준으로 비교하기 어렵습니다.
- 최신 위험 정보와 여행 트렌드를 파악하려면 여러 검색 과정을 반복해야 합니다.
- 검색어를 명확히 정하지 못한 사용자는 목적지를 탐색하는 과정에서 더 큰 피로를 느낍니다.

### 🧩 원인 가설

- 기존 서비스가 후기나 여행 상품 중심으로 구성되어 정량 데이터 비교 기능이 부족합니다.
- 실시간 이벤트와 정기 수집 데이터를 하나의 화면에서 통합하는 구조가 부족합니다.
- 목록과 검색 중심 UX는 국가 간 관계와 전 세계 트렌드를 직관적으로 보여주기 어렵습니다.
- 사용자의 관심 국가와 최근 행동을 활용하는 개인화된 정보 제공이 제한적입니다.

### 📋 조사 근거

- 기존 여행 플랫폼의 탐색 및 검색 흐름 비교
- 여행 커뮤니티에서 반복적으로 등장하는 비용·치안·추천 관련 질문 조사
- 여행 계획 과정에서 사용하는 데이터 출처와 정보 탐색 단계 분석
- 초기 사용자 의견을 바탕으로 지도 중심 탐색과 통합 정보 패널 구성

## 🎯 프로젝트 목표

### 📊 정량적 목표

- 사용자 행동 이벤트를 실시간으로 수집하고 국가별 인기 지표로 집계할 수 있는 파이프라인 구축
- 국가, 뉴스, 블로그를 검색할 수 있는 Elasticsearch 기반 검색 환경 구축
- 환율, 항공권, 여행경보 데이터를 정해진 주기에 맞춰 자동 수집하는 배치 파이프라인 구축
- 서비스와 데이터 인프라를 Docker Compose 환경에서 재현 가능하게 구성

### ✨ 정성적 목표

- 세계지도를 통해 국가를 직관적으로 탐색하는 경험 제공
- 여행 의사결정에 필요한 복합 데이터를 하나의 서비스에서 통합 제공
- 사용자의 즐겨찾기와 행동 이력을 활용한 개인화 기반 마련
- 검색된 최신 정보와 정형 데이터를 활용하는 AI 여행 상담 기능 제공

### ✅ 성공 기준

| 기준 | 확인 방법 |
| --- | --- |
| 지도 기반 탐색 | 국가 검색·선택·상세 패널 연결 및 인기도 오버레이 동작 확인 |
| 실시간 처리 | 행동 이벤트가 Kafka를 거쳐 Flink에서 집계되고 PostgreSQL에 저장되는지 확인 |
| 데이터 자동 수집 | Airflow DAG 실행 결과와 환율·항공권·여행경보 데이터 갱신 여부 확인 |
| 검색 기능 | 국가 자동완성 및 뉴스·블로그 검색 결과의 관련성과 응답 상태 확인 |
| AI 답변 | 검색·DB 조회 컨텍스트가 답변 생성에 포함되고 대화 이력이 저장되는지 확인 |
| 사용성 | 지도 탐색, 상세 정보 확인, 즐겨찾기, 챗봇 사용 흐름에 대한 사용자 피드백 수집 |

> 별도의 부하 테스트나 검색 지연 시간 벤치마크는 수행하지 않았으므로 성능 수치를 임의로 제시하지 않았습니다.

<a id="features"></a>

## 🚀 핵심 기능

### 1. 🗺️ 지도 기반 여행지 탐색

- MapLibre GL과 GeoJSON을 이용한 인터랙티브 세계지도
- 한글·영문 국가명 검색 및 자동완성
- 국가 클릭 시 환율, 항공권, 여행경보, 콘텐츠 상세 패널 제공
- Flink 집계 결과를 이용한 국가별 인기도 색상 시각화
- 대륙과 하위 지역을 기준으로 한 지도 탐색

### 2. 📈 국가별 여행 인사이트

- 최신 환율과 직전 기록 대비 변화량 제공
- 대상 공항 기준 항공권 가격과 이전 수집일 대비 변화량 제공
- 외교부 기반 국가·지역별 여행경보 제공
- 국가별 최신 뉴스와 블로그 검색 결과 제공

### 3. 🔥 실시간 인기 여행지

- 클릭, 검색, 상세 조회, 체류 시간, 즐겨찾기 이벤트 수집
- Django에서 행동 이벤트를 PostgreSQL에 저장하고 Kafka `user_events` 토픽으로 발행
- Flink 윈도우 집계로 국가별 조회·즐겨찾기와 종합 점수 계산
- 최신 집계 결과와 현재 즐겨찾기 수를 결합해 인기 목록 및 지도 점수 제공

### 4. 🔎 검색과 콘텐츠 수집

- Naver API를 통한 국가별 뉴스·블로그 콘텐츠 수집
- Kafka Producer와 Consumer를 이용한 수집·저장 단계 분리
- PostgreSQL 원본 데이터를 Logstash JDBC로 Elasticsearch에 색인
- Nori 분석기와 n-gram 필드를 활용한 한글 검색 및 자동완성
- 국가 코드 필터와 발행일 기준 정렬을 지원하는 뉴스·블로그 검색

### 5. 🤖 AI 여행 챗봇

- 자연어 질문에서 관련 국가 식별
- Elasticsearch에서 관련 뉴스와 블로그 검색
- PostgreSQL에서 환율, 항공권, 여행경보, 인기 국가 조회
- 로그인 사용자의 즐겨찾기와 최근 행동을 개인화 컨텍스트로 활용
- 검색·조회 결과를 프롬프트에 포함해 OpenAI Responses API로 답변 생성
- 사용자별 대화 세션, 메시지, 사용 컨텍스트 저장 및 대화 삭제 지원

### 6. 💬 실시간 커뮤니티

- Django Channels 기반 글로벌 WebSocket 채팅
- JWT 쿼리 토큰을 이용한 WebSocket 사용자 식별
- Redis Channel Layer를 통한 메시지 브로드캐스트
- 로그인 사용자 메시지 영구 저장 및 이전 대화 조회
- D3 Cloud를 활용한 채팅 키워드 워드클라우드

### 7. ❤️ 회원과 개인화

- 이메일 기반 사용자 모델과 JWT 로그인
- Access Token 1일, Refresh Token 7일 정책
- 관심 국가 즐겨찾기 등록·해제 및 마이페이지 목록 제공
- 로그인·비로그인 사용자의 행동 이벤트 수집 지원

## 🖥️ 주요 화면

> [!TIP]
> 기능 설명보다 화면을 먼저 보여주는 구성이 읽기 좋습니다. 각 이미지는 가로 폭을 통일하고, 동작 설명이 필요한 기능만 GIF를 사용합니다.

### 🗺️ 지도 기반 국가 탐색

> **📷 이미지 추가:** `docs/images/feature-map.gif`  
> 국가 검색 → 지도 이동 → 국가 선택 과정을 보여주세요.

국가 검색, 지도 클릭, 실시간 인기도 오버레이를 통해 목적지를 탐색합니다.

### 📊 국가 상세 인사이트

> **📷 이미지 추가:** `docs/images/feature-country-detail.png`  
> 환율, 항공권, 여행경보, 뉴스·블로그가 함께 보이는 화면이 적합합니다.

선택한 국가의 환율, 항공권, 여행경보, 뉴스와 블로그를 한 패널에서 확인합니다.

### 🔥 실시간 인기 여행지

> **📷 이미지 추가:** `docs/images/feature-popularity.png`  
> 인기 목록과 지도 색상 오버레이가 한 화면에 보이도록 구성하세요.

사용자 행동 이벤트를 집계한 인기도 점수를 목록과 지도에 반영합니다.

### 🤖 AI 여행 챗봇

> **📷 이미지 추가:** `docs/images/feature-ai-chat.gif`  
> 질문, 검색 증강 답변, 관련 국가 정보가 이어지는 흐름을 보여주세요.

최신 콘텐츠와 정형 여행 데이터를 바탕으로 질문에 답하고 여행지를 추천합니다.

### 💬 실시간 채팅

> **📷 이미지 추가:** `docs/images/feature-realtime-chat.png`  
> 실시간 메시지와 워드클라우드가 함께 보이는 화면이 적합합니다.

접속한 사용자들이 여행 정보를 실시간으로 교환하고 주요 키워드를 확인합니다.

### 👤 마이페이지

> **📷 이미지 추가:** `docs/images/feature-mypage.png`  
> 즐겨찾기 국가 카드와 프로필 영역을 포함하세요.

관심 국가 목록을 조회하고 사용자 정보를 관리합니다.

<a id="stack"></a>

## 🛠️ 기술 스택

| 영역 | 기술 | 버전·역할 |
| --- | --- | --- |
| Frontend | Vue, Vue Router, Pinia | Vue `3.5.26`, Router `4.6.4`, Pinia `3.0.4` |
| Build | Node.js, Vite | Node `20.19.0`, Vite `7.3.0` |
| UI·Visualization | MapLibre GL, D3 | 지도와 인기도 오버레이, 워드클라우드 |
| HTTP | Axios | REST API 요청과 JWT 헤더 처리 |
| Backend | Python, Django, DRF | Python `3.11`, Django `5.2.8`, DRF `3.16.1` |
| Authentication | SimpleJWT | JWT 발급·갱신 및 API 인증 |
| Realtime | Django Channels, Redis | WebSocket 통신과 Channel Layer |
| Database | PostgreSQL | 서비스 원본·사용자·분석 데이터 저장 |
| Streaming | Kafka, Zookeeper | 이벤트와 콘텐츠 수집 스트림 |
| Stream Processing | Flink, PyFlink | 사용자 행동 실시간 윈도우 집계 |
| Search | Elasticsearch, Logstash, Kibana | 검색 색인, JDBC 동기화, 모니터링 |
| Workflow | Airflow | 환율·항공권·여행경보 수집 및 아카이브 PoC 스케줄링 |
| Archive PoC | PySpark local mode, HDFS | 1년 이상 된 콘텐츠의 Parquet 장기 보관 실험 |
| AI | OpenAI Responses API | 검색 증강형 여행 답변 생성 |
| Infrastructure | Docker, Docker Compose | 전체 서비스 컨테이너 구성 |
| Collaboration | GitHub, Notion, Figma | 형상 관리, 문서화, 화면 설계 |

## 🧠 기술 선정 이유

<details>
<summary><strong>기술별 선택 배경과 적용 방식 자세히 보기</strong></summary>

<br>

### 🖼️ Vue 3, Pinia, MapLibre GL

지도와 상세 패널, 채팅, 챗봇처럼 상태 변화가 많은 화면을 컴포넌트 단위로 분리하기 위해 Vue 3를 사용했습니다. Composition API의 반응형 상태를 이용해 선택 국가, 패널 표시 여부, 지도 상태를 연결했습니다.

인증 정보는 여러 페이지에서 공유되므로 Pinia로 관리하고 Access Token과 사용자 프로필은 새로고침 후에도 유지되도록 Local Storage와 동기화했습니다. 지도는 오픈소스 기반으로 GeoJSON 레이어와 스타일을 세밀하게 제어할 수 있는 MapLibre GL을 선택했습니다.

### ⚙️ Django REST Framework와 SimpleJWT

계정, 여행, 검색, 행동, 분석, 채팅, 챗봇 도메인을 Django 앱으로 분리하고 각 앱이 API와 데이터 모델의 책임을 갖도록 구성했습니다. DRF의 APIView와 Serializer를 사용해 요청 검증과 응답 형식을 통일했으며 drf-yasg로 Swagger 문서를 제공했습니다.

SPA와 API 서버가 분리된 구조에 맞춰 세션 대신 JWT를 사용했습니다. REST 요청은 Axios interceptor가 Bearer Token을 자동 첨부하고, WebSocket은 연결 시 쿼리 문자열의 JWT를 검증해 사용자를 식별합니다.

### 🗄️ PostgreSQL

국가를 중심으로 환율, 공항, 여행경보, 콘텐츠, 행동 이벤트가 관계를 형성하므로 관계형 데이터베이스를 사용했습니다. 외래키와 유일성 제약으로 데이터 정합성을 확보하고, 사용자·국가·시간 기준 인덱스를 두어 주요 조회 패턴을 지원했습니다.

PostgreSQL은 서비스 원본 데이터 저장소로 사용하고 검색은 Elasticsearch, 실시간 전달은 Kafka, 장기 보관은 HDFS가 담당하도록 역할을 분리했습니다.

### ⚡ Kafka와 Flink

사용자 요청 처리와 분석 작업을 분리하고 이벤트 증가에도 확장할 수 있도록 Kafka를 이벤트 버퍼로 도입했습니다. Django는 행동 로그를 DB에 저장한 뒤 `user_events` 토픽에 발행하므로 Flink 장애가 API 요청 전체의 실패로 이어지지 않도록 구성했습니다.

Flink는 연속적으로 들어오는 클릭·조회·즐겨찾기 이벤트를 시간 윈도우로 집계하고 국가별 인기도 결과를 PostgreSQL에 저장합니다. 뉴스와 블로그 수집도 Producer와 Consumer로 분리해 외부 API 호출과 DB 저장의 결합도를 낮췄습니다.

### 🔎 Elasticsearch, Logstash, Nori

국가명 자동완성과 뉴스·블로그 제목 검색은 부분 일치, 한글 형태소 처리, 관련도 점수가 필요하므로 Elasticsearch를 사용했습니다. Nori 분석기와 n-gram 필드에 가중치를 다르게 적용하여 한글·영문 국가 검색과 접두어 자동완성을 지원합니다.

PostgreSQL은 원본 데이터의 기준 저장소로 유지하고 Logstash JDBC 파이프라인이 국가·뉴스·블로그 테이블을 주기적으로 읽어 Elasticsearch에 색인합니다. 애플리케이션이 Elasticsearch에 직접 색인하지 않으므로 데이터 저장과 검색 인덱스 갱신의 책임을 분리할 수 있습니다.

| Pipeline | PostgreSQL 원본 | 실행 주기 | Elasticsearch 대상 | 문서 ID |
| --- | --- | --- | --- | --- |
| `country.conf` | `country` | 5분마다 | `country_index` | `iso2` |
| `news.conf` | `destination_news` | 1분마다 | `news_index` | `id` |
| `blog.conf` | `destination_blog` | 1분마다 | `blog_index` | `id` |

Logstash 컨테이너에는 PostgreSQL JDBC Driver를 마운트하고 DB 접속 정보는 Docker Compose 환경 변수로 전달합니다. 같은 `document_id`로 다시 색인하면 기존 문서가 갱신되므로 반복 조회 시 중복 문서 생성을 방지합니다. 뉴스 파이프라인은 `title`을 `search_text`에도 복사해 검색 필드로 사용합니다.

현재 뉴스·블로그 설정은 `updated_at`을 추적 컬럼으로 지정했지만 SELECT 결과와 Django 모델에는 해당 컬럼이 없고, 쿼리에도 `:sql_last_value` 조건이 없습니다. 따라서 의도한 증분 색인 구조로 동작하지 않으며 전체 행 반복 조회 또는 플러그인 경고 가능성이 있습니다. 운영 환경에서는 `updated_at` 컬럼과 증분 조건을 추가하거나, 변경되지 않는 콘텐츠 특성에 맞춰 `id > :sql_last_value` 방식으로 수정해야 합니다. PostgreSQL에서 삭제된 행도 현재 설정만으로는 Elasticsearch에서 자동 삭제되지 않습니다.

### ⏰ Airflow

환율, 여행경보, 항공권은 출처와 수집 주기가 서로 다릅니다. Airflow DAG로 각 작업의 실행 시간, 재시도, 로그를 관리하여 수동 실행 없이 데이터를 갱신하도록 구성했습니다.

- 환율: 매일 01:00
- 여행경보: 매일 02:00
- 항공권 가격: 매일 03:00
- 장기 데이터 아카이브: 매주 일요일 03:00

### 📦 Spark와 Hadoop HDFS

운영 PostgreSQL에 오래된 콘텐츠가 계속 쌓이는 상황을 가정하여 1년 이상 된 뉴스와 블로그를 국가별 Parquet 파일로 변환하고 HDFS에 저장하는 아카이브 PoC를 구성했습니다. Airflow가 매주 일요일 03시에 `spark-submit --master local[*]`를 실행하고, 저장 작업 이후 PostgreSQL 정리 Task를 수행하도록 설계했습니다.

이 프로젝트에서 Hadoop은 MapReduce나 YARN이 아니라 **HDFS NameNode·DataNode를 제공하는 저장 계층**으로만 사용합니다. PySpark도 Spark Master·Worker 클러스터가 아닌 Airflow 컨테이너 내부 로컬 모드로 실행되므로 실제 분산 처리 구조는 아닙니다.

현재 데이터 규모에는 Airflow와 PyArrow만으로도 충분할 수 있습니다. 따라서 Spark·HDFS는 핵심 운영 기능보다 데이터 증가 시 운영 DB와 장기 보관 저장소를 분리하는 구조를 검증한 실험적 구현으로 구분합니다.

### 💬 Django Channels와 Redis

채팅 메시지를 모든 접속자에게 즉시 전달해야 하므로 HTTP 폴링 대신 WebSocket을 사용했습니다. Django Channels가 연결과 메시지를 처리하고 Redis Channel Layer가 다중 연결 간 브로드캐스트를 담당합니다. 로그인 사용자의 메시지만 PostgreSQL에 저장하고 익명 사용자는 실시간 참여만 가능하도록 구분했습니다.

### 🤖 OpenAI Responses API

LLM이 학습 시점 이후의 환율·항공권·여행경보를 직접 알 수 없다는 한계를 보완하기 위해 서비스 데이터 조회 결과를 프롬프트에 포함했습니다. 단순 자유 대화보다 현재 서비스가 보유한 정보에 근거한 답변을 생성하고, 어떤 데이터가 사용되었는지 메시지의 JSON 컨텍스트에 함께 저장합니다.

</details>

## 🏗️ 시스템 아키텍처

> **🖼️ 최종 이미지 교체 위치:** `docs/architecture/system-architecture.png`  
> Frontend, Backend, Storage, Search, Realtime, Batch/PoC 영역을 색상으로 구분하고 화살표에 프로토콜 또는 데이터 이름을 표시하세요.

전체 시스템은 다음 다섯 영역으로 구성됩니다.

1. Vue 기반 사용자 인터페이스
2. Django REST API 및 Channels WebSocket 서버
3. PostgreSQL, Elasticsearch, Redis 저장 계층
4. Kafka, Flink 기반 실시간 처리 계층
5. Airflow 기반 배치 수집과 PySpark·HDFS 아카이브 PoC

<a id="data-flow"></a>

## 🔄 데이터 흐름

### 👣 사용자 행동과 인기도

```text
Vue
→ POST /interaction/logs/
→ Django: UserEvent 저장
→ Kafka: user_events 발행
→ Flink: 국가·시간 윈도우별 집계
→ PostgreSQL: country_popularity 저장
→ Django Analytics API
→ 인기 국가 목록 및 지도 오버레이
```

행동 유형은 국가 클릭, 검색 결과 선택, 상세 패널 조회, 체류 시간, 즐겨찾기로 구분합니다. 즐겨찾기 이벤트는 행동 기록과 함께 사용자별 관심 국가 상태도 변경합니다.

### 📰 뉴스·블로그 수집과 검색

```text
Naver API
→ Blog/News Kafka Producer
→ travel_blog / travel_news Topic
→ Consumer
→ PostgreSQL
→ Logstash JDBC
→ Elasticsearch
→ Django Search API
→ Vue 검색 결과
```

콘텐츠 URL에는 유일성 제약을 적용하고 Consumer에서 중복 입력을 방지합니다. Elasticsearch에서는 국가 코드 필터와 발행일 내림차순 정렬을 지원합니다.

#### Logstash 색인 단계

```text
PostgreSQL country
→ Logstash JDBC (5분 주기)
→ country_index

PostgreSQL destination_news / destination_blog
→ Logstash JDBC (1분 주기)
→ news_index / blog_index
```

Logstash는 서비스 요청 경로에 직접 참여하지 않습니다. PostgreSQL과 Elasticsearch 사이에서 검색용 문서를 만드는 동기화 계층으로만 사용되며, Django 검색 API는 색인이 끝난 Elasticsearch 인덱스를 조회합니다.

### 📅 정기 여행 데이터 수집

```text
Airflow Scheduler
├─ Naver 환율 수집 → PostgreSQL
├─ Amadeus 항공권 수집 → PostgreSQL
├─ 공공데이터 여행경보 수집 → PostgreSQL
└─ PySpark local 아카이브 PoC → Parquet → HDFS
```

> 아카이브 경로는 구현 코드가 존재하지만 운영 수준으로 완성된 기능은 아닙니다. PostgreSQL JDBC JAR 누락, 하드코딩된 접속 정보, 재실행 중복 가능성, HDFS 저장 검증 후 삭제하는 안전장치가 보완되어야 합니다.

<a id="ai-chatbot"></a>

## 🤖 AI 챗봇 설계

### 🔗 검색 증강 생성 흐름

```text
사용자 질문
→ ISO2 또는 Elasticsearch 국가 검색으로 대상 국가 식별
→ Elasticsearch 뉴스·블로그 검색
→ PostgreSQL 환율·항공권·여행경보 조회
→ 인기 국가 조회
→ 로그인 사용자의 즐겨찾기·최근 행동 조회
→ 수집한 컨텍스트로 프롬프트 구성
→ OpenAI Responses API 호출
→ 답변 및 사용 컨텍스트 저장
```

현재 구현은 벡터 임베딩 기반 RAG가 아니라 **Elasticsearch BM25 키워드 검색과 PostgreSQL 정형 조회를 결합한 검색 증강 생성 방식**입니다. 국가명, 고유명사, 최신 뉴스 검색에는 키워드 검색을 사용하고 수치의 정확성이 중요한 환율·항공권·경보는 데이터베이스에서 직접 조회합니다.

OpenAI API 키가 없거나 외부 호출에 실패하면 수집한 정형 컨텍스트를 기반으로 기본 답변을 생성하도록 구성해 챗봇 기능 전체가 중단되지 않도록 했습니다.

### 🚧 향후 개선

- Elasticsearch `dense_vector`와 kNN을 추가한 하이브리드 검색
- BM25와 벡터 검색 결과 병합 및 reranking
- 문서 청킹과 출처 메타데이터 제공
- 답변 근거 링크와 인용 UI
- 검색 품질 평가용 질문·정답 데이터셋 구축

## 🗂️ 데이터 모델

> **🖼️ ERD 이미지 추가 위치:** `docs/database/erd.png`  
> 원본 PDF: [`front-pjt/TravleLens_ERD.pdf`](./front-pjt/TravleLens_ERD.pdf)  
> GitHub에서 바로 볼 수 있도록 PDF와 별도로 PNG 미리보기를 추가하는 것을 권장합니다.

<details>
<summary><strong>도메인별 데이터 모델 보기</strong></summary>

<br>

| 도메인 | 주요 모델 | 역할 |
| --- | --- | --- |
| Account | `User` | 이메일 기반 인증 사용자 |
| Travel | `Country`, `Currency`, `Airport`, `TravelAlert`, `TargetCountry` | 국가와 여행 인사이트 데이터 |
| Content | `DestinationNews`, `DestinationBlog` | 검색 대상 여행 콘텐츠 |
| Interaction | `UserEvent`, `FavoriteCountry` | 사용자 행동과 관심 국가 |
| Analytics | `CountryPopularity`, `Recommendation` | 국가별 집계 및 추천 결과 |
| Chat | `GlobalChatMessage` | 글로벌 채팅 메시지 |
| Chatbot | `ChatbotConversation`, `ChatbotMessage` | AI 대화 세션, 메시지, 컨텍스트 |

</details>

## 🧱 백엔드 구성

<details>
<summary><strong>Django App별 책임 보기</strong></summary>

<br>

| Django App | 책임 |
| --- | --- |
| `accounts` | 사용자 모델, 회원가입, JWT 로그인, 비밀번호 변경 |
| `travel` | 환율, 항공권, 여행경보, 국가 인사이트 API |
| `content` | 뉴스와 블로그 원본 데이터 모델 및 초기 적재 |
| `interaction` | 행동 로그 수집, Kafka 발행, 즐겨찾기 관리 |
| `analytics` | 최신 인기도 집계 조회와 지도용 점수 제공 |
| `search` | Elasticsearch 국가·뉴스·블로그 검색 |
| `chat` | WebSocket 글로벌 채팅과 메시지 내역 |
| `chatbot` | 검색 증강, OpenAI 호출, 대화 이력 관리 |

</details>

<a id="api"></a>

## 📡 API 명세

<details>
<summary><strong>REST·WebSocket 엔드포인트 전체 보기</strong></summary>

<br>

### 🔐 계정

| Method | Endpoint | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/accounts/register/` | 불필요 | 회원가입 |
| POST | `/accounts/login/` | 불필요 | Access·Refresh Token 발급 |
| POST | `/accounts/refresh/` | 불필요 | Access Token 갱신 |
| POST | `/accounts/change-password/` | 필요 | 비밀번호 변경 |

### ✈️ 여행 정보

| Method | Endpoint | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/travel/insights/country?iso2={ISO2}` | 불필요 | 국가별 환율과 항공권 인사이트 |
| GET | `/travel/alerts` | 불필요 | 여행경보 목록 |
| GET | `/travel/exchange?limit={N}` | 불필요 | 주요 국가 최신 환율 |

### 🔎 검색·분석

| Method | Endpoint | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/search/countries/?q={keyword}` | 불필요 | 국가 검색 |
| GET | `/search/autosearch/?q={prefix}` | 불필요 | 국가 자동완성 |
| GET | `/search/news/?q={keyword}&iso2={ISO2}` | 불필요 | 뉴스 검색 |
| GET | `/search/blogs/?q={keyword}&iso2={ISO2}` | 불필요 | 블로그 검색 |
| GET | `/analytics/popular/?window_type={type}` | 불필요 | 인기 국가 목록 |
| GET | `/analytics/popularity/map/?window_type={type}` | 불필요 | 지도용 국가 인기도 점수 |

### ❤️ 사용자 행동·즐겨찾기

| Method | Endpoint | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/interaction/logs/` | 선택 | 행동 이벤트 저장 및 Kafka 발행 |
| GET | `/interaction/favorites/` | 필요 | 내 즐겨찾기 국가 목록 |
| GET | `/interaction/countries/{iso2}/favorite/` | 필요 | 특정 국가 즐겨찾기 여부 |

### 💬 채팅·챗봇

| Method | Endpoint | 인증 | 설명 |
| --- | --- | --- | --- |
| WS | `/ws/chat/global/?token={access_token}` | 선택 | 글로벌 실시간 채팅 |
| GET | `/api/chat/history/` | 불필요 | 저장된 채팅 내역 |
| POST | `/chatbot/query/` | 선택 | AI 챗봇 질문 및 답변 생성 |
| GET | `/chatbot/history/` | 필요 | 특정 대화 내역 조회 |
| GET | `/chatbot/conversations/` | 필요 | 내 대화 목록 |
| DELETE | `/chatbot/conversations/{id}/` | 필요 | 특정 대화 삭제 |
| DELETE | `/chatbot/conversations/clear/` | 필요 | 전체 대화 삭제 |

</details>

<a id="structure"></a>

## 📁 프로젝트 구조

<details>
<summary><strong>디렉터리 구조 전체 보기</strong></summary>

<br>

```text
travel_lens/
├─ front-pjt/
│  ├─ TravleLens_ERD.pdf
│  └─ travel-front/
│     ├─ public/                 # 지도 스타일, GeoJSON, 지역 데이터
│     └─ src/
│        ├─ api/                 # 기능별 REST API 모듈
│        ├─ assets/              # 서비스 이미지
│        ├─ components/
│        │  ├─ ai/               # AI 챗봇
│        │  ├─ chat/             # 실시간 채팅과 워드클라우드
│        │  ├─ common/           # 헤더와 검색창
│        │  ├─ home/             # 지도와 여행 인사이트
│        │  └─ mypage/           # 프로필과 즐겨찾기
│        ├─ pages/               # 라우트 단위 페이지
│        ├─ router/              # Vue Router 설정
│        └─ store/               # Pinia 사용자 상태
├─ backend-pjt/
│  ├─ accounts/                 # 계정과 JWT 인증
│  ├─ analytics/                # 국가 인기도와 추천
│  ├─ chat/                     # Channels WebSocket 채팅
│  ├─ chatbot/                  # 검색 증강형 AI 챗봇
│  ├─ content/                  # 뉴스와 블로그
│  ├─ interaction/              # 행동 이벤트와 즐겨찾기
│  ├─ search/                   # Elasticsearch 검색 서비스
│  ├─ travel/                   # 국가·환율·항공·경보
│  └─ travel_back/              # Django 프로젝트 설정
├─ data-pipeline/
│  ├─ airflow/dags/             # 외부 데이터 수집 및 아카이브 DAG
│  ├─ flink/jobs/               # 국가 인기도 스트림 집계
│  ├─ hdfs/archive/             # Spark 기반 HDFS 아카이브
│  └─ kafka/
│     ├─ producer/              # 뉴스·블로그 수집
│     └─ consumer/              # PostgreSQL 저장
├─ elasticsearch/
│  ├─ index/                    # 국가·뉴스·블로그 인덱스 정의
│  └─ pipeline/                 # Logstash JDBC 파이프라인
├─ assets/                      # README 이미지
├─ docker-compose.yml           # 전체 서비스 오케스트레이션
└─ README_NEW.md
```

</details>

<a id="contribution"></a>

## 🙋 담당 역할

Git 이력에는 `소재헌` 작성자로 40개 커밋이 기록되어 있으며, 기능 브랜치와 Pull Request 단위로 작업을 통합했습니다. 아래 내용은 커밋 메시지와 실제 변경 파일을 기준으로 정리한 주요 기여입니다.

| 영역 | 주요 기여 | 티켓·근거 |
| --- | --- | --- |
| 서비스·UI/UX | 랜딩, 홈, 로그인·회원가입, 채팅, AI 챗봇, 마이페이지 화면 설계 및 구현 | [`TL-13 ~ TL-18`](https://github.com/sojaeheon/travel_lens/commits/master/?author=sojaeheon) |
| 기반 환경 | PostgreSQL, Kafka, Zookeeper, Docker Compose 초기 구성 | [`TL-11`](https://github.com/sojaeheon/travel_lens/commit/c8eca11), [`TL-12`](https://github.com/sojaeheon/travel_lens/commit/a3a3054) |
| 인증·API | 이메일 사용자 모델, JWT 회원가입·로그인, Swagger, Django 도메인 모델 구성 | [`TL-19`](https://github.com/sojaeheon/travel_lens/commit/3715a2c), [`TL-21`](https://github.com/sojaeheon/travel_lens/commit/e7007c0), [`TL-22`](https://github.com/sojaeheon/travel_lens/commit/e26503d) |
| 지도·여행 정보 | MapLibre 지도, 국가 검색 연동, 위험도 오버레이, 국가 상세 패널, 환율·항공권 정보 | [`TL-20`](https://github.com/sojaeheon/travel_lens/commit/8367594), [`TL-30`](https://github.com/sojaeheon/travel_lens/commit/89aa310) |
| 사용자 행동 | 행동 로그 API, 좋아요 이벤트, 즐겨찾기 저장·조회, 로그인 상태별 UI 정책 | [`TL-24`](https://github.com/sojaeheon/travel_lens/commit/0060a4c) |
| 검색 | 국가·뉴스·블로그 Elasticsearch 인덱스, 검색 API, Logstash 파이프라인 | [`TL-27`](https://github.com/sojaeheon/travel_lens/commit/e4b5d49), [`TL-28`](https://github.com/sojaeheon/travel_lens/commit/2ae33b3) |
| 실시간 분석 | 사용자 이벤트의 Kafka·Flink 연결, 국가 인기도 API와 지도·목록 시각화 | [`TL-25`](https://github.com/sojaeheon/travel_lens/commit/8da6987), [`TL-31`](https://github.com/sojaeheon/travel_lens/commit/479786c) |
| AI | 검색·DB 컨텍스트 기반 여행 챗봇, 대화 이력, 프런트 챗봇 연동 | [`TL-32`](https://github.com/sojaeheon/travel_lens/commit/cc40b8f) |
| 파이프라인 통합 | Airflow 환율·항공권 DAG 연결, HDFS 아카이브 연동 수정, Compose 통합 | [`bf975f6`](https://github.com/sojaeheon/travel_lens/commit/bf975f6), [`07e9126`](https://github.com/sojaeheon/travel_lens/commit/07e9126) |

### 협업 기여 구분

- 실시간 채팅 서버와 워드클라우드의 핵심 구현, 외부 여행 데이터 수집, Spark·Hadoop 초기 작업은 팀원이 담당했습니다.
- 해당 기능을 메인 화면과 인증 상태에 연결하고 데이터 파이프라인·Docker Compose 충돌을 조정하는 통합 작업에 참여했습니다.
- 기능 브랜치와 Pull Request를 사용해 티켓별 변경 범위를 관리하고, 병합 과정에서 폴더 구조와 설정 충돌을 해결했습니다.

<a id="troubleshooting"></a>

## 🧯 트러블슈팅

<details>
<summary><strong>문제 해결 과정 5건 자세히 보기</strong></summary>

<br>

### 1. ⚡ API 처리와 실시간 분석의 결합 문제

**문제**

사용자 행동을 API 요청 안에서 직접 분석하면 처리 시간이 늘어나고 분석 시스템 장애가 사용자 요청 실패로 전파될 수 있었습니다.

**원인**

행동 기록, 집계, 화면 갱신을 하나의 동기 흐름으로 처리하려 한 것이 원인이었습니다. 분석 작업은 요청 처리와 처리량·실패 조건이 다르므로 독립적인 실행 구조가 필요했습니다.

**해결**

Django는 행동 이벤트를 PostgreSQL에 먼저 저장하고 Kafka에 발행하도록 역할을 제한했습니다. Flink가 `user_events`를 별도로 소비해 국가별 윈도우 집계를 수행하고 결과 테이블에 저장하도록 분리했습니다. Kafka 발행 실패는 로깅하되 API의 핵심 행동 기록은 유지하도록 처리했습니다.

**결과**

사용자 API와 분석 파이프라인의 장애 범위를 분리했으며, 집계 로직을 변경하더라도 프론트엔드 이벤트 API 계약을 유지할 수 있는 구조를 확보했습니다.

### 2. 🔎 한글 국가명과 콘텐츠 검색 품질 문제

**문제**

일반적인 문자열 일치만으로는 한글·영문 국가명 자동완성과 뉴스·블로그 제목 검색에서 부분 입력이나 표현 차이를 충분히 처리하기 어려웠습니다.

**원인**

PostgreSQL의 단순 포함 검색은 형태소 분석, 필드별 가중치, 자동완성용 n-gram, 검색 관련도 점수를 제공하는 데 한계가 있었습니다.

**해결**

검색 전용 저장소로 Elasticsearch를 도입하고 Nori와 n-gram 서브필드를 구성했습니다. 국가 검색에서는 한글명, 영문명, 통합 검색 필드에 서로 다른 boost를 적용했으며 콘텐츠 검색은 제목을 우선하도록 가중치를 설정했습니다. 원본 데이터는 PostgreSQL에 유지하고 Logstash JDBC로 검색 인덱스를 동기화했습니다.

**결과**

검색과 트랜잭션 저장의 책임을 분리했고, 한글·영문 국가명 검색, 부분 입력 자동완성, 국가별 뉴스·블로그 필터링을 하나의 검색 계층에서 제공할 수 있게 됐습니다.

### 3. 🔐 WebSocket에서 JWT 인증 상태를 공유하는 문제

**문제**

REST API에서 사용하던 Authorization 헤더 방식을 브라우저 WebSocket 생성자에 동일하게 적용할 수 없었습니다. 사용자를 식별하지 못하면 메시지 저장과 닉네임 표시가 불가능했습니다.

**원인**

기본 WebSocket API는 연결 시 임의의 HTTP Authorization 헤더를 직접 설정하기 어렵고, Django Channels의 기본 Scope에도 SimpleJWT 사용자가 자동으로 연결되지 않습니다.

**해결**

클라이언트가 연결 URL의 `token` 쿼리 파라미터로 Access Token을 전달하고, 커스텀 Channels Middleware가 토큰을 검증해 `scope["user"]`에 사용자를 주입하도록 구현했습니다. 토큰이 없거나 유효하지 않으면 익명 사용자로 접속시키고 로그인 사용자 메시지만 DB에 저장했습니다.

**결과**

REST와 WebSocket에서 동일한 JWT 사용자 체계를 활용하면서 로그인 사용자와 익명 사용자의 채팅 정책을 구분할 수 있었습니다.

### 4. 🤖 최신 여행 데이터와 LLM 답변의 시점 차이

**문제**

LLM 단독 응답은 최신 환율, 항공권, 여행경보와 서비스 사용자의 관심 정보를 반영할 수 없었습니다.

**원인**

모델의 학습 데이터와 실제 서비스 데이터 사이에는 시점 차이가 있으며, 사용자별 즐겨찾기와 행동 기록은 외부 모델이 알 수 없는 정보입니다.

**해결**

질문에서 국가를 식별한 뒤 Elasticsearch의 최신 뉴스·블로그와 PostgreSQL의 환율·항공권·경보를 조회했습니다. 로그인 사용자는 즐겨찾기와 최근 행동도 함께 조회하고, 이 정보를 구조화된 컨텍스트로 만들어 OpenAI Responses API에 전달했습니다. API 키가 없거나 호출이 실패한 경우에는 조회된 데이터로 기본 답변을 생성하도록 fallback을 구성했습니다.

**결과**

챗봇이 서비스가 보유한 최신 데이터와 사용자 정보를 근거로 답변할 수 있게 되었고, 외부 AI API 장애가 전체 상담 기능 중단으로 이어지는 위험을 줄였습니다.

### 5. 🐳 여러 인프라 서비스의 실행 순서와 재현성 문제

**문제**

Django, PostgreSQL, Kafka, Flink, Elasticsearch, Airflow, Redis 등 다수의 서비스가 서로 의존해 로컬 환경에서 동일한 실행 조건을 맞추기 어려웠습니다.

**원인**

각 서비스의 포트, 접속 주소, 초기화 시점, 데이터 볼륨을 개발자가 수동으로 관리하면 환경 차이와 실행 순서에 따른 오류가 발생합니다.

**해결**

Docker Compose에서 공통 네트워크, 서비스 이름 기반 접속, 영속 볼륨, healthcheck와 `depends_on`을 정의했습니다. Django entrypoint는 DB 연결을 기다린 후 마이그레이션과 초기 데이터를 적재하고, Kafka Producer와 Consumer는 브로커 연결 재시도 로직을 사용하도록 구성했습니다.

**결과**

전체 애플리케이션과 데이터 인프라를 하나의 구성 파일로 실행할 수 있게 되었으며, 팀원이 동일한 서비스 이름과 포트 구조를 사용할 수 있는 재현 가능한 개발 환경을 마련했습니다.

</details>

<a id="run"></a>

## ▶️ 실행 방법

<details>
<summary><strong>환경 변수와 로컬·Docker 실행 방법 보기</strong></summary>

<br>

### 📋 사전 요구사항

- Docker 및 Docker Compose
- Node.js `20.19.0` 이상: 프론트엔드 로컬 실행 시
- Python `3.11`: 백엔드 로컬 실행 시
- 외부 API와 데이터베이스 설정을 포함한 환경 변수

### 🔑 환경 변수

민감한 값은 저장소에 커밋하지 않고 루트 또는 서비스별 `.env`에 설정합니다.

```dotenv
POSTGRES_DB=travellens
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

KAFKA_BROKER=kafka:9092
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
AMADEUS_CLIENT_ID=your_client_id
AMADEUS_CLIENT_SECRET=your_client_secret
SERVICE_KEY=your_public_data_key

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5-nano

AIRFLOW_UID=50000
AIRFLOW_FERNET_KEY=
AIRFLOW_CONN_TRAVEL_POSTGRES=postgresql+psycopg2://airflow:airflow@airflow-db:5432/airflow

CORE_CONF_fs_defaultFS=hdfs://namenode:9000
HDFS_CONF_dfs_webhdfs_enabled=true
HDFS_CONF_dfs_permissions_enabled=false
SPARK_MASTER=spark://spark-master:7077
```

### 🐳 Docker Compose 실행

```bash
docker compose up --build
```

백그라운드 실행:

```bash
docker compose up -d --build
```

서비스 상태 확인:

```bash
docker compose ps
```

### 🖥️ 프론트엔드 로컬 실행

```bash
cd front-pjt/travel-front
npm install
npm run dev
```

### ⚙️ 백엔드 로컬 실행

```bash
cd backend-pjt
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_travel_seed
python manage.py load_content_seed
python manage.py runserver
```

### 🌐 서비스 주소

| 서비스 | 주소 |
| --- | --- |
| Frontend | `http://localhost:5173` |
| Backend | `http://localhost:8000` |
| Swagger | `http://localhost:8000/swagger/` |
| ReDoc | `http://localhost:8000/redoc/` |
| Airflow | `http://localhost:8080` |
| Spark Master | `http://localhost:8081` |
| Spark Worker | `http://localhost:8082` |
| Flink | `http://localhost:8084` |
| Elasticsearch | `http://localhost:9200` |
| Kibana | `http://localhost:5601` |
| HDFS NameNode | `http://localhost:9870` |

</details>

## 🚧 한계와 개선 계획

### 🧪 테스트 자동화

현재 Django 테스트 파일은 기본 골격만 존재합니다. 회원가입·인증, 즐겨찾기 토글, 행동 이벤트 발행, 검색 API, 챗봇 컨텍스트 생성에 대한 단위·통합 테스트를 우선 추가해야 합니다. Kafka, Elasticsearch, Redis를 포함한 통합 테스트는 별도 Compose 프로파일로 분리할 계획입니다.

### 🔒 운영 보안

현재 Django 설정의 `DEBUG`, `SECRET_KEY`, CORS, 허용 호스트가 개발 환경 기준입니다. 환경별 설정 파일을 분리하고 비밀 값은 Secret Manager 또는 배포 환경 변수로 관리해야 합니다. WebSocket 토큰의 URL 노출을 줄이기 위한 단기 연결 토큰 또는 쿠키 기반 인증도 검토할 수 있습니다.

### 🧰 환경 설정 분리

프론트엔드 REST와 WebSocket 주소 일부가 `localhost`로 고정되어 있습니다. Vite 환경 변수와 API Gateway 기준 URL을 도입해 개발·스테이징·운영 환경을 코드 변경 없이 전환해야 합니다.

### 🔗 버전 정합성

Airflow 요구사항과 Docker 이미지 버전, Flink와 Kafka Connector 버전에 차이가 있습니다. 실행 이미지를 기준으로 의존성을 고정하고 호환성 테스트를 추가해야 합니다.

### 🔎 검색 고도화

현재 검색 증강은 키워드 검색 기반입니다. 벡터 임베딩, 하이브리드 검색, reranker, 출처 인용을 추가하고 검색 관련성 및 답변 충실도를 평가하는 데이터셋을 구축할 계획입니다.

### 📡 관측 가능성과 배포

Kibana 외에 애플리케이션 로그, 데이터 수집 성공률, Kafka Lag, Flink Job 상태, API 지연 시간을 한곳에서 확인할 수 있는 모니터링이 필요합니다. GitHub Actions 기반 테스트·빌드와 배포 파이프라인도 향후 구성 대상입니다.

## 🌟 기대 효과

### 👤 사용자 관점

- 여러 플랫폼을 오가는 대신 하나의 지도에서 여행지를 탐색하고 비교할 수 있습니다.
- 후기뿐 아니라 환율, 항공권, 여행경보, 인기 지표를 함께 확인할 수 있습니다.
- 자연어 질문을 통해 검색어를 구체화하지 않아도 관련 여행 정보를 얻을 수 있습니다.
- 즐겨찾기와 최근 행동을 기반으로 관심 여행지 중심의 정보를 받을 수 있습니다.

### 🛠️ 기술 관점

- 실시간 이벤트, 배치 수집, 검색, 장기 보관을 목적에 맞는 기술로 분리한 데이터 플랫폼 구조를 경험했습니다.
- 애플리케이션 API와 데이터 파이프라인을 느슨하게 결합하여 각 영역을 독립적으로 확장할 수 있는 기반을 마련했습니다.
- 트랜잭션 DB, 검색 엔진, 메시지 브로커, 스트림 처리, 워크플로 관리 도구를 하나의 서비스 흐름으로 통합했습니다.

<a id="retrospective"></a>

## 📝 회고

TravelLens는 단순한 여행 정보 화면을 만드는 것보다 데이터가 수집되고 처리되어 사용자에게 전달되는 전체 흐름을 설계하는 데 초점을 둔 프로젝트였습니다. 짧은 개발 기간 안에 많은 기술을 연결하면서 각 도구를 사용하는 것 자체보다 어떤 책임을 맡길 것인지가 더 중요하다는 점을 배웠습니다.

특히 PostgreSQL을 원본 저장소로, Elasticsearch를 검색 계층으로, Kafka를 이벤트 전달 계층으로 분리하면서 시스템 경계를 명확히 하는 경험을 했습니다. 동시에 자동화 테스트, 보안 설정, 버전 정합성, 운영 모니터링이 충분하지 않으면 복잡한 아키텍처가 오히려 유지보수 비용이 될 수 있다는 한계도 확인했습니다.

향후에는 현재 구조를 유지하면서 테스트와 관측 가능성을 먼저 강화하고, 실제 검색 품질 평가를 기반으로 벡터 검색과 개인화 추천을 단계적으로 고도화할 계획입니다.
