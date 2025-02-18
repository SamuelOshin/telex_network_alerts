from django.urls import path
from .views import check_network_status, handle_telex_json

urlpatterns = [
    path("check/", check_network_status, name="check_network"),
    path("telex-json/", handle_telex_json, name="handle_telex_json"),
]
