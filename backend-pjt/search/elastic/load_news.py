import os
import psycopg2
from elasticsearch import Elasticsearch, helpers


# ===============================
# PostgreSQL 설정
# ===============================
pg_conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
)

pg_cur = pg_conn.cursor()


# ===============================
# Elasticsearch 설정
# ===============================
es = Elasticsearch(
    f"http://{os.getenv('ELASTICSEARCH_HOST')}:{os.getenv('ELASTICSEARCH_PORT')}"
)


# ===============================
# PostgreSQL → Elasticsearch
# ===============================
pg_cur.execute("""
    SELECT id, title, url, published_at, iso2
    FROM destination_news
""")

rows = pg_cur.fetchall()

actions = []

for row in rows:
    id, title, url, published_at, iso2 = row

    actions.append({
        "_index": "news_index",
        "_id": id,
        "_source": {
            "id": id,
            "title": title,
            "url": url,
            "published_at": published_at,
            "iso2": iso2,
            "search_text": f"{title} {iso2}"
        }
    })

helpers.bulk(es, actions)

print(f"✅ news_index 적재 완료 ({len(actions)}건)")
