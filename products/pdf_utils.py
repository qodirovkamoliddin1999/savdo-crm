"""
Barcode sticker PDF yaratish (40x58mm format)
"""
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as MM
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import barcode
from barcode.writer import ImageWriter
import io
from datetime import datetime


# Sticker o'lchamlari (58mm x 40mm) - Horizontal/Landscape format
# Barcode scanner uchun yaxshiroq
STICKER_WIDTH = 58 * MM
STICKER_HEIGHT = 40 * MM

# Margin
MARGIN = 2 * MM


def create_barcode_stickers_pdf(products_data, filename=None):
    """
    Bir necha mahsulot uchun barcode stickerlar PDF yaratish
    
    products_data: [
        {
            'barcode': '2260212345678',
            'name': 'Mahsulot nomi',
            'price': 100000,
            'quantity': 5  # Nechta sticker kerak
        },
        ...
    ]
    """
    buffer = io.BytesIO()
    
    # PDF yaratish
    c = canvas.Canvas(buffer, pagesize=(STICKER_WIDTH, STICKER_HEIGHT))
    
    total_stickers = sum(item.get('quantity', 1) for item in products_data)
    current_sticker = 0
    
    for product_data in products_data:
        quantity = product_data.get('quantity', 1)
        
        for i in range(quantity):
            current_sticker += 1
            
            # Har bir sticker uchun yangi sahifa
            if current_sticker > 1:
                c.showPage()
            
            # Sticker chizish
            draw_single_sticker(c, product_data)
    
    c.save()
    buffer.seek(0)
    
    return buffer


def draw_single_sticker(c, product_data):
    """
    Bitta sticker chizish (40x58mm)
    Faqat: Mahsulot nomi, Barcode, Sana
    """
    barcode_number = product_data.get('barcode', '')
    product_name = product_data.get('name', 'Mahsulot')
    
    # Mahsulot nomi (yuqorida, kichikroq - ko'proq joy barcode uchun)
    c.setFont("Helvetica-Bold", 7)
    
    # Matnni sticker kengligiga sig'dirish
    max_width = STICKER_WIDTH - (2 * MARGIN)
    if len(product_name) > 35:
        product_name = product_name[:32] + '...'
    
    # Matnni markazga joylashtirish
    text_width = c.stringWidth(product_name, "Helvetica-Bold", 7)
    x_position = (STICKER_WIDTH - text_width) / 2
    y_position = STICKER_HEIGHT - MARGIN - 4
    
    c.drawString(x_position, y_position, product_name)
    
    # Barcode yaratish va qo'shish
    if barcode_number:
        try:
            # Barcode rasm yaratish
            EAN = barcode.get_barcode_class('EAN13')
            ean = EAN(barcode_number, writer=ImageWriter())
            
            barcode_buffer = io.BytesIO()
            ean.write(barcode_buffer, options={
                'module_width': 0.25,
                'module_height': 10.0,
                'quiet_zone': 1.0,
                'font_size': 8,
                'text_distance': 2.0,
                'write_text': True,
            })
            
            barcode_buffer.seek(0)
            
            # Barcode rasmni PDF ga qo'shish
            barcode_img = ImageReader(barcode_buffer)
            
            # Barcode joylashuvi (markazda, kattaroq - scanner uchun yaxshi)
            barcode_width = 50 * MM  # Kattaroq barcode - yaxshi o'qiladi
            barcode_height = 18 * MM  # Balandroq
            barcode_x = (STICKER_WIDTH - barcode_width) / 2
            barcode_y = MARGIN + 6 * MM  # Pastdan joylashgan
            
            c.drawImage(barcode_img, barcode_x, barcode_y, 
                       width=barcode_width, height=barcode_height,
                       preserveAspectRatio=True, mask='auto')
        
        except Exception as e:
            # Agar barcode yaratib bo'lmasa, matn ko'rinishida
            c.setFont("Helvetica", 8)
            text = f"Barcode: {barcode_number}"
            text_width = c.stringWidth(text, "Helvetica", 8)
            x_pos = (STICKER_WIDTH - text_width) / 2
            c.drawString(x_pos, STICKER_HEIGHT - MARGIN - 20 * MM, text)
    
    # Sana (barcode ustida, kichik)
    c.setFont("Helvetica", 6)
    date_text = datetime.now().strftime("%d.%m.%Y")
    date_width = c.stringWidth(date_text, "Helvetica", 6)
    date_x = (STICKER_WIDTH - date_width) / 2
    date_y = MARGIN + 24 * MM  # Barcode ustida
    
    c.drawString(date_x, date_y, date_text)


def create_product_barcode_pdf(product):
    """
    Bitta mahsulot uchun barcode PDF yaratish
    """
    from products.models import Product
    
    if not product.barcode:
        raise ValueError("Mahsulotda barcode yo'q")
    
    product_data = {
        'barcode': product.barcode,
        'name': product.name,
        'price': product.price,
        'quantity': 1
    }
    
    return create_barcode_stickers_pdf([product_data])


def create_bulk_barcode_pdf(product, quantity):
    """
    Bir mahsulotdan bir necha dona sticker yaratish
    """
    if not product.barcode:
        raise ValueError("Mahsulotda barcode yo'q")
    
    product_data = {
        'barcode': product.barcode,
        'name': product.name,
        'price': product.price,
        'quantity': quantity
    }
    
    return create_barcode_stickers_pdf([product_data])


def create_multiple_products_pdf(products_with_quantities):
    """
    Bir necha mahsulotlar uchun sticker yaratish
    
    products_with_quantities: [(product, quantity), ...]
    """
    products_data = []
    
    for product, quantity in products_with_quantities:
        if not product.barcode:
            continue
        
        products_data.append({
            'barcode': product.barcode,
            'name': product.name,
            'price': product.price,
            'quantity': quantity
        })
    
    if not products_data:
        raise ValueError("Barcode'li mahsulotlar topilmadi")
    
    return create_barcode_stickers_pdf(products_data)
