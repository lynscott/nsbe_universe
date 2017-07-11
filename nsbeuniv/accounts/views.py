from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView

from . import forms
# Create your views here.
class SignUp(CreateView):
    form_class = forms.UserSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

class RetentionPage(TemplateView):
    template_name = 'retention.html'
