from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Category, Product


@login_required(login_url="/accounts/login/")
def categories_list_view(request):
    context = {
        "active_icon": "products_categories",
        "categories": Category.objects.all()
    }
    return render(request, "products/categories.html", context=context)


@login_required(login_url="/accounts/login/")
def categories_add_view(request):
    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices
    }

    if request.method == 'POST':
        # Save the POST arguments
        data = request.POST

        attributes = {
            "name": data['name'],
            "status": data['state'],
            "description": data['description']
        }

        # Check if a category with the same attributes exists
        if Category.objects.filter(**attributes).exists():
            messages.error(request, 'Bunday kategoriya allaqachon mavjud!',
                           extra_tags="warning")
            return redirect('products:categories_add')

        try:
            # Create the category
            new_category = Category.objects.create(**attributes)

            # If it doesn't exist, save it
            new_category.save()

            messages.success(request, 'Kategoriya: ' +
                             attributes["name"] + ' muvaffaqiyatli yaratildi!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.success(
                request, 'Yaratish jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
            return redirect('products:categories_add')

    return render(request, "products/categories_add.html", context=context)


@login_required(login_url="/accounts/login/")
def categories_update_view(request, category_id):
    """
    Args:
        request:
        category_id : The category's ID that will be updated
    """

    # Get the category
    try:
        # Get the category to update
        category = Category.objects.get(id=category_id)
    except Exception as e:
        messages.success(
            request, 'Kategoriyani olishda xatolik yuz berdi!', extra_tags="danger")
        print(e)
        return redirect('products:categories_list')

    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices,
        "category": category
    }

    if request.method == 'POST':
        try:
            # Save the POST arguments
            data = request.POST

            attributes = {
                "name": data['name'],
                "status": data['state'],
                "description": data['description']
            }

            # Check if a category with the same attributes exists
            if Category.objects.filter(**attributes).exists():
                messages.error(request, 'Bunday kategoriya allaqachon mavjud!',
                               extra_tags="warning")
                return redirect('products:categories_add')

            # Get the category to update
            category = Category.objects.filter(
                id=category_id).update(**attributes)

            category = Category.objects.get(id=category_id)

            messages.success(request, 'Kategoriya: ' + category.name +
                             ' muvaffaqiyatli yangilandi!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.success(
                request, 'O\'chirish jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
            return redirect('products:categories_list')

    return render(request, "products/categories_update.html", context=context)


@login_required(login_url="/accounts/login/")
def categories_delete_view(request, category_id):
    """
    Args:
        request:
        category_id : The category's ID that will be deleted
    """
    try:
        # Get the category to delete
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, 'Kategoriya: ' + category.name +
                         ' o\'chirildi!', extra_tags="success")
        return redirect('products:categories_list')
    except Exception as e:
        messages.success(
            request, 'O\'chirish jarayonida xatolik yuz berdi!', extra_tags="danger")
        print(e)
        return redirect('products:categories_list')


@login_required(login_url="/accounts/login/")
def products_list_view(request):
    context = {
        "active_icon": "products",
        "products": Product.objects.all()
    }
    return render(request, "products/products.html", context=context)


@login_required(login_url="/accounts/login/")
def products_add_view(request):
    context = {
        "active_icon": "products_categories",
        "product_status": Product.status.field.choices,
        "categories": Category.objects.all().filter(status="ACTIVE")
    }

    if request.method == 'POST':
        # Save the POST arguments
        data = request.POST
        
        # Handle image upload
        image_file = request.FILES.get('image', None)

        attributes = {
            "name": data['name'],
            "status": data['state'],
            "description": data['description'],
            "category": Category.objects.get(id=data['category']),
            "price": data['price'],
            "quantity": data['quantity']
        }
        
        if image_file:
            attributes["image"] = image_file
            
        # Barcode qo'shish (ixtiyoriy)
        if data.get('barcode'):
            if Product.objects.filter(barcode=data['barcode']).exists():
                messages.error(request, 'Bunday barcode allaqachon mavjud!',
                               extra_tags="warning")
                return redirect('products:products_add')
            attributes["barcode"] = data['barcode']

        # Check if a product with the same attributes exists
        if Product.objects.filter(**attributes).exists():
            messages.error(request, 'Bunday mahsulot allaqachon mavjud!',
                           extra_tags="warning")
            return redirect('products:products_add')

        try:
            # Create the product
            new_product = Product.objects.create(**attributes)

            # If it doesn't exist, save it
            new_product.save()

            messages.success(request, 'Mahsulot: ' +
                             attributes["name"] + ' muvaffaqiyatli yaratildi!', extra_tags="success")
            return redirect('products:products_list')
        except Exception as e:
            messages.success(
                request, 'Yaratish jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
            return redirect('products:products_add')

    return render(request, "products/products_add.html", context=context)


@login_required(login_url="/accounts/login/")
def products_update_view(request, product_id):
    """
    Args:
        request:
        product_id : The product's ID that will be updated
    """

    # Get the product
    try:
        # Get the product to update
        product = Product.objects.get(id=product_id)
    except Exception as e:
        messages.success(
            request, 'Mahsulotni olishda xatolik yuz berdi!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')

    context = {
        "active_icon": "products",
        "product_status": Product.status.field.choices,
        "product": product,
        "categories": Category.objects.all()
    }

    if request.method == 'POST':
        try:
            # Save the POST arguments
            data = request.POST
            
            # Handle image upload
            image_file = request.FILES.get('image', None)

            attributes = {
                "name": data['name'],
                "status": data['state'],
                "description": data['description'],
                "category": Category.objects.get(id=data['category']),
                "price": data['price'],
                "quantity": data['quantity']
            }
            
            if image_file:
                attributes["image"] = image_file
                
            # Barcode yangilash (ixtiyoriy)
            if data.get('barcode'):
                # Boshqa mahsulotda shu barcode borligini tekshirish
                if Product.objects.filter(barcode=data['barcode']).exclude(id=product_id).exists():
                    messages.error(request, 'Bunday barcode boshqa mahsulotda mavjud!',
                                   extra_tags="warning")
                    return redirect('products:products_update', product_id=product_id)
                attributes["barcode"] = data['barcode']

            # Check if a product with the same attributes exists
            if Product.objects.filter(**attributes).exists():
                messages.error(request, 'Bunday mahsulot allaqachon mavjud!',
                               extra_tags="warning")
                return redirect('products:products_add')

            # Get the product to update
            product = Product.objects.filter(
                id=product_id).update(**attributes)

            product = Product.objects.get(id=product_id)

            messages.success(request, 'Mahsulot: ' + product.name +
                             ' muvaffaqiyatli yangilandi!', extra_tags="success")
            return redirect('products:products_list')
        except Exception as e:
            messages.success(
                request, 'Yangilash jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
            return redirect('products:products_list')

    return render(request, "products/products_update.html", context=context)


@login_required(login_url="/accounts/login/")
def products_delete_view(request, product_id):
    """
    Args:
        request:
        product_id : The product's ID that will be deleted
    """
    try:
        # Get the product to delete
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, 'Mahsulot: ' + product.name +
                         ' o\'chirildi!', extra_tags="success")
        return redirect('products:products_list')
    except Exception as e:
        messages.success(
            request, 'O\'chirish jarayonida xatolik yuz berdi!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def get_products_ajax_view(request):
    if request.method == 'POST':
        if is_ajax(request=request):
            data = []

            # Faqat faol va omborda mavjud mahsulotlarni qidirish
            products = Product.objects.filter(
                name__icontains=request.POST['term'],
                status='ACTIVE',
                quantity__gt=0  # Omborda mavjud bo'lgan mahsulotlar
            )
            for product in products[0:10]:
                item = product.to_json()
                data.append(item)

            return JsonResponse(data, safe=False)
