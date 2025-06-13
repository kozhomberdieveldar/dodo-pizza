from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Профиль с адресом и телефоном
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

# Категории товаров
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

# Пицца с рейтингом и популярностью
class Pizza(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='pizzas/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_available = models.BooleanField(default=True)
    popularity = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Отзывы на пиццу
class Review(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# Корзина для пользователя
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pizza')

    def get_total_price(self):
        return self.pizza.price * self.quantity

# Заказ с статусом
class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('PROCESSING', 'В обработке'),
        ('DELIVERING', 'Доставляется'),
        ('COMPLETED', 'Выполнен'),
        ('CANCELED', 'Отменён'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('NOT_PAID', 'Не оплачен'),
        ('PAID', 'Оплачен'),
        ('REFUNDED', 'Возвращён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    pizzas = models.ManyToManyField(Pizza, through='OrderItem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='NOT_PAID')
    delivery_time = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=6, decimal_places=2)

    def get_cost(self):
        return self.price_per_item * self.quantity

# Промокоды
class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    min_order_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to
