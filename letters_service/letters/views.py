from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
#from emotions.utils import analyze_emotion_for_letter -> 서비스 따로 돌릴 때 경로
#from routines.models import LetterRoutine, SpecialDateRoutine 
#from emotions.utils import analyze_emotion_for_letter
from .models import Letters
from .forms import LetterForm
from django.utils.timezone import now  # 현재 날짜 가져오기
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import openai
import os
from django.urls import reverse # 내부 API 호출 URL 생성
from django.conf import settings

import requests # 외부 API 호출용

# import json # POST, PUT 요청의 JSON 본문을 파싱하기 위해
# import requests # 다른 내부 API (예: 감정 분석) 호출을 위해

openai.api_key = os.getenv("OPENAI_API_KEY")

# 개발용 가짜 유저 주입
from django.contrib.auth import get_user_model

User = get_user_model()

fake_user = User.objects.first()
letters = Letters.objects.filter(user=fake_user)
#

def home(request):
    # 이 뷰는 'myapp/index.html'을 렌더링하며, letters 서비스의 핵심 HTML 분리와는 별개일 수 있습니다.
    # 새로운 프론트엔드 서비스가 자체 홈페이지를 가질 것이므로, 이 뷰의 역할은 재검토될 수 있습니다.
    # 지금은 그대로 둡니다.
    return render(request, 'myapp/index.html')

# 1️⃣ 편지 작성 뷰
# @login_required(login_url='/auth/login/')  # 👈 직접 로그인 URL 지정 (auth 마이크로서비스)
def write_letter(request):
    # 개발용 가짜 유저 지정
    fake_user = User.objects.first()
    if not fake_user:
        return JsonResponse({"error:" "테스트 유저 없음"})

    if request.method == 'POST':
        form = LetterForm(request.POST, request.FILES)
        if form.is_valid():
            letter = form.save(commit=False)  # ✅ 데이터 저장 전에 추가 설정
            letter.user = fake_user # 원래는 request.user  # 🔥 작성자를 현재 로그인한 사용자로 설정
            letter.category = 'future' # 기본적으로 미래 카테고리로 분류

            gcs_blob_name_for_letter = None # API 응답으로 받을 GCS 파일 경로(blob_name)


            if request.FILES.get('image'):
                file_to_upload = request.FILES['image']
                
                # --- Storage API 호출: 이미지 업로드 ---
                try:
                    # settings.py에 정의된 LETTER_STORAGE_SERVICE_BASE_URL 사용
                    storage_api_base_url = settings.LETTER_STORAGE_SERVICE_BASE_URL.rstrip('/')
                    upload_api_path = "/api/images/" # storage 서비스의 실제 업로드 API 경로
                    full_upload_api_url = f"{storage_api_base_url}{upload_api_path}"
                    
                    files_payload = {'file': (file_to_upload.name, file_to_upload, file_to_upload.content_type)}
                    data_payload = {'id': str(letter.id)} # letter.id가 존재할 때
                    
                    response = requests.post(full_upload_api_url, files=files_payload) # data=data_payload 추가 가능
                    response.raise_for_status() 
                    
                    upload_response_data = response.json()

                    if upload_response_data.get('blob_name'):
                        gcs_blob_name_for_letter = upload_response_data.get('blob_name')
                        print(f"Storage Service API: 이미지 업로드 성공, blob_name: {gcs_blob_name_for_letter}")
                    else:
                        print(f"Storage Service API: 이미지 업로드 실패 - {upload_response_data.get('message')}")
                except requests.exceptions.RequestException as e:
                    print(f"Storage Service API: 이미지 업로드 호출 오류 - {e}")
                except Exception as e: # 더 넓은 범위의 예외 처리
                    print(f"Storage Service API: 이미지 업로드 중 기타 오류 - {e}")

            if gcs_blob_name_for_letter:
                letter.image_url = gcs_blob_name_for_letter # 모델에는 blob_name 또는 전체 GCS URL 저장 (API 응답에 따라)

            letter.save()
           # analyze_emotion_for_letter(letter) # api 호출로 수정하기

           ##### 기존 렌더링 코드 ######
            return redirect('letters:letter_list')  # 편지 목록 페이지로 이동
    else:
        form = LetterForm()
        
    return render(request, 'letters/writing.html', {'form': form})


# 2️⃣ 작성된 편지 목록 보기
# @login_required(login_url='/auth/login/') # 로그인 안 된 경우 이 URL로 리디렉션
def letter_list(request):

    # 개발용 가짜 유저 지정
    fake_user = User.objects.first()
    if not fake_user:
        return JsonResponse({"error": "테스트용 유저가 없습니다."})
    letters = Letter.objects.filter(user=fake_user)   # 원래는 (user=request.user) 
    #

    today = datetime.now().date()
    
    for letter in letters:
        if letter.open_date == today:
            letter.category = 'today'
        elif letter.open_date > today:
            letter.category = 'future'
        else:
            letter.category = 'past'
        letter.save()  # ✅ DB에 저장!


    return render(request, 'letters/letter_list.html', {
        'letters': letters,
    })


# 개별 편지 상세보기 api
# @login_required(login_url='/auth/login/')
def letter_json(request, letter_id):
    # letter = get_object_or_404(Letters, id=letter_id, user=request.user) # 로그인 기능 복원 시
    letter = get_object_or_404(Letters, id=letter_id)

    signed_url_from_api = None
    if letter.image_url: # image_url에 GCS 내의 blob_name이 저장되어 있다고 가정
        blob_name = letter.image_url 
        # --- Storage API 호출: 서명된 URL 생성 ---
        try:
            storage_api_base_url = settings.LETTER_STORAGE_SERVICE_BASE_URL.rstrip('/')
            # storage 서비스의 실제 get-image-url API 경로 사용
            get_url_api_path = f"/api/images/{blob_name}/" # 경로 마지막 / 유의
            full_get_url_api_url = f"{storage_api_base_url}{get_url_api_path}"
            
            response = requests.get(full_get_url_api_url)
            response.raise_for_status()
            
            url_response_data = response.json()

            if url_response_data.get('signed_url'):
                signed_url_from_api = url_response_data.get('signed_url')
                print(f"Storage Service API: Signed URL '{signed_url_from_api}' for blob '{blob_name}'")
            else:
                print(f"Storage Service API: Signed URL 생성 실패 - {url_response_data.get('message')}")
        except requests.exceptions.RequestException as e:
            print(f"Storage Service API: Signed URL 호출 오류 - {e}")
        except Exception as e:
            print(f"Storage Service API: Signed URL 생성 중 기타 오류 - {e}")

    data = {
        'id':letter.id,
        'title': letter.title,
        'content': letter.content,
        'letter_date': letter.open_date.strftime("%Y-%m-%d"), #개봉 가능 날짜
        'image_url': signed_url_from_api # API로부터 받은 서명된 URL (이전 코드에 signed_url로 되어 있던 변수명 수정)
    }
    return JsonResponse(data)


# 4️⃣ 편지 삭제 API (내부 API)
# @csrf_exempt # 실제 API로 분리 시 CSRF 처리 방식 변경 필요 (예: Token Authentication)
# @login_required # 로그인 필요
@require_http_methods(["DELETE"]) # DELETE 요청만 허용
def delete_letter_api_internal(request, letter_id):
    try:
            # 개발용 가짜 유저 지정
        fake_user = User.objects.first()
        # letter = get_object_or_404(Letters, id=letter_id, user=request.user)
        letter = get_object_or_404(Letters, id=letter_id) # 테스트용 유저 정보 뺀 레터
        image_blob_name_to_delete = letter.image_url # DB에서 편지 삭제 전에 blob 이름 저장

        letter.delete() # DB에서 편지 레코드 삭제

        if image_blob_name_to_delete:
            try:
                storage_api_base_url = settings.LETTER_STORAGE_SERVICE_BASE_URL.rstrip('/')
                # storage 서비스의 실제 이미지 삭제 API 경로
                # 이전에 storage 서비스의 image_detail_view가 /api/images/<blob_name>/ DELETE를 처리한다고 가정
                delete_api_path = f"/api/images/{image_blob_name_to_delete}/" 
                full_delete_api_url = f"{storage_api_base_url}{delete_api_path}"

                print(f"Calling Storage Service API (Delete Image): DELETE {full_delete_api_url}")
                response = requests.delete(full_delete_api_url)

                if response.status_code == 204: # 성공 (No Content)
                    print(f"Storage Service API: 이미지 '{image_blob_name_to_delete}' 삭제 성공 (204 No Content).")
                elif response.ok: # 다른 2xx 성공 코드 (예: 200 OK 와 함께 메시지)
                    try:
                        delete_response_data = response.json() # 이 경우에만 JSON 파싱 시도
                        print(f"Storage Service API: 이미지 '{image_blob_name_to_delete}' 삭제 응답 (상태코드 {response.status_code}): {delete_response_data}")
                    except ValueError: # requests.exceptions.JSONDecodeError의 부모 (응답 본문이 JSON이 아닐 때)
                        print(f"Storage Service API: 이미지 '{image_blob_name_to_delete}' 삭제 성공 (상태코드: {response.status_code}), 응답 본문 JSON 아님: {response.text}")
                else: # 2xx가 아닌 경우 (오류 상태 코드)
                    # 여기서 HTTPError 예외를 발생시켜 아래 except 블록에서 처리
                    response.raise_for_status() 
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"Info (delete_letter_api_internal): Image '{image_blob_name_to_delete}' not found in GCS or Storage Service (HTTP 404).")
                else:
                    print(f"Error calling Storage API (Delete Image HTTPError): {e.response.status_code} {e.response.text if e.response else 'No response text'}")
            except requests.exceptions.RequestException as e: # 네트워크 등 기타 요청 오류
                print(f"Error calling Storage API (Delete Image RequestException): {e}")
            except ValueError: # JSONDecodeError (위에서 처리했지만, 만약을 위해)
                 print(f"Storage Service API: 이미지 삭제 응답이 성공적이었으나(상태코드: {response.status_code}), JSON 형식이 아님: {response.text}")
            except Exception as e:
                print(f"An unexpected error occurred during image delete API call: {e}")
            
        return JsonResponse({'status': 'success', 'message': '편지가 성공적으로 삭제되었습니다.'}, status=200)
    except Letters.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '해당 편지를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        print(f"Error deleting letter (main try-except): {e}")
        return JsonResponse({'status': 'error', 'message': '편지 삭제 중 오류가 발생했습니다.'}, status=500)
