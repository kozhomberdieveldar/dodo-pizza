from django.contrib import admin
from .models import Profile, Pizza, Review, CartItem, Order, OrderItem

admin.site.register(Profile)
admin.site.register(Pizza)
admin.site.register(Review)
admin.site.register(CartItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    inlines = [OrderItemInline]

