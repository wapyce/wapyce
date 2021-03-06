"""
Views of core application.
"""

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext as _

from rest_framework.authtoken.models import Token

# Create your views here.

def home(request):
    """
    View of home page.
    """

    return render(request, 'home.html')

def donate(request):
    """
    View of donate page.
    """

    return render(request, 'donate.html')

def login(request):
    """
    View of login page.
    """

    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'account/login.html')

def logout_view(request):
    """
    View to logout user.
    """

    logout(request)
    return redirect('home')

@login_required
def settings_view(request):
    """
    View to settings page of user.
    """

    token = Token.objects.get(user=request.user)
    return render(request, 'account/settings.html', {'user_token': token})

@login_required
def new_user_token(request):
    """
    View to generate a new token for user.
    """

    Token.objects.get(user=request.user).delete()
    Token.objects.create(user=request.user)
    messages.success(request, _('New user token created.'))
    return redirect('settings')
