from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Customer


@login_required(login_url="/accounts/login/")
def customers_list_view(request):
    context = {
        "active_icon": "customers",
        "customers": Customer.objects.all()
    }
    return render(request, "customers/customers.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_add_view(request):
    context = {
        "active_icon": "customers",
    }

    if request.method == 'POST':
        # Save the POST arguments
        data = request.POST

        attributes = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "address": data['address'],
            "email": data['email'],
            "phone": data['phone'],
        }

        # Check if a customer with the same attributes exists
        if Customer.objects.filter(**attributes).exists():
            messages.error(request, 'Bunday mijoz allaqachon mavjud!',
                           extra_tags="warning")
            return redirect('customers:customers_add')

        try:
            # Create the customer
            new_customer = Customer.objects.create(**attributes)

            # If it doesn't exist save it
            new_customer.save()
            
            # AJAX so'rov uchun JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'customer_id': new_customer.id,
                    'customer_name': new_customer.get_full_name(),
                    'message': 'Mijoz muvaffaqiyatli yaratildi!'
                })

            messages.success(request, 'Mijoz: ' + attributes["first_name"] + " " +
                             attributes["last_name"] + ' muvaffaqiyatli yaratildi!', extra_tags="success")
            return redirect('customers:customers_list')
        except Exception as e:
            # AJAX so'rov uchun JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Xatolik: {str(e)}'
                }, status=400)
            
            messages.success(
                request, 'Yaratish jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
            return redirect('customers:customers_add')

    return render(request, "customers/customers_add.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_update_view(request, customer_id):
    """
    Args:
        request:
        customer_id : The customer's ID that will be updated
    """

    # Get the customer
    try:
        # Get the customer to update
        customer = Customer.objects.get(id=customer_id)
    except Exception as e:
        messages.success(
            request, 'Mijozni olishda xatolik yuz berdi!', extra_tags="danger")
        print(e)
        return redirect('customers:customers_list')

    context = {
        "active_icon": "customers",
        "customer": customer,
    }

    if request.method == 'POST':
        try:
            # Save the POST arguments
            data = request.POST

            attributes = {
                "first_name": data['first_name'],
                "last_name": data['last_name'],
                "address": data['address'],
                "email": data['email'],
                "phone": data['phone'],
            }

            # Check if a customer with the same attributes exists
            if Customer.objects.filter(**attributes).exists():
                messages.error(request, 'Bunday mijoz allaqachon mavjud!',
                               extra_tags="warning")
                return redirect('customers:customers_add')

            customer = Customer.objects.get(id=customer_id)

            messages.success(request, 'Mijoz: ' + customer.get_full_name() +
                             ' muvaffaqiyatli yangilandi!', extra_tags="success")
            return redirect('customers:customers_list')
        except Exception as e:
            messages.success(
                request, 'Yangilash jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
            return redirect('customers:customers_list')

    return render(request, "customers/customers_update.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_delete_view(request, customer_id):
    """
    Args:
        request:
        customer_id : The customer's ID that will be deleted
    """
    try:
        # Get the customer to delete
        customer = Customer.objects.get(id=customer_id)
        customer.delete()
        messages.success(request, 'Mijoz: ' + customer.get_full_name() +
                         ' o\'chirildi!', extra_tags="success")
        return redirect('customers:customers_list')
    except Exception as e:
        messages.success(
            request, 'O\'chirish jarayonida xatolik yuz berdi!', extra_tags="danger")
        print(e)
        return redirect('customers:customers_list')
