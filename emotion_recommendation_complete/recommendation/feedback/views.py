# feedback/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

#마이크로
from ..feedback.models import Feedback

#모놀리식
#from emotion_recommendation.recommendation.feedback.models import Feedback




@require_POST
@login_required
def save_feedback(request):
    item_title = request.POST.get("item_title")
    item_type = request.POST.get("item_type")
    feedback = request.POST.get("feedback")

    Feedback.objects.update_or_create(
        user=request.user,
        item_title=item_title,
        item_type=item_type,
        defaults={"feedback": feedback}
    )

    return JsonResponse({
        "message": f"{'좋아요' if feedback == 'like' else '별로예요'}로 저장되었습니다."
    })
