"""
Barcode yaratish va boshqarish uchun utility funksiyalar
"""
import barcode
from barcode.writer import ImageWriter
import io
from datetime import datetime
import random
import string


def generate_barcode_number(product_id=None):
    """
    Mahsulot uchun noyob barcode raqami yaratish
    Format: To'liq tasodifiy 12 raqam + Check digit (EAN-13)
    """
    # 12 ta tasodifiy raqam yaratish
    barcode_base = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    # EAN13 check digit hisoblash
    check_digit = calculate_ean13_check_digit(barcode_base)
    
    return barcode_base + str(check_digit)


def calculate_ean13_check_digit(barcode_12):
    """EAN13 barcode uchun check digit hisoblash"""
    if len(barcode_12) != 12:
        raise ValueError("Barcode 12 ta raqamdan iborat bo'lishi kerak")
    
    odd_sum = sum(int(barcode_12[i]) for i in range(0, 12, 2))
    even_sum = sum(int(barcode_12[i]) for i in range(1, 12, 2))
    
    total = odd_sum + (even_sum * 3)
    check_digit = (10 - (total % 10)) % 10
    
    return check_digit


def generate_barcode_image(barcode_number, format='EAN13'):
    """
    Barcode rasm yaratish
    Returns: BytesIO object with PNG image
    """
    try:
        # Barcode yaratish
        EAN = barcode.get_barcode_class(format)
        ean = EAN(barcode_number, writer=ImageWriter())
        
        # BytesIO buffer'ga yozish
        buffer = io.BytesIO()
        ean.write(buffer, options={
            'module_width': 0.3,
            'module_height': 12.0,
            'quiet_zone': 2.0,
            'font_size': 10,
            'text_distance': 3.0,
            'write_text': True,
        })
        
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        print(f"Barcode yaratishda xatolik: {e}")
        return None


def validate_barcode(barcode_number):
    """
    Barcode to'g'riligini tekshirish
    """
    if not barcode_number:
        return False, "Barcode bo'sh"
    
    # Faqat raqamlar
    if not barcode_number.isdigit():
        return False, "Barcode faqat raqamlardan iborat bo'lishi kerak"
    
    # Uzunlik tekshirish (EAN13 uchun 13 ta raqam)
    if len(barcode_number) != 13:
        return False, "Barcode 13 ta raqamdan iborat bo'lishi kerak"
    
    # Check digit tekshirish
    try:
        calculated_check = calculate_ean13_check_digit(barcode_number[:12])
        actual_check = int(barcode_number[12])
        
        if calculated_check != actual_check:
            return False, "Barcode check digit noto'g'ri"
        
        return True, "Barcode to'g'ri"
    
    except Exception as e:
        return False, f"Barcode tekshirishda xatolik: {e}"


def get_next_barcode_for_product(product):
    """
    Mahsulot uchun keyingi barcode raqamini olish
    """
    from products.models import Product
    
    # Mahsulot uchun yangi barcode yaratish
    max_attempts = 100
    for _ in range(max_attempts):
        new_barcode = generate_barcode_number(product.id)
        
        # Bazada mavjudligini tekshirish
        if not Product.objects.filter(barcode=new_barcode).exists():
            return new_barcode
    
    # Agar 100 ta urinishdan keyin ham topilmasa
    raise ValueError("Noyob barcode yaratib bo'lmadi")


def format_barcode_display(barcode_number):
    """
    Barcode ni chiroyli formatda ko'rsatish
    Misol: 2-2602-12345-6
    """
    if not barcode_number or len(barcode_number) != 13:
        return barcode_number
    
    return f"{barcode_number[0]}-{barcode_number[1:5]}-{barcode_number[5:10]}-{barcode_number[10:]}"
