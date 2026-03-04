from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    # Individual Expense Creation
    path('add/', views.expense_create_view, name='create'),
    
    # Detail and Delete
    path('<int:expense_id>/', views.expense_detail_view, name='detail'),
    path('<int:expense_id>/delete/', views.expense_delete_view, name='delete'),
    
    # Group Expense Creation
    path('group/<int:group_id>/add/', views.group_expense_create_view, name='group_create'),
]