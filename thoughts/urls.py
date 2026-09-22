from django.urls import path
from . import views

urlpatterns = [
    path('', views.thoughts, name='thoughts'),
    path("archive/<str:kind>/", views.thought_archive, name='thought_archive'),
    path('review/<int:id>/', views.review_detail, name='review_detail'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
]
