# helpers/get_travel_alert.py
import os
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://apis.data.go.kr/1262000/TravelAlarmService0404/getTravelAlarm0404List"
SERVICE_KEY = os.getenv("SERVICE_KEY")


def fetch_travel_alarm(iso2: str | None = None, page: int = 1, per_page: int = 100) -> dict:
    """
    TravelAlarmService0404 목록 조회.
    iso2가 주어지면 해당 국가만, 없으면 전체.
    """
    params = {
        "serviceKey": SERVICE_KEY,
        "page": page,
        "perPage": per_page,
        "returnType": "JSON",
    }
    if iso2:
        params["cond[country_iso_alp2::EQ]"] = iso2

    url = f"{BASE_URL}?{urlencode(params, doseq=True)}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()
