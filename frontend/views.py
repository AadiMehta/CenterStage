from django.conf import settings
from django.core.cache import cache
from django.views.generic import TemplateView


class HomeTemplateView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
