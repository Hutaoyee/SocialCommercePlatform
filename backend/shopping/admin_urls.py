"""
管理页面 URL 配置
路径: /manage/shopping/
"""
from django.urls import path
from . import admin_views, order_views

app_name = 'shopping_manage'

urlpatterns = [
    # ==================== 商品管理 ====================
    # SPU管理
    path('products/', admin_views.product_management, name='product_list'),
    path('products/create/', admin_views.spu_create, name='spu_create'),
    path('products/<int:spu_id>/edit/', admin_views.spu_edit, name='spu_edit'),
    path('products/<int:spu_id>/delete/', admin_views.spu_delete, name='spu_delete'),
    path('products/image/<int:image_id>/delete/', admin_views.image_delete, name='image_delete'),
    
    # SKU管理
    path('products/<int:spu_id>/skus/', admin_views.sku_management, name='sku_list'),
    path('products/<int:spu_id>/skus/create/', admin_views.sku_create, name='sku_create'),
    path('skus/<str:sku_code>/edit/', admin_views.sku_edit, name='sku_edit'),
    path('skus/<str:sku_code>/delete/', admin_views.sku_delete, name='sku_delete'),
    
    # 属性管理
    path('attributes/', admin_views.attribute_management, name='attribute_list'),
    path('attributes/create/', admin_views.attribute_create, name='attribute_create'),
    path('attributes/<int:attr_id>/delete/', admin_views.attribute_delete, name='attribute_delete'),
    path('attributes/<int:attr_id>/values/create/', admin_views.attribute_value_create, name='attribute_value_create'),
    path('attributes/values/<int:value_id>/delete/', admin_views.attribute_value_delete, name='attribute_value_delete'),
    
    # SPU属性关联
    path('products/<int:spu_id>/attributes/', admin_views.spu_attribute_management, name='spu_attributes'),
    
    # 分类管理
    path('categories/', admin_views.category_management, name='category_list'),
    path('categories/create/', admin_views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', admin_views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', admin_views.category_delete, name='category_delete'),
    
    # ==================== 订单管理 ====================
    # 订单管理
    path('orders/', order_views.order_management, name='order_list'),
    path('orders/<int:order_id>/', order_views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', order_views.order_update_status, name='order_update_status'),
    path('orders/<int:order_id>/mark-shipped/', order_views.order_mark_shipped, name='order_mark_shipped'),
    path('orders/<int:order_id>/update-shipping/', order_views.order_update_shipping, name='order_update_shipping'),
    path('orders/batch-ship/', order_views.order_batch_ship, name='order_batch_ship'),
    
    # 退款管理
    path('refunds/', order_views.refund_management, name='refund_list'),
    path('refunds/<int:refund_id>/', order_views.refund_detail, name='refund_detail'),
    path('refunds/<int:refund_id>/approve/', order_views.refund_approve, name='refund_approve'),
    path('refunds/<int:refund_id>/reject/', order_views.refund_reject, name='refund_reject'),
    path('refunds/batch-approve/', order_views.refund_batch_approve, name='refund_batch_approve'),
    
    # 评价管理
    path('reviews/', order_views.review_management, name='review_list'),
    path('reviews/<int:review_id>/delete/', order_views.review_delete, name='review_delete'),
]
