from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.CustomAuthToken.as_view(), name='login'),
    path('api/profile/', views.ProfileView.as_view(), name='profile'),
    
    # Пиццы
    path('api/pizzas/', views.PizzaList.as_view(), name='pizza-list'),
    path('api/reviews/', views.ReviewListCreate.as_view(), name='review-list'),
    
    # Корзина
    path('api/cart/', views.CartItemListCreate.as_view(), name='cart-list'),
    path('api/cart/<int:item_id>/', views.CartItemUpdate.as_view(), name='cart-update'),
    path('api/cart/<int:item_id>/delete/', views.CartItemDelete.as_view(), name='cart-delete'),
    
    # Заказы
    path('api/orders/', views.OrderList.as_view(), name='order-list'),
    path('api/orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('api/orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Промокоды
    path('api/promo/create/', views.PromoCodeCreate.as_view(), name='promo-create'),
    path('api/promo/validate/', views.PromoCodeValidate.as_view(), name='promo-validate'),
    
    # Новые API-эндпоинты
    path('api/categories/', views.get_categories, name='get_categories'),
    path('api/categories/<str:category_slug>/products/', views.get_products_by_category, name='get_products_by_category'),
    path('api/orders/', views.create_order, name='create_order'),
    path('api/search/', views.search_products, name='search_products'),
    path('api/cart/update/', views.update_cart_item, name='update_cart_item'),
    path('auth/', include('social_django.urls', namespace='social')),
]