from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser 

from google.cloud import storage 
import uuid
from datetime import timedelta 
from urllib.parse import urlparse 
import os 
from django.conf import settings
from django.db import transaction
from .models import LetterImages

bucket_name=settings.BUCKET_NAME

"""
파일 객체를 GCS에 업로드하고 저장된 blob_name을 반환
"""
def upload_image_to_gcs(file, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # 고유 파일명 생성
    filename = f'letter-images/{uuid.uuid4()}_{file.name}'
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=file.content_type)

    return filename # 저장된 gcs 경로 반환


"""
GCS에 저장된 blob_name에 대한 서명된 URL 생성
"""
def generate_signed_url(bucket_name, blob_name, expiration_minutes=10):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    if blob.exists(): 
        url = blob.generate_signed_url(
            version='v4',
            expiration=timedelta(minutes=expiration_minutes),
            method='GET'
        )

        return url
    
    return None


"""
GCS 전체 URL에서 버킷명 이후의 blob name(경로)만 추출하는 함수
"""
def extract_blob_name_from_image_url(image_url, bucket_name):
    parsed_url = urlparse(image_url)
    path = parsed_url.path.lstrip('/')
    return path


"""
GCS에서 지정된 blob(이미지 파일)을 삭제
"""
def delete_image_from_gcs(blob_name, bucket_name):
    try:
        client = storage.Client() 
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if blob.exists():
            blob.delete()
            # print(f"GCS에서 이미지가 성공적으로 삭제되었습니다.")
            return True
        
        else:
            # print(f"해당 blob_name을 가진 이미지가 GCS에 존재하지 않습니다.")
            return False
    except Exception as e:
        # print(f"GCS에서 이미지를 삭제하는데 실패했습니다.: {e}")
        return False



# --------- API 함수 뷰 ---------
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser]) # 파일 업로드를 위한 파서 지정
def image_upload_view(request):
    """
    POST api/images/ -> 이미지 업로드
    """
    if 'file' not in request.data:
        return Response({'error': '파일이 존재하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    file_obj = request.data['file']
    letter_id = request.data.get('id')

    try:
        # 1. GCS에 이미지 업로드
        uploaded_blob_name = upload_image_to_gcs(file_obj, bucket_name) 

        # 2. DB에 메타데이터 저장
        with transaction.atomic(): # DB 트랜젝션 시작작
            LetterImages.objects.create(
            blob_name=uploaded_blob_name,
            original_filename=file_obj.name,
            file_size=file_obj.size,
            content_type=file_obj.content_type,
            # uploaded_at은 auto_now_add=True 이므로 자동 설정
            letter_id=letter_id
        )

        return Response(
            {'message': '성공적으로 이미지를 GCS에 업로드하고, 메타데이터를 저장했습니다.', 'blob_name': uploaded_blob_name},
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        print(f"GCS에 이미지 업로드 또는 메타데이터 저장 중 문제가 발생했습니다.: {e}")
        # 업로드 실패 시 GCS에 잔여 파일이 남지 않도록 롤백 시도 
        if 'uploaded_blob_name' in locals(): # uploaded_blob_name이 정의되어 있다면
            delete_image_from_gcs(uploaded_blob_name, bucket_name) # GCS에서 삭제 시도
        return Response(
            {'error': f'GCS에 이미지 업로드 또는 메타데이터 저장 중 문제가 발생했습니다: {e}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'DELETE'])
def image_detail_view(request, blob_name):
    """
    GET api/images/<path:blob_name> -> signed URL 가져오기
    DELETE api/images/<path:blob_name> -> 이미지 삭제
    """
    if not blob_name:
        return Response({'error': 'Blob name이 URL에 존재하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # DB에서 해당 이미지 메타데이터 조회 
        image_metadata = LetterImages.objects.get(blob_name=blob_name)
    except LetterImages.DoesNotExist:
        # DB에 메타데이터가 없을 경우
        return Response(
            {'error': '요청하신 이미지를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        signed_url = generate_signed_url(bucket_name, blob_name)
        if signed_url:
            return Response({'signed_url': signed_url})
        else:
            # DB에는 있지만 GCS에 없거나, GCS 오류로 signed URL 생성 실패
            return Response(
                {'error': 'Signed URL 생성에 실패했습니다.'},
                status=status.HTTP_404_NOT_FOUND 
            )

    elif request.method == 'DELETE':
        try:
            with transaction.atomic():
                # DB 메타데이터 삭제
                image_metadata.delete() 

                # DB 삭제가 성공하면 GCS 파일 삭제
                gcs_deleted = delete_image_from_gcs(blob_name, bucket_name)
                
                if not gcs_deleted:
                    # GCS 삭제가 실패하면, DB 트랜잭션을 강제로 롤백하기 위해 예외 발생
                    raise Exception(f"GCS에서 이미지를 삭제하던 도중 오류가 발생했습니다.")
            return Response(
                {'message': '성공적으로 이미지를 GCS에 업로드하고, 메타데이터를 저장했습니다.'},
                status=status.HTTP_204_NO_CONTENT) # GCS와 DB 모두 성공적으로 삭제
            
        except Exception as db_e:
            # GCS는 삭제되었는데 DB 삭제 실패
            # print(f"이미지 메타데이터 삭제 중 문제가 발생했습니다.: {db_e}")
            return Response(
                {'error': 'GCS에서 이미지는 삭제되었으나, 데이터베이스 메타데이터 삭제에 실패했습니다. 관리자에게 문의하세요.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR 
            )
    else:
        # GCS 삭제 자체가 실패한 경우
        return Response(
            {'error': '이미지를 삭제하던 도중 문제가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )