from rest_framework.exceptions import ValidationError


MIN_VALUE_VALIDATOR = 1
MAX_VALUE_VALIDATOR = 32000


def validate_recipe(validated_data):
    """Данные рецепта.
    Проверяет наличие и корректность ингредиентов, тегов,
    изображения и времени приготовления."""
    ingredients_data = validated_data.pop('recipes', [])
    if not ingredients_data:
        raise ValidationError(
            'Рецепт должен содержать хотя бы один ингредиент.')
    if any(ingredients_data.count(ingredient) > 1
            for ingredient in ingredients_data):
        raise ValidationError(
            'Рецепт не должен содержать повторяющиеся ингредиенты.')

    tags_data = validated_data.pop('tags', [])
    if not tags_data:
        raise ValidationError(
            'Рецепт должен содержать хотя бы один тег.')
    if len(tags_data) != len(set(tags_data)):
        raise ValidationError(
            'Рецепт не должен содержать повторяющиеся теги.')

    image_data = validated_data.get('image')
    if not image_data or image_data == "":
        raise ValidationError('Загрузите изображение.')

    cooking_time = validated_data.get('cooking_time')
    if not cooking_time:
        raise ValidationError(
            'Рецепт должен содержать время приготовления.')
    return ingredients_data, tags_data


def validate_subscription(user, author):
    """Проверяет возможность подписки пользователя на автора."""
    if user == author:
        raise ValidationError('Нельзя подписаться на себя')
    if user.follower.filter(author=author).exists():
        raise ValidationError('Нельзя подписаться дважды')


def validate_unsubscription(user, author):
    """Проверяет возможность отписки пользователя от автора."""
    if user.follower.filter(author=author).exists():
        raise ValidationError('Вы не были подписаны на автора')
