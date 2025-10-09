from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/profile/', views.ProfileView.as_view(), name='profile'),
    path('api/delete-account/', views.DeleteAccountView.as_view(), name='delete-account'),
    path('api/products/', views.ProductsView.as_view(), name='products'),
    path('api/orders/', views.OrdersView.as_view(), name='orders'),
]