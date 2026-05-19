from django.shortcuts import render, redirect
from .models import Product, Category
from django.contrib import messages

def inventory_list(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        # If product_id exists, it's an UPDATE operation
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                product.price = request.POST.get('price')
                product.available = request.POST.get('available')
                product.save()
                messages.success(request, f"Product '{product.product_name}' updated successfully.")
            except Product.DoesNotExist:
                messages.error(request, "Product not found. Update failed.")
        # If no product_id, it's a CREATE operation
        else:
            try:
                category_id = request.POST.get('category')
                category_instance = Category.objects.get(id=category_id)
                
                product_name = request.POST.get('product_name')
                new_product = Product.objects.create(
                    product_name=product_name,
                    category=category_instance,
                    price=request.POST.get('price'),
                    available=request.POST.get('available'),
                    image=request.FILES.get('image')
                )
                messages.success(request, f"Product '{new_product.product_name}' added successfully.")
            except Category.DoesNotExist:
                messages.error(request, "Invalid category selected. Product not created.")
            except ValueError:
                messages.error(request, "Invalid data provided. Product not created.")
        return redirect('inventory')

    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()
    db_is_empty = not products.exists()

    context = {
        'products': products,
        'categories': categories,
        'db_is_empty': db_is_empty,
    }
    return render(request, 'admin/inventory.html', context)