from django.urls import path
from . import views

urlpatterns = [
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/details/<int:id>', views.review_details, name='review_details'),
]