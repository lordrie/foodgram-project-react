from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class RecipeService:
    """Сервис для работы с рецептами.
    Добавляет и удаляет рецепт в
    Избранное и/или Список покупок"""
    @staticmethod
    def add(instance, user, pk):
        """Принимает экземпляр сериализатора, добавляет рецепт в Избранное
        и Список покупок"""
        instance = instance(data={'user': user.id, 'recipe': pk})
        if not instance.is_valid():
            raise ValidationError(instance.errors)
        instance.save()
        return Response(instance.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(model, user, pk):
        """Принимает модель, удаляет рецепт из Избранного
        и Списка покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = model.objects.filter(user=user, recipe=recipe)
        if not instance.exists():
            raise ValidationError('Нельзя повторно удалить рецепт')
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
