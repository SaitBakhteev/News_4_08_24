from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import BaseRegisterView, ExitView

urlpatterns = [
    path('login/',
         LoginView.as_view(template_name ='sign/login.html'), name='login'),
    path('logout/',
         LogoutView.as_view(template_name ='account/login.html'), name='logout'),
    path('exit/',
         ExitView.as_view(), name='exit'),
    path('signup/',
         BaseRegisterView.as_view(template_name ='sign/signup.html'), name='signup'),
]