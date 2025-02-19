from django.urls import path
from . import views

urlpatterns = [
    path('configure/', views.configure_webhook, name='configure_webhook'),
    path('integration.json', views.handle_telex_json, name='telex_json'),
]
