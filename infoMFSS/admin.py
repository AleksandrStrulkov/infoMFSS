from django.contrib import admin
from infoMFSS.models import (
    NumberMine,
    Unit,
    Subsystem,
    Equipment,
    InclinedBlocks,
    CableMagazine,
    Tunnel,
    EquipmentInstallation,
    Execution,
    BranchesBox,
    Cable,
    PointPhone,
    DateUpdate,
    Violations,
    Visual,
    Beacon,
)
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin, GroupAdmin


class MyAdminSite(AdminSite):

    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)

        # Сортируем список в алфавитном порядке.
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        return app_list


admin.site = MyAdminSite()


# @admin.register(NumberMine)
class NumberMineAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "address_mine", "slug")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
    )
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Subsystem)
class SubsystemAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Tunnel)
class TunnelAdmin(admin.ModelAdmin):
    list_display = (
        "number_mine",
        "title",
        "inclined_blocks",
        "tuf_bool",
        "inclined_bool",
        "description",
    )
    list_filter = (
        "title",
        "number_mine",
        "inclined_blocks",
        "tuf_bool",
        "inclined_bool",
    )
    search_fields = (
        "title",
        "number_mine",
        "inclined_blocks",
        "tuf_bool",
        "inclined_bool",
    )


# @admin.register(InclinedBlocks)
class InclinedBlocksAdmin(admin.ModelAdmin):
    list_display = ("title", "number_mine", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("title", "number_mine")
    search_fields = ("title", "number_mine")


# @admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "subsystem", "file_pdf", "file_passport", "file_certificate")
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "file_pdf", "file_passport", "file_certificate")
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(PointPhone)
class PointPhoneAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "device_type",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "subscriber_number",
        "description",
        "picket",
        "serial_number",
    )
    list_filter = (
        "title",
        "number_mine",
        "subscriber_number",
    )
    search_fields = ("title", "number_mine", "subscriber_number")


# @admin.register(BranchesBox)
class BranchesBoxAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "device_type",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "subsystem",
        "equipment",
        "picket",
        "description",
        "ip_address",
        "serial_number",
    )
    list_filter = (
        "title",
        "number_mine",
        "subsystem",
        "description",
    )
    search_fields = (
        "title",
        "number_mine",
        "subsystem",
        "description",
    )


class BeaconAdmin(admin.ModelAdmin):
    list_display = (
        "designation",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "picket",
        "mac_address",
        "serial_number",
        "minor",
        "execution_bool",
        "data",
    )
    list_filter = ("designation", "number_mine", "tunnel", "inclined_blocks", "serial_number", "minor", "data")
    search_fields = ("designation", "number_mine", "tunnel", "inclined_blocks", "serial_number", "minor", "data")


@admin.register(Visual)
class VisualAdmin(admin.ModelAdmin):
    list_display = (
        "number_mine",
        "subsystem",
        "equipment",
        "cable",
        "file_pdf",
        "data",
    )
    list_filter = ("number_mine", "subsystem", "equipment", "cable", "data")
    search_fields = ("number_mine", "subsystem", "equipment", "cable", "data")


# @admin.register(Violations)
class ViolationsAdmin(admin.ModelAdmin):
    list_display = (
        "number_act",
        "date_act",
        "issued_by_act",
        "number_mine",
        "title",
        "execution_bool",
        "file_act",
        "file_notification",
    )
    list_filter = ("number_act", "date_act", "issued_by_act", "number_mine", "execution_bool")
    search_fields = ("number_act", "date_act", "issued_by_act", "number_mine", "execution_bool")


# @admin.register(CableMagazine)
class CableMagazineAdmin(admin.ModelAdmin):
    list_display = (
        "cable",
        "name",
        "subsystem",
        "number_mine",
        "inclined_blocks",
        "track_from",
        "track_to",
        "distance",
        "unit",
        "slug",
    )
    # prepopulated_fields = {'slug': ('track_from')}
    prepopulated_fields = {"slug": ("track_from", "track_to")}
    list_filter = (
        "cable",
        "name",
        "subsystem",
        "number_mine",
        "inclined_blocks",
    )
    search_fields = (
        "cable",
        "name",
        "subsystem",
        "number_mine",
        "inclined_blocks",
    )


# @admin.register(EquipmentInstallation)
class EquipmentInstallationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "name",
        "point_phone",
        "point_phone__subscriber_number",
        "branches_box",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "subsystem",
        "picket",
        "description",
        "ip_address",
        "serial_number",
        "device_type",
    )
    list_filter = ("title", "subsystem", "number_mine", "tunnel", "inclined_blocks", "point_phone")
    search_fields = ("title", "subsystem", "number_mine", "tunnel", "inclined_blocks", "point_phone")


# @admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ("equipment_install", "cable_magazine", "execution_bool", "date_start", "date_end", "description")
    # prepopulated_fields = {'slug': ['description']}
    list_filter = ("equipment_install", "cable_magazine", "execution_bool", "date_start", "date_end")
    search_fields = ("equipment_install", "cable_magazine", "execution_bool", "date_start", "date_end")


# @admin.register(DateUpdate)
class DateUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "update",
        "description",
    )


admin.site.register(NumberMine, NumberMineAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Subsystem, SubsystemAdmin)
admin.site.register(Tunnel, TunnelAdmin)
admin.site.register(InclinedBlocks, InclinedBlocksAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Cable, CableAdmin)
admin.site.register(Beacon, BeaconAdmin)
admin.site.register(PointPhone, PointPhoneAdmin)
admin.site.register(BranchesBox, BranchesBoxAdmin)
admin.site.register(Visual, VisualAdmin)
admin.site.register(Violations, ViolationsAdmin)
admin.site.register(CableMagazine, CableMagazineAdmin)
admin.site.register(EquipmentInstallation, EquipmentInstallationAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(DateUpdate, DateUpdateAdmin)


admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)
