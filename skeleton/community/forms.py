# community/forms.py (새로 생성)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nickname', 'profile_image', 'interest_stocks',)

# community/views.py
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # F502: 가입 성공 시 자동 로그인
            return redirect('community:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'community/signup.html', {'form': form})