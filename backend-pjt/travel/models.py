from django.db import models


class Country(models.Model):
    """
    국가 기준 테이블
    - 모든 도메인의 기준 키 (iso2)
    """

    # ISO 국가 코드 (KR, US, JP ...)
    iso2 = models.CharField(max_length=2, primary_key=True)

    # ISO3 코드 (KOR, USA ...)
    iso3 = models.CharField(max_length=3)

    # 국가명 (한글 / 영문)
    name_ko = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)

    # 대륙 정보 (지도 / 필터링 / 통계용)
    continent_name_en = models.CharField(max_length=50)
    continent_name_ko = models.CharField(max_length=50)

    class Meta:
        db_table = "country"

    def __str__(self):
        return self.name_en


class Currency(models.Model):
    """
    국가별 환율 스냅샷
    - 최신 환율만 유지 (히스토리는 별도 파이프라인 가능)
    """

    # 국가 FK (iso2 기준)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="currencies",
        db_column="iso2"
    )

    # 통화 한글명 (미국 달러, 일본 엔 등)
    currency_unit_ko = models.CharField(max_length=100)

    # 통화 코드 (USD, JPY ...)
    currency_code = models.CharField(max_length=50)

    # 환율 단위 (1, 100 등)
    currency_trunc_unit = models.IntegerField()

    # 원화 기준 환율
    currency_krw_unit = models.DecimalField(
        max_digits=15, decimal_places=4,
        null=True, blank=True
    )

    # 환율 업데이트 시각
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "currency"


class Airport(models.Model):
    """
    국가별 주요 공항 + 항공료 정보
    """

    # 소속 국가
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="airports",
        db_column="iso2"
    )

    # 공항명 (한글)
    airport_name_ko = models.CharField(max_length=150)

    # IATA 공항 코드 (ICN, NRT 등)
    airport_code_iata = models.CharField(max_length=10)

    # 평균 / 최저 항공료
    flight_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True
    )

    class Meta:
        db_table = "airport"


class TravelAlert(models.Model):
    """
    외교부 해외안전정보
    - 국가당 1개만 존재
    """

    # 국가와 1:1 관계
    country = models.OneToOneField(
        Country,
        on_delete=models.CASCADE,
        related_name="travel_alert",
        db_column="iso2"
    )

    # 경보 단계 (1~4단계 등)
    alarm_level = models.CharField(max_length=10)

    # 경보 지역 설명
    region = models.CharField(max_length=100)

    # 마지막 업데이트 시각
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "travel_alert"
