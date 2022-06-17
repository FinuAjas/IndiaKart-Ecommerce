from multiprocessing import context
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Account
from category.forms import CategoryForm
from category.models import Category
from orders.forms import OrderStatusForm
from orders.models import Order
from store.models import Product, Variation
from store.forms import ProductForm, ProductGalleryForm, VariationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify


#Admin Home

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminhome(request):
    if request.user.is_authenticated:
        if request.user.is_superadmin:
            users = Account.objects.all()
            categories = Category.objects.all()
            products = Product.objects.all()

            context = {
                'users':users,
                'categories':categories,
                'products':products}
            return render(request, 'admin/adminhome.html',context)    
        else:
            return redirect('admin_login')

    else:
        return redirect('admin_login')  

#Admin Login Logout

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('adminemail')
        password = request.POST.get('adminpassword')
        user = authenticate(email=email, password=password)

        if user.is_superadmin:
            login(request,user)
            # request.session['admin'] = True
            return redirect('adminhome')
        else:
            return redirect('admin_login')
    return render(request, 'admin/admin_login.html')


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_logout(request):
    logout(request)
    # del request.session['adminkey']
    return redirect('admin_login')    
  
        
#Admin Product Management

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_product_list(request):
        if request.user.is_authenticated:
            if request.user.is_superadmin:
                # if request.session.has_key('adminkey'):
                products = Product.objects.all()
                context = {
                    'products' : products
                    }
                return render(request, 'admin/admin_product_list.html', context)  
            else:
                return redirect('admin_login')
        else:
            return redirect('admin_login')     


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_add_product(request):
        if request.user.is_authenticated:
            if request.user.is_superadmin:
                if request.method == 'POST':
                    form = ProductForm(request.POST or None, request.FILES or None)
                    if form.is_valid():
                        product_name = form.cleaned_data['product_name']
                        slug = slugify(product_name)
                    
                        description = form.cleaned_data['description']
                        price = form.cleaned_data['price']
                        images = form.cleaned_data['images']
                        stock = form.cleaned_data['stock']
                        is_available = form.cleaned_data['is_available']
                        category = form.cleaned_data['category']
                        
                        product = Product.objects.create(product_name=product_name, slug=slug, description=description, price=price, images=images, stock=stock,is_available=is_available,category=category)
                        product.save()
                        return redirect('admin_product_list')

                    else:
                        form = ProductForm(request.POST or None, request.FILES or None)
                        context = {
                                'form':form
                            }
                    return render(request, 'admin/admin_add_product.html', context)

                else:
                    form = ProductForm(request.POST or None, request.FILES or None)
                    context = {
                                'form':form
                            }
                    return render(request, 'admin/admin_add_product.html', context)
            else:
                return redirect('admin/admin_login')

        else:
            return redirect('admin_login')              


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_edit_product(request ,id):
    if request.user.is_authenticated:
        if request.user.is_superadmin:
            instance = get_object_or_404(Product, id=id)
            form = ProductForm(request.POST or None, request.FILES or None, instance=instance)
            if request.method == "POST":
                if form.is_valid():
                    form.save()
                    messages.success(request,'Product has been updated')
                    return redirect('admin_product_list')
                else:
                    instance = get_object_or_404(Product, id=id)
                    form = ProductForm(request.POST or None, request.FILES or None, instance=instance)  
                    context = {
                        'form'     : form,
                        'product':instance,
                        }
                    return render(request, 'admin/admin_edit_product.html',context)
            else:
                instance = get_object_or_404(Product, id=id)
                form = ProductForm(request.POST or None, request.FILES or None, instance=instance)  
                context = {
                    'form'     : form,
                    'product':instance,
                    }
                return render(request, 'admin/admin_edit_product.html',context)


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_delete_product(request,id):
    product = Product.objects.get(id=id)
    product.delete()
    # messages.success(request,"Product deleted successfully.")
    return redirect('admin_product_list')

#Admin User Management 

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def users(request):
    users = Account.objects.all()
    context = {
        'users':users,
    }
    return render(request, 'admin/users.html',context)

    
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_activation(request, id):
    user = Account.objects.get(id=id)
    user.is_active = True
    user.save()
    return redirect('users')

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_deactivation(request, id):
    user = Account.objects.get(id=id)
    user.is_active = False
    user.save()
    return redirect('users')
  

#Admin Category Management 

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_categories(request):
    categories = Category.objects.all()
    context = {
        'categories':categories}
    return render(request,'admin/admin_categories.html',context)

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            slug = slugify(category_name)
            description = form.cleaned_data['description']

            category = Category.objects.create(category_name=category_name, slug=slug, description=description)
            category.save()
            return redirect('admin_categories')
        else:
            messages.error(request,'form not valid')
            context = {
            'form':form
            }
            return render(request,'admin/admin_add_category.html',context)
    else:
        form = CategoryForm()
        context = {
            'form':form
            }
        return render(request,'admin/admin_add_category.html',context) 


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_edit_category(request ,id):
    instance = get_object_or_404(Category, id=id)
    form = CategoryForm(request.POST or None, instance=instance)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('admin_categories')
        else:
            instance = get_object_or_404(Category, id=id)
            form = CategoryForm(request.POST or None, instance=instance)
            context = {
                    'form'     : form,
                    'category':instance,
                    }
            return render(request, 'admin/admin_edit_category.html',context)
    else:
        instance = get_object_or_404(Category, id=id)
        form = CategoryForm(request.POST or None, instance=instance)
        context = {
                'form'     : form,
                'category' :instance,
                }
        return render(request, 'admin/admin_edit_category.html',context)



@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_delete_category(request,id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('admin_categories')


#Order Management

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_orders(request):
    orders = Order.objects.all()
    context = {
        'orders':orders,
    }
    return render(request, 'admin/admin_orders.html', context)

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_orders_status_change(request, id):
    instance = get_object_or_404(Order, id=id)
    form = OrderStatusForm(request.POST or None, instance=instance)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('admin_orders')
        else:
            instance = get_object_or_404(Order, id=id)
            form = OrderStatusForm(request.POST or None, instance=instance)
            context = {
                    'form'     : form,
                    'order'    : instance,
                    }
            return render(request, 'admin/admin_orders_status_change.html', context)
    else:
        instance = get_object_or_404(Order, id=id)
        form = OrderStatusForm(request.POST or None, instance=instance)
        context = {
                'form'     : form,
                'order' :instance,
                }
        return render(request, 'admin/admin_orders_status_change.html',context) 

#Varient Management   

@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_variation(request):
    variations = Variation.objects.all()
    context = {
        'variations':variations,
    }
    return render(request, 'admin/admin_variations.html', context)


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_add_variation(request):
    if request.method == "POST":
        form = VariationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('admin_variation')
        else:
            messages.error(request,'form not valid')
            context = {
            'form':form
            }
            return render(request,'admin/admin_add_variations.html',context)
    else:
        form = VariationForm()
        context = {
            'form':form
            }
        return render(request,'admin/admin_add_variations.html',context)


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_add_product_images(request):
    if request.method == "POST":
        form = ProductGalleryForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect('admin_product_list')
        else:
            messages.error(request,'form not valid')
            context = {
            'form':form
            }
            return render(request,'admin/admin_add_product_images.html',context)
    else:
        form = ProductGalleryForm()
        context = {
            'form':form
            }
        return render(request,'admin/admin_add_product_images.html',context)         