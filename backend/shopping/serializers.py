from rest_framework import serializers
from .models import (
    ProductSPU, ProductSKU, ProductReview, Category, Order, OrderItem,
    RefundRequest, OrderItemReview, OrderItemReviewImage
)

class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器，支持层级显示"""
    level = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'level', 'full_name']
    
    def get_full_name(self, obj):
        """获取完整的分类路径，如：服装 > 上衣 > T恤"""
        names = [obj.name]
        parent = obj.parent
        while parent:
            names.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(names)


class ProductSPUSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # 从ProductImage获取主图
    is_favorited = serializers.SerializerMethodField()  # 是否已收藏
    review_count = serializers.SerializerMethodField()  # 评论数

    class Meta:
        model = ProductSPU
        fields = ['id', 'name', 'description', 'category', 'brand', 'series', 'is_active', 
                  'created_at', 'updated_at', 'image', 'is_favorited', 'review_count']

    def get_image(self, obj):
        """返回主图完整 URL"""
        request = self.context.get('request')
        image = obj.images.filter(is_main=True).first()
        if image:
            if request:
                try:
                    return request.build_absolute_uri(image.image.url)
                except Exception:
                    return image.image.url
            return image.image.url
        return None
    
    def get_is_favorited(self, obj):
        """检查当前用户是否已收藏"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from user.models import ProductFavorite
            return ProductFavorite.objects.filter(user=request.user, product=obj).exists()
        return False
    
    def get_review_count(self, obj):
        """获取评论数量"""
        return obj.reviews.count()


class ProductSKUSerializer(serializers.ModelSerializer):
    spu_name = serializers.CharField(source='spu.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductSKU
        fields = ['sku_code', 'spu', 'spu_name', 'title', 'price', 'is_active', 'image']

    def get_image(self, obj):
        """返回SKU主图完整 URL"""
        request = self.context.get('request')
        image = obj.spu.images.filter(is_main=True).first()
        if image:
            if request:
                try:
                    return request.build_absolute_uri(image.image.url)
                except Exception:
                    return image.image.url
            return image.image.url
        return None


class SKUDetailSerializer(serializers.ModelSerializer):
    """SKU详细信息序列化器，包含库存"""
    stock = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductSKU
        fields = ['sku_code', 'title', 'price', 'stock', 'is_active']
    
    def get_stock(self, obj):
        """获取库存数量"""
        inventory = getattr(obj, 'inventory', None)
        return inventory.quantity if inventory else 0


class ProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = ['id', 'spu', 'user', 'username', 'user_avatar', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_user_avatar(self, obj):
        """获取用户头像URL"""
        request = self.context.get('request')
        if obj.user.avatar:
            if request:
                try:
                    return request.build_absolute_uri(obj.user.avatar.url)
                except Exception:
                    return obj.user.avatar.url
            return obj.user.avatar.url
        return None


# ==================== 退款申请序列化器 ====================

class RefundRequestSerializer(serializers.ModelSerializer):
    """退款申请序列化器"""
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = RefundRequest
        fields = [
            'id', 'order', 'order_number', 'reason', 'reason_display', 
            'description', 'refund_amount', 'status', 'status_display',
            'created_at', 'processed_at', 'admin_remark'
        ]
        read_only_fields = ['order', 'refund_amount', 'status', 'processed_at', 'admin_remark', 'order_number']



# ==================== 订单评价序列化器 ====================

class OrderItemReviewImageSerializer(serializers.ModelSerializer):
    """评价图片序列化器"""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItemReviewImage
        fields = ['id', 'image', 'url', 'created_at']
        read_only_fields = ['created_at']
    
    def get_url(self, obj):
        """获取图片完整URL"""
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            try:
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
            except Exception:
                pass
        return None


class OrderItemReviewSerializer(serializers.ModelSerializer):
    """订单商品评价序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    spu_name = serializers.CharField(source='order_item.spu_name', read_only=True)
    images = serializers.SerializerMethodField()  # 评价图片
    # 用于接收上传的图片文件
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = OrderItemReview
        fields = [
            'id', 'order_item', 'user', 'username', 'user_avatar',
            'spu', 'spu_name', 'content', 'images', 'uploaded_images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_item', 'user', 'spu', 'created_at', 'updated_at', 'username', 'user_avatar', 'spu_name']
    
    def get_user_avatar(self, obj):
        """获取用户头像URL"""
        request = self.context.get('request')
        if obj.user.avatar:
            if request:
                try:
                    return request.build_absolute_uri(obj.user.avatar.url)
                except Exception:
                    return obj.user.avatar.url
            return obj.user.avatar.url
        return None
    
    def get_images(self, obj):
        """获取评价图片列表"""
        if hasattr(obj, 'review_images'):
            images = obj.review_images.all()
            serializer = OrderItemReviewImageSerializer(
                images, 
                many=True, 
                context=self.context
            )
            return serializer.data
        return []
    
    def create(self, validated_data):
        """创建评价并处理图片上传"""
        uploaded_images = validated_data.pop('uploaded_images', [])
        review = super().create(validated_data)
        
        # 创建评价图片
        for image in uploaded_images:
            OrderItemReviewImage.objects.create(review=review, image=image)
        
        return review
    
    def update(self, instance, validated_data):
        """更新评价并处理图片上传"""
        uploaded_images = validated_data.pop('uploaded_images', [])
        review = super().update(instance, validated_data)
        
        # 如果有新上传的图片，添加到评价中
        for image in uploaded_images:
            OrderItemReviewImage.objects.create(review=review, image=image)
        
        return review


# ==================== 订单相关序列化器 ====================

class OrderItemSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    image = serializers.SerializerMethodField()
    can_review = serializers.SerializerMethodField()  # 是否可以评价
    review = serializers.SerializerMethodField()  # 评价信息
    
    class Meta:
        model = OrderItem
        fields = ['id', 'sku', 'sku_title', 'spu_name', 'price', 'quantity', 'subtotal', 'image', 'is_reviewed', 'can_review', 'review']
        read_only_fields = ['sku_title', 'spu_name', 'price', 'subtotal', 'image', 'is_reviewed']
    
    def get_image(self, obj):
        """获取商品图片"""
        request = self.context.get('request')
        # 尝试获取SKU图片
        sku_image = obj.sku.images.first()
        if sku_image:
            if request:
                try:
                    return request.build_absolute_uri(sku_image.image.url)
                except Exception:
                    return sku_image.image.url
            return sku_image.image.url
        
        # 否则获取SPU主图
        spu_main_image = obj.sku.spu.images.filter(is_main=True).first()
        if spu_main_image:
            if request:
                try:
                    return request.build_absolute_uri(spu_main_image.image.url)
                except Exception:
                    return spu_main_image.image.url
            return spu_main_image.image.url
        
        return None
    
    def get_can_review(self, obj):
        """判断是否可以评价（订单已完成且未评价）"""
        return obj.order.status == 'completed' and not obj.is_reviewed
    
    def get_review(self, obj):
        """获取评价信息"""
        try:
            if hasattr(obj, 'review') and obj.review:
                return OrderItemReviewSerializer(obj.review, context=self.context).data
        except OrderItemReview.DoesNotExist:
            pass
        return None


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    refund_request = RefundRequestSerializer(read_only=True)
    shipping_address = serializers.ReadOnlyField()  # 添加shipping_address属性
    can_cancel = serializers.SerializerMethodField()  # 是否可以取消
    can_refund = serializers.SerializerMethodField()  # 是否可以申请退款
    can_confirm = serializers.SerializerMethodField()  # 是否可以确认收货
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'receiver_name', 'receiver_phone',
            'receiver_province', 'receiver_city', 'receiver_district', 'receiver_address',
            'shipping_address', 'shipping_company', 'tracking_number', 'total_amount', 
            'status', 'status_display', 'payment_method', 'payment_method_display',
            'created_at', 'paid_at', 'shipped_at', 'completed_at', 'remark', 'items',
            'refund_request', 'can_cancel', 'can_refund', 'can_confirm'
        ]
        read_only_fields = [
            'order_number', 'user', 'created_at', 'paid_at', 
            'shipped_at', 'completed_at', 'status_display', 'payment_method_display'
        ]
    
    def get_can_cancel(self, obj):
        """判断是否可以取消（待支付状态）"""
        return obj.status == 'pending'
    
    def get_can_refund(self, obj):
        """判断是否可以申请退款（已支付或已发货状态，且没有退款申请）"""
        return obj.status in ['paid', 'shipped'] and not hasattr(obj, 'refund_request')
    
    def get_can_confirm(self, obj):
        """判断是否可以确认收货（已发货状态）"""
        return obj.status == 'shipped'


class OrderCreateSerializer(serializers.Serializer):
    """创建订单的序列化器"""
    address_id = serializers.IntegerField(required=True, help_text="收货地址ID")
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="购物车商品ID列表"
    )
    payment_method = serializers.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        default='mock',
        help_text="支付方式"
    )
    remark = serializers.CharField(
        required=False, 
        allow_blank=True, 
        max_length=500,
        help_text="订单备注"
    )
    
    def validate_cart_item_ids(self, value):
        """验证购物车商品ID列表不为空"""
        if not value:
            raise serializers.ValidationError("购物车商品列表不能为空")
        return value
    
    def validate(self, data):
        """综合验证"""
        user = self.context['request'].user
        
        # 验证地址
        from user.models import Address
        try:
            address = Address.objects.get(id=data['address_id'], user=user)
            data['address'] = address
        except Address.DoesNotExist:
            raise serializers.ValidationError({'address_id': '地址不存在'})
        
        # 验证购物车商品
        from user.models import CartItem
        cart_items = CartItem.objects.filter(
            id__in=data['cart_item_ids'],
            user=user
        ).select_related('sku__spu', 'sku__inventory')
        
        if cart_items.count() != len(data['cart_item_ids']):
            raise serializers.ValidationError({'cart_item_ids': '部分商品不存在'})
        
        # 检查商品状态和库存
        for cart_item in cart_items:
            if not cart_item.sku.is_active or not cart_item.sku.spu.is_active:
                raise serializers.ValidationError(f'商品 {cart_item.sku.title} 已下架')
            
            inventory = getattr(cart_item.sku, 'inventory', None)
            if not inventory or inventory.quantity < cart_item.quantity:
                raise serializers.ValidationError(f'商品 {cart_item.sku.title} 库存不足')
        
        data['cart_items'] = cart_items
        return data


# ==================== 用户拥有商品序列化器 ====================

class UserOwnedProductSerializer(serializers.ModelSerializer):
    """用户拥有商品序列化器"""
    spu_name = serializers.CharField(source='sku.spu.name', read_only=True)
    sku_title = serializers.CharField(source='sku.title', read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        from user.models import UserProduct
        model = UserProduct
        fields = ['id', 'user', 'sku', 'spu_name', 'sku_title', 'purchased_at', 'image']
        read_only_fields = ['user', 'purchased_at', 'spu_name', 'sku_title']
    
    def get_image(self, obj):
        """获取商品图片"""
        request = self.context.get('request')
        # 尝试获取SKU图片
        sku_image = obj.sku.images.first()
        if sku_image:
            if request:
                try:
                    return request.build_absolute_uri(sku_image.image.url)
                except Exception:
                    return sku_image.image.url
            return sku_image.image.url
        
        # 否则获取SPU主图
        spu_main_image = obj.sku.spu.images.filter(is_main=True).first()
        if spu_main_image:
            if request:
                try:
                    return request.build_absolute_uri(spu_main_image.image.url)
                except Exception:
                    return spu_main_image.image.url
            return spu_main_image.image.url
        return None