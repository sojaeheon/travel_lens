from elasticsearch import Elasticsearch, helpers
import psycopg2

es = Elasticsearch("http://elasticsearch:9200")

conn = psycopg2.connect(
    host="db",
    dbname="travellens",
    user="travellens",
    password="2049",
    port=5432
)

cur = conn.cursor()
cur.execute("""
    SELECT iso2, iso3, name_ko, name_en, continent_name_ko, continent_name_en
    FROM country
""")

actions = []

for row in cur.fetchall():
    iso2, iso3, name_ko, name_en, cont_ko, cont_en = row

    actions.append({
        "_index": "country_index",
        "_id": iso2,
        "_source": {
            "iso2": iso2,
            "iso3": iso3,
            "name_ko": name_ko,
            "name_en": name_en,
            "continent_name_ko": cont_ko,
            "continent_name_en": cont_en,
            "search_text": f"{name_ko} {name_en} {cont_ko} {cont_en}"
        }
    })

helpers.bulk(es, actions)

cur.close()
conn.close()

print("✅ Country data indexed successfully")
