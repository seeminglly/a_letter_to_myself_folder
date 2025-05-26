from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
# ✅ 수정
from schedule.routine_service.models import LetterRoutine, SpecialDateRoutine
#from emotions.utils import analyze_emotion_for_letter -> 서비스 따로 돌릴 때 경로
#모놀리식으로 실행시킬 때 경로
from emotion_analysis.emotions.utils import analyze_emotion_for_letter

from .models import Letters
from .forms import LetterForm
from . import storage
from django.utils.timezone import now  # 현재 날짜 가져오기
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import openai
import os
from django.conf import settings
openai.api_key = os.getenv("OPENAI_API_KEY")
# Create your views here.
# Create your views here.
def home(request):
    return render(request, 'myapp/index.html')

# 1️⃣ 편지 작성 뷰
def write_letter(request):
    if request.method == 'POST':
        form = LetterForm(request.POST, request.FILES)
        if form.is_valid():
            letter = form.save(commit=False)  # ✅ 데이터 저장 전에 추가 설정
            letter.user = request.user  # 🔥 작성자를 현재 로그인한 사용자로 설정
            letter.category = 'future' # 기본적으로 미래 카테고리로 분류

            # 첨부된 이미지가 있을 경우 GCS에 업로드
            if request.FILES.get('image'):
                file = request.FILES['image']
                gcs_url = storage.upload_image_to_gcs(file, settings.BUCKET_NAME)
                letter.image_url = gcs_url  # GCS 경로 저장

            letter.save()
            analyze_emotion_for_letter(letter)
            return redirect('letters:letter_list')  # 편지 목록 페이지로 이동
            #네임스페이스 letters:를 꼭 붙여줘야 Django가 letter_list 뷰를 찾을 수 있음

    else:
        form = LetterForm()
        
    return render(request, 'letters/writing.html', {'form': form})


# 2️⃣ 작성된 편지 목록 보기
@login_required(login_url='login') #로그인 안 하면 로그인 페이지로 이동
def letter_list(request):
    letters = Letters.objects.filter(user=request.user)


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


#개별 편지 상세보기api
@login_required
def letter_json(request, letter_id):
    letter = get_object_or_404(Letters, id=letter_id)

    # 이미지가 첨부된 편지의 경우 signed URL 생성
    signed_url = None
    print(letter.image_url)
    if letter.image_url:
        blob_name = storage.extract_blob_name_from_image_url(letter.image_url, settings.BUCKET_NAME)
        signed_url = storage.generate_signed_url(
            bucket_name=settings.BUCKET_NAME,
            blob_name = blob_name,
            expiration_minutes = 10
        )
        print(signed_url)

    data = {
        'id':letter.id,
        'title': letter.title,
        'content': letter.content,
        'letter_date': letter.open_date.strftime("%Y-%m-%d"), #개봉 가능 날짜
        'image_url': signed_url # 첨부된 이미지가 없는 경우 signed_url은 None
    }

    return JsonResponse(data)


# 4️⃣ 편지 삭제 API (내부 API)
# @csrf_exempt # 실제 API로 분리 시 CSRF 처리 방식 변경 필요 (예: Token Authentication)
@login_required # API도 로그인 필요
@require_http_methods(["DELETE"]) # DELETE 요청만 허용
def delete_letter_api_internal(request, letter_id):
    try:
        # 본인이 작성한 편지만 삭제 가능하도록 user 조건 추가
        letter = get_object_or_404(Letters, id=letter_id, user=request.user)

        # GCS에서 이미지 파일 삭제 (이미지가 있는 경우)
        if letter.image_url:
            blob_name = storage.extract_blob_name_from_image_url(letter.image_url, settings.BUCKET_NAME)
            if blob_name:
                try:
                    storage.delete_image_from_gcs(blob_name, settings.BUCKET_NAME)
                except Exception as e:
                    # GCS 삭제 실패 시 로깅 등 예외 처리 (편지 DB 삭제는 계속 진행될 수 있도록)
                    print(f"Error deleting image from GCS: {e}") # 실제 운영에서는 로깅 사용

        letter.delete()

        return JsonResponse({'status': 'success', 'message': '편지가 성공적으로 삭제되었습니다.'}, status=200)
    
    except Letters.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '해당 편지를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        # 기타 예외 처리
        print(f"Error deleting letter: {e}") # 실제 운영에서는 로깅 사용
        return JsonResponse({'status': 'error', 'message': '편지 삭제 중 오류가 발생했습니다.'}, status=500)