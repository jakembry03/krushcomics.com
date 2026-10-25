from django.urls import path

from . import views

app_name = "operation_coco"

urlpatterns = [
    path("", views.gate, name="gate"),
    path("login/", views.login, name="login"),
    path("next/", views.next_page, name="next"),
    path("unlock/", views.unlock, name="unlock"),
    path("desktop/", views.desktop, name="desktop"),
    path("desktop/intro-done/", views.desktop_intro_done, name="desktop_intro_done"),
    path("stage/<int:number>/", views.stage, name="stage"),
    path("reset/", views.reset, name="reset"),
]
