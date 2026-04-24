from django.db import models
from django.conf import settings

class Post(models.Model):
    """금융 자산별 토론 게시글"""
    # 1. asset_id: JSON 자산 id와 매칭
    asset_id = models.CharField(max_length=50)
    
    # 2. title, content
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # 3. author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    # 4. 시간 관련 필드 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
