# scripts/currency_crawl_naver.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


NAVER_FX_URL = "https://finance.naver.com/marketindex/exchangeList.naver"


def fetch_naver_fx_rates() -> list[tuple[str, float]]:
    """
    네이버 환전 고시 환율에서 (currency_code, base_rate) 리스트 반환.
    base_rate는 KRW 기준 환율.
    """
    res = requests.get(NAVER_FX_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    rows: list[tuple[str, float]] = []

    name_tds = soup.select("td.tit")
    rate_tds = soup.select("td.sale")

    for name_td, rate_td in zip(name_tds, rate_tds):
        full_name = name_td.get_text(strip=True)
        base_rate_text = rate_td.get_text(strip=True)

        parts = full_name.replace("(100엔)", "").split()
        code = parts[-1]  # USD, JPY, EUR ...
        base_rate = float(base_rate_text.replace(",", ""))

        rows.append((code, base_rate))

    return rows


def build_update_rows() -> list[tuple[float, datetime, str]]:
    """
    currency 테이블 업데이트용 파라미터 리스트 생성.
    (currency_krw_unit, updated_at, currency_code) 튜플들의 리스트.
    """
    now = datetime.now(timezone.utc)
    fx_list = fetch_naver_fx_rates()

    return [(rate, now, code) for code, rate in fx_list]
