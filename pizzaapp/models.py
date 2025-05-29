from django.db import models
from django.contrib.auth.models import User

# Профиль с адресом и телефоном
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

# Пицца с рейтингом и популярностью
class Pizza(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.FloatField(default=0)
    popularity = models.IntegerField(default=0)  # например, число заказов

    def __str__(self):
        return self.name

# Отзывы на пиццу
class Review(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Корзина для пользователя - временное хранение заказа до оплаты
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pizza')

# Заказ с статусом
class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('PROCESSING', 'В обработке'),
        ('DELIVERING', 'Доставляется'),
        ('COMPLETED', 'Выполнен'),
        ('CANCELED', 'Отменён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    pizzas = models.ManyToManyField(Pizza, through='OrderItem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    payment_status = models.CharField(max_length=20, default='NOT_PAID')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=6, decimal_places=2)

    def get_cost(self):
        return self.price_per_item * self.quantity
