from django.db import models
from travel.models import Country

class DestinationBlog(models.Model):
    """
    여행 블로그 메타데이터
    - 본문은 저장하지 않고 링크만 유지
    """

    # 연관 국가
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="blogs",
        db_column="iso2"
    )

    # 게시글 제목
    title = models.TextField()

    # 원문 URL (중복 방지)
    url = models.TextField(unique=True)

    # 발행 시각
    published_at = models.DateTimeField()

    class Meta:
        db_table = "destination_blog"
        indexes = [
            # 국가 + 최신순 조회 최적화
            models.Index(fields=["country", "published_at"]),
        ]


class DestinationNews(models.Model):
    """
    여행 뉴스 메타데이터
    - Elasticsearch 색인 대상
    """

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="news",
        db_column="iso2"
    )

    title = models.TextField()
    url = models.TextField(unique=True)
    published_at = models.DateTimeField()

    class Meta:
        db_table = "destination_news"
        indexes = [
            models.Index(fields=["country", "published_at"]),
        ]