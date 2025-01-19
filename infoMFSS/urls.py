from django.views.generic import TemplateView

from infoMFSS.apps import InfomfssConfig
from django.urls import path
from infoMFSS.views import percent_view, EquipmentListView, CableListView, BoxListView, \
    EquipmentFileListView, CableFileListView, ViolationsListView, VisualListView, ProjectEquipmentListView, \
    ProjectCableListView, MFSSPercentTemplateView, ContactFormView

# from mfss.views import SubsystemTemplateView
# from infoMFSS.views import index

app_name = InfomfssConfig.name

urlpatterns = [
        path('', MFSSPercentTemplateView.as_view(), name='home'),
        path('percents/', percent_view, name='percents'),
        path('equipment_list/', EquipmentListView.as_view(), name='equipment'),
        # path('equipment_list/', EquipmentView.as_view(), name='equipment'),
        path('cable_list/', CableListView.as_view(), name='cable'),
        path('box_list/', BoxListView.as_view(), name='box'),
        path('equipment_file/', EquipmentFileListView.as_view(), name='equipment_file'),
        path('cable_file/', CableFileListView.as_view(), name='cable_file'),
        path('violations/', ViolationsListView.as_view(), name='violations'),
        path('visual/', VisualListView.as_view(), name='visual'),
        path('project_equipment/', ProjectEquipmentListView.as_view(), name='project_equipment'),
        path('project_cable/', ProjectCableListView.as_view(), name='project_cable'),
        path('contact/', ContactFormView.as_view(), name='contact'),
        path('contact/success/', TemplateView.as_view(template_name='mfss/contact_success.html'), name='contact_success'),
]