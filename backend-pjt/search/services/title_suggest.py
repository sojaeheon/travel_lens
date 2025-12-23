from elasticsearch import Elasticsearch
import os

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")

es = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")

def suggest_queries(keyword: str, size: int = 10):
    if not keyword:
        return []

    response = es.search(
        index="title_query_suggest_index",
        size=size,
        query={
            "match": {
                "query": {
                    "query": keyword,
                    "operator": "and"
                }
            }
        },
        sort=[
            {"weight": "desc"}
        ]
    )

    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        results.append({
            "query": src["query"],
            "source": src["source"],
            "doc_id": src["doc_id"],
            "score": hit["_score"],
        })

    return results
