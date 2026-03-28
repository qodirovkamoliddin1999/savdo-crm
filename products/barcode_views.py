"""
Barcode chop etish uchun view'lar
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Product
from .pdf_utils import (
    create_product_barcode_pdf,
    create_bulk_barcode_pdf,
    create_multiple_products_pdf
)
from .barcode_utils import generate_barcode_number, get_next_barcode_for_product
from datetime import datetime


@login_required
@require_http_methods(["GET"])
def download_product_barcode(request, product_id):
    """
    Bitta mahsulot uchun barcode PDF yuklab olish
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Agar barcode bo'lmasa, avtomatik yaratish
    if not product.barcode:
        try:
            product.barcode = get_next_barcode_for_product(product)
            product.save()
        except Exception as e:
            return JsonResponse({'error': f'Barcode yaratishda xatolik: {e}'}, status=400)
    
    try:
        # PDF yaratish
        pdf_buffer = create_product_barcode_pdf(product)
        
        # PDF ni yuklab olish
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        filename = f"barcode_{product.barcode}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        return JsonResponse({'error': f'PDF yaratishda xatolik: {e}'}, status=500)


@login_required
@require_http_methods(["GET"])
def download_bulk_barcode(request, product_id):
    """
    Bir mahsulotdan bir necha dona barcode PDF yuklab olish
    """
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get('quantity', 1))
    
    # Maksimal miqdorni cheklash
    if quantity > 100:
        return JsonResponse({'error': 'Maksimal 100 ta sticker yaratish mumkin'}, status=400)
    
    if quantity < 1:
        return JsonResponse({'error': 'Miqdor kamida 1 bo\'lishi kerak'}, status=400)
    
    # Agar barcode bo'lmasa, avtomatik yaratish
    if not product.barcode:
        try:
            product.barcode = get_next_barcode_for_product(product)
            product.save()
        except Exception as e:
            return JsonResponse({'error': f'Barcode yaratishda xatolik: {e}'}, status=400)
    
    try:
        # PDF yaratish
        pdf_buffer = create_bulk_barcode_pdf(product, quantity)
        
        # PDF ni yuklab olish
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        filename = f"barcode_{product.barcode}_x{quantity}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        return JsonResponse({'error': f'PDF yaratishda xatolik: {e}'}, status=500)


@login_required
@require_http_methods(["POST"])
def download_multiple_barcodes(request):
    """
    Bir necha mahsulotlar uchun barcode PDF yuklab olish
    """
    import json
    
    try:
        data = json.loads(request.body)
        products_data = data.get('products', [])
        
        if not products_data:
            return JsonResponse({'error': 'Mahsulotlar ro\'yxati bo\'sh'}, status=400)
        
        products_with_quantities = []
        
        for item in products_data:
            product_id = item.get('id')
            quantity = item.get('quantity', 1)
            
            product = get_object_or_404(Product, id=product_id)
            
            # Agar barcode bo'lmasa, avtomatik yaratish
            if not product.barcode:
                product.barcode = get_next_barcode_for_product(product)
                product.save()
            
            products_with_quantities.append((product, quantity))
        
        # PDF yaratish
        pdf_buffer = create_multiple_products_pdf(products_with_quantities)
        
        # PDF ni yuklab olish
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        filename = f"barcodes_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Noto\'g\'ri JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'PDF yaratishda xatolik: {e}'}, status=500)


@login_required
@require_http_methods(["GET"])
def print_new_stock_barcodes(request, product_id):
    """
    Omborga yangi mahsulot kelganida barcode'larni chop etish
    Miqdor = yangi kelgan mahsulotlar soni
    """
    product = get_object_or_404(Product, id=product_id)
    new_stock = int(request.GET.get('new_stock', 0))
    
    if new_stock < 1:
        return JsonResponse({'error': 'Yangi mahsulotlar soni kamida 1 bo\'lishi kerak'}, status=400)
    
    if new_stock > 500:
        return JsonResponse({'error': 'Maksimal 500 ta sticker yaratish mumkin'}, status=400)
    
    # Agar barcode bo'lmasa, avtomatik yaratish
    if not product.barcode:
        try:
            product.barcode = get_next_barcode_for_product(product)
            product.save()
        except Exception as e:
            return JsonResponse({'error': f'Barcode yaratishda xatolik: {e}'}, status=400)
    
    try:
        # PDF yaratish
        pdf_buffer = create_bulk_barcode_pdf(product, new_stock)
        
        # PDF ni yuklab olish
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        filename = f"new_stock_{product.name[:20]}_{new_stock}pcs_{datetime.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        return JsonResponse({'error': f'PDF yaratishda xatolik: {e}'}, status=500)


@login_required
@require_http_methods(["POST"])
def generate_barcode_for_product(request, product_id):
    """
    Mahsulot uchun yangi barcode yaratish (API)
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Agar allaqachon barcode bo'lsa
    force_new = request.POST.get('force_new', 'false').lower() == 'true'
    
    if product.barcode and not force_new:
        return JsonResponse({
            'error': 'Mahsulotda allaqachon barcode mavjud',
            'barcode': product.barcode
        }, status=400)
    
    try:
        old_barcode = product.barcode
        product.barcode = get_next_barcode_for_product(product)
        product.save()
        
        return JsonResponse({
            'success': True,
            'barcode': product.barcode,
            'old_barcode': old_barcode,
            'product_id': product.id,
            'product_name': product.name
        })
    
    except Exception as e:
        return JsonResponse({'error': f'Barcode yaratishda xatolik: {e}'}, status=500)
