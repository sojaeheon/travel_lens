from rest_framework import serializers
from .models import FavoriteCountry, UserEvent  # UserEvent 추가
from travel.models import Country

# 1. 📌 기존 행동 로그(UserEvent) 전용 시리얼라이저 (views.py에서 이걸 쓰고 있음)
class UserEventCreateSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    country_code = serializers.CharField()
    value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

# 2. 📌 내가 찜한 나라 목록 조회용 시리얼라이저
class FavoriteCountrySerializer(serializers.ModelSerializer):
    name_en = serializers.ReadOnlyField(source='country.name_en')
    name_ko = serializers.ReadOnlyField(source='country.name_ko')
    iso2 = serializers.ReadOnlyField(source='country.iso2')

    class Meta:
        model = FavoriteCountry
        fields = ['id', 'iso2', 'name_en', 'name_ko', 'created_at']
        read_only_fields = ['created_at']