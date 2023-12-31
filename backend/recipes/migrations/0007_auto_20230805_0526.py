# Generated by Django 3.2.16 on 2023-08-05 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsRecipes', to='recipes.ingredient', verbose_name='Ингредиенты в рецепте'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsRecipes', to='recipes.recipe', verbose_name='Рецепт с ингридиентами'),
        ),
    ]
