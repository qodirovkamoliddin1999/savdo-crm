from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Organization(models.Model):
    """Byudjet tashkilotlari (maktablar, kasalxonalar, davlat idoralari)"""
    
    ORGANIZATION_TYPES = (
        ('SCHOOL', 'Maktab'),
        ('HOSPITAL', 'Kasalxona'),
        ('GOVERNMENT', 'Davlat idorasi'),
        ('UNIVERSITY', 'Universitet'),
        ('OTHER', 'Boshqa'),
    )
    
    # Asosiy ma'lumotlar
    name = models.CharField(max_length=256, verbose_name="To'liq nomi")
    short_name = models.CharField(max_length=100, verbose_name="Qisqacha nomi")
    organization_type = models.CharField(
        max_length=20, 
        choices=ORGANIZATION_TYPES, 
        verbose_name="Tashkilot turi"
    )
    
    # Rasmiy ma'lumotlar
    inn = models.CharField(max_length=20, unique=True, verbose_name="INN")
    oked = models.CharField(max_length=20, blank=True, null=True, verbose_name="OKED")
    mfo = models.CharField(max_length=10, blank=True, null=True, verbose_name="MFO")
    account_number = models.CharField(max_length=30, blank=True, null=True, verbose_name="Hisob raqam")
    
    # Manzil va aloqa
    legal_address = models.TextField(verbose_name="Yuridik manzil")
    actual_address = models.TextField(blank=True, null=True, verbose_name="Haqiqiy manzil")
    phone = models.CharField(max_length=30, verbose_name="Telefon")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Mas'ul shaxslar
    director_name = models.CharField(max_length=256, verbose_name="Direktor F.I.O.")
    director_phone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Direktor telefoni")
    
    responsible_person = models.CharField(max_length=256, verbose_name="Mas'ul shaxs F.I.O.")
    responsible_position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mas'ul shaxs lavozimi")
    responsible_phone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Mas'ul shaxs telefoni")
    
    # Qo'shimcha
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        db_table = 'Organizations'
        verbose_name = "Tashkilot"
        verbose_name_plural = "Tashkilotlar"
        ordering = ['short_name']
    
    def __str__(self):
        return self.short_name
    
    def get_full_address(self):
        """Haqiqiy manzil bo'lmasa yuridik manzilni qaytaradi"""
        return self.actual_address if self.actual_address else self.legal_address


class Contract(models.Model):
    """Tashkilotlar bilan shartnomalar"""
    
    CONTRACT_STATUS = (
        ('ACTIVE', 'Faol'),
        ('EXPIRED', 'Muddati tugagan'),
        ('TERMINATED', 'Bekor qilingan'),
    )
    
    # Asosiy ma'lumotlar
    number = models.CharField(max_length=50, unique=True, verbose_name="Shartnoma raqami")
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='contracts',
        verbose_name="Tashkilot"
    )
    
    # Sanalar
    contract_date = models.DateField(verbose_name="Shartnoma sanasi")
    start_date = models.DateField(verbose_name="Boshlanish sanasi")
    end_date = models.DateField(verbose_name="Tugash sanasi")
    
    # Shartnoma shartlari
    total_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Umumiy summa"
    )
    payment_terms = models.TextField(blank=True, null=True, verbose_name="To'lov shartlari")
    delivery_terms = models.TextField(blank=True, null=True, verbose_name="Yetkazib berish shartlari")
    
    # Holat
    status = models.CharField(
        max_length=20, 
        choices=CONTRACT_STATUS, 
        default='ACTIVE',
        verbose_name="Holati"
    )
    
    # Fayllar
    contract_file = models.FileField(
        upload_to='contracts/', 
        blank=True, 
        null=True,
        verbose_name="Shartnoma fayli"
    )
    
    # Qo'shimcha
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Yaratgan xodim"
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        db_table = 'Contracts'
        verbose_name = "Shartnoma"
        verbose_name_plural = "Shartnomalar"
        ordering = ['-contract_date']
    
    def __str__(self):
        return f"Shartnoma №{self.number} - {self.organization.short_name}"
    
    def is_active(self):
        """Shartnoma faolligini tekshiradi"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'ACTIVE' and self.start_date <= today <= self.end_date


class DeliveryNote(models.Model):
    """Yuk xati (Накладная)"""
    
    PAYMENT_STATUS = (
        ('UNPAID', 'To\'lanmagan'),
        ('PARTIAL', 'Qisman to\'langan'),
        ('PAID', 'To\'langan'),
    )
    
    # Asosiy ma'lumotlar
    number = models.CharField(max_length=50, unique=True, verbose_name="Yuk xati raqami")
    date = models.DateField(verbose_name="Sana")
    
    # Tashkilot va shartnoma
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='delivery_notes',
        verbose_name="Tashkilot"
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_notes',
        verbose_name="Shartnoma"
    )
    
    # Summalar
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Oraliq jami")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Umumiy summa")
    
    # To'lov
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='UNPAID',
        verbose_name="To'lov holati"
    )
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="To'langan summa")
    
    # Qo'shimcha
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Yaratgan xodim"
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        db_table = 'DeliveryNotes'
        verbose_name = "Yuk xati"
        verbose_name_plural = "Yuk xatlari"
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"Yuk xati №{self.number} - {self.organization.short_name}"
    
    def get_remaining_amount(self):
        """Qolgan qarz summasini qaytaradi"""
        return self.total_amount - self.paid_amount
    
    def update_totals(self):
        """Umumiy summani hisoblaydi"""
        details = self.details.all()
        self.subtotal = sum([d.total for d in details])
        self.total_amount = self.subtotal
        self.save()
    
    def update_payment_status(self):
        """To'lov holatini yangilaydi"""
        if self.paid_amount == 0:
            self.payment_status = 'UNPAID'
        elif self.paid_amount >= self.total_amount:
            self.payment_status = 'PAID'
        else:
            self.payment_status = 'PARTIAL'
        self.save()


class DeliveryNoteDetail(models.Model):
    """Yuk xati tafsilotlari"""
    
    delivery_note = models.ForeignKey(
        DeliveryNote,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name="Yuk xati"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Mahsulot"
    )
    
    # Mahsulot ma'lumotlari
    product_name = models.CharField(max_length=256, verbose_name="Mahsulot nomi")
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Seriya raqami")
    
    # Miqdor va narx
    quantity = models.IntegerField(verbose_name="Miqdori")
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Narxi")
    total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Jami")
    
    class Meta:
        db_table = 'DeliveryNoteDetails'
        verbose_name = "Yuk xati tafsiloti"
        verbose_name_plural = "Yuk xati tafsilotlari"
    
    def __str__(self):
        return f"{self.product_name} - {self.quantity} dona"
    
    def save(self, *args, **kwargs):
        """Saqlashdan oldin jami summani hisoblaydi"""
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)
        # Yuk xati umumiy summasini yangilash
        self.delivery_note.update_totals()


class Payment(models.Model):
    """To'lovlar"""
    
    delivery_note = models.ForeignKey(
        DeliveryNote,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Yuk xati"
    )
    
    # To'lov ma'lumotlari
    payment_date = models.DateField(verbose_name="To'lov sanasi")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Summa")
    payment_document = models.CharField(max_length=100, blank=True, null=True, verbose_name="To'lov hujjati")
    
    # Qo'shimcha
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Yaratgan xodim"
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    
    class Meta:
        db_table = 'Payments'
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"To'lov {self.amount} so'm - {self.payment_date}"
    
    def save(self, *args, **kwargs):
        """Saqlashdan keyin yuk xati to'lov holatini yangilaydi"""
        super().save(*args, **kwargs)
        # Yuk xatidagi to'langan summani yangilash
        total_paid = sum([p.amount for p in self.delivery_note.payments.all()])
        self.delivery_note.paid_amount = total_paid
        self.delivery_note.update_payment_status()


class ProductBarcode(models.Model):
    """Mahsulot barcode'lari"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='barcodes',
        verbose_name="Mahsulot"
    )
    
    # Barcode ma'lumotlari
    barcode = models.CharField(max_length=100, unique=True, verbose_name="Barcode")
    internal_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ichki kod")
    
    # Qo'shimcha
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Yaratgan xodim"
    )
    
    class Meta:
        db_table = 'ProductBarcodes'
        verbose_name = "Barcode"
        verbose_name_plural = "Barcode'lar"
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.barcode} - {self.product.name}"


class EmployeePermission(models.Model):
    """Xodimlar ruxsatlari"""
    
    employee = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='warehouse_permissions',
        verbose_name="Xodim"
    )
    
    # Asosiy ruxsatlar
    can_view_organizations = models.BooleanField(default=False, verbose_name="Tashkilotlarni ko'rish")
    can_add_organizations = models.BooleanField(default=False, verbose_name="Tashkilot qo'shish")
    can_edit_organizations = models.BooleanField(default=False, verbose_name="Tashkilotni tahrirlash")
    can_delete_organizations = models.BooleanField(default=False, verbose_name="Tashkilotni o'chirish")
    
    # Shartnomalar
    can_view_contracts = models.BooleanField(default=False, verbose_name="Shartnomalarni ko'rish")
    can_add_contracts = models.BooleanField(default=False, verbose_name="Shartnoma qo'shish")
    can_edit_contracts = models.BooleanField(default=False, verbose_name="Shartnomani tahrirlash")
    can_delete_contracts = models.BooleanField(default=False, verbose_name="Shartnomani o'chirish")
    
    # Yuk xatlari
    can_view_delivery_notes = models.BooleanField(default=False, verbose_name="Yuk xatlarini ko'rish")
    can_add_delivery_notes = models.BooleanField(default=False, verbose_name="Yuk xati yaratish")
    can_delete_delivery_notes = models.BooleanField(default=False, verbose_name="Yuk xatini o'chirish")
    can_print_delivery_notes = models.BooleanField(default=False, verbose_name="Yuk xatini chop etish")
    
    # Mahsulotlar
    can_view_products = models.BooleanField(default=True, verbose_name="Mahsulotlarni ko'rish")
    can_add_products = models.BooleanField(default=False, verbose_name="Mahsulot qo'shish")
    can_edit_products = models.BooleanField(default=False, verbose_name="Mahsulotni tahrirlash")
    can_delete_products = models.BooleanField(default=False, verbose_name="Mahsulotni o'chirish")
    can_edit_prices = models.BooleanField(default=False, verbose_name="Narxlarni o'zgartirish")
    
    # To'lovlar
    can_view_payments = models.BooleanField(default=False, verbose_name="To'lovlarni ko'rish")
    can_add_payments = models.BooleanField(default=False, verbose_name="To'lov qo'shish")
    can_delete_payments = models.BooleanField(default=False, verbose_name="To'lovni o'chirish")
    
    # Hisobotlar
    can_view_reports = models.BooleanField(default=False, verbose_name="Hisobotlarni ko'rish")
    can_export_reports = models.BooleanField(default=False, verbose_name="Hisobotlarni eksport qilish")
    
    # POS va Savdo
    can_view_pos = models.BooleanField(default=True, verbose_name="POS panelini ko'rish")
    can_add_sales = models.BooleanField(default=False, verbose_name="Savdo qilish")
    can_view_sales = models.BooleanField(default=True, verbose_name="Savdlarni ko'rish")
    can_edit_sales = models.BooleanField(default=False, verbose_name="Savdoni tahrirlash")
    can_delete_sales = models.BooleanField(default=False, verbose_name="Savdoni o'chirish")
    
    # Mijozlar
    can_view_customers = models.BooleanField(default=True, verbose_name="Mijozlarni ko'rish")
    can_add_customers = models.BooleanField(default=False, verbose_name="Mijoz qo'shish")
    can_edit_customers = models.BooleanField(default=False, verbose_name="Mijozni tahrirlash")
    can_delete_customers = models.BooleanField(default=False, verbose_name="Mijozni o'chirish")
    
    # Qarz daftari
    can_view_debt = models.BooleanField(default=False, verbose_name="Qarz daftarini ko'rish")
    can_add_debt = models.BooleanField(default=False, verbose_name="Qarz qo'shish")
    can_edit_debt = models.BooleanField(default=False, verbose_name="Qarzni tahrirlash")
    can_delete_debt = models.BooleanField(default=False, verbose_name="Qarzni o'chirish")
    can_add_debt_payments = models.BooleanField(default=False, verbose_name="Qarz to'lovi qilish")
    
    # Ombor (kengaytirilgan)
    can_view_warehouse = models.BooleanField(default=True, verbose_name="Omborni ko'rish")
    can_receive_warehouse = models.BooleanField(default=False, verbose_name="Omborga qabul qilish")
    can_manage_barcodes = models.BooleanField(default=False, verbose_name="Barcodeni boshqarish")
    
    # Qo'shimcha
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        db_table = 'EmployeePermissions'
        verbose_name = "Xodim ruxsati"
        verbose_name_plural = "Xodimlar ruxsatlari"
    
    def __str__(self):
        return f"{self.employee.username} - Ruxsatlar"
    
    def is_admin(self):
        """Xodim admin ekanligini tekshiradi"""
        return self.employee.is_superuser or self.employee.is_staff
