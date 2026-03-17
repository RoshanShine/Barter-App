from django.contrib import admin
from .models import Product, Profile, Rating, Wishlist, ProductImage, Offer

class NoLogMixin:
    """Mixin to disable admin logging because LogEntry fails with MongoDB ObjectIds"""
    def log_addition(self, *args, **kwargs): pass
    def log_change(self, *args, **kwargs): pass
    def log_deletion(self, *args, **kwargs): pass

@admin.register(Profile)
class ProfileAdmin(NoLogMixin, admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'created_at')
    search_fields = ('user__username', 'bio')

@admin.register(Product)
class ProductAdmin(NoLogMixin, admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'exchange_type', 'is_approved')
    list_filter = ('category', 'exchange_type', 'is_approved')
    list_editable = ('is_approved',)
    search_fields = ('name', 'description')
    readonly_fields = ('id',)
    actions = ['approve_products', 'unapprove_products']

    def approve_products(self, request, queryset):
        queryset.update(is_approved=True)

    def unapprove_products(self, request, queryset):
        queryset.update(is_approved=False)

@admin.register(Offer)
class OfferAdmin(NoLogMixin, admin.ModelAdmin):
    list_display = ('product', 'sender', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product__name', 'sender__username', 'message')

@admin.register(Rating)
class RatingAdmin(NoLogMixin, admin.ModelAdmin):
    pass

@admin.register(Wishlist)
class WishlistAdmin(NoLogMixin, admin.ModelAdmin):
    pass

@admin.register(ProductImage)
class ProductImageAdmin(NoLogMixin, admin.ModelAdmin):
    pass
