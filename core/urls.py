from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path("about/", views.about, name="about"),
    path("about-this-site/", views.about_site, name="about_site"),
]