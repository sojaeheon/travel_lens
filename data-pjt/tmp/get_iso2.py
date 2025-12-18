# 국가코드 3자리를 2자리로 가져오는 코드

import csv
import pycountry
import chardet

INPUT_FILE = "외교부_국가정보.csv"      # 원본 CSV 파일명
OUTPUT_FILE = "외교부_국가정보_iso2.csv"  # 결과 CSV 파일명

def alpha3_to_alpha2(alpha3_code: str):
    if not alpha3_code:
        return None
    alpha3_code = alpha3_code.strip().upper()
    c = pycountry.countries.get(alpha_3=alpha3_code)
    return c.alpha_2 if c else None

# 1) 파일 인코딩 추정
with open(INPUT_FILE, "rb") as f:
    raw = f.read()
    guess = chardet.detect(raw)
    encoding = guess["encoding"]
    print("detected encoding:", encoding)

# 2) 추정 인코딩으로 CSV 읽어서 UTF-8-SIG로 다시 저장
def add_iso2_column():
    text = raw.decode(encoding, errors="replace")
    lines = text.splitlines()

    reader = csv.DictReader(lines)
    fieldnames = reader.fieldnames + ["ISO2"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            alpha3 = row.get("국가코드(3자리)", "")
            row["ISO2"] = alpha3_to_alpha2(alpha3)
            writer.writerow(row)

if __name__ == "__main__":
    add_iso2_column()
    print("완료:", OUTPUT_FILE)