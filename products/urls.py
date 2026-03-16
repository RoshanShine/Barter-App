from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('register/', views.register, name='register'),
    
    path('make-offer/<int:pk>/', views.make_offer, name='make_offer'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('handle-offer/<int:pk>/<action>/', views.handle_offer, name='handle_offer'),

    # Profile & Trust
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile-edit/', views.edit_profile, name='edit_profile'),
    path('rate/<str:username>/', views.rate_user, name='rate_user'),
    path('wishlist-toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),

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