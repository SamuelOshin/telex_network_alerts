from django.urls import path
from . import views

urlpatterns = [
    path('check/', views.check_network_status, name='check_status'),
    path('configure/', views.configure_webhook, name='configure_webhook'),
    path('integration.json', views.handle_telex_json, name='telex_json'),
]
