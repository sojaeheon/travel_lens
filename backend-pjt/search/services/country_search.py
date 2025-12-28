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
            "bool": {
                "must": {
                    "multi_match": {
                        "query": keyword,
                        "fields": [
                            "name_ko^3",
                            "name_ko.ngram^5",
                            "name_en^2",
                            "name_en.ngram^3",
                            "search_text",
                            "search_text.ngram",
                        ],
                    }
                },
                "filter": [
                    {"exists": {"field": "iso2"}},
                    {"exists": {"field": "name_ko"}},
                    {"exists": {"field": "name_en"}},
                ],
            }
        },
    )

    results = []
    for hit in response.get("hits", {}).get("hits", []):
        src = hit.get("_source", {})
        iso2 = src.get("iso2")
        name_ko = src.get("name_ko")
        name_en = src.get("name_en")
        if not iso2 or (not name_ko and not name_en):
            continue
        results.append(
            {
                "iso2": iso2,
                "name_ko": name_ko or "",
                "name_en": name_en or "",
                "score": hit.get("_score"),
            }
        )

    return results


def suggest_countries(prefix: str, size: int = 5):
    if not prefix:
        return []

    response = es.search(
        index="country_index",
        size=size,
        _source=["iso2", "name_ko", "name_en"],
        query={
            "bool": {
                "must": {
                    "multi_match": {
                        "query": prefix,
                        "fields": [
                            "name_ko.ngram^5",
                            "name_en.ngram^3",
                            "search_text.ngram",
                        ],
                        "minimum_should_match": "1",
                    }
                },
                "filter": [
                    {"exists": {"field": "iso2"}},
                    {"exists": {"field": "name_ko"}},
                    {"exists": {"field": "name_en"}},
                ],
            }
        },
    )

    results = []
    for hit in response.get("hits", {}).get("hits", []):
        src = hit.get("_source", {})
        iso2 = src.get("iso2")
        name_ko = src.get("name_ko")
        name_en = src.get("name_en")
        if not iso2 or (not name_ko and not name_en):
            continue
        results.append(
            {
                "iso2": iso2,
                "name_ko": name_ko or "",
                "name_en": name_en or "",
            }
        )

    return results
