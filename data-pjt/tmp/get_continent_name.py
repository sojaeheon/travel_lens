import pandas as pd
import country_converter as coco

# 1. 인코딩 맞춰서 읽기
df = pd.read_csv("country_info.csv", encoding="utf-8-sig")

# 2. iso2 -> continent_name_en
cc = coco.CountryConverter()
df["continent_name_en"] = cc.convert(df["iso2"], src="ISO2", to="continent")

# 3. 한글 안 깨지게 저장 (엑셀 열기용)
df.to_csv("country_info_with_continent.csv", index=False, encoding="utf-8-sig")
