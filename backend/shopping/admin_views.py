from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_http_methods
import json

from .models import (
    ProductSPU, ProductSKU, Category, Attribute, AttributeValue,
    ProductSPUAttribute, ProductSKUAttributeValue, Inventory, ProductImage
)


def is_staff(user):
    """检查用户是否为管理员"""
    return user.is_authenticated and user.is_staff


def get_categories_with_level():
    """获取带层级的分类列表"""
    categories = Category.objects.all().order_by('tree_id', 'lft')
    result = []
    for cat in categories:
        indent = '　' * cat.level  # 使用全角空格缩进
        prefix = '└ ' if cat.level > 0 else ''
        result.append({
            'id': cat.id,
            'name': cat.name,
            'display_name': f"{indent}{prefix}{cat.name}",
            'level': cat.level
        })
    return result


# ==================== SPU管理 ====================

@login_required
@user_passes_test(is_staff)
def product_management(request):
    """商品管理主页 - SPU列表"""
    spus = ProductSPU.objects.all().select_related('category').order_by('-created_at')
    categories = get_categories_with_level()
    
    # 搜索过滤
    search = request.GET.get('search', '')
    if search:
        spus = spus.filter(name__icontains=search)
    
    # 分类过滤（包含子分类）
    category_id = request.GET.get('category', '')
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            # 获取该分类及其所有子分类
            descendant_categories = category.get_descendants(include_self=True)
            spus = spus.filter(category__in=descendant_categories)
        except Category.DoesNotExist:
            pass
    
    context = {
        'spus': spus,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
    }
    return render(request, 'shopping/product_list.html', context)


@login_required
@user_passes_test(is_staff)
def spu_create(request):
    """创建SPU"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category')
            brand = request.POST.get('brand', '')
            series = request.POST.get('series', '')
            is_active = request.POST.get('is_active') == 'on'
            
            # 创建SPU
            spu = ProductSPU.objects.create(
                name=name,
                description=description,
                category_id=category_id,
                brand=brand,
                series=series,
                is_active=is_active
            )
            
            # 处理主图上传（只上传一张）
            image = request.FILES.get('images')
            if image:
                ProductImage.objects.create(
                    spu=spu,
                    image=image,
                    is_main=True  # 标记为主图
                )
            
            messages.success(request, f'SPU "{name}" 创建成功！')
            return redirect('shopping_manage:product_list')
        
        except Exception as e:
            messages.error(request, f'创建失败: {str(e)}')
    
    categories = get_categories_with_level()
    context = {'categories': categories}
    return render(request, 'shopping/spu_form.html', context)


@login_required
@user_passes_test(is_staff)
def spu_edit(request, spu_id):
    """编辑SPU"""
    spu = get_object_or_404(ProductSPU, id=spu_id)
    
    if request.method == 'POST':
        try:
            spu.name = request.POST.get('name')
            spu.description = request.POST.get('description', '')
            spu.category_id = request.POST.get('category')
            spu.brand = request.POST.get('brand', '')
            spu.series = request.POST.get('series', '')
            spu.is_active = request.POST.get('is_active') == 'on'
            spu.save()
            
            # 处理新上传的主图（如果有）
            image = request.FILES.get('images')
            if image:
                # 删除旧的主图
                ProductImage.objects.filter(spu=spu, is_main=True).delete()
                # 创建新的主图
                ProductImage.objects.create(
                    spu=spu,
                    image=image,
                    is_main=True
                )
            
            messages.success(request, f'SPU "{spu.name}" 更新成功！')
            return redirect('shopping_manage:product_list')
        
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
    
    categories = get_categories_with_level()
    context = {
        'spu': spu,
        'categories': categories,
        'images': spu.images.filter(is_main=True)  # 只获取主图
    }
    return render(request, 'shopping/spu_form.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def spu_delete(request, spu_id):
    """删除SPU"""
    spu = get_object_or_404(ProductSPU, id=spu_id)
    spu_name = spu.name
    spu.delete()
    messages.success(request, f'SPU "{spu_name}" 已删除！')
    return redirect('shopping_manage:product_list')


@require_http_methods(["POST"])
def image_delete(request, image_id):
    """删除商品图片"""
    # 检查权限
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': '无权限'}, status=403)
    
    try:
        image = get_object_or_404(ProductImage, id=image_id)
        image.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ==================== SKU管理 ====================

@login_required
@user_passes_test(is_staff)
def sku_management(request, spu_id):
    """SKU管理页面"""
    spu = get_object_or_404(ProductSPU, id=spu_id)
    skus = ProductSKU.objects.filter(spu=spu).prefetch_related(
        'attribute_values__attribute',
        'attribute_values__attribute_value',
        'inventory'
    )
    
    # 获取SPU的属性
    spu_attributes = ProductSPUAttribute.objects.filter(spu=spu).select_related('attribute')
    
    context = {
        'spu': spu,
        'skus': skus,
        'spu_attributes': spu_attributes,
    }
    return render(request, 'shopping/sku_list.html', context)


@login_required
@user_passes_test(is_staff)
def sku_create(request, spu_id):
    """创建SKU"""
    spu = get_object_or_404(ProductSPU, id=spu_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                title = request.POST.get('title')
                price = request.POST.get('price')
                stock = request.POST.get('stock', 0)
                is_active = request.POST.get('is_active') == 'on'
                
                # 创建SKU
                sku = ProductSKU.objects.create(
                    spu=spu,
                    title=title,
                    price=price,
                    is_active=is_active
                )
                
                # 创建库存
                Inventory.objects.create(
                    sku=sku,
                    quantity=int(stock)
                )
                
                # 处理属性值
                spu_attributes = ProductSPUAttribute.objects.filter(spu=spu)
                for spu_attr in spu_attributes:
                    attr_id = spu_attr.attribute.id
                    attr_value_id = request.POST.get(f'attr_{attr_id}')
                    if attr_value_id:
                        ProductSKUAttributeValue.objects.create(
                            sku=sku,
                            attribute_id=attr_id,
                            attribute_value_id=attr_value_id
                        )
                
                # 处理图片上传
                images = request.FILES.getlist('images')
                for idx, image in enumerate(images):
                    ProductImage.objects.create(
                        spu=spu,  # 同时绑定SPU
                        sku=sku,  # 绑定SKU
                        image=image,
                        is_main=False  # SKU的图片不能设为主图
                    )
                
                messages.success(request, f'SKU "{title}" 创建成功！')
                return redirect('shopping_manage:sku_list', spu_id=spu_id)
        
        except Exception as e:
            messages.error(request, f'创建失败: {str(e)}')
    
    # 获取SPU的属性及其可选值
    spu_attributes = ProductSPUAttribute.objects.filter(spu=spu).select_related('attribute')
    attributes_with_values = []
    for spu_attr in spu_attributes:
        attribute = spu_attr.attribute
        values = AttributeValue.objects.filter(attribute=attribute)
        attributes_with_values.append({
            'attribute': attribute,
            'values': values
        })
    
    context = {
        'spu': spu,
        'attributes_with_values': attributes_with_values,
    }
    return render(request, 'shopping/sku_form.html', context)


@login_required
@user_passes_test(is_staff)
def sku_edit(request, sku_code):
    """编辑SKU"""
    sku = get_object_or_404(ProductSKU, sku_code=sku_code)
    spu = sku.spu
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                sku.title = request.POST.get('title')
                sku.price = request.POST.get('price')
                sku.is_active = request.POST.get('is_active') == 'on'
                sku.save()
                
                # 更新库存
                stock = request.POST.get('stock', 0)
                inventory, created = Inventory.objects.get_or_create(sku=sku)
                inventory.quantity = int(stock)
                inventory.save()
                
                # 更新属性值
                sku.attribute_values.all().delete()
                spu_attributes = ProductSPUAttribute.objects.filter(spu=spu)
                for spu_attr in spu_attributes:
                    attr_id = spu_attr.attribute.id
                    attr_value_id = request.POST.get(f'attr_{attr_id}')
                    if attr_value_id:
                        ProductSKUAttributeValue.objects.create(
                            sku=sku,
                            attribute_id=attr_id,
                            attribute_value_id=attr_value_id
                        )
                
                # 处理新上传的图片
                images = request.FILES.getlist('images')
                if images:
                    for image in images:
                        ProductImage.objects.create(
                            spu=spu,  # 同时绑定SPU
                            sku=sku,  # 绑定SKU
                            image=image,
                            is_main=False  # SKU的图片不能设为主图
                        )
                
                messages.success(request, f'SKU "{sku.title}" 更新成功！')
                return redirect('shopping_manage:sku_list', spu_id=spu.id)
        
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
    
    # 获取SPU的属性及其可选值
    spu_attributes = ProductSPUAttribute.objects.filter(spu=spu).select_related('attribute')
    attributes_with_values = []
    current_values = {}
    
    for sku_attr_value in sku.attribute_values.all():
        current_values[sku_attr_value.attribute.id] = sku_attr_value.attribute_value.id
    
    for spu_attr in spu_attributes:
        attribute = spu_attr.attribute
        values = AttributeValue.objects.filter(attribute=attribute)
        attributes_with_values.append({
            'attribute': attribute,
            'values': values,
            'current_value': current_values.get(attribute.id)
        })
    
    inventory = getattr(sku, 'inventory', None)
    sku_images = ProductImage.objects.filter(sku=sku).order_by('-is_main', 'id')
    
    context = {
        'sku': sku,
        'spu': spu,
        'attributes_with_values': attributes_with_values,
        'current_stock': inventory.quantity if inventory else 0,
        'sku_images': sku_images,
    }
    return render(request, 'shopping/sku_form.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def sku_delete(request, sku_code):
    """删除SKU"""
    sku = get_object_or_404(ProductSKU, sku_code=sku_code)
    spu_id = sku.spu.id
    sku_title = sku.title
    sku.delete()
    messages.success(request, f'SKU "{sku_title}" 已删除！')
    return redirect('shopping_manage:sku_list', spu_id=spu_id)


# ==================== 属性管理 ====================

@login_required
@user_passes_test(is_staff)
def attribute_management(request):
    """属性管理页面"""
    attributes = Attribute.objects.prefetch_related('values').all()
    
    context = {
        'attributes': attributes,
    }
    return render(request, 'shopping/attribute_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def attribute_create(request):
    """创建属性"""
    try:
        name = request.POST.get('name')
        attribute = Attribute.objects.create(name=name)
        messages.success(request, f'属性 "{name}" 创建成功！')
    except Exception as e:
        messages.error(request, f'创建失败: {str(e)}')
    
    return redirect('shopping_manage:attribute_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def attribute_delete(request, attr_id):
    """删除属性"""
    attribute = get_object_or_404(Attribute, id=attr_id)
    attr_name = attribute.name
    attribute.delete()
    messages.success(request, f'属性 "{attr_name}" 已删除！')
    return redirect('shopping_manage:attribute_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def attribute_value_create(request, attr_id):
    """创建属性值"""
    try:
        attribute = get_object_or_404(Attribute, id=attr_id)
        value = request.POST.get('value')
        AttributeValue.objects.create(attribute=attribute, value=value)
        messages.success(request, f'属性值 "{value}" 创建成功！')
    except Exception as e:
        messages.error(request, f'创建失败: {str(e)}')
    
    return redirect('shopping_manage:attribute_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def attribute_value_delete(request, value_id):
    """删除属性值"""
    attr_value = get_object_or_404(AttributeValue, id=value_id)
    value_str = attr_value.value
    attr_value.delete()
    messages.success(request, f'属性值 "{value_str}" 已删除！')
    return redirect('shopping_manage:attribute_list')


# ==================== SPU属性关联管理 ====================

@login_required
@user_passes_test(is_staff)
def spu_attribute_management(request, spu_id):
    """SPU属性关联管理"""
    spu = get_object_or_404(ProductSPU, id=spu_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 清除现有关联
                ProductSPUAttribute.objects.filter(spu=spu).delete()
                
                # 添加新的关联
                attribute_ids = request.POST.getlist('attributes')
                for attr_id in attribute_ids:
                    ProductSPUAttribute.objects.create(
                        spu=spu,
                        attribute_id=attr_id
                    )
                
                messages.success(request, 'SPU属性更新成功！')
                return redirect('shopping_manage:product_list')
        
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
    
    all_attributes = Attribute.objects.all()
    current_attributes = ProductSPUAttribute.objects.filter(spu=spu).values_list('attribute_id', flat=True)
    
    context = {
        'spu': spu,
        'all_attributes': all_attributes,
        'current_attributes': list(current_attributes),
    }
    return render(request, 'shopping/spu_attribute.html', context)


# ==================== 分类管理 ====================

@login_required
@user_passes_test(is_staff)
def category_management(request):
    """分类管理主页"""
    categories = Category.objects.all().order_by('tree_id', 'lft')
    categories_with_level = get_categories_with_level()
    
    # 计算顶级分类数量
    root_categories_count = Category.objects.filter(level=0).count()
    
    context = {
        'categories': categories,
        'categories_with_level': categories_with_level,
        'root_categories_count': root_categories_count,
    }
    return render(request, 'shopping/category_list.html', context)


@login_required
@user_passes_test(is_staff)
def category_create(request):
    """创建分类"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            parent_id = request.POST.get('parent')
            
            if not name:
                messages.error(request, '分类名称不能为空！')
                return redirect('shopping_manage:category_list')
            
            # 创建分类
            if parent_id:
                parent = get_object_or_404(Category, id=parent_id)
                category = Category.objects.create(name=name, parent=parent)
            else:
                category = Category.objects.create(name=name)
            
            messages.success(request, f'分类 "{name}" 创建成功！')
            return redirect('shopping_manage:category_list')
        
        except Exception as e:
            messages.error(request, f'创建失败: {str(e)}')
            return redirect('shopping_manage:category_list')
    
    # GET请求，显示创建表单
    categories = get_categories_with_level()
    context = {
        'categories': categories,
    }
    return render(request, 'shopping/category_form.html', context)


@login_required
@user_passes_test(is_staff)
def category_edit(request, category_id):
    """编辑分类"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            parent_id = request.POST.get('parent')
            
            if not name:
                messages.error(request, '分类名称不能为空！')
                return redirect('shopping_manage:category_list')
            
            # 检查是否试图将分类设置为自己的子分类
            if parent_id:
                parent = get_object_or_404(Category, id=parent_id)
                if parent == category or parent in category.get_descendants():
                    messages.error(request, '不能将分类设置为自己或自己的子分类的父分类！')
                    return redirect('shopping_manage:category_edit', category_id=category_id)
                category.parent = parent
            else:
                category.parent = None
            
            category.name = name
            category.save()
            
            messages.success(request, f'分类 "{name}" 更新成功！')
            return redirect('shopping_manage:category_list')
        
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
    
    # 获取可选的父分类（排除自己和自己的子分类）
    all_categories = get_categories_with_level()
    descendants_ids = set(category.get_descendants(include_self=True).values_list('id', flat=True))
    available_categories = [cat for cat in all_categories if cat['id'] not in descendants_ids]
    
    context = {
        'category': category,
        'categories': available_categories,
        'is_edit': True,
    }
    return render(request, 'shopping/category_form.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def category_delete(request, category_id):
    """删除分类"""
    category = get_object_or_404(Category, id=category_id)
    
    # 检查是否有子分类
    if category.get_children().exists():
        messages.error(request, f'分类 "{category.name}" 包含子分类，请先删除子分类！')
        return redirect('shopping_manage:category_list')
    
    # 检查是否有商品使用该分类
    if ProductSPU.objects.filter(category=category).exists():
        messages.error(request, f'分类 "{category.name}" 下有商品，无法删除！')
        return redirect('shopping_manage:category_list')
    
    category_name = category.name
    category.delete()
    messages.success(request, f'分类 "{category_name}" 已删除！')
    return redirect('shopping_manage:category_list')
