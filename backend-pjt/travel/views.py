from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Max
from decimal import Decimal

from .models import Currency, Airport, TargetCountry, TravelAlert


def _to_float(v):
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return float(v)


def _value_change(today, prev):
    """
    Absolute change: today - prev
    """
    if today is None or prev is None:
        return None
    return round(float(today) - float(prev), 4)


class CountryInsightView(APIView):
    """
    GET /api/travel/insights/country?iso2=JP
    """
    def get(self, request):
        iso2 = (request.query_params.get("iso2") or "").strip().upper()
        if not iso2:
            return Response({"detail": "iso2 is required"}, status=status.HTTP_400_BAD_REQUEST)

        # =========================
        # 1) 환율 (Currency)
        # =========================
        latest_fx = (
            Currency.objects
            .filter(country_id=iso2, currency_krw_unit__isnull=False)
            .order_by("-recorded_date", "-id")
            .first()
        )

        prev_fx = None
        if latest_fx:
            prev_fx = (
                Currency.objects
                .filter(
                    country_id=iso2,
                    currency_krw_unit__isnull=False,
                    recorded_date__lt=latest_fx.recorded_date
                )
                .order_by("-recorded_date", "-id")
                .first()
            )

        fx_rate = latest_fx.currency_krw_unit if latest_fx else None
        fx_prev = prev_fx.currency_krw_unit if prev_fx else None
        fx_change = _value_change(fx_rate, fx_prev)

        currency_code = latest_fx.currency_code if latest_fx else None

        # =========================
        # 2) 항공료 (Airport)
        # =========================
        # 대표 공항이 있으면 그 공항 우선, 없으면 해당 날짜 최저가
        target = TargetCountry.objects.filter(iso2=iso2).first()
        target_airport_code = target.airport_code_iata if target else None

        latest_date = (
            Airport.objects
            .filter(country_id=iso2, flight_price__isnull=False)
            .aggregate(d=Max("recorded_date"))["d"]
        )

        flight_price = None
        flight_airport_code = None
        flight_airport_name = None
        flight_change = None

        if latest_date:
            qs_today = Airport.objects.filter(
                country_id=iso2,
                recorded_date=latest_date,
                flight_price__isnull=False
            )

            # 1) 대표 공항 우선
            if target_airport_code:
                rec = (
                    qs_today
                    .filter(airport_code_iata=target_airport_code)
                    .order_by("flight_price", "id")
                    .first()
                )
                if rec:
                    flight_price = rec.flight_price
                    flight_airport_code = rec.airport_code_iata
                    flight_airport_name = rec.airport_name_ko

            # 2) 없으면 그날 최저가
            if flight_price is None:
                rec = qs_today.order_by("flight_price", "id").first()
                if rec:
                    flight_price = rec.flight_price
                    flight_airport_code = rec.airport_code_iata
                    flight_airport_name = rec.airport_name_ko

            # 3) change: 이전 날짜의 "같은 공항" 가격으로 계산
            prev_date = (
                Airport.objects
                .filter(country_id=iso2, flight_price__isnull=False, recorded_date__lt=latest_date)
                .aggregate(d=Max("recorded_date"))["d"]
            )

            if prev_date and flight_airport_code:
                prev_rec = (
                    Airport.objects
                    .filter(
                        country_id=iso2,
                        recorded_date=prev_date,
                        airport_code_iata=flight_airport_code,
                        flight_price__isnull=False
                    )
                    .order_by("-recorded_date", "-id")
                    .first()
                )
                if prev_rec:
                    flight_change = _value_change(flight_price, prev_rec.flight_price)

        data = {
            "iso2": iso2,
            "flight": {
                "price": _to_float(flight_price),
                "change": flight_change,  # % (없으면 null)
                "recorded_date": str(latest_date) if latest_date else None,
                "airport_code_iata": flight_airport_code,
                "airport_name_ko": flight_airport_name,
            },
            "fx": {
                "currency_code": currency_code,
                "pair": f"{currency_code} / KRW" if currency_code else None,  # ✅ 표시용
                "rate": _to_float(fx_rate),
                "change": fx_change,  # % (없으면 null)
                "recorded_date": str(latest_fx.recorded_date) if latest_fx else None,
            },
        }
        

        return Response(data, status=status.HTTP_200_OK)


class TravelAlertListView(APIView):
    """
    GET /api/travel/alerts
    """
    def get(self, request):
        alerts = TravelAlert.objects.select_related("country").all()
        data = []
        for alert in alerts:
            data.append({
                "iso2": alert.country_id,
                "alarm_level": alert.alarm_level,
                "region": alert.region,
                "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
            })

        return Response({"results": data}, status=status.HTTP_200_OK)


class ExchangeRateListView(APIView):
    """
    GET /api/travel/exchange?limit=10
    """
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
        except ValueError:
            limit = 10
        limit = max(1, min(limit, 20))

        targets = (
            TargetCountry.objects
            .order_by("name_ko")
        )

        results = []
        for target in targets[:limit]:
            latest_fx = (
                Currency.objects
                .filter(country_id=target.iso2, currency_krw_unit__isnull=False)
                .order_by("-recorded_date", "-id")
                .first()
            )
            if not latest_fx:
                continue

            prev_fx = (
                Currency.objects
                .filter(
                    country_id=target.iso2,
                    currency_krw_unit__isnull=False,
                    recorded_date__lt=latest_fx.recorded_date
                )
                .order_by("-recorded_date", "-id")
                .first()
            )

            rate = latest_fx.currency_krw_unit
            prev = prev_fx.currency_krw_unit if prev_fx else None
            change = _value_change(rate, prev)

            results.append({
                "iso2": target.iso2,
                "name_ko": target.name_ko,
                "currency_code": latest_fx.currency_code,
                "rate": _to_float(rate),
                "change": _to_float(change),
                "recorded_date": str(latest_fx.recorded_date) if latest_fx else None,
            })

        return Response({"results": results}, status=status.HTTP_200_OK)
