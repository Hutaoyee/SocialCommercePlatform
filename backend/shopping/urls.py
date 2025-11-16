from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 类视图
from .admin import AttributeValueAutocomplete

# ViewSets
from .views import (
    ProductSPUViewSet, ProductReviewViewSet, CategoryViewSet, OrderViewSet,
    OrderItemReviewViewSet, UserOwnedProductViewSet
)

# 订单相关视图
from .views import pay_order, confirm_order

# Stripe 支付相关视图
from .views import create_checkout_session, stripe_webhook

# 创建路由器
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'spu', ProductSPUViewSet, basename='spu')
router.register(r'reviews', ProductReviewViewSet, basename='review')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-reviews', OrderItemReviewViewSet, basename='order-review')
router.register(r'owned-products', UserOwnedProductViewSet, basename='owned-product')

app_name = 'shopping'

urlpatterns = [
    # REST API 路由
    path('', include(router.urls)),
    
    # 商品属性值根据属性过滤后的视图
    path('attribute-value-autocomplete/', AttributeValueAutocomplete.as_view(), name='attribute-value-autocomplete'),
    
    # 订单操作
    path('orders/<int:order_id>/pay/', pay_order, name='pay_order'),
    path('orders/<int:order_id>/confirm/', confirm_order, name='confirm_order'),
    
    # Stripe 支付
    path('payments/create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('payments/webhook/', stripe_webhook, name='stripe_webhook'),
]
