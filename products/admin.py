from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product
from .pdf_utils import create_multiple_products_pdf
from .barcode_utils import get_next_barcode_for_product
from datetime import datetime


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'description')
    list_filter = ('status',)
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'barcode', 'status', 'barcode_actions')
    list_filter = ('status', 'category')
    search_fields = ('name', 'barcode', 'description')
    ordering = ('-id',)
    actions = ['generate_barcodes_action', 'print_barcodes_action', 'print_bulk_barcodes_action']
    
    def barcode_actions(self, obj):
        """Barcode tugmalari"""
        if obj.barcode:
            download_url = reverse('products:download_barcode', args=[obj.id])
            bulk_url = reverse('products:download_bulk_barcode', args=[obj.id])
            return format_html(
                '<a class="button" href="{}" target="_blank" style="padding: 5px 10px; background: #417690; color: white; border-radius: 3px; text-decoration: none; margin-right: 5px;">📄 PDF</a>'
                '<a class="button" href="{}?quantity=10" target="_blank" style="padding: 5px 10px; background: #28a745; color: white; border-radius: 3px; text-decoration: none;">📦 10x</a>',
                download_url, bulk_url
            )
        else:
            generate_url = reverse('admin:products_product_change', args=[obj.id])
            return format_html(
                '<a href="{}" style="color: red;">⚠️ Barcode yo\'q</a>',
                generate_url
            )
    
    barcode_actions.short_description = 'Barcode harakatlari'
    
    def generate_barcodes_action(self, request, queryset):
        """Tanlangan mahsulotlar uchun barcode yaratish"""
        generated = 0
        already_have = 0
        
        for product in queryset:
            if not product.barcode:
                try:
                    product.barcode = get_next_barcode_for_product(product)
                    product.save()
                    generated += 1
                except Exception as e:
                    self.message_user(request, f'Xatolik {product.name}: {e}', level='ERROR')
            else:
                already_have += 1
        
        if generated > 0:
            self.message_user(request, f'{generated} ta mahsulot uchun barcode yaratildi.')
        if already_have > 0:
            self.message_user(request, f'{already_have} ta mahsulotda allaqachon barcode mavjud.', level='WARNING')
    
    generate_barcodes_action.short_description = "✨ Tanlanganlarga barcode yaratish"
    
    def print_barcodes_action(self, request, queryset):
        """Tanlangan mahsulotlar uchun barcode PDF yaratish (har biridan 1 ta)"""
        products_with_quantities = []
        
        for product in queryset:
            # Agar barcode bo'lmasa, yaratish
            if not product.barcode:
                try:
                    product.barcode = get_next_barcode_for_product(product)
                    product.save()
                except Exception:
                    continue
            
            products_with_quantities.append((product, 1))
        
        if not products_with_quantities:
            self.message_user(request, 'Hech qanday mahsulotda barcode yo\'q', level='ERROR')
            return
        
        try:
            pdf_buffer = create_multiple_products_pdf(products_with_quantities)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            filename = f"barcodes_selected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            self.message_user(request, f'PDF yaratishda xatolik: {e}', level='ERROR')
    
    print_barcodes_action.short_description = "🖨️ Tanlanganlarga barcode chop etish (1x)"
    
    def print_bulk_barcodes_action(self, request, queryset):
        """Tanlangan mahsulotlar uchun barcode PDF yaratish (har biridan 10 ta)"""
        products_with_quantities = []
        
        for product in queryset:
            # Agar barcode bo'lmasa, yaratish
            if not product.barcode:
                try:
                    product.barcode = get_next_barcode_for_product(product)
                    product.save()
                except Exception:
                    continue
            
            products_with_quantities.append((product, 10))
        
        if not products_with_quantities:
            self.message_user(request, 'Hech qanday mahsulotda barcode yo\'q', level='ERROR')
            return
        
        try:
            pdf_buffer = create_multiple_products_pdf(products_with_quantities)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            filename = f"barcodes_bulk_10x_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            self.message_user(request, f'PDF yaratishda xatolik: {e}', level='ERROR')
    
    print_bulk_barcodes_action.short_description = "🖨️ Tanlanganlarga barcode chop etish (10x)"
