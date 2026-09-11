from django.urls import path
from . import views

urlpatterns = [
    path('', views.reviews, name='reviews'),
    path('details/<int:id>', views.review_details, name='review_details'),
]