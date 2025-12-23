from elasticsearch import Elasticsearch
import os

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")

es = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")

def search_countries(keyword: str, size: int = 10):
    if not keyword:
        return []

    response = es.search(
        index="country_index",
        size=size,
        query={
            "multi_match": {
                "query": keyword,
                "fields": [
                    "name_ko^3",
                    "name_ko.ngram^5",      # ⭐ 핵심
                    "name_en^2",
                    "name_en.ngram^3",      # ⭐ 핵심
                    "search_text",
                    "search_text.ngram"     # ⭐ 핵심
                ]
            }
        }
    )

    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        results.append({
            "iso2": src["iso2"],
            "name_ko": src["name_ko"],
            "name_en": src["name_en"],
            "score": hit["_score"],
        })

    return results

def suggest_countries(prefix: str, size: int = 5):
    if not prefix:
        return []

    response = es.search(
        index="country_index",
        size=size,
        _source=["iso2", "name_ko", "name_en"],
        query={
            "multi_match": {
                "query": prefix,
                "fields": [
                    "name_ko.ngram^5",
                    "name_en.ngram^3",
                    "search_text.ngram"
                ],
                "minimum_should_match": "1"
            }
        }
    )

    return [
        {
            "iso2": hit["_source"]["iso2"],
            "name_ko": hit["_source"]["name_ko"],
            "name_en": hit["_source"]["name_en"],
        }
        for hit in response["hits"]["hits"]
    ]
