from infoMFSS.apps import InfomfssConfig
from django.urls import path
from infoMFSS.views import MFSSTemplateView, percent_view, MyListView

# from mfss.views import SubsystemTemplateView
# from infoMFSS.views import index

app_name = InfomfssConfig.name

urlpatterns = [
    path('', MFSSTemplateView.as_view(), name='home'),
    path('percents/', percent_view, name='percents'),
    path('equipment_list/', MyListView.as_view(), name='equipment')
]
