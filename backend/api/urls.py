from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')

urlpatterns = (
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
)
