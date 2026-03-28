from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.serializers.json import DjangoJSONEncoder
import json
import datetime
from decimal import Decimal

from .models import DebtRecord, DebtPayment
from organizations.models import Organization


@login_required(login_url="/accounts/login/")
def debt_dashboard_view(request):
    """Qarz daftari asosiy sahifasi"""
    
    # Statistika
    total_debt = DebtRecord.objects.aggregate(
        total=Sum('remaining_amount')
    )['total'] or 0
    
    overdue_debt = DebtRecord.objects.filter(
        due_date__lt=timezone.now().date(),
        payment_status__in=['UNPAID', 'PARTIAL']
    ).aggregate(
        total=Sum('remaining_amount')
    )['total'] or 0
    
    # Statuslar bo'yicha statistika
    status_stats = DebtRecord.objects.values('payment_status').annotate(
        count=Count('id'),
        total=Sum('remaining_amount')
    ).order_by('payment_status')
    
    # Oxirgi qarz yozuvlari
    recent_debts = DebtRecord.objects.select_related('organization').order_by('-created_date')[:10]
    
    context = {
        'active_icon': 'debt',
        'total_debt': total_debt,
        'overdue_debt': overdue_debt,
        'status_stats': status_stats,
        'recent_debts': recent_debts,
    }
    
    return render(request, "debt/debt_dashboard.html", context=context)


@login_required(login_url="/accounts/login/")
def debt_list_view(request):
    """Qarzlar ro'yxati"""
    
    # Filter parametrlari
    search_query = request.GET.get('search', '')
    organization_filter = request.GET.get('organization', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    min_amount = request.GET.get('min_amount', '')
    max_amount = request.GET.get('max_amount', '')
    overdue_only = request.GET.get('overdue_only', '') == 'true'
    
    # Asosiy so'rov
    debts = DebtRecord.objects.select_related('organization').all()
    
    # Qidiruv
    if search_query:
        debts = debts.filter(
            Q(organization__name__icontains=search_query) |
            Q(product_or_service__icontains=search_query)
        )
    
    # Tashkilot filteri
    if organization_filter:
        debts = debts.filter(organization_id=organization_filter)
    
    # Status filteri
    if status_filter:
        debts = debts.filter(payment_status=status_filter)
    
    # Sana filteri
    if date_from:
        debts = debts.filter(date__gte=date_from)
    if date_to:
        debts = debts.filter(date__lte=date_to)
    
    # Summa filteri
    if min_amount:
        debts = debts.filter(total_amount__gte=min_amount)
    if max_amount:
        debts = debts.filter(total_amount__lte=max_amount)
    
    # Faqat muddati o'tganlar
    if overdue_only:
        debts = debts.filter(
            due_date__lt=timezone.now().date(),
            payment_status__in=['UNPAID', 'PARTIAL']
        )
    
    # Tartiblash
    sort_by = request.GET.get('sort', '-date')
    if sort_by.startswith('-'):
        debts = debts.order_by(sort_by)
    else:
        debts = debts.order_by(f'-{sort_by}')
    
    # Pagination
    paginator = Paginator(debts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Tashkilotlar ro'yxati (filter uchun)
    organizations = Organization.objects.filter(
        debt_records__isnull=False
    ).distinct().order_by('name')
    
    context = {
        'active_icon': 'debt',
        'page_obj': page_obj,
        'organizations': organizations,
        'search_query': search_query,
        'organization_filter': organization_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'min_amount': min_amount,
        'max_amount': max_amount,
        'overdue_only': overdue_only,
        'sort_by': sort_by,
    }
    
    return render(request, "debt/debt_list.html", context=context)


@login_required(login_url="/accounts/login/")
def debt_add_view(request):
    """Yangi qarz qo'shish"""
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Tashkilotni tekshirish
            organization = get_object_or_404(Organization, id=data['organization'])
            
            # Qarz yozuvini yaratish
            debt = DebtRecord.objects.create(
                organization=organization,
                product_or_service=data['product_or_service'],
                total_amount=data['total_amount'],
                paid_amount=data.get('paid_amount', 0),
                date=data['date'] or timezone.now().date(),
                due_date=data['due_date'],
                notes=data.get('notes', ''),
                created_by=request.user
            )
            
            messages.success(request, "Qarz yozuvi muvaffaqiyatli yaratildi!", extra_tags="success")
            return redirect('debt:debt_list')
            
        except Exception as e:
            messages.error(request, 'Xatolik yuz berdi!', extra_tags="danger")
            print(f"Debt add error: {e}")
    
    context = {
        'active_icon': 'debt',
        'organizations': Organization.objects.all().order_by('name'),
    }
    
    return render(request, "debt/debt_add.html", context=context)


@login_required(login_url="/accounts/login/")
def debt_detail_view(request, debt_id):
    """Qarz yozuvi tafsilotlari"""
    
    debt = get_object_or_404(DebtRecord, id=debt_id)
    payments = debt.payments.all().order_by('-payment_date')
    
    context = {
        'active_icon': 'debt',
        'debt': debt,
        'payments': payments,
    }
    
    return render(request, "debt/debt_detail.html", context=context)


@login_required(login_url="/accounts/login/")
def debt_update_view(request, debt_id):
    """Qarz yozuvini tahrirlash"""
    
    debt = get_object_or_404(DebtRecord, id=debt_id)
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Ma'lumotlarni yangilash
            debt.organization = get_object_or_404(Organization, id=data['organization'])
            debt.product_or_service = data['product_or_service']
            debt.total_amount = data['total_amount']
            debt.paid_amount = data.get('paid_amount', 0)
            debt.date = data['date'] or timezone.now().date()
            debt.due_date = data['due_date']
            debt.notes = data.get('notes', '')
            
            debt.save()
            
            messages.success(request, "Qarz yozuvi muvaffaqiyatli yangilandi!", extra_tags="success")
            return redirect('debt:debt_detail', debt_id=debt.id)
            
        except Exception as e:
            messages.error(request, 'Xatolik yuz berdi!', extra_tags="danger")
            print(f"Debt update error: {e}")
    
    context = {
        'active_icon': 'debt',
        'debt': debt,
        'organizations': Organization.objects.all().order_by('name'),
    }
    
    return render(request, "debt/debt_update.html", context=context)


@login_required(login_url="/accounts/login/")
def debt_delete_view(request, debt_id):
    """Qarz yozuvini o'chirish"""
    
    debt = get_object_or_404(DebtRecord, id=debt_id)
    
    if request.method == 'POST':
        try:
            debt.delete()
            messages.success(request, "Qarz yozuvi o'chirildi!", extra_tags="success")
            return redirect('debt:debt_list')
            
        except Exception as e:
            messages.error(request, 'Xatolik yuz berdi!', extra_tags="danger")
            print(f"Debt delete error: {e}")
    
    context = {
        'active_icon': 'debt',
        'debt': debt,
    }
    
    return render(request, "debt/debt_delete.html", context=context)


# ==================== AJAX VIEWS ====================

@login_required(login_url="/accounts/login/")
def ajax_organization_search(request):
    """Tashkilotlarni qidirish (AJAX)"""
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    organizations = Organization.objects.filter(
        name__icontains=query
    ).order_by('name')[:10]
    
    results = []
    for org in organizations:
        results.append({
            'id': org.id,
            'text': org.name,
            'description': org.address or ''
        })
    
    return JsonResponse({'results': results})


@login_required(login_url="/accounts/login/")
def ajax_debt_list(request):
    """Qarzlar ro'yxati (AJAX)"""
    
    # Filter parametrlari
    search_query = request.GET.get('search', '')
    organization_filter = request.GET.get('organization', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    min_amount = request.GET.get('min_amount', '')
    max_amount = request.GET.get('max_amount', '')
    overdue_only = request.GET.get('overdue_only', '') == 'true'
    
    # Asosiy so'rov
    debts = DebtRecord.objects.select_related('organization').all()
    
    # Filterlar
    if search_query:
        debts = debts.filter(
            Q(organization__name__icontains=search_query) |
            Q(product_or_service__icontains=search_query)
        )
    
    if organization_filter:
        debts = debts.filter(organization_id=organization_filter)
    
    if status_filter:
        debts = debts.filter(payment_status=status_filter)
    
    if date_from:
        debts = debts.filter(date__gte=date_from)
    if date_to:
        debts = debts.filter(date__lte=date_to)
    
    if min_amount:
        debts = debts.filter(total_amount__gte=min_amount)
    if max_amount:
        debts = debts.filter(total_amount__lte=max_amount)
    
    if overdue_only:
        debts = debts.filter(
            due_date__lt=timezone.now().date(),
            payment_status__in=['UNPAID', 'PARTIAL']
        )
    
    # Tartiblash
    sort_by = request.GET.get('sort', '-date')
    if sort_by.startswith('-'):
        debts = debts.order_by(sort_by)
    else:
        debts = debts.order_by(f'-{sort_by}')
    
    # JSON formatga o'tkazish
    data = []
    for debt in debts:
        data.append(debt.to_json())
    
    return JsonResponse({'data': data})


@login_required(login_url="/accounts/login/")
@require_POST
def ajax_add_payment(request, debt_id):
    """To'lov qo'shish (AJAX)"""
    
    try:
        debt = get_object_or_404(DebtRecord, id=debt_id)
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        notes = request.POST.get('notes', '')
        
        # To'lov yozuvini yaratish
        payment = DebtPayment.objects.create(
            debt_record=debt,
            amount=amount,
            payment_date=payment_date or timezone.now().date(),
            notes=notes,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'To\'lov muvaffaqiyatli qo\'shildi!',
            'debt': debt.to_json()
        })
        
    except Exception as e:
        print(f"Payment add error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Xatolik yuz berdi!'
        })


@login_required(login_url="/accounts/login/")
def ajax_debt_statistics(request):
    """Statistika (AJAX)"""
    
    # Umumiy statistika
    total_debt = DebtRecord.objects.aggregate(
        total=Sum('remaining_amount')
    )['total'] or 0
    
    overdue_debt = DebtRecord.objects.filter(
        due_date__lt=timezone.now().date(),
        payment_status__in=['UNPAID', 'PARTIAL']
    ).aggregate(
        total=Sum('remaining_amount')
    )['total'] or 0
    
    # Statuslar bo'yicha
    status_stats = DebtRecord.objects.values('payment_status').annotate(
        count=Count('id'),
        total=Sum('remaining_amount')
    ).order_by('payment_status')
    
    # Oxirgi 7 kun statistikasi
    seven_days_ago = timezone.now().date() - datetime.timedelta(days=7)
    recent_debts = DebtRecord.objects.filter(
        date__gte=seven_days_ago
    ).aggregate(
        count=Count('id'),
        total=Sum('total_amount')
    )
    
    data = {
        'total_debt': float(total_debt),
        'overdue_debt': float(overdue_debt),
        'status_stats': list(status_stats),
        'recent_debts': {
            'count': recent_debts['count'] or 0,
            'total': float(recent_debts['total'] or 0)
        }
    }
    
    return JsonResponse(data)
