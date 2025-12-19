# 외교부 해외여행안전 여행경보 단계
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
import os


load_dotenv()

BASE_URL = "http://apis.data.go.kr/1262000/TravelAlarmService0404/getTravelAlarm0404List"
SERVICE_KEY = os.getenv("SERVICE_KEY")

def get_travel_alarm(iso2=None, page=1, per_page=100):
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
    data = resp.json()

    return data

# 사용 예시
if __name__ == "__main__":
    result = get_travel_alarm(iso2="CN")
    print(result)
