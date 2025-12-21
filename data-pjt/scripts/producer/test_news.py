# scripts/producer/test_news.py

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

NEWS_BASE_URL = "https://news.google.com/"


def parse_google_news_html(html: str, limit: int) -> list[dict]:
    """
    Google News 검색 결과 HTML에서 뉴스 제목/URL 일부를 파싱 (테스트용).
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict] = []

    # 기사 카드 선택자
    cards = soup.select("article, div.xrnccd, div.IFHyqb")
    print("[DEBUG] cards found:", len(cards))

    # 카드 한 개 HTML 확인용
    if cards:
        print("[DEBUG] first card html:\n", cards[0].prettify()[:2000])

    for card in cards:
        # 1차: 구글 뉴스에서 자주 쓰는 제목용 a 태그
        a = card.select_one("a[role=heading], a.DY5T1d, a.JtKRv")

        # 2차: 그래도 없으면 카드 안 첫 번째 a 태그
        if not a:
            a = card.find("a")
        if not a:
            continue

        title = a.get_text(strip=True)
        href = a.get("href")
        if not href:
            continue

        url = urljoin(NEWS_BASE_URL, href)

        results.append(
            {
                "title": title,
                "url": url,
            }
        )

        if len(results) >= limit:
            break

    return results


if __name__ == "__main__":
    path = "news_sample.html"
    print("[DEBUG] CWD:", os.getcwd())
    print("[DEBUG] exists(news_sample.html)?", os.path.exists(path))

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    items = parse_google_news_html(html, limit=5)
    print("[DEBUG] parsed items:", len(items))
    for i, item in enumerate(items, 1):
        print(f"[{i}] {item['title']}")
        print("   ", item["url"])
