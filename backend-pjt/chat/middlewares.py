import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        print(f"✅ 사용자 조회 성공: {user.email} (ID: {user_id})")
        return user
    except User.DoesNotExist:
        print(f"❌ 사용자 없음: ID {user_id}")
        return AnonymousUser()
    except Exception as e:
        print(f"❌ 사용자 조회 에러: {e}")
        return AnonymousUser()

class JwtAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 쿼리 스트링 추출
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        print(f"\n🔌 WebSocket 연결 시도")
        print(f"📌 토큰 존재: {bool(token)}")
        
        if token:
            try:
                # payload['user_id'] 가 SimpleJWT의 기본값입니다.
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                print(f"✅ JWT 디코딩 성공, user_id: {user_id}")
                scope["user"] = await get_user(user_id)
            except jwt.ExpiredSignatureError:
                print(f"❌ JWT 토큰 만료됨")
                scope["user"] = AnonymousUser()
            except jwt.InvalidTokenError as e:
                print(f"❌ JWT 토큰 유효하지 않음: {e}")
                scope["user"] = AnonymousUser()
            except Exception as e:
                print(f"❌ JWT 처리 중 에러: {e}")
                scope["user"] = AnonymousUser()
        else:
            print(f"⚠️  토큰 없음 - 익명 사용자로 처리")
            scope["user"] = AnonymousUser()
            
        print(f"📊 최종 user: {scope['user']}")
        print(f"📊 is_anonymous: {scope['user'].is_anonymous}\n")
        
        return await self.inner(scope, receive, send)
