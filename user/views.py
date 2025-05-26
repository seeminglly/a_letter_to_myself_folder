from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import ProfileForm, ProfilePictureForm
from .models import Profile, UserProfile
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def update_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        picture_form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)

        if profile_form.is_valid() and picture_form.is_valid():
            profile = profile_form.save(commit=False)  # ✅ 수정 전 저장 중지
            profile.user = request.user                # ✅ 필요한 경우 수동 연결
            profile.save()                             # ✅ 수동 저장

            picture_form.save()
            return redirect('mypage')

        else:
            print(profile_form.errors)  # 오류 출력
            print(picture_form.errors)
    else:
        profile_form = ProfileForm(instance=profile)
        picture_form = ProfilePictureForm(instance=user_profile)

    context = {
        'profile_form': profile_form,
        'picture_form': picture_form,
        'profile': profile,
        'user_profile': user_profile
    }
    return render(request, 'commons/update_profile.html', context)
