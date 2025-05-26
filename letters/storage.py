from google.cloud import storage
from datetime import timedelta
from urllib.parse import urlparse
import uuid

def upload_image_to_gcs(file, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # 고유 파일명 생성
    filename = f'letter-images/{uuid.uuid4()}_{file.name}'
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=file.content_type)

    return filename # 저장된 gcs 경로

def generate_signed_url(bucket_name, blob_name, expiration_minutes=10): # blob_name: GCS에 저장된 파일 경로로
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version='v4',
        expiration=timedelta(minutes=expiration_minutes),
        method='GET'
    )

    return url

# letters.image_url(gcs 전체 url)에서 버킷명 이후의 blob name(경로)만 추출하는 함수
def extract_blob_name_from_image_url(image_url, bucket_name):
    parsed_url = urlparse(image_url)

    path = parsed_url.path.lstrip('/')  # e.g., bucket/images/abc.png
    return path  # blob_name 반환 (e.g., images/abc.png)