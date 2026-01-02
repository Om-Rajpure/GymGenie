from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'age', 'gender', 'valid_until', 'is_staff', 'is_active')  # ✅ Corrected here

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('age', 'gender', 'valid_until')}),  # ✅ Corrected here
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('age', 'gender', 'valid_until')}),  # ✅ Corrected here
    )

admin.site.register(CustomUser, CustomUserAdmin)

from django.contrib import admin
from .models import Progress

admin.site.register(Progress)

