from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import (SetPasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .validators import (validate_recipe,
                         MIN_VALUE_VALIDATOR, MAX_VALUE_VALIDATOR)
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscription


User = get_user_model()


class UserReadSerializer(UserSerializer):
    """Базовый сериализатор для кастомной модели User"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверяет подписку"""
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return obj.following.filter(user=current_user).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания новых пользователей."""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class UserСhangePasswordSerializer(SetPasswordSerializer):
    """Сериализатор для изменения пароля пользователя."""
    current_password = serializers.CharField(required=True,
                                             label='Текущий пароль')
    new_password = serializers.CharField(required=True,
                                         label='Новый пароль')

    def validate(self, data):
        request = self.context['request'].user
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        if not request.check_password(current_password):
            raise serializers.ValidationError('Неверный пароль')
        if request.check_password(new_password):
            raise serializers.ValidationError(
                'Новый пароль не должен совпадать с текущим')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи рецепта и ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """"Сериализатор для модели рецепта. Проверяет,
    добавлен ли рецепт в избранное и в список покупок."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer(read_only=True)
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

    def get_is_model(self, model, obj):
        """Проверяет, связан ли рецепт с моделью
        для текущего пользователя."""
        request = self.context['request']
        if request.user.is_authenticated:
            return model.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""
        return self.get_is_model(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в список покупок."""
        return self.get_is_model(ShoppingCart, obj)


class CreateIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    amount = serializers.IntegerField(min_value=MIN_VALUE_VALIDATOR,
                                      max_value=MAX_VALUE_VALIDATOR)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецепта."""
    ingredients = CreateIngredientsSerializer(source='recipes', many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(min_value=MIN_VALUE_VALIDATOR,
                                            max_value=MAX_VALUE_VALIDATOR)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data, tags_data = validate_recipe(validated_data)
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        for tag_data in tags_data:
            recipe.tags.add(tag_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data, tags_data = validate_recipe(validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image')

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
        serializer = RecipeReadSerializer(instance, context=self.context)
        return serializer.data


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Сериализует основную информацию о рецепте."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок. Проверяет подписку.
    Сериализует данные рецепта."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """Проверяет подписку"""
        current_user = self.context['request'].user
        is_user_subscribed = obj.author.follower.filter(
            user=current_user).exists()
        return is_user_subscribed

    def get_recipes(self, obj):
        """Возвращает список рецептов автора.
        Количество рецептов может быть ограничено параметром 'recipes_limit'"""
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = BaseRecipeSerializer(
            recipes, many=True, read_only=True)
        return serializer.data


class RecipeRelatedModelSerializer(serializers.ModelSerializer):
    """Cериализатор для моделей, связанных с рецептами
    (Избранное и Список покупок).
    Проверяет, добавлен ли рецепт пользователем."""

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Повторно нельзя добавить')
        recipe = get_object_or_404(
            Recipe.objects.select_related('author'), pk=recipe.id)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return BaseRecipeSerializer(
            instance.recipe, context={'request': request}).data


class FavoriteSerializer(RecipeRelatedModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(RecipeRelatedModelSerializer):
    """Сериализатор для работы со списком покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
