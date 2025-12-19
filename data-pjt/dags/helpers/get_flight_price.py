# scripts/flight_price_fetcher.py
from datetime import date
from amadeus import Client, ResponseError
from dotenv import load_dotenv
import os

load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
)

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
