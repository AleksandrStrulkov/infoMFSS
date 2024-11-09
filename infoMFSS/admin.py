from django.contrib import admin
from infoMFSS.models import NumberMine, Unit, Subsystem, Equipment, InclinedBlocks, CableMagazine, Tunnel, \
    EquipmentInstallation, Execution, BranchesBox, Cable, PointPhone, DateUpdate


@admin.register(NumberMine)
class NumberMineAdmin(admin.ModelAdmin):
    list_display = ('title', 'address_mine', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title',)
    search_fields = ('title',)


@admin.register(InclinedBlocks)
class InclinedBlocksAdmin(admin.ModelAdmin):
    list_display = ('title', 'number_mine', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title', 'number_mine')
    search_fields = ('title', 'number_mine')


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'description',)
    list_filter = ('title',)
    search_fields = ('title',)


@admin.register(Subsystem)
class SubsystemAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title',)
    search_fields = ('title',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title',)
    search_fields = ('title',)


@admin.register(BranchesBox)
class BranchesBoxAdmin(admin.ModelAdmin):
    list_display = ('title', 'number_mine', 'tunnel', 'inclined_blocks', 'subsystem', 'picket', 'boolean_block',
                    'description', 'slug')
    list_filter = ('title', 'inclined_blocks', 'number_mine', 'tunnel', 'subsystem', 'picket', 'boolean_block')
    search_fields = ('title', 'inclined_blocks', 'number_mine', 'tunnel', 'subsystem', 'picket', 'boolean_block')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug')
    list_filter = ('title',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(PointPhone)
class PointPhoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'number_mine', 'tunnel', 'inclined_blocks', 'subscriber_number', 'picket',
                    'description', 'slug')
    list_filter = ('title', 'number_mine', 'tunnel', 'inclined_blocks', 'subscriber_number', 'picket')
    search_fields = ('title', 'number_mine', 'tunnel', 'inclined_blocks', 'subscriber_number', 'picket')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CableMagazine)
class CableMagazineAdmin(admin.ModelAdmin):
    list_display = ('cable', 'name', 'subsystem', 'number_mine', 'inclined_blocks', 'track_from',
                    'track_to', 'distance', 'unit', 'slug')
    prepopulated_fields = {'slug': ('track_from', 'track_to')}
    list_filter = ('cable', 'name', 'subsystem', 'number_mine', 'inclined_blocks',)
    search_fields = ('cable', 'name', 'subsystem', 'number_mine', 'inclined_blocks',)


@admin.register(Tunnel)
class TunnelAdmin(admin.ModelAdmin):
    list_display = ('number_mine', 'title', 'inclined_blocks', 'tuf_bool', 'inclined_bool', 'description', 'slug')
    prepopulated_fields = {'slug': ('title', 'name_slag',)}
    list_filter = ('title', 'number_mine', 'inclined_blocks', 'tuf_bool', 'inclined_bool',)
    search_fields = ('title', 'number_mine', 'inclined_blocks', 'tuf_bool', 'inclined_bool',)


@admin.register(EquipmentInstallation)
class EquipmentInstallationAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'number_mine', 'tunnel', 'inclined_blocks', 'subsystem', 'picket', 'description')
    list_filter = ('title', 'subsystem', 'number_mine', 'tunnel', 'inclined_blocks',)
    search_fields = ('title', 'subsystem', 'number_mine', 'tunnel', 'inclined_blocks',)


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('equipment_install', 'cable_magazine', 'execution_bool', 'date_start',
                    'date_end', 'description')
    # prepopulated_fields = {'slug': ['description']}
    list_filter = ('equipment_install', 'cable_magazine', 'execution_bool',
                   'date_start', 'date_end')
    search_fields = ('equipment_install', 'cable_magazine', 'execution_bool',
                     'date_start', 'date_end')


@admin.register(DateUpdate)
class DateUpdateAdmin(admin.ModelAdmin):
    list_display = ('update', 'description',)