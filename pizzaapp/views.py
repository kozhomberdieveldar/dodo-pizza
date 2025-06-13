from rest_framework import generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models import Q, F, Avg
from django.shortcuts import render, redirect
from .models import Profile, Pizza, Review, CartItem, Order, PromoCode, Category
from .serializers import (
    UserSerializer, PizzaSerializer, ReviewSerializer,
    CartItemSerializer, OrderSerializer, OrderCreateSerializer,
    ProfileSerializer, PromoCodeSerializer,
)

from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

# Регистрация пользователя с созданием профиля
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        phone = request.data.get('phone')
        address = request.data.get('address')

        if not username or not password or not email:
            return Response({'error': 'Username, email and password required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, phone=phone, address=address)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Авторизация с токеном
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'user_id': token.user_id,
            'username': token.user.username
        })

# Просмотр и обновление профиля
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return self.request.user.profile

# Пиццы с поиском и фильтрацией
class PizzaList(generics.ListAPIView):
    serializer_class = PizzaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'popularity', 'rating']

    def get_queryset(self):
        qs = Pizza.objects.filter(is_available=True)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs

# Отзывы
class ReviewListCreate(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        pizza_id = self.request.query_params.get('pizza')
        if pizza_id:
            return Review.objects.filter(pizza_id=pizza_id).order_by('-created_at')
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)
        pizza = serializer.validated_data['pizza']
        pizza.rating = Review.objects.filter(pizza=pizza).aggregate(
            avg_rating=Avg('rating'))['avg_rating']
        pizza.save()

# Корзина
class CartItemListCreate(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        items = serializer.data
        total = sum(item['total_price'] for item in items)
        return Response({'items': items, 'total': total})

class CartItemUpdate(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

class CartItemDelete(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

# Заказы
class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Order.objects.all()

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Order.objects.all()

# Промокоды
class PromoCodeCreate(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PromoCodeSerializer(data=request.data)
        if serializer.is_valid():
            promo_code = serializer.save()
            return Response({
                'code': promo_code.code,
                'discount_percent': promo_code.discount_percent,
                'discount_amount': promo_code.discount_amount,
                'min_order_amount': promo_code.min_order_amount,
                'valid_from': promo_code.valid_from,
                'valid_to': promo_code.valid_to
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PromoCodeValidate(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Promo code is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            promo = PromoCode.objects.get(code=code, is_active=True)
            if not promo.is_valid():
                return Response({'error': 'Promo code is expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'code': promo.code,
                'discount_percent': promo.discount_percent,
                'discount_amount': promo.discount_amount,
                'min_order_amount': promo.min_order_amount
            })
        except PromoCode.DoesNotExist:
            return Response({'error': 'Invalid promo code'}, status=status.HTTP_400_BAD_REQUEST)

def index(request):
    return render(request, 'index.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    categories = Category.objects.all()
    return Response([{
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug
    } for cat in categories])

@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_by_category(request, category_slug):
    try:
        category = Category.objects.get(slug=category_slug)
        products = Pizza.objects.filter(category=category)
        return Response([{
            'id': pizza.id,
            'name': pizza.name,
            'description': pizza.description,
            'price': pizza.price,
            'image': pizza.image.url if pizza.image else None
        } for pizza in products])
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        cart_data = request.data.get('cart', {})
        items = cart_data.get('items', [])
        
        if not items:
            return Response({'error': 'Cart is empty'}, status=400)
            
        # Создаем заказ
        order = Order.objects.create(
            total_amount=cart_data.get('total', 0),
            status='pending'
        )
        
        # Добавляем товары в заказ
        for item in items:
            pizza = Pizza.objects.get(id=item['pizza_id'])
            order.items.create(
                pizza=pizza,
                quantity=item['quantity'],
                price=item['price']
            )
            
        return Response({
            'order_id': order.id,
            'status': order.status,
            'total': order.total_amount
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'name')
    
    products = Pizza.objects.all()
    
    # Поиск по названию и описанию
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Фильтрация по цене
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Сортировка
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    
    return Response([{
        'id': pizza.id,
        'name': pizza.name,
        'description': pizza.description,
        'price': pizza.price,
        'image': pizza.image.url if pizza.image else None,
        'category': pizza.category.name if pizza.category else None
    } for pizza in products])

@api_view(['POST'])
@permission_classes([AllowAny])
def update_cart_item(request):
    try:
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or not quantity:
            return Response({'error': 'Missing required fields'}, status=400)
            
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'id': cart_item.id,
            'quantity': cart_item.quantity,
            'subtotal': cart_item.subtotal
        })
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Неверный email или пароль')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
        else:
            user = User.objects.create_user(username=username, password=password1)
            auth_login(request, user)
            return redirect('/')
    return render(request, 'register.html')
