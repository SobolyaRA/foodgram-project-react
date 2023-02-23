from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from users.validators import hex_color_field_validator

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        help_text='Введите единицу измерения',
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга
    """
    name = models.CharField(
        max_length=200,
        db_index=True,
        unique=True,
        verbose_name='Название тэга',
        help_text='Введите название тэга',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='HEX цвет',
        unique=True,
        validators=[hex_color_field_validator]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='slug',
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Recipe(models.Model):
    """Модель рецепта.
    Главная модель приложения, описывающая рецепт.
    """
    name = models.CharField(
        max_length=200,
        null=True,
        verbose_name='Название',
        help_text='Введите название рецепта',
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Описание',
        help_text='Введите описание рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Автор',
        related_name='recipes',
    )
    image = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Изображение',
        upload_to='recipes/',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',
        help_text='Выберите тэги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления блюда в минутах',
        validators=[MinValueValidator(
            limit_value=1,
            message='Минимальное время приготовления - 1 минута'),
            MaxValueValidator(
                limit_value=1000,
                message='Максимальное время приготовления - 1000 минут',), ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    is_favorited = models.BooleanField('В избранном', default=False)
    is_in_shopping_cart = models.BooleanField(
        'В списке покупок',
        default=False
    )

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Модель количества ингредиента в рецепте.
    Модель связывает Recipe и Ingredient.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(
            limit_value=1,
            message='Минимально количество ингредиентов - 1.'),
            MaxValueValidator(
                limit_value=256,
                message='Максимальное количество - 256.',), ],
    )

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                name='unique_relationships_ingredient_recipe',
                fields=['ingredient', 'recipe'],
            ),
        ]

    def __str__(self):
        return (f'{self.ingredient} в рецепте {self.recipe}:{self.amount}')


class FavoriteList(models.Model):
    """Модель избранного рецепта пользователя.
    Модель связывает Recipe и  User.
    """
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт пользователя'
        verbose_name_plural = 'Избранные рецепты пользователей'
        constraints = [
            models.UniqueConstraint(
                name='unique_user_favorite_recipe',
                fields=['user', 'recipe'],
            ),
        ]

    def __str__(self):
        return (f'У {self.user} в избранном рецепт: {self.recipe}')


class ShoppingList(models.Model):
    """Модель списка покупок.
    Модель связывает Recipe и  User.
    """
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='recipe_in_shoplist',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_shoplist',
        verbose_name='Рецепт',
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        ordering = ['-date_added', ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                name='unique_user_recipe_shoplist',
                fields=['user', 'recipe'],
            ),
        ]

    def __str__(self):
        return (f'У {self.user} в списке покупок рецепт {self.recipe}')
