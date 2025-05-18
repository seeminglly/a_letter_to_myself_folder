from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
# ✅ 수정
from schedule.routine_service.models import LetterRoutine, SpecialDateRoutine
from emotions.utils import analyze_emotion_for_letter
from .models import Letters
from .forms import LetterForm
from django.utils.timezone import now  # 현재 날짜 가져오기
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import openai
import os
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
            letter.save()
            analyze_emotion_for_letter(letter)
            return redirect('letters:letter_list')  # 편지 목록 페이지로 이동
            #네임스페이스 letters:를 꼭 붙여줘야 Django가 letter_list 뷰를 찾을 수 있음
    else:
        form = LetterForm()
        
    return render(request, 'letters/writing.html', {'form': form})


# 2️⃣ 작성된 편지 목록 보기
@login_required(login_url='commons:login') #로그인 안 하면 로그인 페이지로 이동
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
    data = {
        'id':letter.id,
        'title': letter.title,
        'content': letter.content,
        'letter_date': letter.open_date.strftime("%Y-%m-%d"), #개봉 가능 날짜
    }
    return JsonResponse(data)
