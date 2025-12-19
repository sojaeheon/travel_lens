import pandas as pd

df = pd.read_csv("country_info_with_continent.csv", encoding="utf-8-sig")

continent_en_to_ko = {
    "Africa": "아프리카",
    "Asia": "아시아",
    "Europe": "유럽",
    "America": "아메리카",
    "Oceania": "오세아니아",
    "Antarctica": "남극",
}

df["continent_nm_ko"] = df["continent_name_en"].map(continent_en_to_ko)

df.to_csv("country_info_with_continent.csv", index=False, encoding="utf-8-sig")
