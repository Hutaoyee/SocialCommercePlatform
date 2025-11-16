from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from .models import PostFavorite, ProductFavorite, CartItem, Address
from forum.serializers import PostSerializer

User = get_user_model()  # 获取自定义的 User 模型

class RegisterSerializer(serializers.ModelSerializer):
    # write_only=True: 密码只能写入（注册时），不能读取（查询用户时不返回密码）
    # min_length=6: 密码最少 6 个字符
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已存在")
        return value
    
    # 所有验证通过后，DRF 调用 create() 方法
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        error_messages={
            'required': '请输入用户名',
            'blank': '用户名不能为空'
        }
    )
    
    password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': '请输入密码',
            'blank': '密码不能为空'
        }
    )
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('用户已被禁用')
            else:
                raise serializers.ValidationError('用户名或密码错误')
        else:
            raise serializers.ValidationError('必须提供用户名和密码')
        
        return data

# 用户信息序列化器（用于返回完整用户信息）
class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'gender', 'avatar', 'date_joined', 'is_superuser', 'is_staff']
        read_only_fields = ['id', 'date_joined']
    
    def get_avatar(self, obj):
        """返回头像完整 URL"""
        request = self.context.get('request')
        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
class PostFavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.SerializerMethodField()

    class Meta:
        model = PostFavorite
        fields = ['id', 'user', 'post']
        read_only_fields = ['user']
    
    def get_post(self, obj):
        """使用PostSerializer序列化post对象，并传递request上下文"""
        from forum.serializers import PostSerializer
        request = self.context.get('request')
        return PostSerializer(obj.post, context={'request': request}).data

class ProductFavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = serializers.SerializerMethodField()

    class Meta:
        model = ProductFavorite
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def get_product(self, obj):
        """使用ProductSPUSerializer序列化product对象，并传递request上下文"""
        from shopping.serializers import ProductSPUSerializer
        request = self.context.get('request')
        return ProductSPUSerializer(obj.product, context={'request': request}).data


class CartItemSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    sku = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'sku', 'quantity', 'total_price']
        read_only_fields = ['user', 'total_price']
    
    def get_sku(self, obj):
        """获取SKU详细信息，包括SKU图片"""
        request = self.context.get('request')
        sku = obj.sku
        
        # 获取SKU图片，如果没有则使用SPU主图
        sku_image = sku.images.first()
        spu_main_image = sku.spu.images.filter(is_main=True).first()
        
        if sku_image:
            image_url = request.build_absolute_uri(sku_image.image.url) if request else sku_image.image.url
        elif spu_main_image:
            image_url = request.build_absolute_uri(spu_main_image.image.url) if request else spu_main_image.image.url
        else:
            image_url = None
        
        # 获取库存信息
        inventory = getattr(sku, 'inventory', None)
        stock = inventory.quantity if inventory else 0
        
        # 检查商品是否失效（SKU或SPU不可用）
        is_active = sku.is_active and sku.spu.is_active
        
        return {
            'sku_code': sku.sku_code,
            'title': sku.title,
            'price': str(sku.price),
            'stock': stock,
            'is_active': is_active,
            'image': image_url,
            'spu_name': sku.spu.name,
            'spu_id': sku.spu.id
        }


# 地址序列化器
class AddressSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Address
        fields = ['id', 'user', 'name', 'phone', 'province', 'city', 'district', 'address', 'is_default']
        read_only_fields = ['user']
    
    def validate_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入正确的手机号')
        return value
    
    def create(self, validated_data):
        """创建地址时，如果是第一个地址，自动设为默认"""
        user = self.context['request'].user
        validated_data['user'] = user
        if not Address.objects.filter(user=user).exists():
            validated_data['is_default'] = True
        return super().create(validated_data)