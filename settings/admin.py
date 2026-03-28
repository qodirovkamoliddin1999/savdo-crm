from django.contrib import admin
from django.apps import apps
from .models import FieldSetting, ModelSetting, SystemSetting


@admin.register(FieldSetting)
class FieldSettingAdmin(admin.ModelAdmin):
    list_display = (
        'field_name', 'model_name', 'app_label', 'field_type', 
        'is_required', 'is_visible', 'is_editable', 'is_active'
    )
    list_filter = ('app_label', 'model_name', 'field_type', 'is_required', 'is_visible', 'is_active')
    search_fields = ('field_name', 'model_name', 'app_label', 'verbose_name')
    ordering = ('app_label', 'model_name', 'order', 'field_name')
    list_editable = ('is_required', 'is_visible', 'is_editable', 'is_active')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('app_label', 'model_name', 'field_name', 'field_type')
        }),
        ('Ko\'rinish', {
            'fields': ('verbose_name', 'help_text', 'order')
        }),
        ('Xususiyatlar', {
            'fields': (
                'is_required', 'is_visible', 'is_editable', 
                'show_in_list', 'show_in_form'
            )
        }),
        ('Qiymat sozlamalari', {
            'fields': (
                'default_value', 'min_length', 'max_length', 
                'min_value', 'max_value'
            ),
            'classes': ('collapse',)
        }),
        ('Qo\'shimcha', {
            'fields': ('is_active', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(ModelSetting)
class ModelSettingAdmin(admin.ModelAdmin):
    list_display = (
        'model_name', 'app_label', 'list_per_page', 
        'allow_add', 'allow_edit', 'allow_delete', 'is_active'
    )
    list_filter = ('app_label', 'allow_add', 'allow_edit', 'allow_delete', 'is_active')
    search_fields = ('model_name', 'app_label', 'verbose_name')
    ordering = ('app_label', 'model_name')
    list_editable = ('allow_add', 'allow_edit', 'allow_delete', 'is_active')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('app_label', 'model_name')
        }),
        ('Ko\'rinish', {
            'fields': ('verbose_name', 'verbose_name_plural')
        }),
        ('Admin panel sozlamalari', {
            'fields': (
                'list_per_page', 'list_display_fields', 'search_fields',
                'list_filter_fields', 'ordering_fields', 'readonly_fields'
            )
        }),
        ('Ruxsatlar', {
            'fields': ('allow_add', 'allow_edit', 'allow_delete', 'allow_export')
        }),
        ('Qo\'shimcha', {
            'fields': ('is_active', 'notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'value_type', 'category', 'is_active', 'is_editable')
    list_filter = ('category', 'value_type', 'is_active', 'is_editable')
    search_fields = ('key', 'name', 'description')
    ordering = ('category', 'name')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('key', 'name', 'description', 'category')
        }),
        ('Qiymat', {
            'fields': ('value_type', 'value', 'default_value')
        }),
        ('Sozlamalar', {
            'fields': ('is_active', 'is_editable')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Tahrirlash mumkin bo'lmagan maydonlarni readonly qilish"""
        if obj and not obj.is_editable:
            return ['key', 'value_type']
        return []


# Auto-populate field settings for existing models
class SettingsAutoPopulate:
    """Mavjud modellar uchun avtomatik sozlamalar yaratish"""
    
    @staticmethod
    def populate_field_settings():
        """Barcha modellar uchun maydon sozlamalarini yaratish"""
        created_count = 0
        
        # LOCAL_APPS dan modellarni olish
        local_apps = ['customers', 'pos', 'products', 'sales', 'organizations', 'debt']
        
        for app_label in local_apps:
            try:
                app_models = apps.get_app_config(app_label).get_models()
                
                for model in app_models:
                    model_name = model.__name__
                    
                    # Model sozlamasini yaratish
                    ModelSetting.objects.get_or_create(
                        app_label=app_label,
                        model_name=model_name,
                        defaults={
                            'verbose_name': getattr(model._meta, 'verbose_name', model_name),
                            'verbose_name_plural': getattr(model._meta, 'verbose_name_plural', model_name),
                            'list_per_page': 20,
                        }
                    )
                    
                    # Har bir maydon uchun sozlama yaratish
                    for field in model._meta.get_fields():
                        if hasattr(field, 'name'):
                            field_type = field.__class__.__name__
                            
                            # Maydon sozlamasini yaratish
                            field_setting, created = FieldSetting.objects.get_or_create(
                                app_label=app_label,
                                model_name=model_name,
                                field_name=field.name,
                                defaults={
                                    'field_type': field_type,
                                    'verbose_name': getattr(field, 'verbose_name', field.name),
                                    'help_text': getattr(field, 'help_text', ''),
                                    'is_required': not getattr(field, 'blank', True),
                                    'is_visible': True,
                                    'is_editable': getattr(field, 'editable', True),
                                }
                            )
                            
                            if created:
                                created_count += 1
            
            except Exception as e:
                print(f"Xatolik {app_label} ni qayta ishlashda: {e}")
        
        return created_count
    
    @staticmethod
    def populate_system_settings():
        """Tizim sozlamalarini yaratish"""
        default_settings = [
            {
                'key': 'LANGUAGE_CODE',
                'name': 'Til',
                'value_type': 'STRING',
                'value': 'uz',
                'category': 'Til va mintaqa',
                'description': 'Tizim tili (uz, ru, en)'
            },
            {
                'key': 'TIME_ZONE',
                'name': 'Vaqt mintaqasi',
                'value_type': 'STRING',
                'value': 'Asia/Tashkent',
                'category': 'Til va mintaqa',
                'description': 'Tizim vaqt mintaqasi'
            },
            {
                'key': 'CURRENCY',
                'name': 'Valyuta',
                'value_type': 'STRING',
                'value': 'UZS',
                'category': 'Moliya',
                'description': 'Asosiy valyuta (UZS, USD, EUR)'
            },
            {
                'key': 'DATE_FORMAT',
                'name': 'Sana formati',
                'value_type': 'STRING',
                'value': 'DD.MM.YYYY',
                'category': 'Til va mintaqa',
                'description': 'Sana ko\'rinish formati'
            },
            {
                'key': 'DECIMAL_PLACES',
                'name': 'Kasr raqamlar soni',
                'value_type': 'INTEGER',
                'value': '2',
                'category': 'Moliya',
                'description': 'Pul summalari uchun kasr raqamlar soni'
            },
            {
                'key': 'SESSION_TIMEOUT',
                'name': 'Sessiya muddati (daqiqa)',
                'value_type': 'INTEGER',
                'value': '60',
                'category': 'Xavfsizlik',
                'description': 'Foydalanuvchi sessiyasi muddati (daqiqalarda)'
            },
            {
                'key': 'ITEMS_PER_PAGE',
                'name': 'Sahifadagi elementlar soni',
                'value_type': 'INTEGER',
                'value': '20',
                'category': 'Ko\'rinish',
                'description': 'Ro\'yxatlarda bitta sahifada ko\'rsatiladigan elementlar soni'
            },
            {
                'key': 'ENABLE_NOTIFICATIONS',
                'name': 'Bildirishnomalarni yoqish',
                'value_type': 'BOOLEAN',
                'value': 'True',
                'category': 'Bildirishnomalar',
                'description': 'Tizim bildirishnomalarini yoqish/o\'chirish'
            },
        ]
        
        created_count = 0
        for setting_data in default_settings:
            _, created = SystemSetting.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            if created:
                created_count += 1
        
        return created_count
