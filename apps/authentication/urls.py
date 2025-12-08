from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    path('profile/', views.user_profile, name='user_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/deactivate/', views.user_deactivate, name='user_deactivate'),
    path('users/<int:pk>/activate/', views.user_activate, name='user_activate'),

    path('dashboard/', views.dashboard, name='dashboard'),
]