from django.contrib import admin
from .models import Product, Profile, Rating, Wishlist, ProductImage, Offer, Thread, Message

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'has_agreed_to_terms', 'created_at')
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

    def unapprove_products(self, request, queryset):
        queryset.update(is_approved=False)

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'sender', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product__name', 'sender__username', 'message')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('rater', 'rated_user', 'score', 'created_at')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'text', 'timestamp')
    can_delete = False

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer', 'created_at')
    filter_horizontal = ('participants',)
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'thread', 'timestamp')
    list_filter = ('timestamp', 'sender')
    search_fields = ('text', 'sender__username')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass
