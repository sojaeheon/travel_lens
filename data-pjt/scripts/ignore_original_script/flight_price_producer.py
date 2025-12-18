# test_amadeus_country.py
from datetime import date
from amadeus import Client, ResponseError
from dotenv import load_dotenv
import os


load_dotenv()
## API 키 주의
amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLINET_SECRET")
)

def search_country(dest_airport_code: str):
    today = date.today().isoformat()  # 'YYYY-MM-DD' 형식, 오늘 날짜

    try:
        res = amadeus.shopping.flight_offers_search.get(
            originLocationCode='ICN',              # 항상 인천 출발
            destinationLocationCode=dest_airport_code,  # 나라별 대표 공항 코드 (db에 미리 적재 예정)
            departureDate=today,                   # 오늘 하루 당일만 검색 예정
            adults=1,
            currencyCode='KRW',
            max=1
        )  # 필수 파라미터는 origin, destination, departureDate 세 가지

        print(f"오늘({today}) 기준 ICN -> {dest_airport_code}")
        print("총 개수:", len(res.data))
        for i, offer in enumerate(res.data, start=1):
            price = offer['price']['total']
            cur = offer['price']['currency']
            print(f"{i}. {price} {cur}")
    except ResponseError as e:
        print("Amadeus 에러:", e)

if __name__ == "__main__":
    # 나라별 대표 공항 달라서 전달 필요
    search_country('ACC')
