"""
URL configuration for dodopizza project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from pizzaapp.views import (
    RegisterView, CustomAuthToken, ProfileView, PizzaList, ReviewListCreate,
    CartItemListCreate, CartItemDelete, OrderList, OrderCreateView,
)

# Swagger schema setup
schema_view = get_schema_view(
   openapi.Info(
      title="Dodo Pizza API",
      default_version='v1',
      description="Документация API для приложения Dodo Pizza",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomAuthToken.as_view(), name='login'),

    path('api/profile/', ProfileView.as_view(), name='profile'),

    path('api/pizzas/', PizzaList.as_view(), name='pizza-list'),

    path('api/reviews/', ReviewListCreate.as_view(), name='reviews'),

    path('api/cart/', CartItemListCreate.as_view(), name='cart'),
    path('api/cart/<int:item_id>/', CartItemDelete.as_view(), name='cart-item-delete'),

    path('api/orders/', OrderList.as_view(), name='orders'),
    path('api/orders/create/', OrderCreateView.as_view(), name='order-create'),

    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]