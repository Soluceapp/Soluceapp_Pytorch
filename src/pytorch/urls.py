from django.urls import path,include
from . import views


app_name="pytorch"

urlpatterns = [
    path('configuration_model',views.confmia_user,name="confmia"),
    path('configuration_indicateur',views.confind_user,name="confind"),
    path('previsions',views.prevision_user,name="prevision"),
    path('search/', include('charge.urls')),
]