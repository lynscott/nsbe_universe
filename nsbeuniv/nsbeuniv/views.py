from django.views.generic import TemplateView

class LoggedPage(TemplateView):
    template_name = 'logged.html'

class ThanksPage(TemplateView):
    template_name = 'thanks.html'

class HomePage(TemplateView):
    template_name = 'index.html'
