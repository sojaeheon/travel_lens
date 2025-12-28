# scripts/get_flight_price.py
from datetime import date
from amadeus import Client, ResponseError
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import DictCursor

load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
)

# 11개 주요 여행 국가 (필터링용)
TARGET_COUNTRIES = ['JP', 'VN', 'CN', 'TH', 'PH', 'US', 'TW', 'HK', 'SG', 'MY', 'AU']

# DB에서 대표 공항 로드 (모듈 로드 시 1회만 실행)
def _load_airports_from_db() -> dict[str, str]:
    """flight_history 테이블에서 11개 국가의 대표 공항 로드"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432)
        )
        
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT iso2, airport_code_iata
                FROM flight_history
                WHERE iso2 = ANY(%s)
                  AND airport_code_iata IS NOT NULL
                ORDER BY iso2
            """, (TARGET_COUNTRIES,))
            
            rows = cur.fetchall()
            airports = {row['iso2']: row['airport_code_iata'] for row in rows}
            
            # 누락된 국가 체크
            missing = set(TARGET_COUNTRIES) - set(airports.keys())
            if missing:
                print(f"[경고] DB에 없는 국가: {missing}")
            
            conn.close()
            return airports
            
    except Exception as e:
        print(f"[에러] DB에서 공항 정보 로드 실패: {e}")
        return {}

# 모듈 로드 시 대표 공항 딕셔너리 생성 (1회만 실행)
TARGET_AIRPORTS = _load_airports_from_db()


def get_lowest_price(
    dest_airport_code: str,
    origin_airport_code: str = "ICN",
    target_date: str | None = None,
) -> float | None:
    """
    origin_airport_code -> dest_airport_code 에 대해
    target_date(YYYY-MM-DD)의 최소 가격(KRW)을 반환. 없으면 None.
    """
    if target_date is None:
        target_date = date.today().isoformat()

    try:
        res = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_airport_code,
            destinationLocationCode=dest_airport_code,
            departureDate=target_date,
            adults=1,
            currencyCode="KRW",
            max=1,  # 가장 싼 1개만
        )

        if not res.data:
            return None

        offer = res.data[0]
        price = float(offer["price"]["total"])
        return price

    except ResponseError as e:
        print(f"[Amadeus 에러] {origin_airport_code}->{dest_airport_code}: {e}")
        return None


def get_all_target_countries_prices(
    origin_airport_code: str = "ICN",
    target_date: str | None = None,
) -> dict[str, float | None]:
    """
    11개 주요 국가의 대표 공항에 대해 항공권 가격을 조회.
    
    Returns:
        {
            'JP': 250000.0,
            'VN': 450000.0,
            ...
        }
    """
    if target_date is None:
        target_date = date.today().isoformat()
    
    if not TARGET_AIRPORTS:
        print("[에러] 대표 공항 정보가 없습니다.")
        return {}
    
    results = {}
    
    for country_code, airport_code in TARGET_AIRPORTS.items():
        print(f"[{country_code}] {airport_code} 항공권 가격 조회 중...")
        price = get_lowest_price(
            dest_airport_code=airport_code,
            origin_airport_code=origin_airport_code,
            target_date=target_date
        )
        results[country_code] = price
        
        # API Rate Limiting 방지
        import time
        time.sleep(0.5)
    
    return results


def get_country_price_by_code(
    country_code: str,
    origin_airport_code: str = "ICN", 
    target_date: str | None = None,
) -> float | None:
    """
    특정 국가 코드(ISO2)에 대한 항공권 가격 조회.
    
    Args:
        country_code: 'JP', 'VN' 등의 ISO2 국가 코드
        origin_airport_code: 출발 공항 (기본값: ICN)
        target_date: 출발 날짜 (YYYY-MM-DD)
    
    Returns:
        항공권 가격 (KRW) 또는 None
    """
    if country_code not in TARGET_AIRPORTS:
        print(f"[경고] {country_code}는 지원하지 않는 국가입니다.")
        return None
    
    airport_code = TARGET_AIRPORTS[country_code]
    return get_lowest_price(
        dest_airport_code=airport_code,
        origin_airport_code=origin_airport_code,
        target_date=target_date
    )


# 사용 예시
if __name__ == "__main__":
    # 0. 로드된 대표 공항 목록 확인
    print("=== DB에서 로드된 대표 공항 ===")
    for country, airport in TARGET_AIRPORTS.items():
        print(f"{country}: {airport}")
    
    print("\n" + "="*50 + "\n")
    
    # 1. 특정 국가 조회
    jp_price = get_country_price_by_code('JP', target_date='2025-01-15')
    print(f"일본 항공권 가격: {jp_price:,.0f}원" if jp_price else "일본 가격 조회 실패")
    
    # 2. 11개국 전체 조회
    print("\n=== 11개국 항공권 가격 조회 ===")
    all_prices = get_all_target_countries_prices(target_date='2025-01-15')
    
    for country_code, price in all_prices.items():
        if price:
            print(f"{country_code}: {price:,.0f}원")
        else:
            print(f"{country_code}: 가격 조회 실패")