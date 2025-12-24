# helpers/get_currency_naver.py
import requests
from bs4 import BeautifulSoup

NAVER_FX_URL = "https://finance.naver.com/marketindex/exchangeList.naver"


def fetch_naver_fx_rates() -> dict:
    """
    네이버 환전 고시 환율에서 (currency_code, base_rate) 딕셔너리 반환.
    매매기준율 값을 그대로 반환 (단위 환산 X)
    
    Returns:
        dict: {currency_code: base_rate}
        예: {'USD': 1504.98, 'JPY': 962.81, 'EUR': 1767.01}
    """
    try:
        res = requests.get(NAVER_FX_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        fx_dict = {}

        name_tds = soup.select("td.tit")
        rate_tds = soup.select("td.sale")

        for name_td, rate_td in zip(name_tds, rate_tds):
            full_name = name_td.get_text(strip=True)
            base_rate_text = rate_td.get_text(strip=True)

            # "(100엔)" 같은 단위 표시 제거
            cleaned_name = full_name.replace("(100엔)", "").replace("(100)", "")
            parts = cleaned_name.split()
            
            # currency code 추출
            if len(parts) < 2:
                continue
                
            # 마지막 부분이 숫자면 그 전 것이 currency code
            if parts[-1].isdigit():
                code = parts[-2]  # "베트남 VND 100" → "VND"
            else:
                code = parts[-1]  # "미국 USD" → "USD"
            
            # 매매기준율 파싱 (쉼표 제거, 그대로 저장)
            try:
                base_rate = float(base_rate_text.replace(",", ""))
            except ValueError:
                print(f"[WARNING] {code}의 환율 파싱 실패: {base_rate_text}")
                continue
            
            fx_dict[code] = base_rate
            print(f"[DEBUG] {code}: {base_rate} KRW")

        return fx_dict
        
    except Exception as e:
        print(f"[ERROR] 네이버 환율 크롤링 실패: {e}")
        return {}