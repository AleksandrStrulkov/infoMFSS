from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from users.models import AllowedPerson, Invitation, User


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


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("invite_link", "created_by", "created_at", "expires_at", "is_used")
    list_filter = ("used_at", "created_at")
    search_fields = (
        "token",
        "created_by__email",
        "created_by__username",
        "registered_user__email",
        "registered_user__username",
    )
    readonly_fields = ("token", "invite_link")

    @admin.display(description="Ссылка-приглашение")
    def invite_link(self, obj: Invitation):
        url = reverse("users:register", kwargs={"token": obj.token})
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, url)

    @admin.display(boolean=True, description="Использована")
    def is_used(self, obj: Invitation) -> bool:
        return obj.used_at is not None or obj.registered_user is not None


class AllowedPersonAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "middle_name", "is_active")
    list_filter = ("last_name",)
    search_fields = ("last_name",)


admin.site.register(User, UsersAdmin)
admin.site.register(AllowedPerson, AllowedPersonAdmin)
