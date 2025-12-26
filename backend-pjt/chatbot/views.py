import json
import os
from decimal import Decimal

import requests
from django.db.models import Max
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from analytics.models import CountryPopularity
from interaction.models import FavoriteCountry, UserEvent
from search.services.blog_search import search_blogs
from search.services.country_search import search_countries
from search.services.news_search import search_news
from travel.models import Country, Currency, Airport, TargetCountry, TravelAlert

from .models import ChatbotConversation, ChatbotMessage


MAX_NEWS = 3
MAX_BLOGS = 3
MAX_POPULAR = 5
MAX_FAVORITES = 5
MAX_EVENTS = 5
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "20"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_FLIGHTS = 5


def _to_float(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _resolve_country(iso2, query):
    if iso2:
        return Country.objects.filter(iso2=iso2.upper()).first()

    if not query:
        return None

    try:
        results = search_countries(query, size=1)
    except Exception:
        return None

    if not results:
        return None

    top = results[0]
    return Country.objects.filter(iso2=top.get("iso2")).first()


def _get_latest_fx(iso2):
    latest = (
        Currency.objects
        .filter(country_id=iso2, currency_krw_unit__isnull=False)
        .order_by("-recorded_date", "-id")
        .first()
    )
    if not latest:
        return None

    prev = (
        Currency.objects
        .filter(
            country_id=iso2,
            currency_krw_unit__isnull=False,
            recorded_date__lt=latest.recorded_date,
        )
        .order_by("-recorded_date", "-id")
        .first()
    )

    change = None
    if prev and latest.currency_krw_unit is not None:
        change = _to_float(latest.currency_krw_unit) - _to_float(prev.currency_krw_unit)

    return {
        "currency_code": latest.currency_code,
        "rate": _to_float(latest.currency_krw_unit),
        "change": _to_float(change),
        "recorded_date": str(latest.recorded_date),
    }


def _get_latest_flight(iso2):
    target = TargetCountry.objects.filter(iso2=iso2).first()
    target_airport_code = target.airport_code_iata if target else None

    latest_date = (
        Airport.objects
        .filter(country_id=iso2, flight_price__isnull=False)
        .aggregate(d=Max("recorded_date"))["d"]
    )

    if not latest_date:
        return None

    qs_today = Airport.objects.filter(
        country_id=iso2,
        recorded_date=latest_date,
        flight_price__isnull=False,
    )

    selected = None
    if target_airport_code:
        selected = (
            qs_today
            .filter(airport_code_iata=target_airport_code)
            .order_by("flight_price", "id")
            .first()
        )

    if not selected:
        selected = qs_today.order_by("flight_price", "id").first()

    if not selected:
        return None

    prev_date = (
        Airport.objects
        .filter(country_id=iso2, flight_price__isnull=False, recorded_date__lt=latest_date)
        .aggregate(d=Max("recorded_date"))["d"]
    )

    change = None
    if prev_date:
        prev_rec = (
            Airport.objects
            .filter(
                country_id=iso2,
                recorded_date=prev_date,
                airport_code_iata=selected.airport_code_iata,
                flight_price__isnull=False,
            )
            .order_by("-recorded_date", "-id")
            .first()
        )
        if prev_rec:
            change = _to_float(selected.flight_price) - _to_float(prev_rec.flight_price)

    return {
        "price": _to_float(selected.flight_price),
        "change": _to_float(change),
        "recorded_date": str(latest_date),
        "airport_code_iata": selected.airport_code_iata,
        "airport_name_ko": selected.airport_name_ko,
    }


def _get_recent_flights(limit=MAX_FLIGHTS):
    rows = (
        Airport.objects
        .filter(flight_price__isnull=False)
        .order_by("country_id", "-recorded_date", "-id")
        .distinct("country_id")
        .select_related("country")
    )
    results = []
    for row in rows[:limit]:
        results.append(
            {
                "iso2": row.country_id,
                "name_ko": row.country.name_ko,
                "airport_code_iata": row.airport_code_iata,
                "airport_name_ko": row.airport_name_ko,
                "price": _to_float(row.flight_price),
                "recorded_date": str(row.recorded_date),
            }
        )
    return results


def _get_alert(iso2):
    alert = TravelAlert.objects.filter(country_id=iso2).first()
    if not alert:
        return None
    return {
        "alarm_level": alert.alarm_level,
        "region": alert.region,
        "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
    }


def _get_popular_countries(limit=MAX_POPULAR, window_type="hourly"):
    latest_at = (
        CountryPopularity.objects
        .filter(window_type=window_type)
        .aggregate(latest=Max("calculated_at"))["latest"]
    )
    if not latest_at:
        return []

    rows = (
        CountryPopularity.objects
        .filter(window_type=window_type, calculated_at=latest_at)
        .select_related("country")
        .order_by("-score")
    )

    results = []
    for row in rows[:limit]:
        results.append({
            "iso2": row.country_id,
            "name_ko": row.country.name_ko,
            "name_en": row.country.name_en,
            "score": _to_float(row.score),
            "calculated_at": row.calculated_at.isoformat(),
        })

    return results


def _get_user_profile(user):
    if not user or not user.is_authenticated:
        return None

    favorites = (
        FavoriteCountry.objects
        .filter(user=user)
        .select_related("country")
        .order_by("-created_at")[:MAX_FAVORITES]
    )
    favorite_list = [
        {
            "iso2": row.country_id,
            "name_ko": row.country.name_ko,
            "name_en": row.country.name_en,
        }
        for row in favorites
    ]

    events = (
        UserEvent.objects
        .filter(user=user)
        .select_related("country")
        .order_by("-created_at")[:MAX_EVENTS]
    )
    event_list = [
        {
            "iso2": row.country_id,
            "name_ko": row.country.name_ko,
            "name_en": row.country.name_en,
            "event_type": row.event_type,
            "created_at": row.created_at.isoformat(),
        }
        for row in events
    ]

    return {
        "favorites": favorite_list,
        "recent_events": event_list,
    }


def _search_documents(query, iso2=None):
    if not query:
        return {"news": [], "blogs": []}

    try:
        news_data = search_news(query, iso2=iso2, page=1, size=MAX_NEWS)
    except Exception:
        news_data = {"results": []}

    try:
        blog_data = search_blogs(query, iso2=iso2, page=1, size=MAX_BLOGS)
    except Exception:
        blog_data = {"results": []}

    return {
        "news": news_data.get("results", []),
        "blogs": blog_data.get("results", []),
    }


def _format_change(value, unit=""):
    if value is None:
        return "변동 정보 없음"
    sign = "+" if value > 0 else ""
    return f"{sign}{value}{unit}".strip()


def _build_answer(context):
    country = context.get("country")
    alert = context.get("alert")
    fx = context.get("fx")
    flight = context.get("flight")
    flights = context.get("flights", [])
    news = context.get("news", [])
    blogs = context.get("blogs", [])
    popular = context.get("popular", [])
    user = context.get("user")

    summary = []
    evidence = []
    recommendations = []

    if country:
        summary = []

        if alert:
            evidence.append(f"여행경보: {alert['alarm_level']} ({alert['region']})")

        if fx:
            pair = f"{fx['currency_code']} / KRW" if fx.get("currency_code") else "환율"
            change_text = _format_change(fx.get("change"))
            evidence.append(f"환율: {pair} {fx.get('rate')} ({change_text})")

        if flight:
            change_text = _format_change(flight.get("change"), " KRW")
            evidence.append(
                f"항공료: {flight.get('airport_name_ko')} {flight.get('price')} KRW ({change_text})"
            )
        if flights:
            for item in flights[:3]:
                evidence.append(
                    f"항공료: {item['name_ko']} {item['airport_name_ko']} {item['price']} KRW"
                )

        if news:
            evidence.append(
                f"최근 뉴스: {news[0].get('title', '')} 외 {max(len(news) - 1, 0)}건"
            )
            for item in news[:3]:
                title = item.get("title", "")
                url = item.get("url", "")
                if title and url:
                    evidence.append(f"뉴스 링크: {title} ({url})")

        if blogs:
            evidence.append(
                f"최근 블로그: {blogs[0].get('title', '')} 외 {max(len(blogs) - 1, 0)}건"
            )
            for item in blogs[:3]:
                title = item.get("title", "")
                url = item.get("url", "")
                if title and url:
                    evidence.append(f"블로그 링크: {title} ({url})")

    if not country and popular:
        names = ", ".join([item["name_ko"] for item in popular])
        recommendations.append(f"요즘 인기 여행지: {names}")
        recommendations.append("관심 국가를 알려주면 항공료/환율/경보까지 함께 비교해줄게요.")

    if not country and user:
        favorites = user.get("favorites") or []
        if favorites:
            fav_names = ", ".join([item["name_ko"] for item in favorites])
            recommendations.append(f"내가 찜한 국가 참고: {fav_names}")

    if not summary and not evidence and not recommendations:
        return "데이터가 충분하지 않아 일반 안내만 가능해요. 원하는 조건을 알려주면 더 구체화할게요."

    description = []
    if country:
        description.append(f"{country['name_ko']} ({country['iso2']}) 기준으로 확인된 데이터입니다.")
        if alert:
            description.append("여행경보 정보는 현재 안전도 판단에 참고할 수 있어요.")
        if fx:
            description.append("환율은 예산 계획과 현지 지출 규모를 가늠하는 데 유용합니다.")
        if flight:
            description.append("항공료는 시기별 변동이 커서 최근 값 기준으로 설명합니다.")
        if news or blogs:
            description.append("최근 뉴스/블로그는 현지 분위기와 이슈 파악에 도움이 됩니다.")
    else:
        description.append("국가 지정 없이 현재 보유한 데이터로 추천을 구성합니다.")
        description.append("인기 여행지와 개인 관심 데이터를 바탕으로 방향을 잡았습니다.")
        if flights:
            description.append("최근 항공료 데이터가 있는 국가를 참고해 비용 관점도 반영했습니다.")

    sentences = []
    if description:
        sentences.append(" ".join(description))
    if evidence:
        sentences.append("참고할 만한 근거는 " + "; ".join(evidence) + " 입니다.")
    if recommendations:
        sentences.append("추천 방향은 " + "; ".join(recommendations) + " 입니다.")
    sentences.append("원하는 분위기나 예산을 알려주면 더 구체화할게요.")
    return " ".join(sentences)


def _build_prompt(message, context):
    context_payload = json.dumps(context, ensure_ascii=False)
    return (
        "너는 Travel Lens 여행 데이터 어시스턴트 '트레비'야.\n"
        "가능하면 아래 컨텍스트를 우선 사용하고, 부족하면 일반적인 여행 지식으로 보완해도 돼.\n"
        "숫자/날짜는 컨텍스트에 없으면 대략적인 경향으로 표현하고 단정하지 마.\n"
        "데이터가 부족하더라도 일반적인 여행 추천을 길고 자세하게 작성해줘.\n"
        "답변은 문단 하나로 12~16문장 정도로 작성하고, "
        "질문의 조건(시기/예산/스타일)을 반영해.\n"
        "뉴스/블로그/환율/항공료/경보 근거가 있으면 자연스럽게 포함하고, "
        "없으면 대체로 유효한 여행 원칙(기후, 안전, 이동성, 비용)을 설명해.\n\n"
        f"질문: {message}\n\n"
        f"컨텍스트: {context_payload}\n"
    )


def _generate_answer(message, context):
    if not OPENAI_API_KEY:
        return _build_answer(context)

    try:
        payload = {
            "model": OPENAI_MODEL,
            "input": _build_prompt(message, context),
            "temperature": 0.4,
        }
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=OPENAI_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("output_text")
        return content.strip() if content else _build_answer(context)
    except Exception:
        return _build_answer(context)


def _serialize_messages(messages):
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "context": msg.context,
            "created_at": msg.created_at.isoformat(),
        }
        for msg in messages
    ]


class RagChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response({"detail": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        country_iso2 = (request.data.get("country_iso2") or "").strip().upper() or None
        conversation_id = request.data.get("conversation_id")

        country = _resolve_country(country_iso2, message)

        if country_iso2 and not country:
            return Response({"detail": "invalid country_iso2"}, status=status.HTTP_400_BAD_REQUEST)

        if country:
            country_payload = {
                "iso2": country.iso2,
                "name_ko": country.name_ko,
                "name_en": country.name_en,
            }
        else:
            country_payload = None

        fx = _get_latest_fx(country.iso2) if country else None
        flight = _get_latest_flight(country.iso2) if country else None
        alert = _get_alert(country.iso2) if country else None

        documents = _search_documents(message, iso2=country.iso2 if country else None)

        popular = [] if country else _get_popular_countries()
        user_profile = _get_user_profile(request.user)

        context = {
            "country": country_payload,
            "alert": alert,
            "fx": fx,
            "flight": flight,
            "flights": _get_recent_flights() if not country else [],
            "news": documents.get("news", []),
            "blogs": documents.get("blogs", []),
            "popular": popular,
            "user": user_profile,
        }

        answer = _generate_answer(message, context)

        conversation = None
        if request.user.is_authenticated:
            if conversation_id:
                conversation = ChatbotConversation.objects.filter(
                    id=conversation_id,
                    user=request.user,
                ).first()
            if not conversation:
                conversation = ChatbotConversation.objects.create(user=request.user)
            conversation.last_message_at = timezone.now()
            conversation.save(update_fields=["last_message_at"])

            ChatbotMessage.objects.create(
                conversation=conversation,
                role="user",
                content=message,
            )
            ChatbotMessage.objects.create(
                conversation=conversation,
                role="assistant",
                content=answer,
                context=context,
            )

        response = {
            "answer": answer,
            "context": context,
            "conversation_id": conversation.id if conversation else None,
        }
        return Response(response, status=status.HTTP_200_OK)


class ChatbotHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversation_id = request.query_params.get("conversation_id")

        conversation = None
        if conversation_id:
            conversation = ChatbotConversation.objects.filter(
                id=conversation_id,
                user=request.user,
            ).first()
        if not conversation:
            conversation = (
                ChatbotConversation.objects
                .filter(user=request.user)
                .order_by("-last_message_at", "-id")
                .first()
            )

        if not conversation:
            return Response(
                {"conversation_id": None, "messages": []},
                status=status.HTTP_200_OK,
            )

        messages = (
            ChatbotMessage.objects
            .filter(conversation=conversation)
            .order_by("created_at", "id")
        )

        return Response(
            {
                "conversation_id": conversation.id,
                "messages": _serialize_messages(messages),
            },
            status=status.HTTP_200_OK,
        )


class ChatbotConversationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = (
            ChatbotConversation.objects
            .filter(user=request.user)
            .order_by("-last_message_at", "-id")
        )
        results = []
        for convo in conversations:
            first_user_message = (
                ChatbotMessage.objects
                .filter(conversation=convo, role="user")
                .order_by("created_at", "id")
                .first()
            )
            results.append(
                {
                    "id": convo.id,
                    "started_at": convo.started_at.isoformat(),
                    "last_message_at": convo.last_message_at.isoformat(),
                    "preview": first_user_message.content if first_user_message else "",
                }
            )

        return Response({"results": results}, status=status.HTTP_200_OK)


class ChatbotConversationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, conversation_id):
        conversation = ChatbotConversation.objects.filter(
            id=conversation_id,
            user=request.user,
        ).first()
        if not conversation:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatbotConversationClearAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        ChatbotConversation.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
