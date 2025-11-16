from django.contrib import admin
from django.utils.html import format_html

from .models import Artist, Album, Music, Video, Notice

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_preview', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "无图片"
    image_preview.short_description = '图像'


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'image_preview', 'release_date', 'is_active', 'updated_at']
    search_fields = ['name', 'artist__name']
    list_filter = ['is_active', 'artist', 'release_date']

    def image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.cover_image.url)
        return "无图片"
    image_preview.short_description = '封面'


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'track_number', 'is_active', 'updated_at']
    search_fields = ['title', 'artist__name', 'album__name']
    list_filter = ['is_active', 'artist', 'album']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_type', 'is_active', 'created_at', 'updated_at']
    search_fields = ['title']
    list_filter = ['is_active', 'created_at']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'author__username']
    list_filter = ['is_active', 'author', 'created_at']