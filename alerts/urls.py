from django.urls import path
from .views import check_network_status

urlpatterns = [
    path("check/", check_network_status, name="check_network"),
]
