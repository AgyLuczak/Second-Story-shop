from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category  # Correct import for your models

def all_products(request):
    products = Product.objects.all()
    current_categories = Category.objects.all()
    query = None
    categories = None
    sortkey = request.GET.get('sort', None)
    direction = request.GET.get('direction', 'asc')

    # Initialize flags
    is_sorting_default = True
    is_price_asc = is_price_desc = is_name_asc = is_name_desc = is_category_asc = is_category_desc = False

    if sortkey and direction:
        if sortkey == 'name':
            sortkey = 'lower_name'
            products = products.annotate(lower_name=Lower('name'))
        elif sortkey == 'category':
            sortkey = 'category__name'

        # Apply sorting
        if direction == 'desc':
            sortkey = f'-{sortkey}'
        products = products.order_by(sortkey)

        # Update flags based on current_sorting
        current_sorting = f'{sortkey}_{direction}'
        is_sorting_default = False
        is_price_asc = current_sorting == 'price_asc'
        is_price_desc = current_sorting == 'price_desc'
        is_name_asc = current_sorting == 'name_asc'
        is_name_desc = current_sorting == 'name_desc'
        is_category_asc = current_sorting == 'category__name_asc'
        is_category_desc = current_sorting == 'category__name_desc'

    if 'category' in request.GET:
        categories = request.GET['category'].split(',')
        products = products.filter(category__name__in=categories)
        current_categories = Category.objects.filter(name__in=categories)

    if 'q' in request.GET:
        query = request.GET['q']
        if not query:
            messages.error(request, "You didn't enter any search criteria!")
            return redirect(reverse('products'))
        
        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

    context = {
        'products': products,
        'search_term': query,
        'current_categories': current_categories,
        'is_sorting_default': is_sorting_default,
        'is_price_asc': is_price_asc,
        'is_price_desc': is_price_desc,
        'is_name_asc': is_name_asc,
        'is_name_desc': is_name_desc,
        'is_category_asc': is_category_asc,
        'is_category_desc': is_category_desc,
        'border_class': 'info' if is_sorting_default else 'black',
    }

    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """
    A view to show individual product details
    """
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
