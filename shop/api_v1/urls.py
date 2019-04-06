
from django.urls import include, path
from rest_framework import routers
from django.contrib import admin
from api_v1 import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'photos', views.PhotoViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'orders', views.OrderViewSet)



app_name = 'api_v1'

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='api_token_auth'),
    path('admin/', admin.site.urls),
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('token-login/', views.TokenLoginView.as_view(), name='api_token_re_login'),
    path('register/activate/', views.UserActivateView.as_view(), name='register_activate')
]