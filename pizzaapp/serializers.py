from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Pizza, Review, CartItem, Order, OrderItem, PromoCode

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
        fields = ['id', 'name', 'description', 'price', 'image', 'rating', 'popularity', 'is_available', 'category']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Review
        fields = ['id', 'pizza', 'user', 'rating', 'comment', 'created_at']

class CartItemSerializer(serializers.ModelSerializer):
    pizza = PizzaSerializer(read_only=True)
    pizza_id = serializers.PrimaryKeyRelatedField(queryset=Pizza.objects.all(), source='pizza', write_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'pizza', 'pizza_id', 'quantity', 'added_at', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

class OrderItemSerializer(serializers.ModelSerializer):
    pizza = PizzaSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['pizza', 'quantity', 'price_per_item', 'total_price']

    def get_total_price(self, obj):
        return obj.get_cost()

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'status_display', 'total_price', 'created_at', 'address', 
                 'phone', 'payment_status', 'payment_status_display', 'delivery_time', 
                 'comment', 'items']

class OrderCreateSerializer(serializers.ModelSerializer):
    cart_item_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    address = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    comment = serializers.CharField(required=False)
    promo_code = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Order
        fields = ['cart_item_ids', 'address', 'phone', 'comment', 'promo_code']

    def validate_cart_item_ids(self, value):
        if not value:
            raise serializers.ValidationError("Cart is empty")
        return value

    def validate(self, data):
        promo_code = data.get('promo_code')
        if promo_code:
            try:
                promo = PromoCode.objects.get(code=promo_code, is_active=True)
                if not promo.is_valid():
                    raise serializers.ValidationError("Promo code is expired")
            except PromoCode.DoesNotExist:
                raise serializers.ValidationError("Invalid promo code")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = CartItem.objects.filter(user=user, id__in=validated_data['cart_item_ids'])
        if not cart_items.exists():
            raise serializers.ValidationError("Cart items not found")

        total_price = sum(item.get_total_price() for item in cart_items)
        
        # Apply promo code if provided
        promo_code = validated_data.get('promo_code')
        if promo_code:
            promo = PromoCode.objects.get(code=promo_code)
            if promo.discount_percent > 0:
                total_price = total_price * (1 - promo.discount_percent / 100)
            if promo.discount_amount > 0:
                total_price = max(0, total_price - promo.discount_amount)

        profile = user.profile
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            address=validated_data.get('address', profile.address),
            phone=validated_data.get('phone', profile.phone),
            comment=validated_data.get('comment', '')
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

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['code', 'discount_percent', 'discount_amount', 'min_order_amount', 'valid_from', 'valid_to']
