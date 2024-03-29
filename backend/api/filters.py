from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Фильтр для игредиентов.
    Фильтрует ингредиенты в произвольном месте."""
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для рецепта.
    Фильтрует рецепты по тегам, автору,
    наличию в избранном и в списке покупок."""
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='get_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_queryset(self, queryset, name, value, key):
        user = self.request.user
        if value and not user.is_anonymous:
            filter_key = f'{key}__user'
            filter_args = {filter_key: user}
            return queryset.filter(**filter_args)
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        return self.get_queryset(queryset, name, value, 'in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        return self.get_queryset(queryset, name, value, 'in_favorites')
