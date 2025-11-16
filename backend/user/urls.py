from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView, LoginView, PostFavoriteViewSet, ProductFavoriteViewSet, CartItemViewSet,
    AddressViewSet, upload_avatar, delete_account, update_bio,
    toggle_post_favorite, check_post_favorite,
    toggle_product_favorite, check_product_favorite,
    add_to_cart, update_cart_quantity, remove_from_cart, batch_remove_from_cart,
    set_default_address
)

router = DefaultRouter()
router.register(r'post-favorites', PostFavoriteViewSet, basename='post-favorite')
router.register(r'product-favorites', ProductFavoriteViewSet, basename='product-favorite')
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('upload-avatar/', upload_avatar, name='upload_avatar'),
    path('delete-account/', delete_account, name='delete_account'),
    path('update-bio/', update_bio, name='update_bio'),
    path('posts/<int:post_id>/favorite/', toggle_post_favorite, name='toggle_post_favorite'),
    path('posts/<int:post_id>/check-favorite/', check_post_favorite, name='check_post_favorite'),
    path('products/<int:product_id>/favorite/', toggle_product_favorite, name='toggle_product_favorite'),
    path('products/<int:product_id>/check-favorite/', check_product_favorite, name='check_product_favorite'),
    path('cart-add/', add_to_cart, name='add_to_cart'),
    path('cart-update/<int:cart_item_id>/', update_cart_quantity, name='update_cart_quantity'),
    path('cart-remove/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart-batch-remove/', batch_remove_from_cart, name='batch_remove_from_cart'),
    path('addresses/<int:address_id>/set-default/', set_default_address, name='set_default_address'),
]