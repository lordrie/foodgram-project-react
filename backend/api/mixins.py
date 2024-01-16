from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


class RecipeMixin:
    @staticmethod
    def add(serializer, user, pk):
        serializer = serializer(data={'user': user.id, 'recipe': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(model, user, pk):
        recipe = get_object_or_404(
            Recipe.objects.select_related('author'), pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if not relation.exists():
            return Response('Нельзя повторно удалить рецепт',
                            status=status.HTTP_400_BAD_REQUEST)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
