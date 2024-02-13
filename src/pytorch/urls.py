from django.urls import path,include
from . import views


app_name="pytorch"

urlpatterns = [
    path('configuration_model',views.confmia_user,name="confmia"),
    path('creation_model',views.creamia_user,name="creamia"),
    path('chargement_model',views.chargemia_user,name="chargemia"),
    path('previsions',views.prevision_user,name="prevision"),
    path('board/', include('charge.urls')),
]