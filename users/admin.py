from django.contrib import admin

from users.models import AllowedPerson, User


# Register your models here.
# @admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "middle_name",
        "email",
        "phone",
        "is_staff",
        "is_active",
        "is_activated",
        "date_joined",
        "telegram_id",
        "password",
    )
    list_filter = (
        "last_name",
        "email",
    )
    search_fields = (
        "last_name",
        "email",
    )


class AllowedPersonAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "middle_name", "is_active")
    list_filter = ("last_name",)
    search_fields = ("last_name",)


admin.site.register(User, UsersAdmin)
admin.site.register(AllowedPerson, AllowedPersonAdmin)
