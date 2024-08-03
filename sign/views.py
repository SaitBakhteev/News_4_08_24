from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .models import BaseRegisterForm
from django.urls import reverse
from django.http import HttpResponseRedirect

class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'

class ExitView(LogoutView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.method == 'POST':
                return HttpResponseRedirect('/accounts/login/')
        return HttpResponseRedirect('/news/create')