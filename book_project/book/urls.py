from django.urls import path
from . import views

urlpatterns = [
    path("create-book/", views.BookCreateAPIView.as_view()),
    path("get-book/", views.BookListAPIView.as_view()),
    path("delete-book/<int:pk>/", views.BookDeleteAPIView.as_view()),
    path("register/", views.UserRegistrationAPIView.as_view()),
]
