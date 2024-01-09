from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """
    Inline класс для отображения ингредиентов в рецепте.
    """
    model = Recipe.ingredients.through
    extra = 1


class RecipeIngredientAdmin(admin.ModelAdmin):
    """
    Отображает рецепт, ингредиент и количество в списке.
    Позволяет искать по названию рецепта и ингредиента.
    """
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe__author',)


class RecipeAdmin(admin.ModelAdmin):
    """
    Отображает название рецепта, автора и количество избранных в списке.
    Позволяет искать по названию и имени автора.
    Позволяет фильтровать по автору, названию и тегам.
    """
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'author', 'number_of_favorites')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name', 'tags')

    def number_of_favorites(self, obj):
        return obj.in_favorites.count()
    number_of_favorites.short_description = 'Number of Favorites'


class IngredientAdmin(admin.ModelAdmin):
    """
    Отображает название и единицу измерения в списке.
    Позволяет искать по названию.
    Позволяет фильтровать по названию.
    """
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    """
    Отображает название, цвет и слаг в списке.
    Позволяет искать по названию и слагу.
    """
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


class FavoriteAdmin(admin.ModelAdmin):
    """
    Отображает пользователя и рецепт в списке.
    Позволяет искать по имени пользователя и названию рецепта.
    """
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Отображает пользователя и рецепт в списке.
    Позволяет искать по имени пользователя и названию рецепта.
    """
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
