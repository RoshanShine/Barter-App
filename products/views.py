from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q, Avg
from django.contrib import messages
from users.forms import CustomUserCreationForm

User = get_user_model()

from .models import Product, ProductImage, Offer, Profile, Rating, Wishlist, Thread, Message, Notification
from django.contrib.contenttypes.models import ContentType
from .forms import ProductForm

def create_notification(recipient, actor, target_object, verb, notification_type, description=""):
    if recipient == actor:
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        target_content_type=ContentType.objects.get_for_model(target_object),
        target_object_id=target_object.id,
        verb=verb,
        notification_type=notification_type,
        description=description
    )


def home(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.filter(is_approved=True).order_by('-id')
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    if category:
        products = products.filter(category=category)
        
    return render(request, 'products/home.html', {
        'products': products,
        'categories': Product.CATEGORY_CHOICES,
        'selected_category': category,
        'query': query
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to SwapHub, {user.username}!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def product_list(request):
    products = Product.objects.filter(is_approved=True).order_by('-id')
    return render(request, 'products/product_list.html', {'products': products})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            
            # Save multiple images
            files = request.FILES.getlist('images')
            for f in files:
                ProductImage.objects.create(product=product, image=f)
                
            messages.success(request, "Product added successfully and is awaiting approval.")
            return redirect('dashboard')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            
            # Add more images if needed
            files = request.FILES.getlist('images')
            for f in files:
                ProductImage.objects.create(product=product, image=f)
                
            messages.success(request, "Product updated successfully.")
            return redirect('dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('dashboard')
    return render(request, 'products/delete_confirm.html', {'product': product})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def make_offer(request, pk):
    product = get_object_or_404(Product, pk=pk)
    user_products = Product.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        offer_type = request.POST.get('offer_type')
        offered_price = request.POST.get('offered_price')
        offered_product_id = request.POST.get('offered_product')

        if message and offer_type:
            offered_product = None
            if offered_product_id:
                offered_product = get_object_or_404(Product, id=offered_product_id, user=request.user)

            offer = Offer.objects.create(
                product=product,
                sender=request.user,
                message=message,
                offer_type=offer_type,
                offered_price=offered_price if offered_price else None,
                offered_product=offered_product
            )
            
            # Notify product owner
            create_notification(
                recipient=product.user,
                actor=request.user,
                target_object=offer,
                verb=f"sent you an offer for {product.name}",
                notification_type='offer'
            )
            
            messages.success(request, "Your offer has been sent!")
            return redirect('product_detail', pk=pk)
        else:
            messages.error(request, "Please fill in all required fields.")
            
    return render(request, 'products/make_offer.html', {
        'product': product,
        'user_products': user_products
    })


@login_required
def dashboard(request):
    received_offers = Offer.objects.filter(product__user=request.user).order_by('-created_at')
    sent_offers = Offer.objects.filter(sender=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user)
    my_products = Product.objects.filter(user=request.user).order_by('-id')
    
    # Calculate deals done: accepted offers involving the user (as buyer or seller)
    deals_done_count = Offer.objects.filter(
        (Q(product__user=request.user) | Q(sender=request.user)) & Q(status='accepted')
    ).count()
    
    return render(request, 'products/dashboard.html', {
        'received_offers': received_offers,
        'sent_offers': sent_offers,
        'wishlist_items': wishlist_items,
        'my_products': my_products,
        'deals_done_count': deals_done_count
    })


@login_required
def handle_offer(request, pk, action):
    offer = get_object_or_404(Offer, pk=pk, product__user=request.user)
    
    if action == 'accept':
        offer.status = 'accepted'
        offer.save()
        
        # Notify sender
        create_notification(
            recipient=offer.sender,
            actor=request.user,
            target_object=offer,
            verb=f"accepted your offer for {offer.product.name}",
            notification_type='offer_accepted'
        )
        
        # Create a chat thread for accepted offer
        thread, created = Thread.objects.get_or_create(offer=offer)
        if created:
            thread.participants.add(offer.sender, offer.product.user)
            
        messages.success(request, f"Offer for {offer.product.name} accepted! Chat is now open.")
    elif action == 'reject':
        offer.status = 'rejected'
        offer.save()
        
        # Notify sender
        create_notification(
            recipient=offer.sender,
            actor=request.user,
            target_object=offer,
            verb=f"rejected your offer for {offer.product.name}",
            notification_type='offer_rejected'
        )
        
        messages.warning(request, f"Offer for {offer.product.name} rejected.")
        
    return redirect('dashboard')


@login_required
def chat_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    
    # Permission check: User must be a participant OR a superuser
    if request.user not in thread.participants.all() and not request.user.is_superuser:
        messages.error(request, "You do not have permission to access this chat.")
        return redirect('dashboard')
        
    # Terms check (Admins bypass)
    if not request.user.profile.has_agreed_to_terms and not request.user.is_superuser:
        return render(request, 'products/agree_terms.html', {'thread_id': thread_id})
        
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            msg = Message.objects.create(thread=thread, sender=request.user, text=text)
            
            # Notify the other participant
            other_user = thread.participants.exclude(id=request.user.id).first()
            if other_user:
                create_notification(
                    recipient=other_user,
                    actor=request.user,
                    target_object=msg,
                    verb=f"sent you a message in chat",
                    notification_type='message',
                    description=text[:50] + "..." if len(text) > 50 else text
                )
                
            return redirect('chat_view', thread_id=thread_id)
            
    chat_messages = thread.messages.all()
    return render(request, 'products/chat.html', {
        'thread': thread,
        'chat_messages': chat_messages,
        'other_user': thread.participants.exclude(id=request.user.id).first()
    })


@login_required
def agree_terms(request):
    if request.method == 'POST':
        request.user.profile.has_agreed_to_terms = True
        request.user.profile.save()
        messages.success(request, "Thank you for agreeing to our terms. You can now contact traders safely!")
        
        thread_id = request.POST.get('thread_id')
        next_url = request.POST.get('next')
        
        if next_url:
            return redirect(next_url)
        if thread_id and thread_id != 'None':
            return redirect('chat_view', thread_id=thread_id)
        return redirect('dashboard')
    
    # Also support GET for direct access from "Contact Owner"
    return render(request, 'products/agree_terms.html', {
        'next': request.GET.get('next'),
        'thread_id': request.GET.get('thread_id')
    })


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
    from .forms import UserUpdateForm, ProfileForm
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile_view', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=profile)
        
    return render(request, 'products/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })


@login_required
def settings_notifications(request):
    # This view could handle notification preferences in the future
    return render(request, 'products/settings_notifications.html')


@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    # Mark all as read when viewing the list
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    return render(request, 'products/notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Optional: redirect to target object
    if notification.target_object:
        if notification.notification_type == 'message':
            return redirect('chat_view', thread_id=notification.target_object.thread.id)
        elif notification.notification_type.startswith('offer'):
            return redirect('dashboard')
            
    return redirect('notifications_list')


# Wishlist & Ratings
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'items': items})

@login_required
def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        messages.info(request, f"{product.name} removed from wishlist.")
    else:
        messages.success(request, f"{product.name} added to wishlist!")
    return redirect('product_detail', pk=pk)

@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} added to wishlist!")
    return redirect('product_detail', pk=pk)

@login_required
def rate_user(request, username):
    rated_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment')
        Rating.objects.create(
            rater=request.user,
            rated_user=rated_user,
            score=score,
            comment=comment
        )
        messages.success(request, f"You rated @{username}!")
    return redirect('profile_view', username=username)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'products/change_password.html', {'form': form})