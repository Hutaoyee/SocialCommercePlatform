from django.contrib import admin
from django.utils.html import format_html

from mptt.admin import MPTTModelAdmin
from dal import autocomplete

from django.utils.translation import gettext_lazy as _
from .models import (
    Category, ProductSPU, ProductSKU, Attribute, AttributeValue,
    ProductSPUAttribute, ProductSKUAttributeValue, Inventory, ProductImage, ProductReview,
    Order, OrderItem, RefundRequest, OrderItemReview
)

class CategoryFilter(admin.SimpleListFilter):
    title = _('分类（层级）')  # 过滤器标题
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        # 获取所有分类，按树形排序
        categories = Category.objects.all().order_by('tree_id', 'lft')
        lookups = []
        for category in categories:
            # 添加缩进显示层级
            indent = '—' * category.level  # 使用破折号表示层级
            lookups.append((category.pk, f"{indent} {category.name}"))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            category = Category.objects.get(pk=self.value())
            descendants = category.get_descendants(include_self=True)
            # 根据模型调整字段路径
            if queryset.model == ProductSPU:
                return queryset.filter(category__in=descendants)
            elif queryset.model == ProductSKU:
                return queryset.filter(spu__category__in=descendants)
            elif queryset.model == ProductSKUAttributeValue:
                return queryset.filter(sku__spu__category__in=descendants)
            # 添加其他模型的逻辑
        return queryset


# Category 模型的管理类，使用MPTTModelAdmin 支持树形显示
@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'parent', 'level']  # 列表显示字段：名称、父级、层级
    list_filter = ['level']  # 侧边栏过滤器：按层级过滤
    search_fields = ['name']  # 搜索字段：名称
    mptt_level_indent = 20  # 树形缩进像素

# ProductSPU 模型的管理类
@admin.register(ProductSPU)
class ProductSPUAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'series', 'is_active', 'created_at', 'updated_at']  
    list_filter = ['is_active', 'created_at', CategoryFilter]  
    search_fields = ['name', 'description']  
    readonly_fields = ['created_at', 'updated_at']  # 只读字段：时间戳

# ProductSKU 模型的管理类
@admin.register(ProductSKU)
class ProductSKUAdmin(admin.ModelAdmin):
    list_display = ['sku_code', 'spu', 'title', 'price', 'is_active', 'created_at']  
    list_filter = ['is_active', 'created_at', CategoryFilter]  
    search_fields = ['sku_code', 'title']  
    readonly_fields = ['sku_code', 'created_at', 'updated_at']  
    list_editable = ['price', 'is_active']  # 可在列表页编辑：价格、上架状态

# Attribute 模型的管理类
@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name']  
    search_fields = ['name']  

# AttributeValue 模型的管理类
@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value']  
    list_filter = ['attribute'] 
    search_fields = ['value']  

# ProductSPUAttribute 模型的管理类
@admin.register(ProductSPUAttribute)
class ProductSPUAttributeAdmin(admin.ModelAdmin):
    list_display = ['spu', 'attribute']  
    list_filter = ['attribute', CategoryFilter, ]  
    search_fields = ['spu__name', 'attribute__name']  

# ProductSKUAttributeValue 模型的管理类
@admin.register(ProductSKUAttributeValue)
class ProductSKUAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['sku', 'attribute', 'attribute_value']  
    list_filter = ['attribute', CategoryFilter] 
    search_fields = ['sku__title', 'attribute_value__value']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['attribute_value'].widget = autocomplete.ModelSelect2(
            url='attribute-value-autocomplete',
            forward=['attribute']  # 依赖attribute字段
        )
        return form  

# 过滤完成视图
class AttributeValueAutocomplete(autocomplete.Select2QuerySetView):  # 使用autocomplete.Select2QuerySetView
    def get_queryset(self):
        qs = AttributeValue.objects.all()
        attribute = self.forwarded.get('attribute', None)
        if attribute:
            qs = qs.filter(attribute_id=attribute)
        if self.q:
            qs = qs.filter(value__icontains=self.q)
        return qs

# Inventory 模型的管理类
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['sku', 'quantity', 'updated_at']  
    list_filter = ['quantity']  
    search_fields = ['sku__title']  
    readonly_fields = ['updated_at']  

# ProductImage 模型的管理类
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['spu', 'sku', 'image_preview', 'is_main']  
    list_filter = ['is_main', CategoryFilter] 
    search_fields = ['spu__name', 'sku__title']  

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "无图片"
    image_preview.short_description = '图片预览'

# ProductReview 模型的管理类
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['spu', 'user', 'rating', 'content_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['spu__name', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'


# ==================== 订单管理 ====================

class OrderItemInline(admin.TabularInline):
    """订单商品内联显示"""
    model = OrderItem
    extra = 0
    readonly_fields = ['sku', 'sku_title', 'spu_name', 'price', 'quantity', 'subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'receiver_name', 'receiver_phone']
    readonly_fields = ['order_number', 'created_at', 'paid_at', 'shipped_at', 'completed_at']
    inlines = [OrderItemInline]
    actions = ['mark_as_shipped']
    
    fieldsets = (
        ('订单信息', {
            'fields': ('order_number', 'user', 'total_amount', 'status', 'payment_method')
        }),
        ('收货信息', {
            'fields': ('receiver_name', 'receiver_phone', 'receiver_province', 'receiver_city', 
                      'receiver_district', 'receiver_address')
        }),
        ('时间信息', {
            'fields': ('created_at', 'paid_at', 'shipped_at', 'completed_at')
        }),
        ('其他', {
            'fields': ('remark',)
        }),
    )
    
    def mark_as_shipped(self, request, queryset):
        """批量标记为已发货"""
        from django.utils import timezone
        
        updated = queryset.filter(status='paid').update(
            status='shipped',
            shipped_at=timezone.now()
        )
        
        self.message_user(request, f'成功发货 {updated} 个订单')
    mark_as_shipped.short_description = '标记为已发货'
    
    def has_add_permission(self, request):
        """禁止在admin中直接创建订单"""
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'spu_name', 'sku_title', 'price', 'quantity', 'subtotal', 'is_reviewed']
    list_filter = ['order__created_at', 'is_reviewed']
    search_fields = ['order__order_number', 'spu_name', 'sku_title']
    readonly_fields = ['order', 'sku', 'sku_title', 'spu_name', 'price', 'quantity', 'subtotal']
    
    def has_add_permission(self, request):
        """禁止在admin中直接创建订单商品"""
        return False


# ==================== 退款申请管理 ====================

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'reason', 'refund_amount', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['order__order_number', 'description']
    readonly_fields = ['order', 'reason', 'description', 'refund_amount', 'created_at']
    
    fieldsets = (
        ('退款信息', {
            'fields': ('order', 'reason', 'description', 'refund_amount', 'status')
        }),
        ('处理信息', {
            'fields': ('processed_at', 'admin_remark')
        }),
    )
    
    actions = ['approve_refund', 'reject_refund']
    
    def approve_refund(self, request, queryset):
        """批量同意退款"""
        from django.utils import timezone
        
        updated = 0
        for refund in queryset.filter(status='pending'):
            refund.status = 'approved'
            refund.processed_at = timezone.now()
            refund.save()
            
            # 更新订单状态
            refund.order.status = 'refunded'
            refund.order.save()
            
            # 恢复库存
            for item in refund.order.items.all():
                inventory = item.sku.inventory
                inventory.quantity += item.quantity
                inventory.save()
            
            updated += 1
        
        self.message_user(request, f'成功处理 {updated} 个退款申请')
    approve_refund.short_description = '同意退款'
    
    def reject_refund(self, request, queryset):
        """批量拒绝退款"""
        from django.utils import timezone
        
        updated = queryset.filter(status='pending').update(
            status='rejected',
            processed_at=timezone.now()
        )
        
        self.message_user(request, f'成功拒绝 {updated} 个退款申请')
    reject_refund.short_description = '拒绝退款'
    
    def has_add_permission(self, request):
        """禁止在admin中直接创建退款申请"""
        return False


# ==================== 订单评价管理 ====================

@admin.register(OrderItemReview)
class OrderItemReviewAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'user', 'spu', 'rating', 'content_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'spu__name', 'content']
    readonly_fields = ['order_item', 'user', 'spu', 'created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评价内容'
    
    def has_add_permission(self, request):
        """禁止在admin中直接创建评价"""
        return False