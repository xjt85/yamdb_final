from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from reviews.models import Category, Genre, Review, Title
from users.models import User
from api_yamdb.settings import EMAIL_HOST_USER
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .pagination import TitlesPagination
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    ReviewCommentPermission,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleSerializer,
    TokenConfirmationSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .utils import get_tokens_for_user


@api_view(['POST'])
def sign_up(request):
    def send_email(user):
        token = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            f'Код подтверждения: {token}',
            EMAIL_HOST_USER,
            [user.email],
        )

    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')

    try:
        user = User.objects.get_or_create(email=email, username=username)[0]
    except Exception:
        return Response(
            'Введено неверное имя пользователя или e-mail',
            status=status.HTTP_400_BAD_REQUEST
        )

    send_email(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    serializer = TokenConfirmationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')

    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        return Response(get_tokens_for_user(user))
    return Response(
        data='Неверный код подтверждения',
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['username']
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = TitlesPagination


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = TitlesPagination


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    pagination_class = TitlesPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewCommentPermission]
    pagination_class = TitlesPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [ReviewCommentPermission]
    pagination_class = TitlesPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title__pk=title_id)
        serializer.save(author=self.request.user, review=review)
