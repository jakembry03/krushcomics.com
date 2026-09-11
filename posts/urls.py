from django.urls import path
from . import views

urlpatterns = [
    path('', views.posts, name='posts'),
    path('details/<int:id>/', views.post_details, name='post_details'),
]