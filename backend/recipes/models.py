from django.db import models
from users.models import User


class Tag(models.Model):

    PINK = '#F08080'
    ORANGE = '#FF8C00'
    BLUE = '#7FFFD4'
    YELLOW = '#FFFF00'

    COLORS = [
        (PINK, 'Розовый'),
        (ORANGE, 'Оранжевый'),
        (BLUE, 'Синий'),
        (YELLOW, 'Жёлтый'),
    ]

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=7,
        choices=COLORS,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг')

    class Meta:
        ordering = ["name"]
        verbose_name = 'Тег'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название', max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название')
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe_images/',
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag, through='TagsRecipe', related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name


class TagsRecipe(models.Model):

    tag = models.ForeignKey(
        Tag, verbose_name='Теги в рецепте', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт с тегами',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Теги в рецепте'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты в рецепте',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт с ингридиентами',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=0,
    )

    class Meta:
        verbose_name = 'Количетсво ингредиента в рецепте'
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'ingredient',),
                                    name='Unique Ingredients')
            ]

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredient}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite_recipe',
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Избранное'

    def __str__(self):
        return f'{self.user} favorite {self.recipe}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт в списке покупок',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Список покупок'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='Unique shopping cart',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
