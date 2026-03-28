from django.db import models
from django.forms import model_to_dict


class Category(models.Model):
    STATUS_CHOICES = (  # new
        ("ACTIVE", "Faol"),
        ("INACTIVE", "Nofaol")
    )

    name = models.CharField(max_length=256, verbose_name="Nomi")
    description = models.TextField(max_length=256, verbose_name="Tavsif")
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=100,
        verbose_name="Kategoriya holati",
    )

    class Meta:
        # Table's name
        db_table = "Category"
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    STATUS_CHOICES = (  # new
        ("ACTIVE", "Faol"),
        ("INACTIVE", "Nofaol")
    )

    name = models.CharField(max_length=256, verbose_name="Nomi")
    description = models.TextField(max_length=256, verbose_name="Tavsif")
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=100,
        verbose_name="Mahsulot holati",
    )
    category = models.ForeignKey(
        Category, related_name="category", on_delete=models.CASCADE, db_column='category', verbose_name="Kategoriya")

    price = models.FloatField(default=0, verbose_name="Narxi")
    quantity = models.IntegerField(default=0, verbose_name="Ombordagi miqdori")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Rasm")
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True, verbose_name="Shtrix-kod")

    class Meta:
        # Table's name
        db_table = "Product"
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self) -> str:
        return self.name

    def to_json(self):
        item = model_to_dict(self)
        item['id'] = self.id
        item['text'] = self.name
        item['category'] = self.category.name
        item['quantity'] = 1
        item['total_product'] = 0
        return item
