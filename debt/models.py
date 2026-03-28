from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from organizations.models import Organization


class DebtRecord(models.Model):
    """Qarz yozuvlari"""
    
    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'To\'lanmagan'),
        ('PARTIAL', 'Qisman'),
        ('PAID', 'To\'liq'),
    ]
    
    # Asosiy maydonlar
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='debt_records',
        verbose_name="Tashkilot"
    )
    
    product_or_service = models.TextField(verbose_name="Mahsulot yoki bajarilgan ish")
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Umumiy summa"
    )
    
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="To\'langan summa"
    )
    
    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Qolgan qarz"
    )
    
    # Sana maydonlari
    date = models.DateField(
        default=timezone.now,
        verbose_name="Sana"
    )
    
    due_date = models.DateField(
        verbose_name="To\'lov muddati"
    )
    
    # Status
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='UNPAID',
        verbose_name="To\'lov holati"
    )
    
    # Qo'shimcha maydonlar
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Izohlar"
    )
    
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan sana"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Yaratgan xodim"
    )
    
    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="Yangilangan sana"
    )
    
    class Meta:
        db_table = 'DebtRecords'
        verbose_name = "Qarz yozuvi"
        verbose_name_plural = "Qarz yozuvlari"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['date']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.organization.name} - {self.product_or_service} ({self.total_amount})"
    
    def save(self, *args, **kwargs):
        # Avtomatik hisob-kitoblar
        self.calculate_amounts()
        self.determine_status()
        super().save(*args, **kwargs)
    
    def calculate_amounts(self):
        """Qolgan qarzni hisoblash"""
        self.remaining_amount = self.total_amount - self.paid_amount
        
        # Manfiy bo'lishiga yo'l qo'ymaslik
        if self.remaining_amount < 0:
            self.remaining_amount = 0
            self.paid_amount = self.total_amount
    
    def determine_status(self):
        """Statusni avtomatik aniqlash"""
        if self.paid_amount <= 0:
            self.payment_status = 'UNPAID'
        elif self.paid_amount >= self.total_amount:
            self.payment_status = 'PAID'
            self.paid_amount = self.total_amount
            self.remaining_amount = 0
        else:
            self.payment_status = 'PARTIAL'
    
    @property
    def is_overdue(self):
        """Muddati o'tganmi"""
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.payment_status != 'PAID'
    
    @property
    def days_overdue(self):
        """Qancha kun muddati o'tgan"""
        from django.utils import timezone
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    @property
    def status_color(self):
        """Status rangi"""
        if self.payment_status == 'PAID':
            return 'success'  # Yashil
        elif self.payment_status == 'PARTIAL':
            return 'warning'  # Sariq
        else:
            if self.is_overdue:
                return 'danger'  # Qizil (muddati o'tgan)
            return 'danger'  # Qizil (qarzdor)
    
    @property
    def status_badge_class(self):
        """Badge klassi"""
        colors = {
            'UNPAID': 'danger',
            'PARTIAL': 'warning',
            'PAID': 'success'
        }
        return colors.get(self.payment_status, 'secondary')
    
    def to_json(self):
        """JSON formatga o'tkazish"""
        return {
            'id': self.id,
            'organization': {
                'id': self.organization.id,
                'name': self.organization.name
            },
            'product_or_service': self.product_or_service,
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'remaining_amount': float(self.remaining_amount),
            'date': self.date.strftime('%Y-%m-%d'),
            'due_date': self.due_date.strftime('%Y-%m-%d'),
            'payment_status': self.payment_status,
            'payment_status_display': self.get_payment_status_display(),
            'notes': self.notes,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'status_color': self.status_color,
            'status_badge_class': self.status_badge_class,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S')
        }


class DebtPayment(models.Model):
    """Qarz to'lov yozuvlari"""
    
    debt_record = models.ForeignKey(
        DebtRecord,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Qarz yozuvi"
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="To'lov summasi"
    )
    
    payment_date = models.DateField(
        default=timezone.now,
        verbose_name="To'lov sanasi"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="To'lov izohi"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Kiritgan xodim"
    )
    
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan sana"
    )
    
    class Meta:
        db_table = 'DebtPayments'
        verbose_name = "Qarz to'lovi"
        verbose_name_plural = "Qarz to'lovlari"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.debt_record} - {self.amount} ({self.payment_date})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Asosiy qarz yozuvini yangilash
        debt = self.debt_record
        debt.paid_amount += self.amount
        debt.save()
