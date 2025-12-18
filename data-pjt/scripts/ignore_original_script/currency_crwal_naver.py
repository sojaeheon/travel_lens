# 네이버 환전 고시 환율

import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://finance.naver.com/marketindex/exchangeList.naver"

res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

rows = []

# 통화명: td.tit, 매매기준율: td.sale
name_tds = soup.select("td.tit")
rate_tds = soup.select("td.sale")

for name_td, rate_td in zip(name_tds, rate_tds):
    full_name = name_td.get_text(strip=True)      
    base_rate_text = rate_td.get_text(strip=True) 

    parts = full_name.replace("(100엔)", "").split()
    code = parts[-1]                 # USD, JPY, EUR ...
    country_kor = " ".join(parts[:-1])  # 미국, 일본, 유로 등

    base_rate = float(base_rate_text.replace(",", ""))

    rows.append(
        {
            "country_name": country_kor,
            "currency_code": code,
            "base_rate": base_rate,
        }
    )

df = pd.DataFrame(rows)
print(df)

df.to_csv("naver_fx_rates.csv", index=False, encoding="utf-8-sig")
