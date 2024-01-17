from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import Recipe, ShoppingCart
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

User = get_user_model


class RecipeService:
    """Сервис для работы с рецептами.
    Принимает класс сериализатора,
    добавляет или удаляет рецепт из
    Избранного и Списка покупок."""

    def add_delete(serializer_class, request, pk):

        user = request.user
        if request.method == 'POST':
            serializer = serializer_class(data={'user': user.id, 'recipe': pk})
            if not serializer.is_valid():
                raise ValidationError('Ошибка валидации')
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe)
        if not instance.exists():
            raise ValidationError('Рецепт не был добавлен')
        serializer = serializer_class(instance.first())
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingListService:
    """Сервис для работы со списком покупок."""
    def __init__(self, user):
        self.user = user

    def get_shopping_list(self):
        shopping_list = ShoppingCart.objects.filter(user=self.user)
        ingredients = {}
        for item in shopping_list:
            for recipe_ingredient in item.recipe.recipes.all():
                name = recipe_ingredient.ingredient.name
                amount = recipe_ingredient.amount
                unit = recipe_ingredient.ingredient.measurement_unit
                if name in ingredients:
                    ingredients[name]['amount'] += amount
                else:
                    ingredients[name] = {'amount': amount, 'unit': unit}

        content_lines = ["Список покупок:\n"]
        for name, info in ingredients.items():
            line = f'{name} — {info["amount"]} {info["unit"]}'
            content_lines.append(line)
        content = "\n".join(content_lines)

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment;'
        'filename="shopping_list.txt"'
        return response
