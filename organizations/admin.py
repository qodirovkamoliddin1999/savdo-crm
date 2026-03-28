from django.contrib import admin
from .models import (
    Organization, Contract, DeliveryNote, DeliveryNoteDetail, 
    Payment, ProductBarcode, EmployeePermission
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'organization_type', 'inn', 'phone', 'is_active')
    list_filter = ('organization_type', 'is_active')
    search_fields = ('name', 'short_name', 'inn', 'phone', 'email')
    ordering = ('short_name',)
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'short_name', 'organization_type')
        }),
        ('Rasmiy ma\'lumotlar', {
            'fields': ('inn', 'oked', 'mfo', 'account_number')
        }),
        ('Manzil va aloqa', {
            'fields': ('legal_address', 'actual_address', 'phone', 'email')
        }),
        ('Mas\'ul shaxslar', {
            'fields': (
                'director_name', 'director_phone',
                'responsible_person', 'responsible_position', 'responsible_phone'
            )
        }),
        ('Qo\'shimcha', {
            'fields': ('notes', 'is_active'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('number', 'organization', 'contract_date', 'start_date', 'end_date', 'status', 'total_amount')
    list_filter = ('status', 'contract_date')
    search_fields = ('number', 'organization__name')
    ordering = ('-contract_date',)
    autocomplete_fields = ['organization']


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ('number', 'organization', 'date', 'total_amount', 'paid_amount', 'payment_status')
    list_filter = ('payment_status', 'date')
    search_fields = ('number', 'organization__name')
    ordering = ('-date',)
    autocomplete_fields = ['organization', 'contract']


@admin.register(DeliveryNoteDetail)
class DeliveryNoteDetailAdmin(admin.ModelAdmin):
    list_display = ('delivery_note', 'product_name', 'quantity', 'price', 'total')
    search_fields = ('product_name', 'serial_number')
    autocomplete_fields = ['delivery_note', 'product']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('delivery_note', 'payment_date', 'amount', 'payment_document')
    list_filter = ('payment_date',)
    search_fields = ('payment_document', 'delivery_note__number')
    ordering = ('-payment_date',)
    autocomplete_fields = ['delivery_note']


@admin.register(ProductBarcode)
class ProductBarcodeAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'product', 'internal_code', 'created_date')
    search_fields = ('barcode', 'internal_code', 'product__name')
    autocomplete_fields = ['product']


@admin.register(EmployeePermission)
class EmployeePermissionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'can_add_sales', 'can_view_reports', 'can_manage_barcodes')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    list_filter = ('can_add_sales', 'can_view_reports')
    
    fieldsets = (
        ('Xodim', {
            'fields': ('employee',)
        }),
        ('Tashkilotlar', {
            'fields': (
                'can_view_organizations', 'can_add_organizations',
                'can_edit_organizations', 'can_delete_organizations'
            )
        }),
        ('Shartnomalar', {
            'fields': (
                'can_view_contracts', 'can_add_contracts',
                'can_edit_contracts', 'can_delete_contracts'
            )
        }),
        ('Yuk xatlari', {
            'fields': (
                'can_view_delivery_notes', 'can_add_delivery_notes',
                'can_delete_delivery_notes', 'can_print_delivery_notes'
            )
        }),
        ('Mahsulotlar', {
            'fields': (
                'can_view_products', 'can_add_products',
                'can_edit_products', 'can_delete_products', 'can_edit_prices'
            )
        }),
        ('To\'lovlar', {
            'fields': (
                'can_view_payments', 'can_add_payments', 'can_delete_payments'
            )
        }),
        ('POS va Savdo', {
            'fields': (
                'can_view_pos', 'can_add_sales', 'can_view_sales',
                'can_edit_sales', 'can_delete_sales'
            )
        }),
        ('Mijozlar', {
            'fields': (
                'can_view_customers', 'can_add_customers',
                'can_edit_customers', 'can_delete_customers'
            )
        }),
        ('Qarz daftari', {
            'fields': (
                'can_view_debt', 'can_add_debt', 'can_edit_debt',
                'can_delete_debt', 'can_add_debt_payments'
            )
        }),
        ('Ombor', {
            'fields': (
                'can_view_warehouse', 'can_receive_warehouse', 'can_manage_barcodes'
            )
        }),
        ('Hisobotlar', {
            'fields': ('can_view_reports', 'can_export_reports')
        }),
        ('Qo\'shimcha', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
