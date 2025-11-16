from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
import json
import os

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from .models import (
    ProductSPU, ProductSKU, Attribute, AttributeValue, 
    ProductSKUAttributeValue, ProductSPUAttribute, ProductReview, 
    Category, Order, OrderItem, Inventory, RefundRequest, OrderItemReview
)
from .serializers import (
    ProductSPUSerializer, ProductSKUSerializer, ProductReviewSerializer, 
    SKUDetailSerializer, CategorySerializer, OrderSerializer, 
    OrderCreateSerializer, OrderItemSerializer, RefundRequestSerializer,
    OrderItemReviewSerializer, UserOwnedProductSerializer
)
from .pagination import ProductPagination

# Create your views here.

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    分类视图集，只读
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None  # 禁用分页，返回所有分类
    
    def get_queryset(self):
        """返回所有分类，按树形结构排序"""
        return Category.objects.all().order_by('tree_id', 'lft')


class ProductSPUViewSet(viewsets.ModelViewSet):
    """
    SPU视图集，支持分页、搜索、过滤
    """
    queryset = ProductSPU.objects.filter(is_active=True)
    serializer_class = ProductSPUSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = ProductPagination
    
    def get_queryset(self):
        queryset = ProductSPU.objects.filter(is_active=True)
        
        # 按分类过滤（包含子分类）
        category_id = self.request.query_params.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                # 获取该分类及其所有子分类
                categories = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=categories)
            except Category.DoesNotExist:
                pass
        
        # 按品牌过滤
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        # 搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def skus(self, request, pk=None):
        """
        获取SPU的所有SKU信息，包括属性、库存、价格
        """
        spu = self.get_object()
        
        # 获取SPU的所有属性
        spu_attributes = ProductSPUAttribute.objects.filter(spu=spu).select_related('attribute')
        
        # 构建属性和属性值的数据结构
        attributes_data = []
        for spu_attr in spu_attributes:
            attribute = spu_attr.attribute
            # 获取该SPU下所有SKU使用的属性值
            attribute_values = AttributeValue.objects.filter(
                productskuattributevalue__sku__spu=spu,
                attribute=attribute
            ).distinct()
            
            attributes_data.append({
                'id': attribute.id,
                'name': attribute.name,
                'values': [{'id': av.id, 'value': av.value} for av in attribute_values]
            })
        
        # 获取所有SKU及其属性值
        skus = ProductSKU.objects.filter(spu=spu, is_active=True).prefetch_related(
            'attribute_values__attribute',
            'attribute_values__attribute_value',
            'inventory',
            'images'  # 预加载SKU图片
        )
        
        # 获取SPU主图
        spu_main_image = spu.images.filter(is_main=True).first()
        spu_image_url = request.build_absolute_uri(spu_main_image.image.url) if spu_main_image else None
        
        skus_data = []
        for sku in skus:
            sku_attrs = {}
            for sku_attr_value in sku.attribute_values.all():
                sku_attrs[sku_attr_value.attribute.id] = sku_attr_value.attribute_value.id
            
            # 获取SKU图片，如果没有则使用SPU主图
            sku_image = sku.images.first()
            image_url = request.build_absolute_uri(sku_image.image.url) if sku_image else spu_image_url
            
            inventory = getattr(sku, 'inventory', None)
            skus_data.append({
                'sku_code': sku.sku_code,
                'title': sku.title,
                'price': str(sku.price),
                'stock': inventory.quantity if inventory else 0,
                'attributes': sku_attrs,
                'image': image_url  # 添加图片URL
            })
        
        return Response({
            'attributes': attributes_data,
            'skus': skus_data
        })
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def reviews(self, request, pk=None):
        """
        获取SPU的所有评价（从订单评价中获取）
        """
        spu = self.get_object()
        # 获取该SPU的所有订单评价
        reviews = OrderItemReview.objects.filter(spu=spu).select_related(
            'user', 'order_item'
        ).order_by('-created_at')
        serializer = OrderItemReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)


class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    商品评论视图集
    """
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = ProductReview.objects.all()
        
        # 按SPU过滤
        spu_id = self.request.query_params.get('spu')
        if spu_id:
            queryset = queryset.filter(spu_id=spu_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ==================== 订单管理 ====================

class OrderViewSet(viewsets.ModelViewSet):
    """订单管理视图集"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user).prefetch_related('items__sku__spu')
        
        # 按状态过滤
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """创建订单"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        validated_data = serializer.validated_data
        address = validated_data['address']
        cart_items = validated_data['cart_items']
        payment_method = validated_data.get('payment_method', 'mock')
        remark = validated_data.get('remark', '')
        
        # 计算订单总金额
        total_amount = sum(item.total_price for item in cart_items)
        
        # 创建订单
        order = Order.objects.create(
            user=user,
            receiver_name=address.name,
            receiver_phone=address.phone,
            receiver_province=address.province,
            receiver_city=address.city,
            receiver_district=address.district,
            receiver_address=address.address,
            total_amount=total_amount,
            payment_method=payment_method,
            remark=remark
        )
        
        # 创建订单商品并扣减库存
        for cart_item in cart_items:
            sku = cart_item.sku
            inventory = sku.inventory
            
            # 再次检查库存（防止并发问题）
            if inventory.quantity < cart_item.quantity:
                raise serializers.ValidationError(f'商品 {sku.title} 库存不足')
            
            # 扣减库存
            inventory.quantity -= cart_item.quantity
            inventory.save()
            
            # 创建订单商品
            OrderItem.objects.create(
                order=order,
                sku=sku,
                sku_title=sku.title,
                spu_name=sku.spu.name,
                price=sku.price,
                quantity=cart_item.quantity,
                subtotal=cart_item.total_price
            )
        
        # 删除购物车中的商品
        from user.models import CartItem
        CartItem.objects.filter(id__in=[item.id for item in cart_items]).delete()
        
        # 返回订单信息
        order_serializer = OrderSerializer(order, context={'request': request})
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()
        
        if order.status != 'pending':
            return Response({'error': '只能取消待支付的订单'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # 恢复库存
            for item in order.items.all():
                inventory = item.sku.inventory
                inventory.quantity += item.quantity
                inventory.save()
            
            # 更新订单状态
            order.status = 'cancelled'
            order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        """申请退款"""
        order = self.get_object()
        
        # 检查订单状态
        if order.status not in ['paid', 'shipped']:
            return Response({
                'error': '只能对已支付或已发货的订单申请退款'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已有退款申请
        if hasattr(order, 'refund_request'):
            return Response({
                'error': '该订单已提交退款申请'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建退款申请
        serializer = RefundRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(
                order=order,
                refund_amount=order.total_amount  # 默认退全款
            )
            
            return Response({
                'message': '退款申请提交成功',
                'refund_request': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm_delivery(self, request, pk=None):
        """确认收货"""
        order = self.get_object()
        
        if order.status != 'shipped':
            return Response({
                'error': '只能确认已发货的订单'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # 更新订单状态
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            
            # 将商品添加到用户拥有列表
            from user.models import UserProduct
            for item in order.items.all():
                # 使用get_or_create，如果已存在则不重复添加
                user_product, created = UserProduct.objects.get_or_create(
                    user=order.user,
                    sku=item.sku
                )
                # UserProduct模型中没有quantity和order字段，只需创建即可
        
        serializer = self.get_serializer(order)
        return Response({
            'message': '确认收货成功，商品已添加到您的拥有列表',
            'order': serializer.data
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_order(request, order_id):
    """支付订单（模拟支付）"""
    user = request.user
    
    try:
        order = Order.objects.get(id=order_id, user=user)
        
        if order.status != 'pending':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 模拟支付成功
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        # 如果用户购买的是虚拟商品（音乐等），自动添加到用户拥有的商品
        from user.models import UserProduct
        for item in order.items.all():
            UserProduct.objects.get_or_create(
                user=user,
                sku=item.sku,
                defaults={'purchased_at': timezone.now()}
            )
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response({
            'message': '支付成功',
            'order': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_order(request, order_id):
    """确认收货（旧接口，保持兼容）"""
    user = request.user
    
    try:
        order = Order.objects.get(id=order_id, user=user)
        
        if order.status != 'shipped':
            return Response({'error': '只能确认已发货的订单'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # 更新订单状态
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            
            # 将订单中的商品添加到用户拥有的商品中
            from user.models import UserProduct
            for item in order.items.all():
                # 使用get_or_create，如果已存在则不重复添加
                UserProduct.objects.get_or_create(
                    user=user,
                    sku=item.sku
                )
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response({
            'message': '确认收货成功，商品已添加到您的拥有列表',
            'order': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)


# ==================== 订单评价管理 ====================

class OrderItemReviewViewSet(viewsets.ModelViewSet):
    """订单商品评价管理"""
    serializer_class = OrderItemReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的评价"""
        return OrderItemReview.objects.filter(user=self.request.user).select_related(
            'order_item__order',
            'order_item__sku__spu',
            'user'
        ).order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        """创建评价"""
        from rest_framework import serializers as drf_serializers
        
        order_item_id = self.request.data.get('order_item')
        
        # 验证订单商品
        try:
            order_item = OrderItem.objects.select_related('order', 'sku__spu').get(
                id=order_item_id,
                order__user=self.request.user
            )
        except OrderItem.DoesNotExist:
            raise drf_serializers.ValidationError('订单商品不存在或无权访问')
        
        # 检查订单是否已完成
        if order_item.order.status != 'completed':
            raise drf_serializers.ValidationError('只能评价已完成的订单')
        
        # 检查是否已评价
        if order_item.is_reviewed:
            raise drf_serializers.ValidationError('该商品已评价')
        
        # 保存评价（rating 使用模型默认值5）
        review = serializer.save(
            user=self.request.user,
            spu=order_item.sku.spu,
            rating=5  # 明确设置评分为5
        )
        
        # 标记为已评价
        order_item.is_reviewed = True
        order_item.save()
    
    def perform_update(self, serializer):
        """更新评价"""
        from rest_framework import serializers as drf_serializers
        
        # 确保只能更新自己的评价
        if serializer.instance.user != self.request.user:
            raise drf_serializers.ValidationError('无权修改此评价')
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """删除评价"""
        from rest_framework import serializers as drf_serializers
        
        # 确保只能删除自己的评价
        if instance.user != self.request.user:
            raise drf_serializers.ValidationError('无权删除此评价')
        
        # 取消订单商品的评价标记
        order_item = instance.order_item
        order_item.is_reviewed = False
        order_item.save()
        
        instance.delete()
    
    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """删除评价图片"""
        from rest_framework.response import Response
        from rest_framework import status
        from rest_framework import serializers as drf_serializers
        from .models import OrderItemReviewImage
        
        review = self.get_object()
        
        # 确保只能删除自己评价的图片
        if review.user != request.user:
            raise drf_serializers.ValidationError('无权删除此图片')
        
        try:
            image = OrderItemReviewImage.objects.get(id=image_id, review=review)
            image.delete()
            return Response({'detail': '图片已删除'}, status=status.HTTP_204_NO_CONTENT)
        except OrderItemReviewImage.DoesNotExist:
            return Response({'detail': '图片不存在'}, status=status.HTTP_404_NOT_FOUND)


# ==================== 用户拥有商品管理 ====================

class UserOwnedProductViewSet(viewsets.ModelViewSet):
    """用户拥有的商品列表"""
    serializer_class = UserOwnedProductSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'delete']  # 只允许查看和删除
    
    def get_queryset(self):
        """只返回当前用户拥有的商品"""
        from user.models import UserProduct
        return UserProduct.objects.filter(user=self.request.user).select_related(
            'sku__spu'
        ).prefetch_related(
            'sku__spu__images'
        ).order_by('-purchased_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def destroy(self, request, *args, **kwargs):
        """删除拥有记录"""
        instance = self.get_object()
        
        # 确保只能删除自己的记录
        if instance.user != request.user:
            return Response({
                'error': '无权删除此记录'
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({
            'message': '删除成功'
        }, status=status.HTTP_204_NO_CONTENT)


# ==================== Stripe 支付集成 ====================

# 配置 Stripe API 密钥
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    创建 Stripe Checkout Session
    
    请求参数:
    - order_id: 订单ID
    - success_url: 支付成功后的回调URL（可选，默认为前端地址）
    - cancel_url: 取消支付后的回调URL（可选，默认为前端地址）
    """
    try:
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({
                'error': '缺少订单ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取订单
        order = Order.objects.get(id=order_id, user=request.user)
        
        # 检查订单状态
        if order.status != 'pending':
            return Response({
                'error': '订单状态不正确，只能支付待支付订单'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取前端地址（从环境变量或请求头获取）
        frontend_url = os.environ.get('FRONTEND_URL')
        
        # 从请求参数获取回调URL，如果没有则使用默认值
        success_url = request.data.get('success_url', f'{frontend_url}/order-success?session_id={{CHECKOUT_SESSION_ID}}')
        cancel_url = request.data.get('cancel_url', f'{frontend_url}/order-cancel')
        
        # 构建订单商品列表
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'cny',  # 人民币
                    'product_data': {
                        'name': item.sku.title,
                        'description': f'{item.sku.spu.name} - {item.sku.title}',
                    },
                    'unit_amount': int(item.price * 100),  # Stripe 使用分为单位，所以乘以100
                },
                'quantity': item.quantity,
            })
        
        # 创建 Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'order_id': str(order.id),
                'user_id': str(request.user.id),
            },
            client_reference_id=str(order.id),
        )
        
        # 返回 session ID 和 URL
        return Response({
            'sessionId': checkout_session.id,
            'url': checkout_session.url,
            'publishableKey': settings.STRIPE_PUBLISHABLE_KEY,
        }, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({
            'error': '订单不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'创建支付会话失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # Webhook 不需要身份验证
def stripe_webhook(request):
    """
    处理 Stripe Webhook 事件
    
    主要处理以下事件:
    - checkout.session.completed: 支付成功
    - payment_intent.succeeded: 支付意图成功
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # 获取 webhook secret
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    if not webhook_secret:
        # 如果没有配置 webhook secret，在开发环境下可以跳过验证
        # 生产环境必须配置！
        if settings.DEBUG:
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                return HttpResponse(status=400)
        else:
            return HttpResponse('Webhook secret not configured', status=500)
    else:
        # 验证 webhook 签名
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            # 无效的 payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # 无效的签名
            return HttpResponse(status=400)
    
    # 处理事件
    event_type = event['type']
    
    if event_type == 'checkout.session.completed':
        # 支付成功
        session = event['data']['object']
        
        # 获取订单ID
        order_id = session.get('metadata', {}).get('order_id') or session.get('client_reference_id')
        
        if order_id:
            try:
                with transaction.atomic():
                    order = Order.objects.get(id=order_id)
                    
                    # 更新订单状态为已支付
                    if order.status == 'pending':
                        order.status = 'paid'
                        order.paid_at = timezone.now()
                        order.payment_method = 'stripe'
                        order.save()
                        
                        # 如果是虚拟商品，自动添加到用户拥有列表
                        from user.models import UserProduct
                        for item in order.items.all():
                            UserProduct.objects.get_or_create(
                                user=order.user,
                                sku=item.sku,
                                defaults={'purchased_at': timezone.now()}
                            )
                        
                        print(f'✅ 订单 {order_id} 支付成功，已更新状态')
                    else:
                        print(f'⚠️ 订单 {order_id} 状态为 {order.status}，跳过更新')
                        
            except Order.DoesNotExist:
                print(f'❌ 订单 {order_id} 不存在')
                return HttpResponse(status=404)
            except Exception as e:
                print(f'❌ 处理订单 {order_id} 时出错: {str(e)}')
                return HttpResponse(status=500)
    
    elif event_type == 'payment_intent.succeeded':
        # 支付意图成功（如果使用 PaymentIntent 而不是 Checkout）
        payment_intent = event['data']['object']
        print(f'✅ PaymentIntent {payment_intent["id"]} 成功')
    
    else:
        print(f'ℹ️ 未处理的事件类型: {event_type}')
    
    return HttpResponse(status=200)