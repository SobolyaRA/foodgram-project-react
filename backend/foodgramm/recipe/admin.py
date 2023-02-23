from django.contrib import admin

from recipe.models import (Ingredient, Tag, Recipe, IngredientAmount,
                           ShoppingList, FavoriteList)

from users.models import Follow


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('^name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'count_favorites')
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngredientInline,)

    def count_favorites(self, obj):
        return FavoriteList.objects.filter(recipe=obj).count()

    count_favorites.short_description = 'В избранном'


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'date_added')


class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount', 'recipe')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(FavoriteList, FavoriteListAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(IngredientAmount)
