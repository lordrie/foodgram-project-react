from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    """
    Отображает имя пользователя, email, имя и фамилию в списке.
    Позволяет искать по имени пользователя и email.
    Позволяет фильтровать по имени пользователя и email.
    """
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    """
    Отображает пользователя, автора и дату создания в списке.
    Позволяет искать по имени пользователя и автора.
    Позволяет фильтровать по имени пользователя и автора.
    """
    list_display = ('user', 'author', 'created')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user__username', 'author__username')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
