from django.core.management.base import BaseCommand
from django.apps import apps
from settings.models import FieldSetting, ModelSetting, SystemSetting


class Command(BaseCommand):
    help = 'Barcha modellar uchun sozlamalarni avtomatik yaratish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fields',
            action='store_true',
            help='Maydon sozlamalarini yaratish',
        )
        parser.add_argument(
            '--models',
            action='store_true',
            help='Model sozlamalarini yaratish',
        )
        parser.add_argument(
            '--system',
            action='store_true',
            help='Tizim sozlamalarini yaratish',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Barcha sozlamalarni yaratish',
        )

    def handle(self, *args, **options):
        if options['all'] or (not options['fields'] and not options['models'] and not options['system']):
            self.populate_all()
        else:
            if options['fields']:
                self.populate_field_settings()
            if options['models']:
                self.populate_model_settings()
            if options['system']:
                self.populate_system_settings()

    def populate_all(self):
        self.stdout.write(self.style.SUCCESS('Barcha sozlamalarni yaratish boshlandi...'))
        self.populate_field_settings()
        self.populate_model_settings()
        self.populate_system_settings()
        self.stdout.write(self.style.SUCCESS('Barcha sozlamalar yaratildi!'))

    def populate_field_settings(self):
        """Maydon sozlamalarini yaratish"""
        self.stdout.write('Maydon sozlamalarini yaratish...')
        created_count = 0
        updated_count = 0
        
        # LOCAL_APPS dan modellarni olish
        local_apps = ['customers', 'pos', 'products', 'sales', 'organizations', 'debt']
        
        for app_label in local_apps:
            try:
                app_models = apps.get_app_config(app_label).get_models()
                
                for model in app_models:
                    model_name = model.__name__
                    
                    # Har bir maydon uchun sozlama yaratish
                    for field in model._meta.get_fields():
                        if hasattr(field, 'name') and not field.name.endswith('_ptr'):
                            field_type = field.__class__.__name__
                            
                            # Maydon sozlamasini yaratish yoki yangilash
                            field_setting, created = FieldSetting.objects.get_or_create(
                                app_label=app_label,
                                model_name=model_name,
                                field_name=field.name,
                                defaults={
                                    'field_type': field_type,
                                    'verbose_name': getattr(field, 'verbose_name', field.name),
                                    'help_text': getattr(field, 'help_text', ''),
                                    'is_required': not getattr(field, 'blank', True) and not getattr(field, 'null', True),
                                    'is_visible': True,
                                    'is_editable': getattr(field, 'editable', True),
                                }
                            )
                            
                            if created:
                                created_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✓ {app_label}.{model_name}.{field.name}')
                                )
                            else:
                                updated_count += 1
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Xatolik {app_label} ni qayta ishlashda: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} ta maydon sozlamasi yaratildi, {updated_count} ta mavjud.')
        )

    def populate_model_settings(self):
        """Model sozlamalarini yaratish"""
        self.stdout.write('Model sozlamalarini yaratish...')
        created_count = 0
        
        # LOCAL_APPS dan modellarni olish
        local_apps = ['customers', 'pos', 'products', 'sales', 'organizations', 'debt']
        
        for app_label in local_apps:
            try:
                app_models = apps.get_app_config(app_label).get_models()
                
                for model in app_models:
                    model_name = model.__name__
                    
                    # Model sozlamasini yaratish
                    model_setting, created = ModelSetting.objects.get_or_create(
                        app_label=app_label,
                        model_name=model_name,
                        defaults={
                            'verbose_name': getattr(model._meta, 'verbose_name', model_name),
                            'verbose_name_plural': getattr(model._meta, 'verbose_name_plural', model_name),
                            'list_per_page': 20,
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ {app_label}.{model_name}')
                        )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Xatolik {app_label} ni qayta ishlashda: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} ta model sozlamasi yaratildi.')
        )

    def populate_system_settings(self):
        """Tizim sozlamalarini yaratish"""
        self.stdout.write('Tizim sozlamalarini yaratish...')
        
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
                'key': 'CURRENCY_SYMBOL',
                'name': 'Valyuta belgisi',
                'value_type': 'STRING',
                'value': 'so\'m',
                'category': 'Moliya',
                'description': 'Valyuta belgisi'
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
            {
                'key': 'TAX_PERCENTAGE',
                'name': 'Standart soliq foizi',
                'value_type': 'FLOAT',
                'value': '12.0',
                'category': 'Moliya',
                'description': 'Savdolar uchun standart soliq foizi'
            },
            {
                'key': 'LOW_STOCK_ALERT',
                'name': 'Kam qoldi ogohlantiruvi',
                'value_type': 'INTEGER',
                'value': '10',
                'category': 'Ombor',
                'description': 'Omborda mahsulot qolganda ogohlantirish miqdori'
            },
        ]
        
        created_count = 0
        for setting_data in default_settings:
            setting, created = SystemSetting.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {setting_data["key"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} ta tizim sozlamasi yaratildi.')
        )
