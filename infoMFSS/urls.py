from django.views.generic import TemplateView

from infoMFSS.apps import InfomfssConfig
from django.urls import path
from infoMFSS.views import EquipmentListView, CableListView, BoxListView, \
    EquipmentFileListView, CableFileListView, ViolationsListView, ProjectEquipmentListView, \
    ProjectCableListView, MFSSPercentTemplateView, ContactFormView, PercentView, QuantityEquipmentCableView, \
    CreateEquipmentView, CreateCableView, CreatePointPhoneView, CreateBranchesBoxView, CreateCableMagazineView, \
    CreateViolationsView, VisualView, CreateVisualView, CreateEquipmentInstallationView, CreateExecutionView, \
    EquipmentView, UpdateEquipmentView, DeleteEquipmentView, CableView, UpdateCableView, DeleteCableView, \
    PointPhoneView, UpdatePointPhoneView, DeletePointPhoneView

# from mfss.views import SubsystemTemplateView
# from infoMFSS.views import index

app_name = InfomfssConfig.name

urlpatterns = [
        path('', MFSSPercentTemplateView.as_view(), name='home'),
        path('percents/', PercentView.as_view(), name='percents'),
        path('equipment_list/', EquipmentListView.as_view(), name='equipment'),
        path('cable_list/', CableListView.as_view(), name='cable'),
        path('box_list/', BoxListView.as_view(), name='box'),
        path('equipment_file/', EquipmentFileListView.as_view(), name='equipment_file'),
        path('cable_file/', CableFileListView.as_view(), name='cable_file'),
        path('violations/', ViolationsListView.as_view(), name='violations'),
        path('visual/', VisualView.as_view(), name='visual'),
        path('project_equipment/', ProjectEquipmentListView.as_view(), name='project_equipment'),
        path('project_cable/', ProjectCableListView.as_view(), name='project_cable'),
        path('contact/', ContactFormView.as_view(), name='contact'),
        path(
            'contact/success/', TemplateView.as_view(template_name='infoMFSS/contact_success.html'), name='contact_success'
            ),
        path(
            'quantity/', QuantityEquipmentCableView.as_view(template_name='infoMFSS/quantity_equipment_cable.html'),
            name='quantity_equipment_cable'
            ),
        # Создание (только для модератора)
        path('moderator/create/equipment/', CreateEquipmentView.as_view(), name='create_equipment'),
        path('moderator/create/cable/', CreateCableView.as_view(), name='create_cable'),
        path('moderator/create/pointphone/', CreatePointPhoneView.as_view(), name='create_pointphone'),
        path('moderator/create/branchesbox/', CreateBranchesBoxView.as_view(), name='create_branchesbox'),
        path('moderator/create/cablemagazine/', CreateCableMagazineView.as_view(), name='create_cablemagazine'),
        path('moderator/create/violations/', CreateViolationsView.as_view(), name='create_violations'),
        path('moderator/create/visual/', CreateVisualView.as_view(), name='create_visual'),
        path('moderator/create/equipment-installation/', CreateEquipmentInstallationView.as_view(),
             name='create_equipment_installation'),
        path('moderator/create/execution/', CreateExecutionView.as_view(), name='create_execution'),
        # Просмотр и выбор для редактирования и удаления (только для модератора)
        path('moderator/list/equipment/', EquipmentView.as_view(), name='equipment_list'),
        path('moderator/list/cable/', CableView.as_view(), name='cable_list'),
        path('moderator/list/point_phone/', PointPhoneView.as_view(), name='point_phone_list'),
        # Редактирование (только для модератора)
        path('moderator/update/equipment/<int:pk>', UpdateEquipmentView.as_view(), name='equipment_update'),
        path('moderator/update/cable/<int:pk>', UpdateCableView.as_view(), name='cable_update'),
        path('moderator/update/point_phone/<int:pk>', UpdatePointPhoneView.as_view(), name='point_phone_update'),
        # Удаление (только для модератора)
        path('moderator/delete/equipment/<int:pk>', DeleteEquipmentView.as_view(), name='equipment_delete'),
        path('moderator/delete/cable/<int:pk>', DeleteCableView.as_view(), name='cable_delete'),
        path('moderator/delete/point_phone/<int:pk>', DeletePointPhoneView.as_view(), name='point_phone_delete'),
]
