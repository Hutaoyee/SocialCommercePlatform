from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
import json

from .models import Order, OrderItem, RefundRequest, OrderItemReview
from user.models import UserProduct


def is_staff(user):
    """检查用户是否为管理员"""
    return user.is_authenticated and user.is_staff


# ==================== 订单管理 ====================

@login_required
@user_passes_test(is_staff)
def order_management(request):
    """订单管理主页 - 订单列表"""
    orders = Order.objects.all().select_related('user').prefetch_related('items').order_by('-created_at')
    
    # 搜索过滤
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__username__icontains=search) |
            Q(shipping_address__icontains=search)
        )
    
    # 状态过滤
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    
    # 日期范围过滤
    date_range = request.GET.get('date_range', '')
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            orders = orders.filter(created_at__date=today)
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            orders = orders.filter(created_at__date__gte=week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            orders = orders.filter(created_at__date__gte=month_ago)
    
    # 统计数据
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'paid_orders': Order.objects.filter(status='paid').count(),
        'shipped_orders': Order.objects.filter(status='shipped').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'cancelled_orders': Order.objects.filter(status='cancelled').count(),
        'today_orders': Order.objects.filter(created_at__date=timezone.now().date()).count(),
        'total_amount': Order.objects.filter(status__in=['paid', 'shipped', 'completed']).aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
    }
    
    context = {
        'orders': orders,
        'stats': stats,
        'search': search,
        'current_status': status,
        'current_date_range': date_range,
        'status_choices': Order.ORDER_STATUS_CHOICES,
    }
    
    return render(request, 'shopping/order_management.html', context)


@login_required
@user_passes_test(is_staff)
def order_detail(request, order_id):
    """订单详情页"""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related(
            'items__sku__spu',
            'items__review'
        ),
        id=order_id
    )
    
    # 获取退款申请
    refund_request = None
    if hasattr(order, 'refund_request'):
        refund_request = order.refund_request
    
    context = {
        'order': order,
        'refund_request': refund_request,
    }
    
    return render(request, 'shopping/order_detail.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def order_update_status(request, order_id):
    """更新订单状态"""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    if new_status not in dict(Order.ORDER_STATUS_CHOICES):
        messages.error(request, '无效的订单状态')
        return redirect('shopping_manage:order_detail', order_id=order_id)
    
    old_status = order.status
    order.status = new_status
    order.save()
    
    messages.success(request, f'订单状态已从 {order.get_status_display()} 更新为 {dict(Order.ORDER_STATUS_CHOICES)[new_status]}')
    
    return redirect('shopping_manage:order_detail', order_id=order_id)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def order_mark_shipped(request, order_id):
    """标记订单为已发货"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'paid':
        messages.error(request, '只能标记已付款的订单为已发货')
        return redirect('shopping_manage:order_detail', order_id=order_id)
    
    # 获取物流信息
    shipping_company = request.POST.get('shipping_company', '').strip()
    tracking_number = request.POST.get('tracking_number', '').strip()
    
    if not shipping_company or not tracking_number:
        messages.error(request, '请填写物流公司和物流单号')
        return redirect('shopping_manage:order_detail', order_id=order_id)
    
    order.status = 'shipped'
    order.shipping_company = shipping_company
    order.tracking_number = tracking_number
    order.shipped_at = timezone.now()
    order.save()
    
    messages.success(request, f'订单已发货 - {shipping_company}: {tracking_number}')
    return redirect('shopping_manage:order_detail', order_id=order_id)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def order_update_shipping(request, order_id):
    """更新物流信息"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status not in ['shipped', 'completed']:
        messages.error(request, '只能修改已发货或已完成订单的物流信息')
        return redirect('shopping_manage:order_detail', order_id=order_id)
    
    # 获取物流信息
    shipping_company = request.POST.get('shipping_company', '').strip()
    tracking_number = request.POST.get('tracking_number', '').strip()
    
    if not shipping_company or not tracking_number:
        messages.error(request, '请填写物流公司和物流单号')
        return redirect('shopping_manage:order_detail', order_id=order_id)
    
    order.shipping_company = shipping_company
    order.tracking_number = tracking_number
    order.save()
    
    messages.success(request, f'物流信息已更新 - {shipping_company}: {tracking_number}')
    return redirect('shopping_manage:order_detail', order_id=order_id)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def order_batch_ship(request):
    """批量发货"""
    order_ids = request.POST.getlist('order_ids[]')
    
    if not order_ids:
        return JsonResponse({'success': False, 'message': '请选择要发货的订单'})
    
    try:
        with transaction.atomic():
            orders = Order.objects.filter(id__in=order_ids, status='paid')
            count = orders.count()
            orders.update(status='shipped', shipped_at=timezone.now())
        
        return JsonResponse({
            'success': True,
            'message': f'成功发货 {count} 个订单'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'批量发货失败：{str(e)}'
        })


# ==================== 退款管理 ====================

@login_required
@user_passes_test(is_staff)
def refund_management(request):
    """退款管理页面"""
    refunds = RefundRequest.objects.all().select_related(
        'order__user'
    ).order_by('-created_at')
    
    # 状态过滤
    status = request.GET.get('status', '')
    if status:
        refunds = refunds.filter(status=status)
    
    # 搜索
    search = request.GET.get('search', '')
    if search:
        refunds = refunds.filter(
            Q(order__order_number__icontains=search) |
            Q(order__user__username__icontains=search)
        )
    
    # 统计
    stats = {
        'total': RefundRequest.objects.count(),
        'pending': RefundRequest.objects.filter(status='pending').count(),
        'approved': RefundRequest.objects.filter(status='approved').count(),
        'rejected': RefundRequest.objects.filter(status='rejected').count(),
        'processing': RefundRequest.objects.filter(status='processing').count(),
        'completed': RefundRequest.objects.filter(status='completed').count(),
    }
    
    context = {
        'refunds': refunds,
        'stats': stats,
        'current_status': status,
        'search': search,
        'status_choices': RefundRequest.REFUND_STATUS_CHOICES,
    }
    
    return render(request, 'shopping/refund_management.html', context)


@login_required
@user_passes_test(is_staff)
def refund_detail(request, refund_id):
    """退款详情页"""
    refund = get_object_or_404(
        RefundRequest.objects.select_related(
            'order__user'
        ).prefetch_related('order__items__sku__spu'),
        id=refund_id
    )
    
    context = {
        'refund': refund,
        'reason_display': dict(RefundRequest.REFUND_REASON_CHOICES).get(refund.reason, refund.reason),
    }
    
    return render(request, 'shopping/refund_detail.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def refund_approve(request, refund_id):
    """批准退款"""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    
    if refund.status != 'pending':
        messages.error(request, '只能批准待审核的退款申请')
        return redirect('shopping_manage:refund_detail', refund_id=refund_id)
    
    admin_note = request.POST.get('admin_note', '')
    
    try:
        with transaction.atomic():
            # 更新退款状态
            refund.status = 'approved'
            refund.admin_note = admin_note
            refund.processed_at = timezone.now()
            refund.save()
            
            # 更新订单状态为已取消
            order = refund.order
            order.status = 'cancelled'
            order.save()
            
            # 恢复库存
            for item in order.items.all():
                inventory = item.sku.inventory
                inventory.quantity += item.quantity  # 使用 quantity 而不是 stock
                inventory.save()
            
            messages.success(request, '退款已批准，订单已取消，库存已恢复')
    except Exception as e:
        messages.error(request, f'批准退款失败：{str(e)}')
    
    return redirect('shopping_manage:refund_detail', refund_id=refund_id)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def refund_reject(request, refund_id):
    """拒绝退款"""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    
    if refund.status != 'pending':
        messages.error(request, '只能拒绝待审核的退款申请')
        return redirect('shopping_manage:refund_detail', refund_id=refund_id)
    
    admin_note = request.POST.get('admin_note', '')
    
    if not admin_note:
        messages.error(request, '拒绝退款必须填写原因')
        return redirect('shopping_manage:refund_detail', refund_id=refund_id)
    
    refund.status = 'rejected'
    refund.admin_note = admin_note
    refund.processed_at = timezone.now()
    refund.save()
    
    messages.success(request, '退款已拒绝')
    return redirect('shopping_manage:refund_detail', refund_id=refund_id)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def refund_batch_approve(request):
    """批量批准退款"""
    refund_ids = request.POST.getlist('refund_ids[]')
    
    if not refund_ids:
        return JsonResponse({'success': False, 'message': '请选择要批准的退款申请'})
    
    try:
        with transaction.atomic():
            refunds = RefundRequest.objects.filter(id__in=refund_ids, status='pending')
            count = 0
            
            for refund in refunds:
                # 更新退款状态
                refund.status = 'approved'
                refund.save()
                
                # 恢复库存
                for item in refund.order.items.all():
                    inventory = item.sku.inventory
                    inventory.stock += item.quantity
                    inventory.save()
                
                count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'成功批准 {count} 个退款申请'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'批量批准失败：{str(e)}'
        })


# ==================== 评价管理 ====================

@login_required
@user_passes_test(is_staff)
def review_management(request):
    """评价管理页面"""
    reviews = OrderItemReview.objects.all().select_related(
        'user',
        'order_item__order',
        'spu'
    ).order_by('-created_at')
    
    # 搜索
    search = request.GET.get('search', '')
    if search:
        reviews = reviews.filter(
            Q(content__icontains=search) |
            Q(user__username__icontains=search) |
            Q(spu__name__icontains=search)
        )
    
    # 统计
    stats = {
        'total': OrderItemReview.objects.count(),
    }
    
    context = {
        'reviews': reviews,
        'stats': stats,
        'search': search,
    }
    
    return render(request, 'shopping/review_management.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def review_delete(request, review_id):
    """删除评价"""
    review = get_object_or_404(OrderItemReview, id=review_id)
    
    try:
        # 更新订单项的评价状态
        order_item = review.order_item
        order_item.is_reviewed = False
        order_item.save()
        
        review.delete()
        
        return JsonResponse({
            'success': True,
            'message': '评价已删除'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'删除失败：{str(e)}'
        })
