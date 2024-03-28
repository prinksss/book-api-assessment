from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .models import Book, Token
from .serializers import BookSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from django.core.cache import cache


class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            generate_tokens_for_user(user)

            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    Token.objects.create(
        user=user, access_token=access_token, refresh_token=refresh_token
    )


# Create your views here.
class BookCreateAPIView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def create(self, request, *args, **kwargs):
        if "book_cache" not in cache:
            cache.set("book_cache", [])

        book_data = request.data

        book_cache = cache.get("book_cache")
        for book_item in book_cache:
            if all(
                book_item[key] == book_data[key] for key in book_data if key != "id"
            ):
                raise ValidationError("Book with these attributes already exists")

        serializer = self.get_serializer(data=book_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        book_cache.append(serializer.data)
        cache.set("book_cache", book_cache)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class BookListAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        queryset = Book.objects.all()
        author_name = self.request.query_params.get("author", None)
        publisher_name = self.request.query_params.get("publisher", None)

        if author_name:
            queryset = queryset.filter(author__icontains=author_name)
        if publisher_name:
            queryset = queryset.filter(publisher__icontains=publisher_name)

        return queryset


class BookDeleteAPIView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        book_id = kwargs.get("pk")
        try:
            book = self.queryset.get(pk=book_id)
            book.delete()
            return Response(
                {"message": "Book deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Book.DoesNotExist:
            return Response(
                {"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND
            )


def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Save tokens in the database
    Token.objects.create(
        user=user, access_token=access_token, refresh_token=refresh_token
    )
