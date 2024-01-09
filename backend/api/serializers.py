from djoser.serializers import (UserSerializer, UserCreateSerializer,
                                SetPasswordSerializer)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient

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
