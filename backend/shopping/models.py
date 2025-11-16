from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

# 动态图片上传路径函数
def product_image_upload_path(instance, filename):
    """
    动态生成图片上传路径，基于SPU的品牌和系列。
    """
    if instance.spu:
        brand = (instance.spu.brand or 'no_brand').replace(' ', '_')  # 替换空格为下划线
        series = (instance.spu.series or 'no_series').replace(' ', '_')
        return f'products/{brand}/{series}/{filename}'
    else:
        return f'products/other/{filename}'  # 默认路径

# Create your models here.
# 商品分类表
class Category(MPTTModel):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    parent = TreeForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, verbose_name="父级分类"
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"
        indexes = [
            models.Index(fields=['parent']),  # 优化树查询
        ]

    def __str__(self):
        return self.name

# SPU表
class ProductSPU(models.Model):
    name = models.CharField(max_length=200, verbose_name="商品名称")
    description = models.TextField(blank=True, verbose_name="商品描述")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="所属分类")
    brand = models.CharField(max_length=100, blank=True, verbose_name="品牌")  
    series = models.CharField(max_length=100, blank=True, verbose_name="系列")  
    is_active = models.BooleanField(default=True, verbose_name="是否上架")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "SPU"
        verbose_name_plural = "SPU"
        indexes = [
            models.Index(fields=['category', 'is_active']),  # 优化按分类和状态查询
            models.Index(fields=['brand']),  
            models.Index(fields=['series']),  
        ]

    def __str__(self):
        return self.name

# SKU表
class ProductSKU(models.Model):

    sku_code = models.CharField(max_length=100, primary_key=True, editable=False,verbose_name="SKU编码")
    spu = models.ForeignKey(ProductSPU, on_delete=models.CASCADE, related_name='skus', verbose_name="所属SPU")
    title = models.CharField(max_length=200, verbose_name="SKU标题")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")

    is_active = models.BooleanField(default=True, verbose_name="是否上架")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "SKU"
        verbose_name_plural = "SKU"
        indexes = [
            models.Index(fields=['spu', 'is_active']),  # 优化按SPU和状态查询SKU
            models.Index(fields=['price']),  # 优化价格排序
        ]

    def save(self, *args, **kwargs):
        if not self.sku_code:
            # 获取当前 SPU 下已存在的 SKU 数量
            count = ProductSKU.objects.filter(spu=self.spu).count() + 1
            self.sku_code = f"{self.spu.id}-{count}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
# SKU属性表： 总共有哪些属性
class Attribute(models.Model):
    name = models.CharField(max_length=100, verbose_name="属性名称")

    class Meta:
        verbose_name = "属性"
        verbose_name_plural = "属性"

    def __str__(self):
        return self.name

# SKU属性值表： 每个属性有哪些值
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name="所属属性")
    value = models.CharField(max_length=100, verbose_name="属性值")

    class Meta:
        verbose_name = "属性值"
        verbose_name_plural = "属性值"
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

# 属性所有表：一个SPU有哪些属性
class ProductSPUAttribute(models.Model):
    spu = models.ForeignKey(ProductSPU, on_delete=models.CASCADE, related_name='attributes', verbose_name="所属SPU")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name="属性")

    class Meta:
        verbose_name = "SPU属性"
        verbose_name_plural = "SPU属性"
        # 确保同一个 SPU（商品）不能重复关联同一个属性。
        unique_together = ('spu', 'attribute')
        indexes = [
            models.Index(fields=['spu']),  # 优化反查SPU属性
        ]

    def __str__(self):
        return f"{self.spu.name} - {self.attribute.name}"
    
# 属性值所有表：一个SKU有哪些属性值
class ProductSKUAttributeValue(models.Model):
    sku = models.ForeignKey(ProductSKU, on_delete=models.CASCADE, related_name='attribute_values', verbose_name="所属SKU")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name="属性")  
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, verbose_name="属性值")

    class Meta:
        verbose_name = "SKU属性值"
        verbose_name_plural = "SKU属性值"
        unique_together = ('sku', 'attribute')  # 修改为确保每个SKU对每个属性只有一个值
        indexes = [
            models.Index(fields=['sku']),  # 优化反查SKU属性值
            models.Index(fields=['attribute']),  # 优化按属性查询
        ]

    def __str__(self):
        return f"{self.sku.title} - {self.attribute_value}"

    def save(self, *args, **kwargs):
        # 确保attribute_value属于指定的attribute
        if self.attribute_value.attribute != self.attribute:
            raise ValueError("属性值必须属于指定的属性")
        
        # 确保attribute在SPU的属性中
        if not ProductSPUAttribute.objects.filter(spu=self.sku.spu, attribute=self.attribute).exists():
            raise ValueError("SKU 的属性必须在所属 SPU 的属性列表中")
        super().save(*args, **kwargs)

# 库存表
class Inventory(models.Model):
    sku = models.OneToOneField(ProductSKU, on_delete=models.CASCADE, related_name='inventory', verbose_name="SKU")
    quantity = models.PositiveIntegerField(default=0, verbose_name="库存数量")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "库存"
        verbose_name_plural = "库存"
        indexes = [
            models.Index(fields=['quantity']),  # 优化库存查询
        ]

    def __str__(self):
        return f"{self.sku.title} - {self.quantity}"

# 商品图片表
class ProductImage(models.Model):
    spu = models.ForeignKey(ProductSPU, on_delete=models.CASCADE, related_name='images', verbose_name="SPU", null=True, blank=True)
    sku = models.ForeignKey(ProductSKU, on_delete=models.CASCADE, related_name='images', verbose_name="SKU", null=True, blank=True)
    image = models.ImageField(upload_to=product_image_upload_path, verbose_name="图片")
    is_main = models.BooleanField(default=False, verbose_name="是否主图")

    class Meta:
        verbose_name = "商品图片"
        verbose_name_plural = "商品图片"
        indexes = [
            models.Index(fields=['spu', 'is_main']),  # 优化SPU主图查询
            models.Index(fields=['sku', 'is_main']),  # 优化SKU主图查询
        ]

    def __str__(self):
        return f"{self.spu.name if self.spu else self.sku.title} - {self.image.name}"

# 商品评论表
class ProductReview(models.Model):
    spu = models.ForeignKey(ProductSPU, on_delete=models.CASCADE, related_name='reviews', verbose_name="所属SPU")
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='product_reviews', verbose_name="评论用户")
    content = models.TextField(verbose_name="评论内容")
    rating = models.PositiveSmallIntegerField(default=5, verbose_name="评分")  # 1-5星
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "商品评论"
        verbose_name_plural = "商品评论"
        indexes = [
            models.Index(fields=['spu', 'created_at']),
            models.Index(fields=['user']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 评论 {self.spu.name}"


# 订单表
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('stripe', 'Stripe'),
        ('mock', '模拟支付'),
    ]
    
    order_number = models.CharField(max_length=64, unique=True, verbose_name="订单号")
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='orders', verbose_name="用户")
    
    # 收货地址信息（冗余存储，防止用户删除地址后订单信息丢失）
    receiver_name = models.CharField(max_length=100, verbose_name="收货人姓名")
    receiver_phone = models.CharField(max_length=20, verbose_name="联系电话")
    receiver_province = models.CharField(max_length=50, verbose_name="省份")
    receiver_city = models.CharField(max_length=50, verbose_name="城市")
    receiver_district = models.CharField(max_length=50, verbose_name="区县")
    receiver_address = models.CharField(max_length=200, verbose_name="详细地址")
    
    # 订单金额
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单总金额")
    
    # 订单状态
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name="订单状态")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, verbose_name="支付方式")
    
    # 物流信息
    shipping_company = models.CharField(max_length=100, blank=True, verbose_name="物流公司")
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name="物流单号")
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name="发货时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    
    # 备注
    remark = models.TextField(blank=True, verbose_name="备注")
    
    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"订单 {self.order_number}"
    
    @property
    def shipping_address(self):
        """组合收货地址"""
        return f"{self.receiver_name} {self.receiver_phone} | {self.receiver_province}{self.receiver_city}{self.receiver_district} {self.receiver_address}"
    
    def save(self, *args, **kwargs):
        # 自动生成订单号
        if not self.order_number:
            import time
            self.order_number = f"ORD{int(time.time() * 1000)}{self.user.id:06d}"
        super().save(*args, **kwargs)


# 订单商品表
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="所属订单")
    sku = models.ForeignKey(ProductSKU, on_delete=models.PROTECT, verbose_name="SKU")  # 使用PROTECT防止误删
    
    # 冗余商品信息（防止商品信息变更影响历史订单）
    sku_title = models.CharField(max_length=200, verbose_name="SKU标题")
    spu_name = models.CharField(max_length=200, verbose_name="商品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    quantity = models.PositiveIntegerField(verbose_name="数量")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="小计")
    
    # 评价状态
    is_reviewed = models.BooleanField(default=False, verbose_name="是否已评价")
    
    class Meta:
        verbose_name = "订单商品"
        verbose_name_plural = "订单商品"
        indexes = [
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.spu_name}"
    
    def save(self, *args, **kwargs):
        # 自动计算小计
        if not self.subtotal:
            self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


# 退款申请表
class RefundRequest(models.Model):
    REFUND_STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已同意'),
        ('rejected', '已拒绝'),
        ('completed', '已完成'),
    ]
    
    REFUND_REASON_CHOICES = [
        ('not_received', '未收到货'),
        ('not_as_described', '商品与描述不符'),
        ('quality_issue', '质量问题'),
        ('wrong_item', '发错货'),
        ('other', '其他原因'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund_request', verbose_name="关联订单")
    reason = models.CharField(max_length=50, choices=REFUND_REASON_CHOICES, verbose_name="退款原因")
    description = models.TextField(verbose_name="详细说明")
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="退款金额")
    
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending', verbose_name="处理状态")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="处理时间")
    admin_remark = models.TextField(blank=True, verbose_name="管理员备注")
    
    class Meta:
        verbose_name = "退款申请"
        verbose_name_plural = "退款申请"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"退款申请 - {self.order.order_number}"


class OrderItemReview(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='review', verbose_name="订单商品")
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='order_reviews', verbose_name="评价用户")
    spu = models.ForeignKey(ProductSPU, on_delete=models.CASCADE, related_name='order_reviews', verbose_name="关联SPU")
    
    content = models.TextField(verbose_name="评价内容")
    rating = models.PositiveSmallIntegerField(default=5, verbose_name="评分")  # 1-5星
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "订单商品评价"
        verbose_name_plural = "订单商品评价"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['spu', 'created_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 评价 {self.order_item.spu_name}"

# 评价图片路径函数
def review_image_upload_path(instance, filename):
    """评价图片上传路径: reviews/{spu_id}/{filename}"""
    import os
    from django.utils import timezone
    ext = os.path.splitext(filename)[1]
    filename = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{instance.review.user.id}{ext}"
    return f'reviews/{instance.review.spu.id}/{filename}'


class OrderItemReviewImage(models.Model):
    """评价图片"""
    review = models.ForeignKey(OrderItemReview, on_delete=models.CASCADE, related_name='review_images', verbose_name="关联评价")
    image = models.ImageField(upload_to=review_image_upload_path, verbose_name="图片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    
    class Meta:
        verbose_name = "评价图片"
        verbose_name_plural = "评价图片"
        ordering = ['created_at']
    
    def __str__(self):
        return f"评价图片 - {self.review.id}"

