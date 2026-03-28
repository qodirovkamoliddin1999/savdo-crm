# Sozlamalar Tizimi - Foydalanish Qo'llanmasi

## Kirish

Admin panelda **"Sozlamalar"** bo'limi yaratildi. Bu yerda siz barcha modellar va ularning maydonlarini dinamik ravishda sozlashingiz mumkin.

## Sozlamalar Turlari

### 1. Maydon Sozlamalari (Field Settings)

Har bir model maydonini individual sozlash imkoniyati:

#### Sozlash mumkin bo'lgan parametrlar:

- ✅ **Majburiy maydon** - Maydonni to'ldirish majburiyligini boshqarish
- ✅ **Ko'rinsin** - Maydonni formada yashirish/ko'rsatish
- ✅ **Tahrirlash mumkin** - Maydonni faqat o'qish rejimiga o'tkazish
- ✅ **Ro'yxatda ko'rsatish** - Admin panelda ro'yxatda ko'rsatish
- ✅ **Formada ko'rsatish** - Forma sahifasida ko'rsatish
- ✅ **Default qiymat** - Avtomatik qiymat o'rnatish
- ✅ **Min/Max uzunlik** - Matn uzunligini cheklash
- ✅ **Min/Max qiymat** - Raqamli qiymatlarni cheklash
- ✅ **Yordam matni** - Foydalanuvchilarga ko'rsatma berish

#### Misol: Mijoz telefon raqamini ixtiyoriy qilish

1. Admin panelda **Sozlamalar → Maydon sozlamalari** ga o'ting
2. `customers.Customer.phone` ni toping
3. **"Majburiy maydon"** belgilanmasini o'chiring
4. Saqlang

Endi telefon raqami ixtiyoriy maydon bo'ladi!

### 2. Model Sozlamalari (Model Settings)

Butun model uchun umumiy sozlamalar:

#### Sozlash mumkin bo'lgan parametrlar:

- 📋 **Sahifadagi yozuvlar soni** - Paginatsiya sozlamalari
- 🔍 **Qidiruv maydonlari** - Qaysi maydonlar bo'yicha qidirish
- 🔽 **Filter maydonlari** - Qaysi maydonlar bo'yicha filtrlash
- 📊 **Ro'yxatda ko'rsatiladigan maydonlar** - Jadvalda ko'rsatiladigan ustunlar
- 🔒 **Ruxsatlar** - Qo'shish, tahrirlash, o'chirish huquqlarini boshqarish

#### Misol: Mahsulotlar ro'yxatini sozlash

1. **Sozlamalar → Model sozlamalari** ga o'ting
2. `products.Product` ni tanlang
3. **Ro'yxatda ko'rsatiladigan maydonlar** ga: `name, category, price, quantity, status` kiriting
4. **Qidiruv maydonlari** ga: `name, barcode` kiriting
5. Saqlang

### 3. Tizim Sozlamalari (System Settings)

Umumiy tizim parametrlari:

#### Mavjud sozlamalar:

| Sozlama | Tavsif | Default qiymat |
|---------|--------|----------------|
| **Til** | Interfeys tili | uz |
| **Vaqt mintaqasi** | Tizim vaqti | Asia/Tashkent |
| **Valyuta** | Asosiy valyuta | UZS |
| **Valyuta belgisi** | Valyuta ko'rinishi | so'm |
| **Sana formati** | Sana ko'rinishi | DD.MM.YYYY |
| **Kasr raqamlar soni** | Pul uchun kasr | 2 |
| **Sessiya muddati** | Login muddati | 60 daqiqa |
| **Sahifadagi elementlar** | Ro'yxatlar hajmi | 20 |
| **Soliq foizi** | Standart soliq | 12% |
| **Kam qoldi ogohlantiruvi** | Ombor ogohlantiruvi | 10 dona |

## Admin Panelda Foydalanish

### Sozlamalarga kirish:

1. Admin panelga kiring (`/admin`)
2. **"SOZLAMALAR"** bo'limini toping
3. 3 ta bo'lim mavjud:
   - Maydon sozlamalari
   - Model sozlamalari
   - Tizim sozlamalari

### Maydon sozlamasini o'zgartirish:

**Misol: Mijoz email adresini majburiy qilish**

```
1. Sozlamalar → Maydon sozlamalari
2. Filter: App label = "customers", Model = "Customer"
3. "email" maydonini tanlang
4. ✓ "Majburiy maydon" ni belgilang
5. "Yordam matni" ga: "Email manzilni kiriting (masalan: info@example.com)"
6. Saqlang
```

### Filterlar bilan ishlash:

Admin panelda qulaylik uchun:
- **App bo'yicha** filter: customers, products, sales va h.k.
- **Maydon turi** bo'yicha: CharField, IntegerField va h.k.
- **Holat** bo'yicha: Faol/Nofaol

### Ommaviy o'zgartirish:

Bir necha maydonni birdan o'zgartirish:
1. Kerakli maydonlarni belgilang (checkbox)
2. Yuqoridagi "Action" dan tanlay oling
3. Ommaviy tahrirlash oynasi ochiladi

## Dasturlash uchun

### Formalarni dinamik qilish:

```python
from django import forms
from settings.utils import DynamicFormMixin
from customers.models import Customer

class CustomerForm(DynamicFormMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
```

Bu form avtomatik ravishda sozlamalarga bog'lanadi!

### Tizim sozlamalaridan foydalanish:

```python
from settings.utils import get_system_setting, set_system_setting

# Sozlamani o'qish
currency = get_system_setting('CURRENCY', 'UZS')
tax_rate = get_system_setting('TAX_PERCENTAGE', 12.0)

# Sozlamani o'zgartirish
set_system_setting('CURRENCY', 'USD')
```

### Maydon validatsiyasi:

```python
from settings.utils import validate_field_value

is_valid, error_msg = validate_field_value(
    'customers', 'Customer', 'phone', '+998901234567'
)

if not is_valid:
    print(error_msg)
```

## Management Commands

### Sozlamalarni avtomatik yaratish:

```bash
# Barcha sozlamalarni yaratish
python manage.py populate_settings --all

# Faqat maydon sozlamalari
python manage.py populate_settings --fields

# Faqat model sozlamalari
python manage.py populate_settings --models

# Faqat tizim sozlamalari
python manage.py populate_settings --system
```

## Foydali Maslahatlar

### 1. Majburiy maydonlarni boshqarish

Agar siz mijozlardan ba'zi ma'lumotlarni to'plamaysiz:
- Email ixtiyoriy qilish: `is_required = False`
- Telefon ixtiyoriy qilish: `is_required = False`

### 2. Maxfiy ma'lumotlarni yashirish

Ayrim maydonlarni oddiy xodimlardan yashirish:
- `is_visible = False` - Formada ko'rinmaydi
- `is_editable = False` - Faqat o'qish mumkin

### 3. Default qiymatlar

Tez-tez ishlatiladigan qiymatlarni avtomatik o'rnatish:
- Mahsulot statusi: `default_value = "ACTIVE"`
- Soliq foizi: `default_value = "12"`

### 4. Validatsiya qo'shish

Ma'lumotlar sifatini oshirish:
- Telefon uzunligi: `min_length = 9, max_length = 13`
- Mahsulot narxi: `min_value = 0, max_value = 1000000000`

### 5. Performance (Tezlik)

Barcha sozlamalar **cache** dan foydalanadi:
- O'zgartirishdan keyin 1 soat saqlanadi
- Yangilash uchun serverni qayta ishga tushirish shart emas

## Xavfsizlik

⚠️ **Muhim:**
- Faqat admin foydalanuvchilar sozlamalarni o'zgartirishi mumkin
- Tizim sozlamalarini ehtiyotkorlik bilan o'zgartiring
- O'zgartirishlardan oldin zaxira (backup) yarating

## Muammolarni hal qilish

### Sozlamalar ishlamayapti?

1. Cache ni tozalang:
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

2. Migratsiyalarni tekshiring:
```bash
python manage.py migrate settings
```

3. Sozlamalarni qayta yarating:
```bash
python manage.py populate_settings --all
```

## Qo'shimcha Imkoniyatlar

Kelajakda qo'shilishi mumkin bo'lgan funksiyalar:

- 📧 Email shablonlarini sozlash
- 🎨 Interfeys ranglarini sozlash
- 📊 Hisobot formatlarini sozlash
- 🔔 Bildirishnoma sozlamalari
- 🌐 Ko'p tillilik sozlamalari
- 🔐 Xavfsizlik sozlamalari (parol siyosati va h.k.)

## Yordam

Savol yoki takliflaringiz bo'lsa, admin panel orqali yoki dasturchilar bilan bog'laning.

---

**Yaratilgan sana:** 2026-02-17  
**Versiya:** 1.0  
**Mualliflar:** APTECH CRM Team
