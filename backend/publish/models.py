from django.db import models

# 动态图片上传路径函数
def album_upload_path(instance, filename):

    if instance.artist:
        artist = (instance.artist.name or 'no_artist').replace(' ', '_')  # 替换空格为下划线
        return f'publish/album/{artist}/{filename}'
    else:
        return f'publish/album/other/{filename}'  # 默认路径

def music_upload_path(instance, filename):

    if instance.artist:
        artist = (instance.artist.name or 'no_artist').replace(' ', '_')  # 替换空格为下划线
        album = (instance.album.name if instance.album else 'no_album').replace(' ', '_')  # 检查album是否存在
        return f'publish/music/{artist}/{album}/{filename}'
    else:
        return f'publish/music/other/{filename}'  # 默认路径

# Create your models here.

class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="艺术家姓名")
    image = models.ImageField(upload_to='publish/artists/', blank=True, verbose_name="艺术家图片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "艺术家"
        verbose_name_plural = "艺术家"
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class Album(models.Model):
    name = models.CharField(max_length=200, verbose_name="专辑名")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name="艺术家")
    cover_image = models.ImageField(upload_to=album_upload_path, blank=True, verbose_name="封面图片")
    release_date = models.DateField(blank=True, null=True, verbose_name="发行日期")
    description = models.TextField(blank=True, verbose_name="描述")
    product = models.ForeignKey('shopping.ProductSPU', on_delete=models.SET_NULL, null=True, blank=True, related_name='albums', verbose_name="关联商品")
    is_active = models.BooleanField(default=True, verbose_name="是否发布")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "专辑"
        verbose_name_plural = "专辑"
        indexes = [
            models.Index(fields=['artist']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.artist.name}"
    
class Music(models.Model):
    title = models.CharField(max_length=200, verbose_name="音乐标题")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name="艺术家")
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, related_name='tracks', blank=True, null=True, verbose_name="所属专辑")
    track_number = models.PositiveIntegerField(blank=True, null=True, verbose_name="轨道号")
    duration = models.DurationField(blank=True, null=True, verbose_name="时长")
    file = models.FileField(upload_to=music_upload_path, blank=True, verbose_name="音乐文件")
    is_active = models.BooleanField(default=True, verbose_name="是否发布")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "音乐"
        verbose_name_plural = "音乐"
        indexes = [
            models.Index(fields=['artist']),
            models.Index(fields=['album']),
            models.Index(fields=['track_number']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    # 获取所属专辑的封面图片
    @property
    def cover_image(self):
        if self.album and self.album.cover_image:
            return self.album.cover_image
        return None  # 或返回默认图片路径
    
class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name="视频标题")
    description = models.TextField(blank=True, verbose_name="描述")
    video_type = models.CharField(max_length=20, choices=[('live', 'Live'), ('interview', 'Interview'), ('documentary', 'Documentary')], default='live', verbose_name="视频类型")
    file = models.FileField(upload_to='videos/', blank=True, null=True, verbose_name="视频文件")
    bilibili_url = models.URLField(blank=True, null=True, verbose_name="B站外链")
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, verbose_name="缩略图")
    duration = models.DurationField(blank=True, null=True, verbose_name="时长")
    is_active = models.BooleanField(default=True, verbose_name="是否发布")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = "视频"
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title
    
class Notice(models.Model):
    title = models.CharField(max_length=200, verbose_name="公告标题")
    content = models.TextField(verbose_name="公告内容")
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name="发布者")
    is_active = models.BooleanField(default=True, verbose_name="是否发布")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "公告"
        verbose_name_plural = "公告"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title