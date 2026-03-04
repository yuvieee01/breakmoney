from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('', views.friend_list_view, name='list'),
    path('add/', views.friend_add_view, name='add'),
    path('<int:friend_id>/', views.friend_detail_view, name='detail'),
    path('<int:friend_id>/remove/', views.friend_remove_view, name='remove'),
]