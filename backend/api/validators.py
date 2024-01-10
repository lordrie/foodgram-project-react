from rest_framework import serializers


def validate_recipe_data(validated_data):
    ingredients_data = validated_data.pop('recipes', [])
    if not ingredients_data:
        raise serializers.ValidationError(
            "Рецепт должен содержать хотя бы один ингредиент.")
    if any(ingredients_data.count(ingredient) > 1
            for ingredient in ingredients_data):
        raise serializers.ValidationError(
            "Рецепт не должен содержать повторяющиеся ингредиенты.")

    tags_data = validated_data.pop('tags', [])
    if not tags_data:
        raise serializers.ValidationError(
            "Рецепт должен содержать хотя бы один тег.")
    if len(tags_data) != len(set(tags_data)):
        raise serializers.ValidationError(
            "Рецепт не должен содержать повторяющиеся теги.")

    image_data = validated_data.get('image')
    if not image_data or image_data == "":
        raise serializers.ValidationError("Загрузите изображение.")

    cooking_time = validated_data.get('cooking_time')
    if not cooking_time:
        raise serializers.ValidationError(
            "Рецепт должен содержать время приготовления.")

    return ingredients_data, tags_data
