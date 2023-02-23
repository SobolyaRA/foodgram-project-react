# Generated by Django 2.2.19 on 2023-02-20 18:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_auto_20230218_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientamount',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Минимально количество ингредиентов - 1.'), django.core.validators.MaxValueValidator(limit_value=32, message='Максимальное количество - 32.')], verbose_name='Количество ингредиента'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Минимальное время приготовления - 1 минута'), django.core.validators.MaxValueValidator(limit_value=300, message='Максимальное время приготовления - 300 минут')], verbose_name='Время приготовления блюда в минутах'),
        ),
    ]