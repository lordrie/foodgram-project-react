from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class RecipeService:
    @staticmethod
    def add(instance, user, pk):
        instance = instance(data={'user': user.id, 'recipe': pk})
        if not instance.is_valid():
            raise ValidationError(instance.errors)
        instance.save()
        return Response(instance.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = model.objects.filter(user=user, recipe=recipe)
        if not instance.exists():
            raise ValidationError('Нельзя повторно удалить рецепт')
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
