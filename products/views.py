from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q

from .models import Product
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

    return render(request, 'products/product_detail.html', {
        'product': product,
        'description_lines': description_lines,
        'barter_lines': barter_lines,
    })


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()

            return redirect('home')

        else:
            print(form.errors)   # ← this prints errors in terminal

    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


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