from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from .models import LetterRoutine, SpecialDateRoutine
from django.utils.timezone import now  # 현재 날짜 가져오기
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta


# Create your views here.
#편지 루틴 만들기
@login_required(login_url='commons:login')
@csrf_exempt
def save_routine(request):
    days = range(1, 32)
    routine = None  # ✅ 기본값 설정
    special_routine = None  # ✅ 기본값 설정

    if "title" in request.POST:
        title = request.POST.get("title") or "기본 루틴 제목"
        routine_type = request.POST.get("routine_type")
        day_of_week = request.POST.get("day_of_week") if routine_type == "weekly" else None
        day_of_month = request.POST.get("day_of_month") if routine_type == "monthly" else None
        time = request.POST.get("routine_time")

        routine = LetterRoutine.objects.create(
            user=request.user,
            title=title,
            routine_type=routine_type,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            time=time
        )

    elif "name" in request.POST:
        name = request.POST.get("name")
        date = request.POST.get("date")

        special_routine = SpecialDateRoutine.objects.create(
            user=request.user,
            name=name,
            date=date
        )

    # ✅ 내 루틴 보기
    routines = LetterRoutine.objects.filter(user=request.user)
    specialDays = SpecialDateRoutine.objects.filter(user=request.user)

    lists = {
        "days": days,
        "routines": routines,
        "specialDays": specialDays,
        "routine_id": routine.id if routine else None,  # ✅ `None` 체크 추가
        "special_routine_id": special_routine.id if special_routine else None  # ✅ `None` 체크 추가
    }

    return render(request, "routines/routine.html", lists)





WEEKDAYS = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
}
@login_required
def get_routine_events(request):
    """ 사용자의 편지 루틴을 JSON 데이터로 반환 """
    user = request.user
    routines = LetterRoutine.objects.filter(user=user)
    special_dates = SpecialDateRoutine.objects.filter(user=user)

    today = datetime.today().date()
    events = []

    # 루틴 처리
    for routine in routines:
        # 주간 루틴
        if routine.routine_type == "weekly":
            weekday = routine.day_of_week
            if weekday:
                weekday_num = WEEKDAYS[weekday]
                next_date = today + timedelta(days=(weekday_num - today.weekday() + 7) % 7)
                for i in range(52):
                    events.append({
                        "id": routine.id,
                        "title": routine.title,
                        "start": (next_date + timedelta(weeks=i)).strftime("%Y-%m-%d"),
                        "allDay": True
                    }) 

        # 월간 루틴
        elif routine.routine_type == "monthly":
            for month in range(1, 13):
                try:
                    events.append({
                        "id": routine.id,
                        "title": routine.title,
                        "start": f"2025-{month:02d}-{routine.day_of_month:02d}",
                        "allDay": True
                    })
                except:
                    continue

    # 🎉 기념일(SpecialDateRoutine) 처리
    for special in special_dates:
        events.append({
            "title": f"🎉 {special.name}",
            "start": special.date.strftime("%Y-%m-%d"),
            "allDay": True,
            "color": "#3399ff"
        })

    return JsonResponse(events, safe=False)

def delete_routine(request, pk):
    try:
        routine = get_object_or_404(LetterRoutine, pk=pk, user=request.user)
        routine.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

