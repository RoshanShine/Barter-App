from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q, Avg
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Product, Offer, Profile, Rating, Wishlist
from .forms import ProductForm


def home(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    products = Product.objects.all().order_by('-id')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query) |
            Q(barter_description__icontains=query) |
            Q(condition__icontains=query)
        )

    if category:
        products = products.filter(category=category)

    return render(request, 'products/home.html', {
        'products': products,
        'query': query,
        'selected_category': category,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    description_lines = product.description.split('\n') if product.description else []
    barter_lines = product.barter_description.split('\n') if product.barter_description else []

    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'description_lines': description_lines,
        'barter_lines': barter_lines,
        'is_in_wishlist': is_in_wishlist,
    })


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()

            # Handle more_images
            files = request.FILES.getlist('more_images')
            for f in files:
                ProductImage.objects.create(product=product, image=f)

            messages.success(request, "Product listed successfully!")
            return redirect('home')

        else:
            print(form.errors)

    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


@login_required
def make_offer(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if product.user == request.user:
        messages.warning(request, "You cannot make an offer on your own product.")
        return redirect('product_detail', pk=pk)
        
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Offer.objects.create(
                product=product,
                sender=request.user,
                message=message
            )
            messages.success(request, "Your offer has been sent!")
            return redirect('product_detail', pk=pk)
            
    return render(request, 'products/make_offer.html', {'product': product})


@login_required
def dashboard(request):
    received_offers = Offer.objects.filter(product__user=request.user).order_by('-created_at')
    sent_offers = Offer.objects.filter(sender=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    return render(request, 'products/dashboard.html', {
        'received_offers': received_offers,
        'sent_offers': sent_offers,
        'wishlist_items': wishlist_items
    })


@login_required
def handle_offer(request, pk, action):
    offer = get_object_or_404(Offer, pk=pk, product__user=request.user)
    
    if action == 'accept':
        offer.status = 'accepted'
        messages.success(request, f"Offer for {offer.product.name} accepted!")
    elif action == 'reject':
        offer.status = 'rejected'
        messages.warning(request, f"Offer for {offer.product.name} rejected.")
        
    offer.save()
    return redirect('dashboard')


@login_required
def profile_view(request, username):
    user_obj = get_object_or_404(User, username=username)
    user_products = Product.objects.filter(user=user_obj).order_by('-id')
    received_ratings = Rating.objects.filter(rated_user=user_obj).order_by('-created_at')
    avg_rating = received_ratings.aggregate(Avg('score'))['score__avg'] or 0
    
    return render(request, 'products/profile.html', {
        'profile_user': user_obj,
        'user_products': user_products,
        'ratings': received_ratings,
        'avg_rating': avg_rating
    })


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')
        
        profile.bio = bio
        if avatar:
            profile.avatar = avatar
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('profile_view', username=request.user.username)
        
    return render(request, 'products/edit_profile.html', {'profile': profile})


@login_required
def rate_user(request, username):
    rated_user = get_object_or_404(User, username=username)
    if rated_user == request.user:
        messages.error(request, "You cannot rate yourself.")
        return redirect('profile_view', username=username)
        
    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment')
        
        Rating.objects.update_or_create(
            rater=request.user,
            rated_user=rated_user,
            defaults={'score': score, 'comment': comment}
        )
        messages.success(request, f"Rating submitted for {username}!")
        return redirect('profile_view', username=username)
        
    return render(request, 'products/rate_user.html', {'rated_user': rated_user})


@login_required
def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        messages.success(request, "Added to wishlist.")
        
    return redirect('product_detail', pk=pk)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})