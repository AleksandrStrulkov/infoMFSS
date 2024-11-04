from infoMFSS.apps import InfomfssConfig
from django.urls import path
from infoMFSS.views import MFSSTemplateView
# from mfss.views import SubsystemTemplateView
from infoMFSS.views import index

app_name = InfomfssConfig.name

urlpatterns = [
    path('', MFSSTemplateView.as_view(), name='home'),
    path('subsystem_list/', index, name='subsystem'),
]
