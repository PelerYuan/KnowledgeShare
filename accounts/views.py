import os

from PIL import Image
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from .forms import SignUpForm, UserForm


# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def avatar_process(avatar, name):
    img = Image.open(avatar)
    # save as png
    img.save(settings.MEDIA_ROOT + f'/avatars/{name}.png')


@login_required
def user_update_view(request):
    user = request.user
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            avatar_process(form.cleaned_data.get('avatar'), user.username)
            return redirect(reverse('my_account'))
    else:
        form = UserForm(instance=user)

    return render(request, 'my_account.html', {
        'form': form, 'user': user
    })

def password_reset_notification(request):
    return render(request, 'password_reset_notification.html')