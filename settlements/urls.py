from django.urls import path
from . import views

app_name = 'settlements'

urlpatterns = [
    path('new/', views.create_settlement_view, name='create'),
    path('<int:settlement_id>/delete/', views.delete_settlement_view, name='delete'),
]
