from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Pizza, Review, CartItem, Order, OrderItem

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'address']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)
        profile = instance.profile
        profile.phone = profile_data.get('phone', profile.phone)
        profile.address = profile_data.get('address', profile.address)
        profile.save()
        return instance

class PizzaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = ['id', 'name', 'description', 'price', 'rating', 'popularity']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Review
        fields = ['id', 'pizza', 'user', 'rating', 'comment', 'created_at']

class CartItemSerializer(serializers.ModelSerializer):
    pizza = PizzaSerializer(read_only=True)
    pizza_id = serializers.PrimaryKeyRelatedField(queryset=Pizza.objects.all(), source='pizza', write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'pizza', 'pizza_id', 'quantity', 'added_at']

class OrderItemSerializer(serializers.ModelSerializer):
    pizza = PizzaSerializer()

    class Meta:
        model = OrderItem
        fields = ['pizza', 'quantity', 'price_per_item']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'created_at', 'address', 'phone', 'payment_status', 'items']

class OrderCreateSerializer(serializers.Serializer):
    cart_item_ids = serializers.ListField(child=serializers.IntegerField())

    def validate_cart_item_ids(self, value):
        if not value:
            raise serializers.ValidationError("Cart is empty")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = CartItem.objects.filter(user=user, id__in=validated_data['cart_item_ids'])
        if not cart_items.exists():
            raise serializers.ValidationError("Cart items not found")

        total_price = sum(item.pizza.price * item.quantity for item in cart_items)
        profile = user.profile
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            address=profile.address,
            phone=profile.phone,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                pizza=item.pizza,
                quantity=item.quantity,
                price_per_item=item.pizza.price,
            )
        cart_items.delete()  # Очистка корзины после оформления заказа
        return order
