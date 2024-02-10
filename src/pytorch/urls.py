from django.urls import path,include
from . import views


app_name="pytorch"

urlpatterns = [
    path('board/configuration_IA',views.confmia_user,name="confmia"),
    path('board/previsions',views.prevision_user,name="prevision"),

]