from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    has_agreed_to_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def average_rating(self):
        ratings = self.user.received_ratings.all()
        if not ratings:
            return 0
        return sum(r.score for r in ratings) / len(ratings)


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('mobiles', 'Mobiles'),
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('vehicles', 'Vehicles'),
        ('appliances', 'Appliances'),
        ('books', 'Books'),
        ('fashion', 'Fashion'),
    ]

    EXCHANGE_CHOICES = [
        ('money', 'Money Only'),
        ('barter', 'Barter Only'),
        ('both', 'Money or Barter'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    condition = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='electronics')

    exchange_type = models.CharField(max_length=10, choices=EXCHANGE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    barter_description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/')  # Primary thumbnail
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('offer', 'New Offer'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_rejected', 'Offer Rejected'),
        ('message', 'New Message'),
        ('system', 'System Update'),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications_sent', null=True, blank=True)
    
    # Generic link to target object
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    
    verb = models.CharField(max_length=255) # e.g., "sent you an offer for"
    description = models.TextField(blank=True, null=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.verb}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)


class Offer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    OFFER_TYPE_CHOICES = [
        ('money', 'Money'),
        ('barter', 'Barter'),
        ('both', 'Both (Money + Barter)'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_offers')
    
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES, default='barter')
    offered_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='offered_in_deals')
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer for {self.product.name} from {self.sender.username}"


class Thread(models.Model):
    offer = models.OneToOneField(Offer, on_delete=models.CASCADE, related_name='thread')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thread for Offer #{self.offer.id}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Msg from {self.sender.username} at {self.timestamp}"


class Rating(models.Model):
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rater', 'rated_user')


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


# Signals for Profile
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
