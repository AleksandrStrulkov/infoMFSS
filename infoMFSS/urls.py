from django.urls import path
from django.views.generic import TemplateView

from infoMFSS.apps import InfomfssConfig
from infoMFSS.views import (BeaconListView, BeaconView, BoxListView,
                            BranchesBoxView, CableFileListView, CableListView,
                            CableMagazineView, CableView, ContactFormView,
                            CreateBeaconView, CreateBranchesBoxView,
                            CreateCableMagazineView, CreateCableView,
                            CreateDateView, CreateEquipmentInstallationView,
                            CreateEquipmentView, CreateExecutionView,
                            CreatePointPhoneView, CreateViolationsView,
                            CreateVisualView, DeleteBeaconView,
                            DeleteBranchesBoxView, DeleteCableMagazineView,
                            DeleteCableView, DeleteEquipmentInstallationView,
                            DeleteEquipmentView, DeleteExecutionView,
                            DeletePointPhoneView, DeleteViolationsView,
                            DeleteVisualView, EquipmentFileListView,
                            EquipmentInstallationView, EquipmentListView,
                            EquipmentView, ExecutionView,
                            MFSSPercentTemplateView, PercentView,
                            PointPhoneView, ProjectCableListView,
                            ProjectEquipmentListView,
                            QuantityEquipmentCableView, UpdateBeaconView,
                            UpdateBranchesBoxView, UpdateCableMagazineView,
                            UpdateCableView, UpdateEquipmentInstallationView,
                            UpdateEquipmentView, UpdateExecutionView,
                            UpdatePointPhoneView, UpdateViolationsView,
                            UpdateVisualView, ViolationsListView,
                            ViolationsView, VisualistView, VisualView)

# from mfss.views import SubsystemTemplateView
# from infoMFSS.views import index

app_name = InfomfssConfig.name

urlpatterns = [
    path("", MFSSPercentTemplateView.as_view(), name="home"),
    path("percents/", PercentView.as_view(), name="percents"),
    path("equipment_list/", EquipmentListView.as_view(), name="equipment"),
    path("cable_list/", CableListView.as_view(), name="cable"),
    path("box_list/", BoxListView.as_view(), name="box"),
    path("equipment_file/", EquipmentFileListView.as_view(), name="equipment_file"),
    path("cable_file/", CableFileListView.as_view(), name="cable_file"),
    path("violations/", ViolationsListView.as_view(), name="violations"),
    path("visual/", VisualView.as_view(), name="visual"),
    path("project_equipment/", ProjectEquipmentListView.as_view(), name="project_equipment"),
    path("project_cable/", ProjectCableListView.as_view(), name="project_cable"),
    path("contact/", ContactFormView.as_view(), name="contact"),
    path(
        "contact/success/", TemplateView.as_view(template_name="infoMFSS/contact_success.html"), name="contact_success"
    ),
    path(
        "quantity/",
        QuantityEquipmentCableView.as_view(template_name="infoMFSS/quantity_equipment_cable.html"),
        name="quantity_equipment_cable",
    ),
    path("beacon_list/", BeaconListView.as_view(), name="beacon"),
    # Создание (только для модератора)
    path("moderator/create/equipment/", CreateEquipmentView.as_view(), name="create_equipment"),
    path("moderator/create/cable/", CreateCableView.as_view(), name="create_cable"),
    path("moderator/create/beacon/", CreateBeaconView.as_view(), name="create_beacon"),
    path("moderator/create/pointphone/", CreatePointPhoneView.as_view(), name="create_pointphone"),
    path("moderator/create/branchesbox/", CreateBranchesBoxView.as_view(), name="create_branchesbox"),
    path("moderator/create/cablemagazine/", CreateCableMagazineView.as_view(), name="create_cablemagazine"),
    path("moderator/create/violations/", CreateViolationsView.as_view(), name="create_violations"),
    path("moderator/create/visual/", CreateVisualView.as_view(), name="create_visual"),
    path(
        "moderator/create/equipment-installation/",
        CreateEquipmentInstallationView.as_view(),
        name="create_equipment_installation",
    ),
    path("moderator/create/execution/", CreateExecutionView.as_view(), name="create_execution"),
    path("moderator/create/date/", CreateDateView.as_view(), name="create_date"),
    # Просмотр и выбор для редактирования и удаления (только для модератора)
    path("moderator/list/equipment/", EquipmentView.as_view(), name="equipment_list"),
    path("moderator/list/cable/", CableView.as_view(), name="cable_list"),
    path("moderator/list/beacon/", BeaconView.as_view(), name="beacon_list"),
    path("moderator/list/point_phone/", PointPhoneView.as_view(), name="point_phone_list"),
    path("moderator/list/branches_box/", BranchesBoxView.as_view(), name="branches_box_list"),
    path("moderator/list/cable_magazine/", CableMagazineView.as_view(), name="cable_magazine_list"),
    path("moderator/list/violations/", ViolationsView.as_view(), name="violations_list"),
    path("moderator/list/visual/", VisualistView.as_view(), name="visual_list"),
    path(
        "moderator/list/equipment_installation/",
        EquipmentInstallationView.as_view(),
        name="equipment_installation_list",
    ),
    path("moderator/list/execution/", ExecutionView.as_view(), name="execution_list"),
    # Редактирование (только для модератора)
    path("moderator/update/equipment/<int:pk>", UpdateEquipmentView.as_view(), name="equipment_update"),
    path("moderator/update/cable/<int:pk>", UpdateCableView.as_view(), name="cable_update"),
    path("moderator/update/beacon/<int:pk>", UpdateBeaconView.as_view(), name="beacon_update"),
    path("moderator/update/point_phone/<int:pk>", UpdatePointPhoneView.as_view(), name="point_phone_update"),
    path("moderator/update/branchesbox/<int:pk>", UpdateBranchesBoxView.as_view(), name="branchesbox_update"),
    path("moderator/update/cablemagazine/<int:pk>", UpdateCableMagazineView.as_view(), name="cablemagazine_update"),
    path("moderator/update/violations/<int:pk>", UpdateViolationsView.as_view(), name="violations_update"),
    path("moderator/update/visual/<int:pk>", UpdateVisualView.as_view(), name="visual_update"),
    path(
        "moderator/update/equipment_installation/<int:pk>",
        UpdateEquipmentInstallationView.as_view(),
        name="equipment_installation_update",
    ),
    path("moderator/update/execution/<int:pk>", UpdateExecutionView.as_view(), name="execution_update"),
    # Удаление (только для модератора)
    path("moderator/delete/equipment/<int:pk>", DeleteEquipmentView.as_view(), name="equipment_delete"),
    path("moderator/delete/cable/<int:pk>", DeleteCableView.as_view(), name="cable_delete"),
    path("moderator/delete/beacon/<int:pk>", DeleteBeaconView.as_view(), name="beacon_delete"),
    path("moderator/delete/point_phone/<int:pk>", DeletePointPhoneView.as_view(), name="point_phone_delete"),
    path("moderator/delete/branchesbox/<int:pk>", DeleteBranchesBoxView.as_view(), name="branchesbox_delete"),
    path("moderator/delete/cablemagazine/<int:pk>", DeleteCableMagazineView.as_view(), name="cablemagazine_delete"),
    path("moderator/delete/violations/<int:pk>", DeleteViolationsView.as_view(), name="violations_delete"),
    path("moderator/delete/visual/<int:pk>", DeleteVisualView.as_view(), name="visual_delete"),
    path(
        "moderator/delete/equipment_installation/<int:pk>",
        DeleteEquipmentInstallationView.as_view(),
        name="equipment_installation_delete",
    ),
    path("moderator/delete/execution/<int:pk>", DeleteExecutionView.as_view(), name="execution_delete"),
]
