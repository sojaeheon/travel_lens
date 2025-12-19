# producer/travel_blog_kafka_producer.py
import time
import json
import requests
from kafka import KafkaProducer
from urllib.parse import quote_plus
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()
# Naver API 설정 (https://developers.naver.com 에서 발급)
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

COUNTRIES = [
    {"name": "가나", "continent": "아프리카", "lang": "ko", "region": "KR"},
    {"name": "코소보", "continent": "유럽", "lang": "ko", "region": "KR"},
    {"name": "독일", "continent": "유럽", "lang": "ko", "region": "KR"},
    {"name": "중국", "continent": "아시아", "lang": "ko", "region": "KR"},
]

KAFKA_BROKER = "localhost:9092"
TOPIC = "travel_blogs"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
)

def fetch_naver_blog(country: dict, limit: int = 10):
    """
    네이버 블로그 검색 API를 사용해서 여행 블로그 가져오기.
    검색어: 대륙명 + 나라명 + 여행
    """
    search_query = f"{country['continent']} {country['name']} 여행"
    
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    
    params = {
        "query": search_query,
        "display": limit,
        "start": 1,
        "sort": "date"  # 최신순
    }
    
    url = "https://openapi.naver.com/v1/search/blog"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        for item in data.get("items", []):
            blog_item = {
                "country": country["name"],
                "continent": country["continent"],
                "search_keyword": search_query,
                "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),  # HTML 태그 제거
                "link": item.get("link", ""),
                "description": item.get("description", "").replace("<b>", "").replace("</b>", ""),
                "bloggername": item.get("bloggername", ""),
                "bloggerlink": item.get("bloggerlink", ""),
                "postdate": item.get("postdate", ""),
            }
            yield blog_item
            
    except Exception as e:
        print(f"Error fetching blog for {search_query}: {e}")

def main():
    seen_links = set()
    
    while True:
        try:
            for country in COUNTRIES:
                for blog_item in fetch_naver_blog(country, limit=10):
                    link = blog_item["link"]
                    
                    if link and link not in seen_links:
                        seen_links.add(link)
                        producer.send(TOPIC, blog_item)
                        print(
                            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                            f"Sent ({country['continent']} {country['name']}): {blog_item['title']}"
                        )
            
            time.sleep(60)
            
        except Exception as e:
            print("Error:", e)
            time.sleep(60)

if __name__ == "__main__":
    main()