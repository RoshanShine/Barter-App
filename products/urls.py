from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<str:pk>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('register/', views.register, name='register'),
    
    path('make-offer/<str:pk>/', views.make_offer, name='make_offer'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('handle-offer/<str:pk>/<action>/', views.handle_offer, name='handle_offer'),
    path('chat/<int:thread_id>/', views.chat_view, name='chat_view'),
    path('agree-terms/', views.agree_terms, name='agree_terms'),
    path('product/<str:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<str:pk>/delete/', views.delete_product, name='delete_product'),

    # Profile & Trust
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile-edit/', views.edit_profile, name='edit_profile'),
    path('profile-edit/security/', views.change_password, name='change_password'),
    path('profile-edit/notifications/', views.settings_notifications, name='settings_notifications'),
    path('rate/<str:username>/', views.rate_user, name='rate_user'),
    path('wishlist-toggle/<str:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Notifications List
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-as-read/<int:pk>/', views.mark_notification_as_read, name='mark_notification_as_read'),

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'
    ),
]