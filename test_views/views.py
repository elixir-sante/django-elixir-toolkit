from django.shortcuts import render
from django.views.generic import FormView

from test_views.forms import FormExample


# class HomeTestView(TemplateView):
#     template_name = "home.html"


class FormTestView(FormView):
    template_name = "form_test.html"
    form_class = FormExample

    # def form_valid(self, form):
    #     return super().form_valid(form)
