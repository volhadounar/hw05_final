from django.views.generic import CreateView
from django.urls import reverse_lazy
import datetime as dt
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"


def year(request):
    d = dt.datetime.now().date().year
    return {
        "year": d
    }
