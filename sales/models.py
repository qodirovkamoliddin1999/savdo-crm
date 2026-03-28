from django.db import models
import django.utils.timezone
from django.contrib.auth.models import User
from customers.models import Customer
from products.models import Product
from organizations.models import Organization


class Sale(models.Model):
    date_added = models.DateTimeField(
        default=django.utils.timezone.now,
        verbose_name="Sana"
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,   # mijoz ishlatilgan bo'lsa o'chmaydi
        db_column='customer',
        verbose_name="Mijoz",
        null=True,
        blank=True,
        help_text="Mijoz yoki Tashkilotdan biri bo'lishi kerak"
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,  # tashkilot o'chsa null bo'ladi
        db_column='organization',
        verbose_name="Tashkilot",
        null=True,
        blank=True,
        help_text="Agar tashkilotga savdo bo'lsa tanlang"
    )

    employee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # xodim o'chsa null bo'ladi
        db_column='employee',
        verbose_name="Xodim",
        null=True,
        blank=True
    )

    sub_total = models.FloatField(default=0, verbose_name="Oraliq jami")
    grand_total = models.FloatField(default=0, verbose_name="Umumiy jami")
    tax_amount = models.FloatField(default=0, verbose_name="Soliq miqdori")
    tax_percentage = models.FloatField(default=0, verbose_name="Soliq foizi")
    amount_payed = models.FloatField(default=0, verbose_name="To'langan summa")
    amount_change = models.FloatField(default=0, verbose_name="Qaytim")

    class Meta:
        db_table = 'Sales'
        verbose_name = "Savdo"
        verbose_name_plural = "Savdolar"

    def __str__(self):
        return f"Savdo ID: {self.id} | Umumiy jami: {self.grand_total} | Sana: {self.date_added}"

    def sum_items(self):
        return sum(d.quantity for d in self.details.all())


class SaleDetail(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,   # savdo o'chsa detail ham o'chadi
        db_column='sale',
        verbose_name="Savdo",
        related_name="details"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,   # ishlatilgan mahsulot o'chmaydi
        db_column='product',
        verbose_name="Mahsulot"
    )

    price = models.FloatField(verbose_name="Narxi")
    quantity = models.IntegerField(verbose_name="Miqdori")
    total_detail = models.FloatField(verbose_name="Jami")

    class Meta:
        db_table = 'SaleDetails'
        verbose_name = "Savdo tafsiloti"
        verbose_name_plural = "Savdo tafsilotlari"

    def __str__(self):
        return f"Tafsilot ID: {self.id} | Savdo ID: {self.sale.id} | Miqdori: {self.quantity}"
