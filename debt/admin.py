from django.contrib import admin
from django.utils.html import format_html
from .models import DebtRecord, DebtPayment


@admin.register(DebtRecord)
class DebtRecordAdmin(admin.ModelAdmin):
    list_display = (
        'organization', 'product_or_service', 'total_amount', 
        'paid_amount', 'remaining_amount', 'payment_status_badge', 
        'date', 'due_date', 'overdue_indicator'
    )
    list_filter = ('payment_status', 'date', 'due_date')
    search_fields = ('organization__name', 'product_or_service', 'notes')
    ordering = ('-date',)
    autocomplete_fields = ['organization']
    readonly_fields = ('remaining_amount', 'payment_status', 'created_date', 'updated_date')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('organization', 'product_or_service')
        }),
        ('Moliyaviy ma\'lumotlar', {
            'fields': ('total_amount', 'paid_amount', 'remaining_amount', 'payment_status')
        }),
        ('Sanalar', {
            'fields': ('date', 'due_date')
        }),
        ('Qo\'shimcha', {
            'fields': ('notes', 'created_by', 'created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_status_badge(self, obj):
        """To'lov holati rangli badge"""
        colors = {
            'UNPAID': 'red',
            'PARTIAL': 'orange',
            'PAID': 'green'
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    
    payment_status_badge.short_description = 'To\'lov holati'
    
    def overdue_indicator(self, obj):
        """Muddati o'tganligini ko'rsatish"""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {} kun kechikkan</span>',
                obj.days_overdue
            )
        return '✓'
    
    overdue_indicator.short_description = 'Muddat'


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ('debt_record', 'amount', 'payment_date', 'created_by', 'created_date')
    list_filter = ('payment_date', 'created_date')
    search_fields = ('debt_record__organization__name', 'notes')
    ordering = ('-payment_date',)
    autocomplete_fields = ['debt_record']
    readonly_fields = ('created_date',)
    
    fieldsets = (
        ('To\'lov ma\'lumotlari', {
            'fields': ('debt_record', 'amount', 'payment_date')
        }),
        ('Qo\'shimcha', {
            'fields': ('notes', 'created_by', 'created_date')
        }),
    )
