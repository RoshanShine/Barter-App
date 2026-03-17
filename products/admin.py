from django.contrib import admin
from .models import Product, Profile, Rating, Wishlist, ProductImage, Offer

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'created_at')
    search_fields = ('user__username', 'bio')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'exchange_type', 'is_approved')
    list_filter = ('category', 'exchange_type', 'is_approved')
    list_editable = ('is_approved',)
    search_fields = ('name', 'description')
    readonly_fields = ('id',)
    actions = ['approve_products', 'unapprove_products']

    def approve_products(self, request, queryset):
        queryset.update(is_approved=True)
    approve_products.short_description = "Approve selected products"

    def unapprove_products(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_products.short_description = "Unapprove selected products"

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'sender', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product__name', 'sender__username', 'message')

admin.site.register(Rating)
admin.site.register(Wishlist)
admin.site.register(ProductImage)
