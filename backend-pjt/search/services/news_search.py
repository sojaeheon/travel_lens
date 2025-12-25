from elasticsearch import Elasticsearch
import os

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
es = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")

def search_news(keyword: str, iso2: str | None = None, page: int = 1, size: int = 10):
    must = []
    filters = []

    if keyword:
        must.append({
            "multi_match": {
                "query": keyword,
                "fields": ["title^3", "search_text"]
            }
        })

    if iso2:
        # Use keyword field to avoid analyzer lowercasing on text field.
        filters.append({"term": {"iso2.keyword": iso2}})

    query = {
        "bool": {
            "must": must if must else [{"match_all": {}}],
            "filter": filters
        }
    }

    response = es.search(
        index="news_index",
        from_=(page - 1) * size,          # ✅ 핵심
        size=size,
        query=query,
        sort=[{"published_at": {"order": "desc"}}],
        track_total_hits=True              # ✅ total 정확히 받기
    )

    total = response["hits"]["total"]["value"]

    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        results.append({
            "id": src.get("id"),
            "title": src.get("title"),
            "url": src.get("url"),
            "published_at": src.get("published_at"),
            "iso2": src.get("iso2"),
            "score": hit.get("_score"),
        })

    return {"total": total, "results": results}
