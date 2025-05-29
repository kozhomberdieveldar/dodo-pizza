from rest_framework import generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Profile, Pizza, Review, CartItem, Order
from .serializers import (
    UserSerializer, PizzaSerializer, ReviewSerializer,
    CartItemSerializer, OrderSerializer, OrderCreateSerializer,
    ProfileSerializer,
)

from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

# Регистрация пользователя с созданием профиля
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not password or not email:
            return Response({'error': 'Username, email and password required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)  # создаём профиль с пустыми данными
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
    permission_classes = [permissions.IsAuthenticated]

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
        qs = Pizza.objects.all()
        # Можно добавить дополнительную фильтрацию здесь
        return qs

# Отзывы
class ReviewListCreate(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        pizza_id = self.request.query_params.get('pizza')
        if pizza_id:
            return Review.objects.filter(pizza_id=pizza_id).order_by('-created_at')
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Корзина
class CartItemListCreate(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemDelete(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

# Заказы: просмотр и создание из корзины
class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user).order_by('-created_at')
        # Можно добавить фильтрацию по статусу, дате и т.п.
        return qs

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
