from rest_framework import serializers
from .models import Artist, Album, Music, Video, Notice

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    product_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Album
        fields = '__all__'
    
    def get_product_info(self, obj):
        if obj.product:
            # 获取主图
            main_image = obj.product.images.filter(is_main=True).first()
            if not main_image:
                # 如果没有主图，获取第一张图片
                main_image = obj.product.images.first()
            
            return {
                'id': obj.product.id,
                'name': obj.product.name,
                'description': obj.product.description,
                'image': main_image.image.url if main_image else None,
            }
        return None

class MusicSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    class Meta:
        model = Music
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class NoticeSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Notice
        fields = '__all__'