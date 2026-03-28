"""
Sozlamalar bilan ishlash uchun yordamchi funksiyalar
"""
from django import forms
from .models import FieldSetting, ModelSetting, SystemSetting


class DynamicFormMixin:
    """Form maydonlarini dinamik sozlamalar asosida o'zgartirish"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_field_settings()
    
    def apply_field_settings(self):
        """Maydon sozlamalarini qo'llash"""
        if not hasattr(self, 'Meta') or not hasattr(self.Meta, 'model'):
            return
        
        model = self.Meta.model
        app_label = model._meta.app_label
        model_name = model.__name__
        
        for field_name, field in self.fields.items():
            # Maydon sozlamasini olish
            config = FieldSetting.get_field_config(app_label, model_name, field_name)
            
            if config:
                # Majburiylikni o'zgartirish
                if 'is_required' in config:
                    field.required = config['is_required']
                
                # Ko'rinadigan nomni o'zgartirish
                if config.get('verbose_name'):
                    field.label = config['verbose_name']
                
                # Yordam matnini o'zgartirish
                if config.get('help_text'):
                    field.help_text = config['help_text']
                
                # Default qiymatni o'rnatish
                if config.get('default_value') and not self.instance.pk:
                    field.initial = config['default_value']
                
                # Maydonni yashirish
                if not config.get('is_visible', True):
                    field.widget = forms.HiddenInput()
                
                # Tahrirlash mumkin emasligini belgilash
                if not config.get('is_editable', True):
                    field.disabled = True
                
                # Maksimal uzunlikni o'rnatish
                if config.get('max_length') and hasattr(field, 'max_length'):
                    field.max_length = config['max_length']
                
                # Min/Max qiymatlarni o'rnatish
                if isinstance(field, (forms.IntegerField, forms.FloatField, forms.DecimalField)):
                    if config.get('min_value') is not None:
                        field.min_value = config['min_value']
                        field.widget.attrs['min'] = config['min_value']
                    
                    if config.get('max_value') is not None:
                        field.max_value = config['max_value']
                        field.widget.attrs['max'] = config['max_value']


class DynamicModelAdminMixin:
    """ModelAdmin ni dinamik sozlamalar bilan kengaytirish"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_model_settings()
    
    def apply_model_settings(self):
        """Model sozlamalarini qo'llash"""
        if hasattr(self, 'model'):
            app_label = self.model._meta.app_label
            model_name = self.model.__name__
            
            try:
                setting = ModelSetting.objects.get(
                    app_label=app_label,
                    model_name=model_name,
                    is_active=True
                )
                
                # Sahifadagi elementlar sonini o'rnatish
                if setting.list_per_page:
                    self.list_per_page = setting.list_per_page
                
                # List display maydonlarini o'rnatish
                if setting.list_display_fields:
                    fields = [f.strip() for f in setting.list_display_fields.split(',')]
                    self.list_display = fields
                
                # Qidiruv maydonlarini o'rnatish
                if setting.search_fields:
                    fields = [f.strip() for f in setting.search_fields.split(',')]
                    self.search_fields = fields
                
                # Filter maydonlarini o'rnatish
                if setting.list_filter_fields:
                    fields = [f.strip() for f in setting.list_filter_fields.split(',')]
                    self.list_filter = fields
                
                # Saralash maydonlarini o'rnatish
                if setting.ordering_fields:
                    fields = [f.strip() for f in setting.ordering_fields.split(',')]
                    self.ordering = fields
                
                # Readonly maydonlarini o'rnatish
                if setting.readonly_fields:
                    fields = [f.strip() for f in setting.readonly_fields.split(',')]
                    self.readonly_fields = fields
                
            except ModelSetting.DoesNotExist:
                pass
    
    def has_add_permission(self, request):
        """Qo'shish ruxsatini tekshirish"""
        base_permission = super().has_add_permission(request)
        if not base_permission:
            return False
        
        try:
            setting = ModelSetting.objects.get(
                app_label=self.model._meta.app_label,
                model_name=self.model.__name__,
                is_active=True
            )
            return setting.allow_add
        except ModelSetting.DoesNotExist:
            return True
    
    def has_change_permission(self, request, obj=None):
        """Tahrirlash ruxsatini tekshirish"""
        base_permission = super().has_change_permission(request, obj)
        if not base_permission:
            return False
        
        try:
            setting = ModelSetting.objects.get(
                app_label=self.model._meta.app_label,
                model_name=self.model.__name__,
                is_active=True
            )
            return setting.allow_edit
        except ModelSetting.DoesNotExist:
            return True
    
    def has_delete_permission(self, request, obj=None):
        """O'chirish ruxsatini tekshirish"""
        base_permission = super().has_delete_permission(request, obj)
        if not base_permission:
            return False
        
        try:
            setting = ModelSetting.objects.get(
                app_label=self.model._meta.app_label,
                model_name=self.model.__name__,
                is_active=True
            )
            return setting.allow_delete
        except ModelSetting.DoesNotExist:
            return True


def get_system_setting(key, default=None):
    """Tizim sozlamasini olish"""
    return SystemSetting.get_value(key, default)


def set_system_setting(key, value):
    """Tizim sozlamasini o'rnatish"""
    return SystemSetting.set_value(key, value)


def get_field_setting(app_label, model_name, field_name):
    """Maydon sozlamasini olish"""
    return FieldSetting.get_field_config(app_label, model_name, field_name)


def validate_field_value(app_label, model_name, field_name, value):
    """Maydon qiymatini sozlamalar asosida tekshirish"""
    config = FieldSetting.get_field_config(app_label, model_name, field_name)
    
    if not config:
        return True, None
    
    # Majburiy maydonni tekshirish
    if config.get('is_required') and not value:
        return False, f"{field_name} maydoni majburiy"
    
    # Matn uzunligini tekshirish
    if isinstance(value, str):
        if config.get('min_length') and len(value) < config['min_length']:
            return False, f"{field_name} kamida {config['min_length']} belgidan iborat bo'lishi kerak"
        
        if config.get('max_length') and len(value) > config['max_length']:
            return False, f"{field_name} maksimal {config['max_length']} belgidan iborat bo'lishi kerak"
    
    # Raqam qiymatlarini tekshirish
    if isinstance(value, (int, float)):
        if config.get('min_value') is not None and value < config['min_value']:
            return False, f"{field_name} kamida {config['min_value']} bo'lishi kerak"
        
        if config.get('max_value') is not None and value > config['max_value']:
            return False, f"{field_name} maksimal {config['max_value']} bo'lishi kerak"
    
    return True, None
