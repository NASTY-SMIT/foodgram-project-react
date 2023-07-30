import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core import exceptions as django_exceptions
from rest_framework import serializers
from .mixins import UsernameValidationMixin
from recipes.models import (Recipe, Ingredient, Tag,
                            IngredientRecipe, Favorite,
                            ShoppingCart)
from users.models import Follow, User


class SignUpSerializer(UserCreateSerializer, UsernameValidationMixin):
    '''Регистрация пользователя'''
    email = serializers.EmailField(max_length=254,
                                   validators=[validate_email])
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', )

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if User.objects.filter(username=username, email=email).exists():
            return attrs
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Такой ник уже существует'
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Такой email уже существует'
            )
        return attrs


class ShowUserSerializer(UserSerializer):
    '''Список пользователей, просмотр профиля'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Follow.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        return False


class SetPasswordSerializer(serializers.Serializer):
    '''Изменение пароля'''
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            error_message = {'new_password': list(e.messages)}
            raise serializers.ValidationError(error_message)
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class Base64ImageField(serializers.ImageField):
    '''Картинки'''
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserRecipeSerializer(serializers.ModelSerializer):
    '''Для избранных, списка покупок и подписки'''
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time', ]
        read_only_fields = ('__all__',)


class UserSubscribeSerializer(ShowUserSerializer):
    '''Вывод авторов, на которых подписан пользователь'''

    recipes = UserRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)
        read_only_fields = ('__all__',)

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Follow.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        return False

    def get_recipes_count(self, obj: User) -> int:

        return obj.recipes.count()


class SubscribeAuthorSerializer(serializers.ModelSerializer):
    '''Подписки'''
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = UserRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, valid_data):
        if (self.context['request'].user == valid_data):
            raise serializers.ValidationError({'errors': 'Ошибка'})
        return valid_data

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Follow.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        return False

    def get_recipes_count(self, valid_data):
        return valid_data.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    '''Список тэгов'''
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''Список игредиентов'''
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    '''Ингридиенты с колличеством'''

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ShowRecipeSerializer(serializers.ModelSerializer):
    '''Список рецептов'''
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = ShowUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, read_only=True, source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time', ]

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and Favorite.objects.filter(recipe=obj, user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and ShoppingCart.objects.filter(recipe=obj,
                                                user=user).exists())


class CreateRecipeSerializer(serializers.ModelSerializer):
    '''Создание, редактирование рецепта'''
    ingredients = IngredientRecipeSerializer(many=True,)
    image = Base64ImageField(required=False, allow_null=True)
    author = ShowUserSerializer(read_only=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ['id', 'ingredients', 'tags', 'image', 'name',
                  'text', 'author', 'cooking_time', ]

    def validate(self, data):
        required_fields = ['ingredients', 'tags', 'image',
                           'name', 'text', 'cooking_time']
        missing_fields = [field for field in required_fields
                          if not data.get(field)]
        if missing_fields:
            raise serializers.ValidationError(
                f'Пожалуйста, заполните {", ".join(missing_fields)}')
        if data.get('cooking_time') and data['cooking_time'] <= 0:
            raise serializers.ValidationError(
                {'error': 'Время приготовления не может быть < 1 минуты'})
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.add(*tags)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            IngredientRecipe.objects.create(
                ingredient=ingredient_id, recipe=recipe, amount=amount
            )

        return recipe

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            IngredientRecipe.objects.create(
                ingredient=ingredient_id, recipe=instance, amount=amount
            )
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}).data
