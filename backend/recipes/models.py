from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тегов для рецепта"""
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет', max_length=7, unique=True)
    slug = models.SlugField(
        'Слаг', max_length=200, unique=True,
        validators=[RegexValidator(regex=r'^[-a-zA-Z0-9_]+$')])

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель игредиента."""
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=200)

    class Meta:
        verbose_name = 'Игредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}:{self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    tags = models.ManyToManyField(Tag, verbose_name='Тег')
    image = models.ImageField('Изображение рецепта',
                              upload_to='recipes/images')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Игредиенты')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта',
                               related_name='recipes')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)', default=1,
        validators=(MinValueValidator(1, 'Минимум 1 минута'), ))
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт: {self.name}. Автор: {self.author}'


class RecipeIngredient(models.Model):
    """Игредиенты определенного рецепта.
    Промежуточная таблица, связывает Ingredient и Recipe."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient')
    amount = models.PositiveIntegerField(
        'Количество', default=1,
        validators=(MinValueValidator(1, 'Минимум 1'),))

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"


class Favorite(models.Model):
    """Модель избранное."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_favorites')]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """Список покупок пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='shopping_list')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='shopping_list')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_shoppinglist')]

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
