from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Max, Count
from decimal import Decimal

from .models import CountryPopularity
from interaction.models import FavoriteCountry


def _to_float(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


class PopularCountryView(APIView):
    """
    GET /analytics/popular/?limit=5&window_type=hourly
    """
    def get(self, request):
        window_type = (request.query_params.get("window_type") or "hourly").strip()
        try:
            limit = int(request.query_params.get("limit", 5))
        except ValueError:
            limit = 5

        limit = max(1, min(limit, 20))

        latest_at = (
            CountryPopularity.objects
            .filter(window_type=window_type)
            .aggregate(latest=Max("calculated_at"))["latest"]
        )

        if not latest_at:
            return Response(
                {"results": [], "window_type": window_type, "calculated_at": None},
                status=status.HTTP_200_OK
            )

        popularity = (
            CountryPopularity.objects
            .filter(window_type=window_type, calculated_at=latest_at)
            .select_related("country")
        )

        favorite_counts = dict(
            FavoriteCountry.objects
            .values("country_id")
            .annotate(count=Count("id"))
            .values_list("country_id", "count")
        )

        results = []
        for row in popularity:
            base_score = _to_float(row.score) or 0.0
            favorite_count = favorite_counts.get(row.country_id, 0)
            adjusted_score = base_score + (favorite_count * 10.0)

            results.append({
                "iso2": row.country_id,
                "name_ko": row.country.name_ko,
                "name_en": row.country.name_en,
                "score": round(adjusted_score, 2),
                "base_score": round(base_score, 2),
                "favorite_count": int(favorite_count),
                "view_count": int(row.view_count),
                "calculated_at": row.calculated_at.isoformat(),
            })

        results.sort(key=lambda item: item["score"], reverse=True)

        return Response(
            {
                "window_type": window_type,
                "calculated_at": latest_at.isoformat(),
                "results": results[:limit],
            },
            status=status.HTTP_200_OK
        )


class CountryPopularityMapView(APIView):
    """
    GET /analytics/popularity/map/?window_type=hourly
    """
    def get(self, request):
        window_type = (request.query_params.get("window_type") or "hourly").strip()

        latest_at = (
            CountryPopularity.objects
            .filter(window_type=window_type)
            .aggregate(latest=Max("calculated_at"))["latest"]
        )

        if not latest_at:
            return Response(
                {
                    "window_type": window_type,
                    "calculated_at": None,
                    "min_score": 0.0,
                    "max_score": 0.0,
                    "results": [],
                },
                status=status.HTTP_200_OK
            )

        popularity = (
            CountryPopularity.objects
            .filter(window_type=window_type, calculated_at=latest_at)
            .select_related("country")
        )

        favorite_counts = dict(
            FavoriteCountry.objects
            .values("country_id")
            .annotate(count=Count("id"))
            .values_list("country_id", "count")
        )

        results = []
        for row in popularity:
            base_score = _to_float(row.score) or 0.0
            favorite_count = favorite_counts.get(row.country_id, 0)
            adjusted_score = base_score + (favorite_count * 10.0)

            results.append({
                "iso2": row.country_id,
                "score": round(adjusted_score, 2),
            })

        scores = [item["score"] for item in results if item["score"] is not None]
        min_score = min(scores) if scores else 0.0
        max_score = max(scores) if scores else 0.0

        return Response(
            {
                "window_type": window_type,
                "calculated_at": latest_at.isoformat(),
                "min_score": round(float(min_score), 2),
                "max_score": round(float(max_score), 2),
                "results": results,
            },
            status=status.HTTP_200_OK
        )
