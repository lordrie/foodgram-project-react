from djoser.serializers import (UserSerializer, UserCreateSerializer,
                                SetPasswordSerializer)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import (Tag, Ingredient, RecipeIngredient,
                            Recipe, Favorite, ShoppingCart)
from drf_extra_fields.fields import Base64ImageField

User = get_user_model()


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return obj.follower.filter(id=request.user.id).exists()


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class UserSetPasswordSerializer(SetPasswordSerializer):
    current_password = serializers.CharField(required=True,
                                             label='Текущий пароль')
    new_password = serializers.CharField(required=True,
                                         label='Новый пароль')

    def validate(self, data):
        request = self.context['request'].user
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        if not request.check_password(current_password):
            raise serializers.ValidationError(
                'Не верный пароль')
        if request.check_password(new_password):
            raise serializers.ValidationError(
                'Новый пароль не должен совпадать с текущим')
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """GET"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(source='recipes',
                                             many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class CreateIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientsSerializer(source='recipes', many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipes')
        if not ingredients_data:
            raise serializers.ValidationError(
                "Рецепт должен содержать хотя бы один ингредиент.")
        if any(ingredients_data.count(ingredient) > 1
               for ingredient in ingredients_data):
            raise serializers.ValidationError(
                "Рецепт не должен содержать повторяющиеся ингредиенты.")

        tags_data = validated_data.pop('tags')
        if not tags_data:
            raise serializers.ValidationError(
                "Рецепт должен содержать хотя бы один тег.")
        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError(
                "Рецепт не должен содержать повторяющиеся теги.")

        image_data = validated_data.get('image')
        if not image_data:
            raise serializers.ValidationError(
                "Рецепт должен содержать изображение.")

        cooking_time = validated_data.get('cooking_time')
        if not cooking_time:
            raise serializers.ValidationError(
                "Рецепт должен содержать время приготовления.")

        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe, **ingredient_data)
        for tag_data in tags_data:
            recipe.tags.add(tag_data)
        return recipe

    def update(self, instance, validated_data):
        print(validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        image_data = validated_data.get('image')
        if not image_data or image_data == "":
            raise serializers.ValidationError({"Загрузите изображение"})
        instance.image = image_data

        ingredients_data = validated_data.pop('recipes', [])
        if not ingredients_data:
            raise serializers.ValidationError(
                {"Рецепт должен содержать хотя бы один ингредиент."})
        if any(ingredients_data.count(ingredient) > 1
               for ingredient in ingredients_data):
            raise serializers.ValidationError(
                {"Рецепт не должен содержать повторяющиеся ингредиенты."})

        tags_data = validated_data.pop('tags', [])
        if not tags_data:
            raise serializers.ValidationError(
                {"Рецепт должен содержать хотя бы один тег."})
        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError(
                {"Рецепт не должен содержать повторяющиеся теги."})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.recipes.all().delete()

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=instance, **ingredient_data)
        instance.tags.clear()
        for tag_data in tags_data:
            instance.tags.add(tag_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data
