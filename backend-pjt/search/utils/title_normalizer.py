import re

def normalize_title(title: str) -> list[str]:
    """
    뉴스/블로그 제목 → 검색어 자동완성 후보 리스트
    """
    if not title:
        return []

    original = title.strip()

    # 1. 괄호 / 대괄호 제거
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", original)

    # 2. 부제 제거 (-, :, | 기준)
    cleaned = re.split(r"[-:|]", cleaned)[0]

    # 3. 공백 정리
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    candidates = []

    # 4. 최소 길이
    if len(cleaned) >= 2:
        candidates.append(cleaned)

    # 5. 길이 제한 버전 추가
    if len(cleaned) > 30:
        short = cleaned[:30].rstrip()
        if short not in candidates:
            candidates.append(short)

    return candidates
