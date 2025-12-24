# helpers/get_currency_naver.py
import requests
from bs4 import BeautifulSoup

NAVER_FX_URL = "https://finance.naver.com/marketindex/exchangeList.naver"


def fetch_naver_fx_rates() -> dict:
    """
    네이버 환전 고시 환율에서 (currency_code, base_rate) 딕셔너리 반환.
    base_rate는 KRW 기준 환율.
    """
    res = requests.get(NAVER_FX_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    fx_dict = {}

    name_tds = soup.select("td.tit")
    rate_tds = soup.select("td.sale")

    for name_td, rate_td in zip(name_tds, rate_tds):
        full_name = name_td.get_text(strip=True)
        base_rate_text = rate_td.get_text(strip=True)

        # "(100엔)" 제거
        cleaned_name = full_name.replace("(100엔)", "")
        parts = cleaned_name.split()
        
        # 마지막 부분이 숫자면 그 전 것이 currency code
        if parts[-1].isdigit():
            code = parts[-2]  # "베트남 VND 100" → "VND"
        else:
            code = parts[-1]  # "미국 USD" → "USD"
        
        base_rate = float(base_rate_text.replace(",", ""))

        fx_dict[code] = base_rate
        print(f"[DEBUG] {code}: {base_rate}")

    return fx_dict