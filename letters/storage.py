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



def delete_image_from_gcs(blob_name, bucket_name):
    """GCS에서 지정된 blob(이미지 파일)을 삭제합니다."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if blob.exists():
            blob.delete()
            print(f"Blob {blob_name} deleted from bucket {bucket_name}.") # 성공 로그
            return True
        else:
            print(f"Blob {blob_name} not found in bucket {bucket_name}.") # 파일 없음 로그
            return False
    except Exception as e:
        # 실제 운영 환경에서는 여기서 예외를 다시 raise 하거나, False를 반환하는 등
        # 호출한 쪽에서 실패를 인지할 수 있도록 처리하는 게 좋다.
        print(f"Exception in delete_image_from_gcs for blob {blob_name}: {e}") # 예외 발생 로그
        # raise # 또는 return False
        return False # 예외 발생 시 False 반환하여 호출 측에서 인지하도록