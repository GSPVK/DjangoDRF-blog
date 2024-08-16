from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users.forms import CreationForm
from users.models import Profile

User = get_user_model()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id']
    readonly_fields = ['user']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'phone_number', 'fullname', 'get_user_groups']
    readonly_fields = ['last_login', 'date_joined']
    add_form = CreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',), },),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'first_name', 'last_name', 'username', 'user_group', 'email', 'phone_number', 'password1',
                    'password2'),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups')

    def get_user_groups(self, obj):
        groups = obj.groups.all()
        return ', '.join(group.name for group in groups)

    get_user_groups.short_description = 'Group'
