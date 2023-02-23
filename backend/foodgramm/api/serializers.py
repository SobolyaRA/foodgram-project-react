from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (FavoriteList, Ingredient, IngredientAmount, Recipe,
                           ShoppingList, Tag)
from rest_framework import serializers
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user,
                                     author=obj.id).exists()

    def create(self, validated_data):
        """Создание нового пользователя с запрошенными полями
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь
    """
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_is_subcriber(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author
                                     ).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag
    """
    class Meta:
        model = Tag
        fields = '__all__'


class TagListField(serializers.RelatedField):
    """Сериализатор для получения списка тэгов
    """
    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'color': obj.color,
            'slug': obj.slug
        }

    def to_internal_value(self, data):
        try:
            return Tag.objects.get(id=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Недопустимый первичный ключ "404" - объект не существует.'
            )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientAmount
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    name = serializers.StringRelatedField(
        source='ingredient.name', read_only=True)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def _get_ingredient(self, ingredient_id):
        return get_object_or_404(Ingredient, id=ingredient_id)

    def get_name(self, amount):
        return self._get_ingredient(amount.ingredient.id).name

    def get_measurement_unit(self, amount):
        return self._get_ingredient(amount.ingredient.id).measurement_unit


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка рецептов
    """
    image = Base64ImageField(max_length=None, use_url=True)
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredient_in_recipe',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'author',
            'is_favorite',
            'is_shopping_cart',
        )

    def get_is_favorited(self, obj):
        """Проверка, находится ли рецепт в избранном
        """
        request = self.context.get('request')
        if request.user.is_authenticated:
            return FavoriteList.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверка, находится ли рецепт в списке  покупок
        """
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingList.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов
    """
    image = Base64ImageField(max_length=None, use_url=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    tags = TagListField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def create_ingredients(self, ingredients, recipe):
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        """Создание рецепта
        """
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.create_ingredients(ingredients=ingredients_data, recipe=recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта
        """
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class FavoriteListSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов
    """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = FavoriteList
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe')
        extra_kwargs = {'user': {'write_only': True},
                        'recipe': {'write_only': True}}

    def validate(self, data):
        if FavoriteList.objects.filter(user=data['user'],
                                       recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data


class ShoppingListSerializer(FavoriteListSerializer):
    """Сериализатор списка покупок
    """
    class Meta(FavoriteListSerializer.Meta):
        model = ShoppingList

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        shopping_cart_exists = ShoppingList.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()

        if shopping_cart_exists:
            raise serializers.ValidationError(
                'В списке покупок такой рецепт есть'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe,
            context=context).data
