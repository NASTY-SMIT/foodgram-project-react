from django.contrib.auth import get_user_model
from django_filters import rest_framework

from recipes.models import Tag, Recipe

User = get_user_model()


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = rest_framework.ModelChoiceFilter(
        queryset=User.objects.all(),
    )
    is_favorited = rest_framework.BooleanFilter(
        method='is_favorited_method')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='is_in_shopping_cart_method')

    def is_favorited_method(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        if value:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def is_in_shopping_cart_method(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        if value:
            return queryset.filter(shopping_cart_recipe__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
