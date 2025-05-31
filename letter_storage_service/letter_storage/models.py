from django.db import models

class LetterImages(models.Model):
    """
    편지에 첨부된 이미지의 메타데이터를 저장.
    실제 이미지는 GCS에 저장된다.
    """
    # GCS 버킷 내의 파일 경로
    # letter-service는 이 blob_name을 사용하여 이미지를 조회/삭제 요청
    blob_name = models.CharField(
        max_length=500, 
        unique=True, 
        help_text="GCS에 저장된 파일의 고유 경로"
    )
    
    # 원본 파일명 (사용자가 업로드한 파일명)
    original_filename = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="사용자가 업로드한 원본 파일의 이름"
    )
    
    # 파일 크기 (바이트 단위)
    file_size = models.PositiveIntegerField(
        help_text="이미지 파일의 크기 (바이트)"
    )
    
    # 업로드 시간
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="이미지가 GCS에 업로드된 시간"
    )
    
    # 이미지 타입 (e.g., image/jpeg, image/png)
    content_type = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="이미지 파일의 Content-Type (MIME 타입)"
    )
    
    # 편지 ID
    letter_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="편지 고유 ID"
    )

    class Meta:
        verbose_name = "첨부 이미지"
        verbose_name_plural = "첨부 이미지들"
        ordering = ['-uploaded_at'] # 최신 이미지가 먼저 오도록 정렬

    def __str__(self):
        return f"{self.original_filename} ({self.blob_name})"