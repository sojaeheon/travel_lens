from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from search.services.country_search import (
    search_countries,
    suggest_countries
)
from search.services.news_search import search_news
from search.services.blog_search import search_blogs



class CountrySearchView(APIView):
    """
    GET /api/search/countries?q=프랑
    """

    @swagger_auto_schema(
        operation_summary="나라 검색",
        operation_description="검색어를 기준으로 나라 목록을 검색합니다.",
        manual_parameters=[
            openapi.Parameter(
                name="q",
                in_=openapi.IN_QUERY,
                description="검색어 (예: 프랑, France)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="size",
                in_=openapi.IN_QUERY,
                description="반환할 최대 결과 수 (기본값: 10)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def get(self, request):
        keyword = request.query_params.get("q", "").strip()
        size = int(request.query_params.get("size", 10))

        results = search_countries(keyword, size)

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class CountrySuggestView(APIView):
    """
    GET /api/search/countries/suggest?q=프
    """

    @swagger_auto_schema(
        operation_summary="나라 자동완성",
        operation_description="입력 중인 문자열을 기준으로 나라 자동완성 목록을 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                name="q",
                in_=openapi.IN_QUERY,
                description="자동완성 검색어 (예: 프, fr)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="size",
                in_=openapi.IN_QUERY,
                description="반환할 최대 결과 수 (기본값: 5)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def get(self, request):
        prefix = request.query_params.get("q", "").strip()
        size = int(request.query_params.get("size", 5))

        results = suggest_countries(prefix, size)

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

class NewsSearchView(APIView):
    """
    GET /api/search/news?q=르완다&iso2=RW
    """

    @swagger_auto_schema(
        operation_summary="뉴스 검색",
        manual_parameters=[
            openapi.Parameter(
                name="q",
                in_=openapi.IN_QUERY,
                description="검색어",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="iso2",
                in_=openapi.IN_QUERY,
                description="국가 코드 (선택)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="size",
                in_=openapi.IN_QUERY,
                description="반환 개수 (기본 10)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def get(self, request):
        keyword = request.query_params.get("q", "").strip()
        iso2 = request.query_params.get("iso2")
        size = int(request.query_params.get("size", 10))

        results = search_news(keyword, iso2, size)

        return Response(
            {
                "count": len(results),
                "results": results
            },
            status=status.HTTP_200_OK
        )
    
class BlogSearchView(APIView):
    """
    GET /api/search/blogs?q=르완다&iso2=RW
    """

    @swagger_auto_schema(
        operation_summary="블로그 검색",
        operation_description="블로그 제목을 기준으로 검색합니다.",
        manual_parameters=[
            openapi.Parameter(
                name="q",
                in_=openapi.IN_QUERY,
                description="검색어",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="iso2",
                in_=openapi.IN_QUERY,
                description="국가 코드 (선택)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="size",
                in_=openapi.IN_QUERY,
                description="반환 개수 (기본 10)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def get(self, request):
        keyword = request.query_params.get("q", "").strip()
        iso2 = request.query_params.get("iso2")
        size = int(request.query_params.get("size", 10))

        results = search_blogs(keyword, iso2, size)

        return Response(
            {
                "count": len(results),
                "results": results
            },
            status=status.HTTP_200_OK
        )
    
