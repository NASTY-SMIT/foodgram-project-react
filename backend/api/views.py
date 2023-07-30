from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser.views import UserViewSet
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .filters import RecipeFilter
from .serializers import (SignUpSerializer, ShowUserSerializer,
                          SetPasswordSerializer,
                          UserSubscribeSerializer, SubscribeAuthorSerializer,
                          IngredientSerializer, TagSerializer,
                          ShowRecipeSerializer, UserRecipeSerializer,
                          CreateRecipeSerializer)
from users.models import Follow, User
from .pagination import CustomPaginator
from recipes.models import (Ingredient, Tag, Recipe, Favorite, ShoppingCart,
                            IngredientRecipe)
from .permissions import AdminOrAuthorPermission


class UserViewSet(UserViewSet):

    queryset = User.objects.all()
    pagination_class = CustomPaginator
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):

        if self.action in ['subscriptions', 'subscribe']:
            return UserSubscribeSerializer
        elif self.request.method == 'GET':
            return ShowUserSerializer
        elif self.request.method == 'POST':
            return SignUpSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, ]

        return super(self.__class__, self).get_permissions()

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = ShowUserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPaginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = UserSubscribeSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])

        if request.method == 'POST':
            serializer = SubscribeAuthorSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            if author == request.user:
                return Response({'detail': 'Не подписывайтесь на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=request.user,
                                     author=author).exists():
                return Response({'detail': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                follow = Follow.objects.get(user=request.user, author=author)
            except Follow.DoesNotExist:
                return Response({'detail': 'Вы не подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'name__istartswith'
    pagination_class = None

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AdminOrAuthorPermission, ]
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipeFilter
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        elif self.action in ['favorite', 'shopping_cart', ]:
            return UserRecipeSerializer

        return CreateRecipeSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = UserRecipeSerializer(recipe, context={"request": request})

        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                return Response({'errors': 'Рецепта нет в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            favorite = get_object_or_404(Favorite, user=request.user,
                                         recipe=recipe)
            favorite.delete()
            return Response({'detail': 'Рецепт удален из избранного'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = UserRecipeSerializer(recipe, data=request.data,
                                              context={"request": request})
            serializer.is_valid()
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепта не было в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = IngredientRecipe.objects.filter(
            recipe__shopping_cart_recipe__user=user)
        ingredients = shopping_cart.values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount'))

        file_name = 'shopping_cart.txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'

        for ingredient in ingredients:
            response.write(
                f"{ingredient['name']} - {ingredient['amount']}"
                f" {ingredient['measurement_unit']}\n")

        return response
