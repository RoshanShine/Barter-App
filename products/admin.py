from django.contrib import admin
from .models import Product, Profile, Rating, Wishlist, ProductImage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'created_at')
    search_fields = ('user__username', 'bio')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'exchange_type', 'price')
    list_filter = ('category', 'exchange_type')
    search_fields = ('name', 'description', 'location')

admin.site.register(Rating)
admin.site.register(Wishlist)
admin.site.register(ProductImage)
