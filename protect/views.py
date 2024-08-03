from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class IndexView(TemplateView, LoginRequiredMixin):
    template_name = 'protect/index.html'

# Create your views here.
