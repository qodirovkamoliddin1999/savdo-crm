# Avtomatik Barcode Tizimi - Qo'llanma

## 🎯 Asosiy Funksiyalar

✅ **Avtomatik barcode yaratish** - Mahsulot qo'shilganda avtomatik barcode yaratiladi  
✅ **PDF sticker yaratish** - 40x58mm o'lchamda chop etishga tayyor PDF  
✅ **Ommaviy chop etish** - Bir necha mahsulotga bir vaqtda barcode yaratish  
✅ **Yangi partiya** - Yangi mahsulot kelganida kerakli miqdorda sticker chop etish  

---

## 📦 Barcode Format

**Format:** EAN-13 (13 ta raqam)  
**Tuzilma:** `2-YYMM-XXXXX-C`

- `2` - Mahalliy barcode belgisi
- `YYMM` - Yil va oy (masalan: 2602 = 2026-yil fevral)
- `XXXXX` - Mahsulot ID yoki noyob raqam
- `C` - Check digit (avtomatik hisoblanadi)

**Misol:** `2260212345-6`

---

## 🚀 Foydalanish

### 1. Yangi Mahsulot Qo'shish

Mahsulot qo'shganingizda barcode **avtomatik yaratiladi**:

```
1. Admin panel → Mahsulotlar → Mahsulot qo'shish
2. Mahsulot ma'lumotlarini kiriting
3. Saqlang
4. ✅ Barcode avtomatik yaratildi!
```

### 2. Mavjud Mahsulotga Barcode Qo'shish

Agar mahsulotda barcode bo'lmasa:

**Admin panel orqali:**
1. Mahsulotlar ro'yxatida mahsulotni tanlang
2. "Actions" dan **"✨ Tanlanganlarga barcode yaratish"** ni tanlang
3. "Go" ni bosing

**Yoki:**
1. Mahsulotni tahrirlash
2. Saqlang
3. Avtomatik barcode qo'shiladi

### 3. Barcode Sticker Chop Etish

#### A) Bitta mahsulot uchun:

Admin panelda mahsulotlar ro'yxatida:
- **"📄 PDF"** tugmasi - 1 ta sticker
- **"📦 10x"** tugmasi - 10 ta sticker

#### B) Ko'p mahsulotlar uchun:

1. Kerakli mahsulotlarni belgilang (checkbox)
2. "Actions" dan tanlang:
   - **"🖨️ Barcode chop etish (1x)"** - har biridan 1 ta
   - **"🖨️ Barcode chop etish (10x)"** - har biridan 10 ta
3. "Go" ni bosing
4. PDF avtomatik yuklab olinadi

### 4. Yangi Partiya Kelganida

Omborga yangi mahsulot keldi (masalan, 50 dona)?

**URL orqali:**
```
/products/barcode/new-stock/{product_id}/?new_stock=50
```

**Natija:** 50 ta sticker PDF shaklida yuklab olinadi

---

## 📏 Sticker O'lchamlari

- **O'lchami:** 40mm × 58mm
- **Format:** Standart sticker printer uchun
- **Mazmuni:**
  - Mahsulot nomi (yuqorida)
  - Barcode (o'rtada, EAN-13)
  - Narx (pastda, katta)
  - Sana (juda kichik)

---

## 🔧 API Endpoints

### 1. Bitta mahsulot uchun PDF
```
GET /products/barcode/download/{product_id}/
```

### 2. Ommaviy PDF (miqdor bilan)
```
GET /products/barcode/bulk/{product_id}/?quantity=20
```

### 3. Yangi partiya
```
GET /products/barcode/new-stock/{product_id}/?new_stock=100
```

### 4. Ko'p mahsulotlar
```
POST /products/barcode/multiple/
Content-Type: application/json

{
    "products": [
        {"id": 1, "quantity": 10},
        {"id": 2, "quantity": 5},
        {"id": 3, "quantity": 15}
    ]
}
```

### 5. Barcode yaratish (API)
```
POST /products/barcode/generate/{product_id}/
```

---

## 💡 Misollar

### Misol 1: Yangi mahsulot qo'shish

```python
# Mahsulot yaratish
product = Product.objects.create(
    name="Coca Cola 1.5L",
    category=category,
    price=12000,
    quantity=0
)

# Barcode avtomatik yaratiladi!
print(product.barcode)  # Natija: 2260212345678
```

### Misol 2: 100 ta yangi mahsulot keldi

```python
# URL: /products/barcode/new-stock/1/?new_stock=100

# Yoki kodda:
from products.pdf_utils import create_bulk_barcode_pdf

pdf = create_bulk_barcode_pdf(product, quantity=100)
# 100 ta sticker PDF yaratildi!
```

### Misol 3: Bir necha mahsulot uchun

```python
from products.pdf_utils import create_multiple_products_pdf

products_list = [
    (product1, 10),  # 10 ta sticker
    (product2, 5),   # 5 ta sticker
    (product3, 20),  # 20 ta sticker
]

pdf = create_multiple_products_pdf(products_list)
```

---

## 🖨️ Printer Sozlamalari

### Tavsiya etilgan printer:

- **Turi:** Thermal sticker printer
- **O'lchami:** 40mm × 58mm sticker
- **Namuna:** Xprinter XP-420B, TSC TDP-225, Zebra GK420d

### Printer sozlash:

1. PDF ni oching
2. Print → Properties
3. **Paper Size:** Custom (40mm × 58mm)
4. **Quality:** High (300+ DPI)
5. **Margins:** 0mm (barcha tomondan)
6. Chop eting!

---

## ⚙️ Texnik Ma'lumotlar

### Barcode Turi: EAN-13

- **Uzunlik:** 13 raqam
- **Check digit:** Avtomatik hisoblanadi
- **Validatsiya:** To'liq qo'llab-quvvatlanadi

### Fayl Formati

- **PDF:** ReportLab kutubxonasi bilan yaratiladi
- **O'lchami:** ~10-20 KB har bir sticker
- **Sifati:** Chop etish uchun optimallashtirilgan

### Avtomatik Yaratish

Signal orqali mahsulot saqlanganida:
```python
# products/signals.py
@receiver(pre_save, sender=Product)
def auto_generate_barcode(sender, instance, **kwargs):
    if not instance.barcode:
        instance.barcode = get_next_barcode_for_product(instance)
```

---

## 🔍 Barcode Tekshirish

### Barcode to'g'riligini tekshirish:

```python
from products.barcode_utils import validate_barcode

is_valid, message = validate_barcode("2260212345678")

if is_valid:
    print("✓ Barcode to'g'ri")
else:
    print(f"✗ {message}")
```

### Qidiruv:

Admin panelda barcode bo'yicha qidirish mumkin:
```
Mahsulotlar → Qidiruv → "2260212345678"
```

---

## 📊 Hisobot va Monitoring

### Barcode bo'lmagan mahsulotlar:

```python
Product.objects.filter(barcode__isnull=True)
```

### Oxirgi yaratilgan barcode'lar:

```python
Product.objects.exclude(barcode__isnull=True).order_by('-id')[:10]
```

---

## 🐛 Muammolarni Hal Qilish

### 1. Barcode yaratilmayapti

**Sabab:** Signal ishlamayapti

**Yechim:**
```bash
# products/apps.py da ready() method borligini tekshiring
python manage.py shell
>>> from products.signals import *
```

### 2. PDF yuklab olinmayapti

**Sabab:** Kutubxona o'rnatilmagan

**Yechim:**
```bash
pip install python-barcode qrcode reportlab pillow
```

### 3. Barcode duplikat

**Sabab:** Noyoblik tekshiruvi

**Yechim:** Tizim avtomatik boshqa barcode yaratadi (100 urinish)

### 4. PDF ko'rinmayapti

**Sabab:** Printer sozlamalari

**Yechim:**
- Custom paper size: 40mm × 58mm
- Margin: 0mm
- Scale: 100%

---

## 📦 Miqdorlar va Cheklovlar

| Amal | Maksimal miqdor |
|------|----------------|
| Bitta mahsulot | Cheklovsiz |
| Bulk barcode | 100 dona |
| Yangi partiya | 500 dona |
| PDF hajmi | ~2 MB (100 sticker) |

---

## 🔐 Xavfsizlik

- ✅ Faqat tizimga kirgan foydalanuvchilar barcode yaratishi mumkin
- ✅ Barcode noyob va takrorlanmaydi
- ✅ Har bir amal log'lanadi
- ✅ Check digit orqali validatsiya

---

## 🎨 Customization

### Sticker dizaynini o'zgartirish:

`products/pdf_utils.py` faylida `draw_single_sticker()` funksiyasini tahrirlang:

```python
# Rang o'zgartirish
c.setFillColorRGB(1, 0, 0)  # Qizil

# Font o'zgartirish
c.setFont("Helvetica-Bold", 12)

# Qo'shimcha ma'lumot qo'shish
c.drawString(x, y, "YANGI CHEGIRMA!")
```

---

## 📞 Yordam

**Muammo yuzaga kelsa:**

1. Log'larni tekshiring
2. Admin panel → Mahsulotlar
3. Barcode ustunida "⚠️ Barcode yo'q" bo'lsa, mahsulotni qayta saqlang
4. Yoki `populate_barcodes` management commandini ishga tushiring

---

## ✅ Deployment Checklist

- [x] `python-barcode` o'rnatilgan
- [x] `reportlab` o'rnatilgan  
- [x] `qrcode` o'rnatilgan
- [x] `Pillow` o'rnatilgan
- [x] Signal faollashtirilgan
- [x] URL'lar qo'shilgan
- [x] Admin actions qo'shilgan
- [x] Printer sozlangan (40x58mm)

---

**Yaratilgan:** 2026-02-17  
**Versiya:** 1.0  
**Muallif:** APTECH CRM Development Team

**Muvaffaqiyat tilaymiz! 🎉**
