from rest_framework import serializers


class UserEventCreateSerializer(serializers.Serializer):
    """
    프론트엔드 → Django로 들어오는
    행동 로그 데이터 검증용 Serializer
    """

    # 국가 코드 (ISO2 기준)
    country_code = serializers.CharField(max_length=2)

    # 프론트에서 정의한 이벤트 타입
    event_type = serializers.CharField()

    # 체류 시간, 좋아요 여부(true/false) 등
    value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
