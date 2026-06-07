from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from foodapp import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home & Profile
    path('', views.home, name='home'),
    # 🔑 FIXED: Changed name from 'profile_page' to 'profile' to match your dashboard buttons!
    path('profile/', views.profile_view, name='profile'),

    # Registration
    path('ngo/register/', views.register_ngo, name='register_ngo'),
    path('volunteer/register/', views.register_volunteer, name='register_volunteer'),

    # Login/Logout
    path('login/', views.user_login, name='user_login'),
    path('accounts/login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Food Logic
    path('food/add/', views.add_food, name='add_food'),
    path('food/list/', views.food_list, name='food_list'),
    path('food/request/', views.request_food, name='request_food'),

    # Dashboards & Workspaces
    path('ngo/dashboard/', views.ngo_dashboard, name='ngo_dashboard'),
    path('volunteer/dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    
    # Volunteer Operations
    path('accept-delivery/<int:request_id>/', views.accept_delivery, name='accept_delivery'),
    path('mark-delivered/<int:request_id>/', views.mark_delivered, name='mark_delivered'),
]