# producer/travel_news_kafka_producer.py
import time
import json
import feedparser
from kafka import KafkaProducer
from urllib.parse import quote_plus

# 대상 나라 목록 (필요하면 추가)
COUNTRIES = [
    {"name": "가나", "continent": "아프리카", "lang": "ko", "region": "KR"},
    {"name": "코소보", "continent": "유럽", "lang": "ko", "region": "KR"},
    {"name": "독일", "continent": "유럽", "lang": "ko", "region": "KR"},
    {"name": "중국", "continent": "아시아", "lang": "ko", "region": "KR"},
]

# Kafka 브로커 주소 (docker-compose랑 맞추기)
KAFKA_BROKER = "localhost:9092"
TOPIC = "travel_news"

# Kafka Producer (value를 JSON으로 직렬화)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
)

def build_rss_url(country: dict) -> str:
    """
    대륙명 + 나라명 + 여행 키워드로 Google News RSS URL 생성.
    예) https://news.google.com/rss/search?q=아프리카+가나+여행&hl=ko&gl=KR&ceid=KR:ko
    """
    query = quote_plus(f"{country['continent']} {country['name']} 여행")
    base = "https://news.google.com/rss/search"
    return f"{base}?q={query}&hl={country['lang']}&gl={country['region']}&ceid={country['region']}:{country['lang']}"

def fetch_rss_feed(country: dict, limit: int = 5):
    """
    해당 나라의 여행 관련 Google News RSS를 파싱해서 뉴스 아이템을 yield.
    """
    rss_url = build_rss_url(country)
    feed = feedparser.parse(rss_url)
    
    search_query = f"{country['continent']} {country['name']} 여행"

    for entry in feed.entries[:limit]:
        news_item = {
            "country": country["name"],
            "continent": country["continent"],
            "search_keyword": search_query,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": entry.get("published", ""),
            # Google News RSS 특성상 author가 없을 수도 있음
            "author": entry.get("author", ""),
            "rss_url": rss_url
        }
        yield news_item

def main():
    # 중복 전송 방지용 (링크 기준)
    seen_links = set()

    while True:
        try:
            for country in COUNTRIES:
                for news_item in fetch_rss_feed(country, limit=5):
                    link = news_item["link"]

                    if link and link not in seen_links:
                        seen_links.add(link)
                        producer.send(TOPIC, news_item)
                        print(
                            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                            f"Sent ({country['continent']} {country['name']}): {news_item['title']}"
                        )

            # 60초마다 새 RSS 확인
            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            # 에러나도 너무 자주 돌지 않게 대기
            time.sleep(60)

if __name__ == "__main__":
    main()