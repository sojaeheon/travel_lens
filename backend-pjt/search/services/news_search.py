from elasticsearch import Elasticsearch
import os

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")

es = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")


def search_news(keyword: str, iso2: str | None = None, size: int = 10):
    if not keyword:
        return []

    must = [{
        "multi_match": {
            "query": keyword,
            "fields": [
                "title^3",
                "search_text"
            ]
        }
    }]

    filters = []
    if iso2:
        filters.append({"term": {"iso2": iso2}})

    query = {
        "bool": {
            "must": must,
            "filter": filters
        }
    }

    response = es.search(
        index="news_index",
        size=size,
        query=query,
        sort=[{"published_at": "desc"}]
    )

    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        results.append({
            "id": src["id"],
            "title": src["title"],
            "url": src["url"],
            "published_at": src["published_at"],
            "iso2": src["iso2"],
            "score": hit["_score"],
        })

    return results
