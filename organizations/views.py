from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Organization, Contract, DeliveryNote, DeliveryNoteDetail, Payment, ProductBarcode, EmployeePermission
from products.models import Product
import json
from datetime import date, datetime, timedelta
from django.db.models import Sum, Count, Q


# ==================== TASHKILOTLAR ====================

@login_required(login_url="/accounts/login/")
def organizations_list_view(request):
    """Tashkilotlar ro'yxati"""
    context = {
        "active_icon": "organizations",
        "organizations": Organization.objects.all()
    }
    return render(request, "organizations/organizations_list.html", context=context)


@login_required(login_url="/accounts/login/")
def organizations_add_view(request):
    """Yangi tashkilot qo'shish"""
    context = {
        "active_icon": "organizations",
        "organization_types": Organization.ORGANIZATION_TYPES
    }
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # INN tekshirish
            if Organization.objects.filter(inn=data['inn']).exists():
                messages.error(request, 'Bunday INN raqamli tashkilot allaqachon mavjud!',
                             extra_tags="warning")
                return redirect('organizations:organizations_add')
            
            # Tashkilot yaratish
            organization = Organization.objects.create(
                name=data['name'],
                short_name=data['short_name'],
                organization_type=data['organization_type'],
                inn=data['inn'],
                oked=data.get('oked', ''),
                mfo=data.get('mfo', ''),
                account_number=data.get('account_number', ''),
                legal_address=data['legal_address'],
                actual_address=data.get('actual_address', ''),
                phone=data['phone'],
                email=data.get('email', ''),
                director_name=data['director_name'],
                director_phone=data.get('director_phone', ''),
                responsible_person=data['responsible_person'],
                responsible_position=data.get('responsible_position', ''),
                responsible_phone=data.get('responsible_phone', ''),
                notes=data.get('notes', ''),
            )
            
            messages.success(request, f"Tashkilot '{organization.short_name}' muvaffaqiyatli yaratildi!",
                           extra_tags="success")
            return redirect('organizations:organizations_list')
            
        except Exception as e:
            messages.error(request, 'Yaratish jarayonida xatolik yuz berdi!',
                         extra_tags="danger")
            print(e)
            return redirect('organizations:organizations_add')
    
    return render(request, "organizations/organizations_add.html", context=context)


@login_required(login_url="/accounts/login/")
def organizations_update_view(request, organization_id):
    """Tashkilotni tahrirlash"""
    organization = get_object_or_404(Organization, id=organization_id)
    
    context = {
        "active_icon": "organizations",
        "organization": organization,
        "organization_types": Organization.ORGANIZATION_TYPES
    }
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # INN tekshirish (o'zidan boshqa)
            if Organization.objects.filter(inn=data['inn']).exclude(id=organization_id).exists():
                messages.error(request, 'Bunday INN raqamli tashkilot allaqachon mavjud!',
                             extra_tags="warning")
                return redirect('organizations:organizations_update', organization_id=organization_id)
            
            # Yangilash
            organization.name = data['name']
            organization.short_name = data['short_name']
            organization.organization_type = data['organization_type']
            organization.inn = data['inn']
            organization.oked = data.get('oked', '')
            organization.mfo = data.get('mfo', '')
            organization.account_number = data.get('account_number', '')
            organization.legal_address = data['legal_address']
            organization.actual_address = data.get('actual_address', '')
            organization.phone = data['phone']
            organization.email = data.get('email', '')
            organization.director_name = data['director_name']
            organization.director_phone = data.get('director_phone', '')
            organization.responsible_person = data['responsible_person']
            organization.responsible_position = data.get('responsible_position', '')
            organization.responsible_phone = data.get('responsible_phone', '')
            organization.notes = data.get('notes', '')
            organization.save()
            
            messages.success(request, f"Tashkilot '{organization.short_name}' muvaffaqiyatli yangilandi!",
                           extra_tags="success")
            return redirect('organizations:organizations_list')
            
        except Exception as e:
            messages.error(request, 'Yangilash jarayonida xatolik yuz berdi!',
                         extra_tags="danger")
            print(e)
    
    return render(request, "organizations/organizations_update.html", context=context)


@login_required(login_url="/accounts/login/")
def organizations_delete_view(request, organization_id):
    """Tashkilotni o'chirish"""
    try:
        organization = get_object_or_404(Organization, id=organization_id)
        organization.delete()
        messages.success(request, f"Tashkilot '{organization.short_name}' o'chirildi!",
                       extra_tags="success")
    except Exception as e:
        messages.error(request, 'O\'chirish jarayonida xatolik yuz berdi!',
                     extra_tags="danger")
        print(e)
    
    return redirect('organizations:organizations_list')


@login_required(login_url="/accounts/login/")
def organizations_detail_view(request, organization_id):
    """Tashkilot tafsilotlari"""
    organization = get_object_or_404(Organization, id=organization_id)
    
    context = {
        "active_icon": "organizations",
        "organization": organization,
        "contracts": organization.contracts.all()
    }
    
    return render(request, "organizations/organizations_detail.html", context=context)


# ==================== SHARTNOMALAR ====================

@login_required(login_url="/accounts/login/")
def contracts_list_view(request):
    """Shartnomalar ro'yxati"""
    context = {
        "active_icon": "contracts",
        "contracts": Contract.objects.all()
    }
    return render(request, "organizations/contracts_list.html", context=context)


@login_required(login_url="/accounts/login/")
def contracts_add_view(request):
    """Yangi shartnoma qo'shish"""
    context = {
        "active_icon": "contracts",
        "organizations": Organization.objects.filter(is_active=True),
        "contract_statuses": Contract.CONTRACT_STATUS
    }
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Shartnoma raqami tekshirish
            if Contract.objects.filter(number=data['number']).exists():
                messages.error(request, 'Bunday raqamli shartnoma allaqachon mavjud!',
                             extra_tags="warning")
                return redirect('organizations:contracts_add')
            
            # Shartnoma yaratish
            contract = Contract.objects.create(
                number=data['number'],
                organization_id=data['organization'],
                contract_date=data['contract_date'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                total_amount=data.get('total_amount') or None,
                payment_terms=data.get('payment_terms', ''),
                delivery_terms=data.get('delivery_terms', ''),
                status=data.get('status', 'ACTIVE'),
                notes=data.get('notes', ''),
                created_by=request.user
            )
            
            messages.success(request, f"Shartnoma №{contract.number} muvaffaqiyatli yaratildi!",
                           extra_tags="success")
            return redirect('organizations:contracts_list')
            
        except Exception as e:
            messages.error(request, 'Yaratish jarayonida xatolik yuz berdi!',
                         extra_tags="danger")
            print(e)
            return redirect('organizations:contracts_add')
    
    return render(request, "organizations/contracts_add.html", context=context)


@login_required(login_url="/accounts/login/")
def contracts_update_view(request, contract_id):
    """Shartnomani tahrirlash"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    context = {
        "active_icon": "contracts",
        "contract": contract,
        "organizations": Organization.objects.filter(is_active=True),
        "contract_statuses": Contract.CONTRACT_STATUS
    }
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Shartnoma raqami tekshirish (o'zidan boshqa)
            if Contract.objects.filter(number=data['number']).exclude(id=contract_id).exists():
                messages.error(request, 'Bunday raqamli shartnoma allaqachon mavjud!',
                             extra_tags="warning")
                return redirect('organizations:contracts_update', contract_id=contract_id)
            
            # Yangilash
            contract.number = data['number']
            contract.organization_id = data['organization']
            contract.contract_date = data['contract_date']
            contract.start_date = data['start_date']
            contract.end_date = data['end_date']
            contract.total_amount = data.get('total_amount') or None
            contract.payment_terms = data.get('payment_terms', '')
            contract.delivery_terms = data.get('delivery_terms', '')
            contract.status = data.get('status', 'ACTIVE')
            contract.notes = data.get('notes', '')
            contract.save()
            
            messages.success(request, f"Shartnoma №{contract.number} muvaffaqiyatli yangilandi!",
                           extra_tags="success")
            return redirect('organizations:contracts_list')
            
        except Exception as e:
            messages.error(request, 'Yangilash jarayonida xatolik yuz berdi!',
                         extra_tags="danger")
            print(e)
    
    return render(request, "organizations/contracts_update.html", context=context)


@login_required(login_url="/accounts/login/")
def contracts_delete_view(request, contract_id):
    """Shartnomani o'chirish"""
    try:
        contract = get_object_or_404(Contract, id=contract_id)
        contract.delete()
        messages.success(request, f"Shartnoma №{contract.number} o'chirildi!",
                       extra_tags="success")
    except Exception as e:
        messages.error(request, 'O\'chirish jarayonida xatolik yuz berdi!',
                     extra_tags="danger")
        print(e)
    
    return redirect('organizations:contracts_list')


@login_required(login_url="/accounts/login/")
def contracts_detail_view(request, contract_id):
    """Shartnoma tafsilotlari"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    context = {
        "active_icon": "contracts",
        "contract": contract
    }
    
    return render(request, "organizations/contracts_detail.html", context=context)


# ==================== YUK XATLARI ====================

@login_required(login_url="/accounts/login/")
def delivery_notes_list_view(request):
    """Yuk xatlari ro'yxati"""
    context = {
        "active_icon": "delivery_notes",
        "delivery_notes": DeliveryNote.objects.all()
    }
    return render(request, "organizations/delivery_notes_list.html", context=context)


@login_required(login_url="/accounts/login/")
def delivery_notes_add_view(request):
    """Yangi yuk xati yaratish"""
    context = {
        "active_icon": "delivery_notes",
        "organizations": Organization.objects.filter(is_active=True),
        "products": Product.objects.filter(status='ACTIVE')
    }
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Yuk xati raqamini generatsiya qilish
            today = date.today()
            year = today.year
            # Shu yildagi yuk xatlar sonini hisoblash
            count = DeliveryNote.objects.filter(date__year=year).count() + 1
            number = f"YX-{year}-{count:05d}"
            
            # Yuk xati yaratish
            delivery_note = DeliveryNote.objects.create(
                number=number,
                date=data['date'],
                organization_id=data['organization'],
                contract_id=data.get('contract') or None,
                notes=data.get('notes', ''),
                created_by=request.user
            )
            
            # Mahsulotlarni qo'shish (JSON formatda keladi)
            products_data = json.loads(data.get('products_json', '[]'))
            
            for product_data in products_data:
                product = Product.objects.get(id=product_data['product_id'])
                
                DeliveryNoteDetail.objects.create(
                    delivery_note=delivery_note,
                    product=product,
                    product_name=product.name,
                    serial_number=product_data.get('serial_number', ''),
                    quantity=int(product_data['quantity']),
                    price=float(product_data['price'])
                )
                
                # Ombordan mahsulot ayirish
                product.quantity -= int(product_data['quantity'])
                product.save()
            
            # Umumiy summani hisoblash
            delivery_note.update_totals()
            
            messages.success(request, f"Yuk xati №{delivery_note.number} muvaffaqiyatli yaratildi!",
                           extra_tags="success")
            return redirect('organizations:delivery_notes_detail', delivery_note_id=delivery_note.id)
            
        except Exception as e:
            messages.error(request, 'Yaratish jarayonida xatolik yuz berdi!',
                         extra_tags="danger")
            print(e)
            return redirect('organizations:delivery_notes_add')
    
    return render(request, "organizations/delivery_notes_add.html", context=context)


@login_required(login_url="/accounts/login/")
def delivery_notes_detail_view(request, delivery_note_id):
    """Yuk xati tafsilotlari"""
    delivery_note = get_object_or_404(DeliveryNote, id=delivery_note_id)
    
    context = {
        "active_icon": "delivery_notes",
        "delivery_note": delivery_note,
        "details": delivery_note.details.all(),
        "payments": delivery_note.payments.all()
    }
    
    return render(request, "organizations/delivery_notes_detail.html", context=context)


@login_required(login_url="/accounts/login/")
def delivery_notes_delete_view(request, delivery_note_id):
    """Yuk xatini o'chirish"""
    try:
        delivery_note = get_object_or_404(DeliveryNote, id=delivery_note_id)
        
        # Mahsulotlarni omborga qaytarish
        for detail in delivery_note.details.all():
            detail.product.quantity += detail.quantity
            detail.product.save()
        
        delivery_note.delete()
        messages.success(request, f"Yuk xati №{delivery_note.number} o'chirildi!",
                       extra_tags="success")
    except Exception as e:
        messages.error(request, 'O\'chirish jarayonida xatolik yuz berdi!',
                     extra_tags="danger")
        print(e)
    
    return redirect('organizations:delivery_notes_list')


@login_required(login_url="/accounts/login/")
def delivery_note_pdf_view(request, delivery_note_id):
    """Yuk xati PDF chiqarish"""
    delivery_note = get_object_or_404(DeliveryNote, id=delivery_note_id)
    details = delivery_note.details.all()
    
    context = {
        'delivery_note': delivery_note,
        'details': details,
        'organization': delivery_note.organization
    }
    
    # HTML ni render qilish
    html_string = render_to_string('organizations/delivery_note_pdf.html', context)
    
    # PDF yaratish (xhtml2pdf yordamida)
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="yuk_xati_{delivery_note.number}.pdf"'
            return response
        else:
            messages.error(request, 'PDF yaratishda xatolik yuz berdi!', extra_tags="danger")
            return redirect('organizations:delivery_notes_detail', delivery_note_id=delivery_note_id)
    except Exception as e:
        print(f"PDF Error: {e}")
        messages.error(request, 'PDF yaratishda xatolik yuz berdi!', extra_tags="danger")
        return redirect('organizations:delivery_notes_detail', delivery_note_id=delivery_note_id)


# ==================== BARCODE ====================

@login_required(login_url="/accounts/login/")
def barcode_search_view(request):
    """Barcode qidirish (AJAX) - takomillashtirilgan"""
    if request.method == 'GET':
        barcode = request.GET.get('barcode', '').strip()
        
        if not barcode:
            return HttpResponse(json.dumps({'success': False, 'message': 'Barcode kiritilmagan'}), 
                              content_type='application/json')
        
        # Debug: qanday barcode qidirilayotganini ko'rish
        print(f"🔍 Barcode qidirilmoqda: '{barcode}' (uzunlik: {len(barcode)})")
        
        try:
            product = None
            barcode_info = {}
            
            # Avval ProductBarcode dan qidiramiz
            try:
                product_barcode = ProductBarcode.objects.get(barcode=barcode)
                product = product_barcode.product
                barcode_info = {
                    'barcode': product_barcode.barcode,
                    'internal_code': product_barcode.internal_code or '',
                    'source': 'ProductBarcode'
                }
                print(f"✓ Topildi ProductBarcode'da: {product.name}")
            except ProductBarcode.DoesNotExist:
                print(f"✗ ProductBarcode'da topilmadi")
                pass
            
            # Agar ProductBarcode da topilmasa, Product modelidan qidiramiz
            if not product:
                try:
                    product = Product.objects.get(barcode=barcode)
                    barcode_info = {
                        'barcode': product.barcode,
                        'internal_code': '',
                        'source': 'Product'
                    }
                    print(f"✓ Topildi Product'da: {product.name}")
                except Product.DoesNotExist:
                    print(f"✗ Product'da ham topilmadi")
                    
                    # Debug: mavjud barcode'larni ko'rsatish
                    all_barcodes = Product.objects.filter(barcode__isnull=False).values_list('barcode', flat=True)[:10]
                    print(f"📊 Mavjud barcode'lar (10 ta): {list(all_barcodes)}")
                    pass
            
            if product:
                data = {
                    'success': True,
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'quantity': product.quantity,
                        'category': product.category.name,
                        'image': product.image.url if product.image else None,
                        **barcode_info
                    }
                }
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'success': False, 'message': 'Barcode topilmadi'}), 
                                  content_type='application/json')
            
        except Exception as e:
            print(f"❌ Barcode search error: {e}")
            import traceback
            traceback.print_exc()
            return HttpResponse(json.dumps({'success': False, 'message': f'Xatolik: {str(e)}'}), 
                              content_type='application/json')
    
    return HttpResponse(json.dumps({'success': False, 'message': 'Noto\'g\'ri so\'rov'}), 
                       content_type='application/json')


@login_required(login_url="/accounts/login/")
def barcode_generate_view(request, product_id):
    """Mahsulot uchun barcode yaratish"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Barcode mavjudligini tekshirish
            if ProductBarcode.objects.filter(barcode=data['barcode']).exists():
                messages.error(request, 'Bunday barcode allaqachon mavjud!', extra_tags="warning")
                return redirect('organizations:barcode_generate', product_id=product_id)
            
            # Barcode yaratish
            ProductBarcode.objects.create(
                product=product,
                barcode=data['barcode'],
                internal_code=data.get('internal_code', ''),
                notes=data.get('notes', ''),
                created_by=request.user
            )
            
            messages.success(request, f"Barcode muvaffaqiyatli yaratildi!", extra_tags="success")
            return redirect('products:products_list')
            
        except Exception as e:
            messages.error(request, 'Yaratish jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
    
    context = {
        'product': product,
        'existing_barcodes': product.barcodes.all()
    }
    
    return render(request, "organizations/barcode_generate.html", context=context)


# ==================== TO'LOVLAR ====================

@login_required(login_url="/accounts/login/")
def payment_add_view(request, delivery_note_id):
    """Yuk xatiga to'lov qo'shish"""
    delivery_note = get_object_or_404(DeliveryNote, id=delivery_note_id)
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # To'lov yaratish
            Payment.objects.create(
                delivery_note=delivery_note,
                payment_date=data['payment_date'],
                amount=float(data['amount']),
                payment_document=data.get('payment_document', ''),
                notes=data.get('notes', ''),
                created_by=request.user
            )
            
            messages.success(request, "To'lov muvaffaqiyatli qo'shildi!", extra_tags="success")
            return redirect('organizations:delivery_notes_detail', delivery_note_id=delivery_note_id)
            
        except Exception as e:
            messages.error(request, 'Yaratish jarayonida xatolik yuz berdi!', extra_tags="danger")
            print(e)
            return redirect('organizations:delivery_notes_detail', delivery_note_id=delivery_note_id)
    
    context = {
        'delivery_note': delivery_note,
        'remaining_amount': delivery_note.get_remaining_amount()
    }
    
    return render(request, "organizations/payment_add.html", context=context)


@login_required(login_url="/accounts/login/")
def payment_delete_view(request, payment_id):
    """To'lovni o'chirish"""
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        delivery_note_id = payment.delivery_note.id
        payment.delete()
        messages.success(request, "To'lov o'chirildi!", extra_tags="success")
    except Exception as e:
        messages.error(request, 'O\'chirish jarayonida xatolik yuz berdi!', extra_tags="danger")
        print(e)
    
    return redirect('organizations:delivery_notes_detail', delivery_note_id=delivery_note_id)


# ==================== HISOBOTLAR ====================

@login_required(login_url="/accounts/login/")
def reports_dashboard_view(request):
    """Hisobotlar bosh sahifasi"""
    
    # Umumiy statistika
    total_organizations = Organization.objects.filter(is_active=True).count()
    total_contracts = Contract.objects.filter(status='ACTIVE').count()
    total_delivery_notes = DeliveryNote.objects.count()
    total_products = Product.objects.filter(status='ACTIVE').count()
    
    # Moliyaviy statistika
    total_sales = DeliveryNote.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = DeliveryNote.objects.aggregate(total=Sum('paid_amount'))['total'] or 0
    total_debt = total_sales - total_paid
    
    # To'lov holati bo'yicha
    unpaid_count = DeliveryNote.objects.filter(payment_status='UNPAID').count()
    partial_count = DeliveryNote.objects.filter(payment_status='PARTIAL').count()
    paid_count = DeliveryNote.objects.filter(payment_status='PAID').count()
    
    # Oxirgi 30 kun
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_delivery_notes = DeliveryNote.objects.filter(date__gte=thirty_days_ago).count()
    recent_sales = DeliveryNote.objects.filter(date__gte=thirty_days_ago).aggregate(
        total=Sum('total_amount'))['total'] or 0
    
    # Eng ko'p buyurtma bergan tashkilotlar
    top_organizations = Organization.objects.annotate(
        dn_count=Count('delivery_notes')
    ).order_by('-dn_count')[:5]
    
    # Ombor holati
    low_stock_products = Product.objects.filter(quantity__lte=10, status='ACTIVE').order_by('quantity')[:10]
    
    context = {
        'active_icon': 'reports',
        'total_organizations': total_organizations,
        'total_contracts': total_contracts,
        'total_delivery_notes': total_delivery_notes,
        'total_products': total_products,
        'total_sales': total_sales,
        'total_paid': total_paid,
        'total_debt': total_debt,
        'unpaid_count': unpaid_count,
        'partial_count': partial_count,
        'paid_count': paid_count,
        'recent_delivery_notes': recent_delivery_notes,
        'recent_sales': recent_sales,
        'top_organizations': top_organizations,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, "organizations/reports_dashboard.html", context=context)


@login_required(login_url="/accounts/login/")
def reports_inventory_view(request):
    """Ombor hisoboti"""
    
    # Ombor statistikasi
    total_products = Product.objects.filter(status='ACTIVE').count()
    total_quantity = Product.objects.filter(status='ACTIVE').aggregate(
        total=Sum('quantity'))['total'] or 0
    
    # Kategoriya bo'yicha
    from products.models import Category
    categories_stats = []
    for category in Category.objects.all():
        products = Product.objects.filter(category=category, status='ACTIVE')
        total_qty = products.aggregate(total=Sum('quantity'))['total'] or 0
        categories_stats.append({
            'category': category,
            'count': products.count(),
            'quantity': total_qty
        })
    
    # Kam qolgan mahsulotlar
    low_stock = Product.objects.filter(quantity__lte=10, status='ACTIVE').order_by('quantity')
    out_of_stock = Product.objects.filter(quantity=0, status='ACTIVE')
    
    context = {
        'active_icon': 'reports',
        'total_products': total_products,
        'total_quantity': total_quantity,
        'categories_stats': categories_stats,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }
    
    return render(request, "organizations/reports_inventory.html", context=context)


@login_required(login_url="/accounts/login/")
def reports_sales_view(request):
    """Savdo hisoboti"""
    
    # Filtrlar
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    organization_id = request.GET.get('organization')
    
    delivery_notes = DeliveryNote.objects.all()
    
    if start_date:
        delivery_notes = delivery_notes.filter(date__gte=start_date)
    if end_date:
        delivery_notes = delivery_notes.filter(date__lte=end_date)
    if organization_id:
        delivery_notes = delivery_notes.filter(organization_id=organization_id)
    
    # Statistika
    total_count = delivery_notes.count()
    total_amount = delivery_notes.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = delivery_notes.aggregate(total=Sum('paid_amount'))['total'] or 0
    total_debt = total_amount - total_paid
    
    context = {
        'active_icon': 'reports',
        'delivery_notes': delivery_notes.order_by('-date'),
        'organizations': Organization.objects.filter(is_active=True),
        'total_count': total_count,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_debt': total_debt,
        'start_date': start_date,
        'end_date': end_date,
        'selected_org': organization_id,
    }
    
    return render(request, "organizations/reports_sales.html", context=context)


# ==================== XODIMLAR RUXSATLARI ====================

@login_required(login_url="/accounts/login/")
def employees_list_view(request):
    """Xodimlar ro'yxati"""
    from django.contrib.auth.models import User
    
    employees = User.objects.all().order_by('username')
    
    # Har bir xodim uchun ruxsatlarni olish
    employees_data = []
    for emp in employees:
        try:
            permissions = EmployeePermission.objects.get(employee=emp)
        except EmployeePermission.DoesNotExist:
            permissions = None
        
        employees_data.append({
            'employee': emp,
            'permissions': permissions,
            'has_permissions': permissions is not None
        })
    
    context = {
        'active_icon': 'employees',
        'employees_data': employees_data,
    }
    
    return render(request, "organizations/employees_list.html", context=context)


@login_required(login_url="/accounts/login/")
def employee_permissions_view(request, employee_id):
    """Xodim ruxsatlarini boshqarish"""
    from django.contrib.auth.models import User
    
    employee = get_object_or_404(User, id=employee_id)
    
    # Ruxsatlarni olish yoki yaratish
    permissions, created = EmployeePermission.objects.get_or_create(employee=employee)
    
    if request.method == 'POST':
        try:
            # Barcha ruxsatlarni yangilash
            permissions.can_view_organizations = 'can_view_organizations' in request.POST
            permissions.can_add_organizations = 'can_add_organizations' in request.POST
            permissions.can_edit_organizations = 'can_edit_organizations' in request.POST
            permissions.can_delete_organizations = 'can_delete_organizations' in request.POST
            
            permissions.can_view_contracts = 'can_view_contracts' in request.POST
            permissions.can_add_contracts = 'can_add_contracts' in request.POST
            permissions.can_edit_contracts = 'can_edit_contracts' in request.POST
            permissions.can_delete_contracts = 'can_delete_contracts' in request.POST
            
            permissions.can_view_delivery_notes = 'can_view_delivery_notes' in request.POST
            permissions.can_add_delivery_notes = 'can_add_delivery_notes' in request.POST
            permissions.can_delete_delivery_notes = 'can_delete_delivery_notes' in request.POST
            permissions.can_print_delivery_notes = 'can_print_delivery_notes' in request.POST
            
            permissions.can_view_products = 'can_view_products' in request.POST
            permissions.can_add_products = 'can_add_products' in request.POST
            permissions.can_edit_products = 'can_edit_products' in request.POST
            permissions.can_delete_products = 'can_delete_products' in request.POST
            permissions.can_edit_prices = 'can_edit_prices' in request.POST
            
            permissions.can_view_payments = 'can_view_payments' in request.POST
            permissions.can_add_payments = 'can_add_payments' in request.POST
            permissions.can_delete_payments = 'can_delete_payments' in request.POST
            
            permissions.can_view_reports = 'can_view_reports' in request.POST
            permissions.can_export_reports = 'can_export_reports' in request.POST
            
            # POS va Savdo ruxsatlari
            permissions.can_view_pos = 'can_view_pos' in request.POST
            permissions.can_add_sales = 'can_add_sales' in request.POST
            permissions.can_view_sales = 'can_view_sales' in request.POST
            permissions.can_edit_sales = 'can_edit_sales' in request.POST
            permissions.can_delete_sales = 'can_delete_sales' in request.POST
            
            # Mijozlar ruxsatlari
            permissions.can_view_customers = 'can_view_customers' in request.POST
            permissions.can_add_customers = 'can_add_customers' in request.POST
            permissions.can_edit_customers = 'can_edit_customers' in request.POST
            permissions.can_delete_customers = 'can_delete_customers' in request.POST
            
            # Qarz daftari ruxsatlari
            permissions.can_view_debt = 'can_view_debt' in request.POST
            permissions.can_add_debt = 'can_add_debt' in request.POST
            permissions.can_edit_debt = 'can_edit_debt' in request.POST
            permissions.can_delete_debt = 'can_delete_debt' in request.POST
            permissions.can_add_debt_payments = 'can_add_debt_payments' in request.POST
            
            # Ombor ruxsatlari (kengaytirilgan)
            permissions.can_view_warehouse = 'can_view_warehouse' in request.POST
            permissions.can_receive_warehouse = 'can_receive_warehouse' in request.POST
            permissions.can_manage_barcodes = 'can_manage_barcodes' in request.POST
            
            permissions.notes = request.POST.get('notes', '')
            
            permissions.save()
            
            messages.success(request, "Ruxsatlar muvaffaqiyatli yangilandi!", extra_tags="success")
            return redirect('organizations:employees_list')
            
        except Exception as e:
            messages.error(request, 'Xatolik yuz berdi!', extra_tags="danger")
            print(e)
    
    context = {
        'active_icon': 'employees',
        'employee': employee,
        'permissions': permissions,
    }
    
    return render(request, "organizations/employee_permissions.html", context=context)


# ==================== OMBOR BOSHQARUVI ====================

@login_required(login_url="/accounts/login/")
def warehouse_inventory_view(request):
    """Ombordagi mahsulotlar"""
    
    # Filtrlar
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'name')  # Default: nom bo'yicha
    
    products = Product.objects.all()
    
    # Kategoriya filtri
    if category_id and category_id.strip():
        try:
            products = products.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    # Holat filtri
    if status and status.strip():
        products = products.filter(status=status)
    
    # Qidirish filtri
    if search and search.strip() and search.lower() != 'none':
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    # Tartiblash
    sort_options = {
        'name': 'name',                          # Nom bo'yicha (A-Z)
        'name_desc': '-name',                    # Nom bo'yicha (Z-A)
        'category': 'category__name',            # Kategoriya bo'yicha
        'category_desc': '-category__name',      # Kategoriya bo'yicha (teskari)
        'quantity': 'quantity',                  # Miqdor bo'yicha (kam -> ko'p)
        'quantity_desc': '-quantity',            # Miqdor bo'yicha (ko'p -> kam)
        'price': 'price',                        # Narx bo'yicha (arzon -> qimmat)
        'price_desc': '-price',                  # Narx bo'yicha (qimmat -> arzon)
        'id': 'id',                              # ID bo'yicha (eski -> yangi)
        'id_desc': '-id',                        # ID bo'yicha (yangi -> eski)
    }
    
    order_by = sort_options.get(sort_by, 'name')
    products = products.order_by(order_by)
    
    # Statistika
    from products.models import Category
    total_products = products.count()
    total_quantity = products.aggregate(total=Sum('quantity'))['total'] or 0
    low_stock_count = products.filter(quantity__lte=10).count()
    out_of_stock_count = products.filter(quantity=0).count()
    
    context = {
        'active_icon': 'warehouse',
        'products': products,
        'categories': Category.objects.all(),
        'total_products': total_products,
        'total_quantity': total_quantity,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'selected_category': category_id,
        'selected_status': status,
        'search_query': search,
        'current_sort': sort_by,
    }
    
    return render(request, "organizations/warehouse_inventory.html", context=context)


@login_required(login_url="/accounts/login/")
def warehouse_receive_view(request):
    """Mahsulot qabul qilish (Kirish) - barcode bilan"""
    from products.models import Category
    
    if request.method == 'POST':
        try:
            # Barcode orqali mahsulot qidirish
            barcode = request.POST.get('barcode', '').strip()
            product_id = request.POST.get('product_id')
            
            if barcode:
                # Barcode orqali mahsulot topish
                product = None
                try:
                    # Avval ProductBarcode dan qidiramiz
                    from .models import ProductBarcode
                    product_barcode = ProductBarcode.objects.get(barcode=barcode)
                    product = product_barcode.product
                except ProductBarcode.DoesNotExist:
                    pass
                
                # Agar ProductBarcode da topilmasa, Product modelidan qidiramiz
                if not product:
                    try:
                        product = Product.objects.get(barcode=barcode)
                    except Product.DoesNotExist:
                        pass
                
                if product:
                    quantity = int(request.POST.get('quantity', 0))
                    product.quantity += quantity
                    product.save()
                    
                    messages.success(request, f"{product.name} (barcode: {barcode}) ga {quantity} dona qo'shildi!", extra_tags="success")
                else:
                    messages.error(request, f"Barcode '{barcode}' bo'yicha mahsulot topilmadi!", extra_tags="warning")
                    
                return redirect('organizations:warehouse_receive')
            
            elif product_id:
                # Mavjud mahsulotga qo'shish
                product = get_object_or_404(Product, id=product_id)
                quantity = int(request.POST.get('quantity', 0))
                product.quantity += quantity
                product.save()
                
                messages.success(request, f"{product.name} ga {quantity} dona qo'shildi!", extra_tags="success")
            else:
                # Yangi mahsulot yaratish
                Product.objects.create(
                    name=request.POST['name'],
                    description=request.POST.get('description', ''),
                    category_id=request.POST['category'],
                    price=float(request.POST['price']),
                    quantity=int(request.POST['quantity']),
                    barcode=request.POST.get('barcode', ''),
                    status='ACTIVE'
                )
                
                messages.success(request, "Yangi mahsulot muvaffaqiyatli qo'shildi!", extra_tags="success")
            
            return redirect('organizations:warehouse_receive')
            
        except Exception as e:
            messages.error(request, 'Xatolik yuz berdi!', extra_tags="danger")
            print(e)
    
    context = {
        'active_icon': 'warehouse',
        'categories': Category.objects.all(),
        'products': Product.objects.filter(status='ACTIVE').order_by('name'),
    }
    
    return render(request, "organizations/warehouse_receive.html", context=context)


@login_required(login_url="/accounts/login/")
def warehouse_product_history_view(request, product_id):
    """Mahsulot tarixi"""
    product = get_object_or_404(Product, id=product_id)
    
    # Yuk xatlaridagi chiqishlar
    deliveries = DeliveryNoteDetail.objects.filter(product=product).select_related('delivery_note').order_by('-delivery_note__date')
    
    # Barcode'lar
    barcodes = ProductBarcode.objects.filter(product=product).order_by('-created_date')
    
    context = {
        'active_icon': 'warehouse',
        'product': product,
        'deliveries': deliveries,
        'barcodes': barcodes,
    }
    
    return render(request, "organizations/warehouse_product_history.html", context=context)
