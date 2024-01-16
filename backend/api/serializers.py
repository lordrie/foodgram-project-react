from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import (SetPasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription

from .validators import validate_recipe_data

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


class UserСhangePasswordSerializer(SetPasswordSerializer):
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

    def get_is_model(self, model, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return model.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        return self.get_is_model(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_model(ShoppingCart, obj)


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
        ingredients_data, tags_data = validate_recipe_data(validated_data)
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        for tag_data in tags_data:
            recipe.tags.add(tag_data)
        return recipe

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class RecipeUpdateSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientsSerializer(source='recipes', many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def update(self, instance, validated_data):
        ingredients_data, tags_data = validate_recipe_data(validated_data)
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
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class SmallRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
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
        current_user = self.context.get('request').user
        is_user_subscribed = Subscription.objects.filter(
            user=current_user, author=obj.author).exists()
        return is_user_subscribed

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return SmallRecipeSerializer(recipes, many=True).data


class BaseRecipeSerializer(serializers.ModelSerializer):
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
        return SmallRecipeSerializer(
            instance.recipe, context={'request': request}).data


class FavoriteSerializer(BaseRecipeSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(BaseRecipeSerializer):
    """Сериализатор для работы со списком покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
