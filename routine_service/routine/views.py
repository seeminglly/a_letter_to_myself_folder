from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import LetterRoutine, SpecialDateRoutine
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, localtime
from datetime import datetime, timedelta

#@login_required(login_url='login')


# 뷰 함수 안에 임시 유저 설정
# 실제 서비스에선 쓰면 안 됨!!!!!!!!!!!!!!!!
from django.contrib.auth import get_user_model



@csrf_exempt
def save_routine(request):
    
    
    User = get_user_model()
    
    #임시 유저 할당!!
    request.user = User.objects.first()
    
    
    days = range(1, 32)
    routine = None
    special_routine = None

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

    routines = LetterRoutine.objects.filter(user=request.user)
    specialDays = SpecialDateRoutine.objects.filter(user=request.user)

    lists = {
        "days": days,
        "routines": routines,
        "specialDays": specialDays,
        "routine_id": routine.id if routine else None,
        "special_routine_id": special_routine.id if special_routine else None
    }

    #return render(request, "routines/routine.html", lists)

    return JsonResponse({
        "routine_id": routine.id if routine else None,
        "special_routine_id": special_routine.id if special_routine else None
    })

WEEKDAYS = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}

#@login_required
def get_routine_events(request):
    
    
    
    
    
    User = get_user_model()
    
    #임시 유저 할당!!
    request.user = User.objects.first()
    
    
    
    user = request.user
    routines = LetterRoutine.objects.filter(user=user)
    special_dates = SpecialDateRoutine.objects.filter(user=user)

    
    today = datetime.today().date()
    events = []

    for routine in routines:
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


def get_today_routines(request):
    now_dt = localtime(now()).replace(second=0, microsecond=0)
    today = now_dt.strftime("%A")
    current_day = now_dt.day
    window_start = (now_dt - timedelta(minutes=1)).time()
    window_end = (now_dt + timedelta(minutes=1)).time()
    
    
    User = get_user_model()
    
    user = User.objects.first()  # 임시 사용자
    
    
    

    routines = LetterRoutine.objects.filter(user=user, time__range=(window_start, window_end))
    result = []

    for r in routines:
        if r.routine_type == 'weekly' and r.day_of_week == today:
            result.append({
                "user_email": r.user.email,
                "username": r.user.username,
                "time": str(r.time)
            })
        elif r.routine_type == 'monthly' and r.day_of_month == current_day:
            result.append({
                "user_email": r.user.email,
                "username": r.user.username,
                "time": str(r.time)
            })

    return JsonResponse(result, safe=False)

@csrf_exempt
def test_routines_for_scheduler(request):
    routines = LetterRoutine.objects.all()[:3]  # 일부만 테스트용으로
    result = []

    for r in routines:
        result.append({
            "email": "dummy@example.com",   # 실제 email 없어도 됨
            "username": "TestUser",
            "time": str(r.time),
        })

    return JsonResponse(result, safe=False)