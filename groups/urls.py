from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.group_list_view, name='list'),
    path('new/', views.group_create_view, name='create'),
    path('<int:group_id>/', views.group_detail_view, name='detail'),
    path('<int:group_id>/balances/', views.group_balances_view, name='balances'), # NEW ROUTE
    path('<int:group_id>/delete/', views.group_delete_view, name='delete'),
    path('<int:group_id>/remove-member/<int:user_id>/', views.group_remove_member_view, name='remove_member'),
]