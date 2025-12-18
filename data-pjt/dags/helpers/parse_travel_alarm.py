# helpers/parse_travel_alarm.py
import logging
from datetime import datetime, timezone
from typing import List, Tuple

logger = logging.getLogger(__name__)

# travel_alert 테이블용 타입: (iso2, alarm_level, region, updated_at)
Row = Tuple[str, int, str, datetime]


def parse_travel_alerts(json_data: dict, iso2: str | None = None) -> List[Row]:
    """
    TravelAlarmService0404 응답을 travel_alert 테이블에 맞는 튜플 리스트로 변환.
    - totalCount == 0 이면 빈 리스트 반환
    - 여러 item 이 있어도 모두 변환해서 반환
    """
    rows: List[Row] = []

    body = json_data.get("response", {}).get("body", {})
    total_count = body.get("totalCount", 0)

    if not total_count:
        if iso2:
            logger.info("no travel alarm for ISO2=%s (totalCount=0)", iso2)
        else:
            logger.info("no travel alarm in response (totalCount=0)")
        return rows

    items = body.get("items", {}).get("item", [])
    if not items:
        if iso2:
            logger.info("no items list for ISO2=%s (totalCount=%s)", iso2, total_count)
        else:
            logger.info("no items list in response (totalCount=%s)", total_count)
        return rows

    # item 이 dict 하나로 올 수도 있고, 리스트로 올 수도 있어서 통일
    if isinstance(items, dict):
        items = [items]

    for it in items:
        iso2_val = it.get("country_iso_alp2") or iso2
        level = it.get("alarm_lvl") or it.get("alarm_level")
        region = it.get("region_ty") or it.get("continent_nm") or ""

        # written_dt 가 없으면 지금 시각으로 보정
        written_raw = it.get("written_dt") or it.get("last_updt_dtm")

        if not iso2_val or not level:
            continue

        try:
            if written_raw:
                # 예: "2024-12-01 12:34:56" 형식 가정
                written_at = datetime.fromisoformat(
                    written_raw.replace(" ", "T")
                )
            else:
                written_at = datetime.now(timezone.utc)
        except Exception:
            written_at = datetime.now(timezone.utc)

        rows.append((iso2_val, int(level), region, written_at))

    return rows
