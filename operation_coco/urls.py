from django.urls import path

from . import views

app_name = "operation_coco"

urlpatterns = [
    path("", views.gate, name="gate"),
    path("login/", views.login, name="login"),
    path("next/", views.next_page, name="next"),
    path("unlock/", views.unlock, name="unlock"),
]
