from django.urls import path,include
from . import views


app_name="pytorch"

urlpatterns = [
    path('config_system',views.confsys_user,name="confsys"),
    path('solution_pytorch',views.solution_user,name="solution"),
    path('previsions',views.prevision_user,name="prevision"),
    path('search/', include('charge.urls')),
]