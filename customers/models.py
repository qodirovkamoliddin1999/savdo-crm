from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=256, verbose_name="Ism")
    last_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="Familiya")
    address = models.TextField(max_length=256, blank=True, null=True, verbose_name="Manzil")
    email = models.EmailField(max_length=256, blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Telefon")

    class Meta:
        db_table = 'Customers'
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def to_select2(self):
        item = {
            "label": self.get_full_name(),
            "value": self.id
        }
        return item
