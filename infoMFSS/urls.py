from infoMFSS.apps import InfomfssConfig
from django.urls import path
from infoMFSS.views import MFSSTemplateView, percent_view, EquipmentListView, CableListView

# from mfss.views import SubsystemTemplateView
# from infoMFSS.views import index

app_name = InfomfssConfig.name

urlpatterns = [
    path('', MFSSTemplateView.as_view(), name='home'),
    path('percents/', percent_view, name='percents'),
    path('equipment_list/', EquipmentListView.as_view(), name='equipment'),
    path('cable_list/', CableListView.as_view(), name='cable')
]
