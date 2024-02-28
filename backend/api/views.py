from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, SetPasswordSerializer
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from users.models import User, Follow
from recipes.models import Tag, Ingredient, Recipe
from .mixins import CreateListRetrieveMixin
from .permissions import IsAuthorStaffOrReadOnly
from .serializers import (
    CustomUserSerialiser,
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    FollowSerializer
)


class UserViewSet(CreateListRetrieveMixin):
    queryset = User.objects.all()
    serializer_class = CustomUserSerialiser

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return CustomUserSerialiser

    @action(
        detail=False,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = self.request.user
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        return Response('Пароль успешно изменен', status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.follower.all()
        pages = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=request.data,
                context={'user': user, 'author': author})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(
                serializer.data,
                status.HTTP_201_CREATED
            )
        subscription = Follow.objects.filter(user=user, author=author).first()
        if not subscription:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(
            'Успешная отписка',
            status.HTTP_204_NO_CONTENT
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = settings.ALLOWED_METHODS
    permission_classes = (IsAuthorStaffOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
