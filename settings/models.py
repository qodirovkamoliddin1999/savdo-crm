from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache


class FieldSetting(models.Model):
    """Har bir model maydonlari uchun sozlamalar"""
    
    FIELD_TYPES = (
        ('CharField', 'Matn'),
        ('TextField', 'Katta matn'),
        ('IntegerField', 'Butun son'),
        ('FloatField', 'O\'nlik son'),
        ('DecimalField', 'Pul'),
        ('BooleanField', 'Ha/Yo\'q'),
        ('DateField', 'Sana'),
        ('DateTimeField', 'Sana va vaqt'),
        ('EmailField', 'Email'),
        ('ForeignKey', 'Bog\'lanish'),
        ('ImageField', 'Rasm'),
        ('FileField', 'Fayl'),
    )
    
    # Model va maydon identifikatori
    app_label = models.CharField(max_length=100, verbose_name="Ilova nomi")
    model_name = models.CharField(max_length=100, verbose_name="Model nomi")
    field_name = models.CharField(max_length=100, verbose_name="Maydon nomi")
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES, verbose_name="Maydon turi")
    
    # Asosiy sozlamalar
    verbose_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="Ko'rinadigan nom")
    help_text = models.TextField(blank=True, null=True, verbose_name="Yordam matni")
    
    # Maydon xususiyatlari
    is_required = models.BooleanField(default=True, verbose_name="Majburiy maydon")
    is_visible = models.BooleanField(default=True, verbose_name="Ko'rinsin")
    is_editable = models.BooleanField(default=True, verbose_name="Tahrirlash mumkin")
    show_in_list = models.BooleanField(default=True, verbose_name="Ro'yxatda ko'rsatish")
    show_in_form = models.BooleanField(default=True, verbose_name="Formada ko'rsatish")
    
    # Qiymat sozlamalari
    default_value = models.TextField(blank=True, null=True, verbose_name="Default qiymat")
    min_length = models.IntegerField(blank=True, null=True, verbose_name="Minimal uzunlik")
    max_length = models.IntegerField(blank=True, null=True, verbose_name="Maksimal uzunlik")
    min_value = models.FloatField(blank=True, null=True, verbose_name="Minimal qiymat")
    max_value = models.FloatField(blank=True, null=True, verbose_name="Maksimal qiymat")
    
    # Tartib
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")
    
    # Qo'shimcha
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        db_table = 'FieldSettings'
        verbose_name = "Maydon sozlamasi"
        verbose_name_plural = "Maydon sozlamalari"
        unique_together = ('app_label', 'model_name', 'field_name')
        ordering = ['app_label', 'model_name', 'order', 'field_name']
    
    def __str__(self):
        return f"{self.app_label}.{self.model_name}.{self.field_name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Cache'ni tozalash
        cache_key = f"field_settings_{self.app_label}_{self.model_name}_{self.field_name}"
        cache.delete(cache_key)
    
    @classmethod
    def get_field_config(cls, app_label, model_name, field_name):
        """Maydon sozlamalarini olish (cache bilan)"""
        cache_key = f"field_settings_{app_label}_{model_name}_{field_name}"
        config = cache.get(cache_key)
        
        if config is None:
            try:
                setting = cls.objects.get(
                    app_label=app_label,
                    model_name=model_name,
                    field_name=field_name,
                    is_active=True
                )
                config = {
                    'is_required': setting.is_required,
                    'is_visible': setting.is_visible,
                    'is_editable': setting.is_editable,
                    'verbose_name': setting.verbose_name,
                    'help_text': setting.help_text,
                    'default_value': setting.default_value,
                    'min_length': setting.min_length,
                    'max_length': setting.max_length,
                    'min_value': setting.min_value,
                    'max_value': setting.max_value,
                }
                cache.set(cache_key, config, 3600)  # 1 soat
            except cls.DoesNotExist:
                config = {}
        
        return config


class ModelSetting(models.Model):
    """Model uchun umumiy sozlamalar"""
    
    # Model identifikatori
    app_label = models.CharField(max_length=100, verbose_name="Ilova nomi")
    model_name = models.CharField(max_length=100, verbose_name="Model nomi")
    
    # Ko'rinish sozlamalari
    verbose_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="Model nomi (birlik)")
    verbose_name_plural = models.CharField(max_length=256, blank=True, null=True, verbose_name="Model nomi (ko'plik)")
    
    # Admin panel sozlamalari
    list_per_page = models.IntegerField(default=20, verbose_name="Sahifadagi yozuvlar soni")
    list_display_fields = models.TextField(blank=True, null=True, verbose_name="Ro'yxatda ko'rsatiladigan maydonlar (vergul bilan)")
    search_fields = models.TextField(blank=True, null=True, verbose_name="Qidiruv maydonlari (vergul bilan)")
    list_filter_fields = models.TextField(blank=True, null=True, verbose_name="Filter maydonlari (vergul bilan)")
    ordering_fields = models.TextField(blank=True, null=True, verbose_name="Saralash maydonlari (vergul bilan)")
    readonly_fields = models.TextField(blank=True, null=True, verbose_name="Faqat o'qish uchun maydonlar (vergul bilan)")
    
    # Ruxsatlar
    allow_add = models.BooleanField(default=True, verbose_name="Qo'shish ruxsati")
    allow_edit = models.BooleanField(default=True, verbose_name="Tahrirlash ruxsati")
    allow_delete = models.BooleanField(default=True, verbose_name="O'chirish ruxsati")
    allow_export = models.BooleanField(default=True, verbose_name="Eksport ruxsati")
    
    # Qo'shimcha
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        db_table = 'ModelSettings'
        verbose_name = "Model sozlamasi"
        verbose_name_plural = "Model sozlamalari"
        unique_together = ('app_label', 'model_name')
        ordering = ['app_label', 'model_name']
    
    def __str__(self):
        return f"{self.app_label}.{self.model_name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Cache'ni tozalash
        cache_key = f"model_settings_{self.app_label}_{self.model_name}"
        cache.delete(cache_key)


class SystemSetting(models.Model):
    """Tizim umumiy sozlamalari"""
    
    SETTING_TYPES = (
        ('STRING', 'Matn'),
        ('INTEGER', 'Butun son'),
        ('FLOAT', 'O\'nlik son'),
        ('BOOLEAN', 'Ha/Yo\'q'),
        ('JSON', 'JSON'),
    )
    
    # Sozlama identifikatori
    key = models.CharField(max_length=100, unique=True, verbose_name="Kalit")
    name = models.CharField(max_length=256, verbose_name="Nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    
    # Qiymat
    value_type = models.CharField(max_length=20, choices=SETTING_TYPES, verbose_name="Qiymat turi")
    value = models.TextField(verbose_name="Qiymat")
    default_value = models.TextField(blank=True, null=True, verbose_name="Default qiymat")
    
    # Kategoriya
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kategoriya")
    
    # Qo'shimcha
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_editable = models.BooleanField(default=True, verbose_name="Tahrirlash mumkin")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        db_table = 'SystemSettings'
        verbose_name = "Tizim sozlamasi"
        verbose_name_plural = "Tizim sozlamalari"
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Cache'ni tozalash
        cache_key = f"system_setting_{self.key}"
        cache.delete(cache_key)
    
    @classmethod
    def get_value(cls, key, default=None):
        """Sozlama qiymatini olish (cache bilan)"""
        cache_key = f"system_setting_{key}"
        value = cache.get(cache_key)
        
        if value is None:
            try:
                setting = cls.objects.get(key=key, is_active=True)
                value = setting.value
                cache.set(cache_key, value, 3600)  # 1 soat
            except cls.DoesNotExist:
                value = default
        
        return value
    
    @classmethod
    def set_value(cls, key, value):
        """Sozlama qiymatini o'rnatish"""
        setting, created = cls.objects.get_or_create(key=key)
        setting.value = str(value)
        setting.save()
        return setting
