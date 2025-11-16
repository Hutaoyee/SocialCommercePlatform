from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

# 序列化器
from .serializers import RegisterSerializer
from .serializers import LoginSerializer
from .serializers import UserSerializer
from .serializers import PostFavoriteSerializer
from .serializers import ProductFavoriteSerializer
from .serializers import CartItemSerializer
from .serializers import AddressSerializer

# 模型
from .models import PostFavorite, ProductFavorite, CartItem, Address

# Create your views here.

# API视图
class RegisterView(APIView):
    permission_classes = [AllowAny]  # 允许未认证用户访问

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': '注册成功',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
class LoginView(APIView):
    permission_classes = [AllowAny]
        
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 生成 JWT Token
            refresh = RefreshToken.for_user(user)
            
            # 序列化用户完整信息
            user_serializer = UserSerializer(user, context={'request': request})
            
            return Response({
                'message': '登录成功',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
# 指定可以处理哪些方法
@api_view(['POST'])
# 指定权限类
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """上传或更新用户头像"""
    user = request.user
        
    # 检查是否有文件上传
    if 'avatar' not in request.FILES:
        return Response({'error': '请选择图片文件'}, status=status.HTTP_400_BAD_REQUEST)
        
    # 删除旧头像（如果存在且不是默认头像）
    if user.avatar and user.avatar.name != 'avatars/default.png':
        user.avatar.delete(save=False)
        
    # 保存新头像
    user.avatar = request.FILES['avatar']
    user.save()
        
    # 返回更新后的用户信息
    serializer = UserSerializer(user, context={'request': request})
        
    return Response({
        'message': '头像上传成功',
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_bio(request):
    user = request.user
    bio = request.data.get('bio', '')
        
    # 简单校验
    if not isinstance(bio, str):
        return Response({'error': 'bio 必须为字符串'}, status=status.HTTP_400_BAD_REQUEST)
        
    if len(bio) > 300:  # 根据需要调整长度限制
        return Response({'error': '个人简介不能超过 300 字符'}, status=status.HTTP_400_BAD_REQUEST)

    user.bio = bio
    user.save()

    serializer = UserSerializer(user, context={'request': request})
    return Response({
        'message': '个人简介更新成功', 
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """注销用户账户"""
    user = request.user
        
    # 获取用户提交的密码
    password = request.data.get('password', '')
        
    # 验证密码
    if not user.check_password(password):
        return Response({
            'error': '密码错误'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        # 删除用户头像文件（如果存在且不是默认头像）
        if user.avatar and user.avatar.name != 'avatars/default.png':
            user.avatar.delete(save=False)
                
        # 删除用户账户
        username = user.username
        user.delete()
                
        return Response({
            'message': f'账户 {username} 已成功注销'
        }, status=status.HTTP_200_OK)
                
    except Exception as e:
        return Response({
            'error': f'账户注销失败：{str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 自定义分页类，允许客户端指定page_size
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


# 帖子收藏ViewSet
class PostFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = PostFavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
        
    def get_queryset(self):
        return PostFavorite.objects.filter(user=self.request.user).select_related(
            'post', 
            'post__author'
        ).prefetch_related(
            'post__images',
            'post__tags',
            'post__products'
        )
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_context(self):
        """添加request到序列化器上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_favorite(request, post_id):
    user = request.user
    try:
        favorite = PostFavorite.objects.filter(user=user, post_id=post_id).first()
        if favorite:
            favorite.delete()
            return Response({'message': '已取消收藏', 'is_favorited': False}, status=status.HTTP_200_OK)
        else:
            PostFavorite.objects.create(user=user, post_id=post_id)
            return Response({'message': '收藏成功', 'is_favorited': True}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'操作失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_post_favorite(request, post_id):
    user = request.user
    is_favorited = PostFavorite.objects.filter(user=user, post_id=post_id).exists()
    return Response({'is_favorited': is_favorited}, status=status.HTTP_200_OK)


# 商品收藏管理 ViewSet
class ProductFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = ProductFavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return ProductFavorite.objects.filter(user=self.request.user).select_related(
            'product', 
            'user'
        ).prefetch_related(
            'product__images'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_context(self):
        """添加request到序列化器上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_product_favorite(request, product_id):
    user = request.user
    try:
        favorite = ProductFavorite.objects.filter(user=user, product_id=product_id).first()
        if favorite:
            favorite.delete()
            return Response({'message': '已取消收藏', 'is_favorited': False}, status=status.HTTP_200_OK)
        else:
            ProductFavorite.objects.create(user=user, product_id=product_id)
            return Response({'message': '收藏成功', 'is_favorited': True}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'操作失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_product_favorite(request, product_id):
    user = request.user
    is_favorited = ProductFavorite.objects.filter(user=user, product_id=product_id).exists()
    return Response({'is_favorited': is_favorited}, status=status.HTTP_200_OK)


# 购物车管理 ViewSet
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related(
            'sku__spu',
            'sku__inventory'
        ).prefetch_related('sku__spu__images')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_context(self):
        """添加request到序列化器上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """添加商品到购物车"""
    user = request.user
    sku_code = request.data.get('sku_code')
    quantity = request.data.get('quantity', 1)
    
    if not sku_code:
        return Response({'error': 'sku_code是必需的'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from shopping.models import ProductSKU
        sku = ProductSKU.objects.get(sku_code=sku_code, is_active=True)
        
        # 检查库存
        inventory = getattr(sku, 'inventory', None)
        if not inventory or inventory.quantity < quantity:
            return Response({'error': '库存不足'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果已存在，更新数量
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            sku=sku,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if inventory.quantity < new_quantity:
                return Response({'error': '库存不足'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item, context={'request': request})
        return Response({
            'message': '添加到购物车成功',
            'cart_item': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except ProductSKU.DoesNotExist:
        return Response({'error': 'SKU不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'操作失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_quantity(request, cart_item_id):
    """更新购物车商品数量"""
    user = request.user
    quantity = request.data.get('quantity')
    
    if quantity is None or quantity < 1:
        return Response({'error': '数量必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=user)
        
        # 检查库存
        inventory = getattr(cart_item.sku, 'inventory', None)
        if not inventory or inventory.quantity < quantity:
            return Response({'error': '库存不足'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartItemSerializer(cart_item, context={'request': request})
        return Response({
            'message': '更新成功',
            'cart_item': serializer.data
        }, status=status.HTTP_200_OK)
        
    except CartItem.DoesNotExist:
        return Response({'error': '购物车项不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, cart_item_id):
    """从购物车移除商品"""
    user = request.user
    
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=user)
        cart_item.delete()
        return Response({'message': '已从购物车移除'}, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({'error': '购物车项不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_remove_from_cart(request):
    """批量删除购物车商品"""
    user = request.user
    cart_item_ids = request.data.get('cart_item_ids', [])
    
    if not cart_item_ids or not isinstance(cart_item_ids, list):
        return Response({'error': 'cart_item_ids必须是数组'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        deleted_count = CartItem.objects.filter(id__in=cart_item_ids, user=user).delete()[0]
        return Response({
            'message': f'成功删除{deleted_count}个商品',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'删除失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 地址管理 ====================

class AddressViewSet(viewsets.ModelViewSet):
    """地址管理 ViewSet"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # 禁用分页，直接返回数组
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-id')
    
    def perform_create(self, serializer):
        # 不在这里设置user，让序列化器的create方法处理
        serializer.save()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_default_address(request, address_id):
    """设置默认地址"""
    user = request.user
    
    try:
        address = Address.objects.get(id=address_id, user=user)
        
        # 取消其他地址的默认状态
        Address.objects.filter(user=user, is_default=True).update(is_default=False)
        
        # 设置当前地址为默认
        address.is_default = True
        address.save()
        
        serializer = AddressSerializer(address)
        return Response({
            'message': '默认地址设置成功',
            'address': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Address.DoesNotExist:
        return Response({'error': '地址不存在'}, status=status.HTTP_404_NOT_FOUND)