from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    '''Кастомная модель Администратора'''
    model = User
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'email', 'first_name', )
    search_fields = ('username', 'email',)
    list_display_links = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
