from rest_framework import serializers
from .models import Tag, Post, Image, Reply
from django.apps import apps  # 用于延迟导入模型

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ReplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = '__all__'

    def get_author(self, obj):
        request = self.context.get('request')
        avatar_url = obj.author.avatar.url if obj.author.avatar else None

        if avatar_url and request:
            avatar_url = request.build_absolute_uri(avatar_url)

        return {
            'id': obj.author.id,
            'name': obj.author.username,
            'avatar': avatar_url
        }

    def get_children(self, obj):
        children = obj.children.all()
        return ReplySerializer(children, many=True, context=self.context).data

class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    products = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(), 
        write_only=True, 
        required=False,
        source='tags'
    )

    image_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Image.objects.all(), 
        write_only=True, 
        required=False,
        source='images'
    )

    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        product_ids = validated_data.pop('product_ids', [])
        post = super().create(validated_data)
        
        if product_ids:
            ProductSPU = apps.get_model('shopping', 'ProductSPU')
            products = ProductSPU.objects.filter(id__in=product_ids)
            post.products.set(products)
        
        return post

    def update(self, instance, validated_data):
        product_ids = validated_data.pop('product_ids', None)
        post = super().update(instance, validated_data)
        
        if product_ids is not None:
            ProductSPU = apps.get_model('shopping', 'ProductSPU')
            products = ProductSPU.objects.filter(id__in=product_ids)
            post.products.set(products)
        
        return post

    def get_author(self, obj):
        request = self.context.get('request')
        avatar_url = obj.author.avatar.url if obj.author.avatar else None

        if avatar_url and request:
            avatar_url = request.build_absolute_uri(avatar_url)

        return {
            'id': obj.author.id,
            'name': obj.author.username,
            'avatar': avatar_url
        }
    
    def get_products(self, obj):
        """返回关联商品信息，包含图片"""
        request = self.context.get('request')
        products = obj.products.all()
        result = []
        for product in products:
            # 获取主图
            image = product.images.filter(is_main=True).first()
            image_url = None
            if image:
                if request:
                    try:
                        image_url = request.build_absolute_uri(image.image.url)
                    except Exception:
                        image_url = image.image.url
                else:
                    image_url = image.image.url
            
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'image': image_url
            })
        return result