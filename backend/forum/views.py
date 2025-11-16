from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Tag, Post, Image, Reply
from .serializers import TagSerializer, PostSerializer, ImageSerializer, ReplySerializer
from .pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    
    def get_permissions(self):
        """
        读取操作允许所有人，创建/更新/删除操作只允许管理员
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPageNumberPagination  # 使用自定义分页
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']  # 默认按更新时间倒序

    def get_queryset(self):
        queryset = Post.objects.all()
        
        # 按作者过滤
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # 搜索标题或关联商品名称
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |  # 模糊搜索标题
                Q(products__name__icontains=search)  # 模糊搜索商品名称（从iexact改为icontains）
            ).distinct()
        
        # 按标签过滤（交集）
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_ids = [int(tag_id) for tag_id in tags.split(',') if tag_id.isdigit()]
            for tag_id in tag_ids:
                queryset = queryset.filter(tags__id=tag_id)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # 禁用分页，返回所有回复
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'author', 'parent']

    def get_queryset(self):
        queryset = Reply.objects.all()
        
        # 按帖子过滤
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_destroy(self, instance):
        # Django的CASCADE会自动删除子回复
        instance.delete()
