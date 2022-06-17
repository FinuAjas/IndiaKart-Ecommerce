from datetime import datetime
import datetime
import json
from django.shortcuts import redirect, render
from accounts.models import UserProfile
from cart.models import CartItem
from store.models import Product
from .models import Order, OrderProduct, Payment
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt


def place_order(request, total=0, quantity=0):
    try:
        address_id = request.POST['ship_address']
    except:
        return redirect('checkout')
        
    current_user = request.user

    try:
        order = Order.objects.get(user=current_user, is_ordered=False)
        cart_items = CartItem.objects.filter(user = current_user)
        grand_total = 0
        tax = 0
        for cart_item in cart_items:
            total   += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = round((5 * total)/100,2)
        grand_total = round(total + tax,2)

        context = {
            'order' : order,
            'cart_items' : cart_items,
            'total' : total,
            'tax' : tax,
            'grand_total' : grand_total,
            # 'form':form
        }
        return render(request,'orders/payments.html',context)

    except:
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <=0:
            return redirect('store')

        grand_total = 0
        tax         = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = round((5 * total)/100,2)
        grand_total = total + tax 

        if request.method == 'POST':
            form = CouponApplyForm()
            address_id = request.POST['ship_address']
            address = UserProfile.objects.filter(id = address_id, user = request.user.id)
            order_note = request.POST['order_note']
            user = request.user
            for i in address:
                address_line_1 = i.address_line_1
                address_line_2 = i.address_line_2
                country = i.country
                state = i.state
                city = i.city

            data = Order()
            data.user               = current_user
            data.first_name         = user.first_name
            data.last_name          = user.last_name
            data.phone              = user.phone_number
            data.email              = user.email
            data.address_line_1     = address_line_1
            data.address_line_2     = address_line_2
            data.country            = country
            data.state              = state
            data.city               = city
            data.order_note         = order_note
            data.order_total        = grand_total
            data.tax                = tax
            data.ip                 = request.META.get('REMOTE_ADDR')
            data.save()
            yr                      = int(datetime.date.today().strftime('%Y'))
            dt                      = int(datetime.date.today().strftime('%d'))
            mt                      = int(datetime.date.today().strftime('%m'))
            d                       = datetime.date(yr,mt,dt)
            current_date            = d.strftime("%Y%m%d")
            order_number            = current_date + str(data.id)
            data.order_number       = order_number
            data.save()


            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            user = request.user

            context = {
                'user':user,
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
                    }
            return render(request,'orders/payments.html',context)
        else:
            return redirect('checkout')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered = False, order_number=body['orderID'])

    payment = Payment(
        user            = request.user,
        payment_id      = body['transID'],
        payment_method  = body['payment_method'],
        amount_paid     = order.order_total,
        status          = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    # move the cart products to the ordered products table
    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

    #for variation - Many to Many field, first save data and then update.
        cart_item = CartItem.objects.get(id = item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    # reduce the quantity of sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear the cart
    CartItem.objects.filter(user=request.user).delete()

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
        }

    return JsonResponse(data)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            subtotal = subtotal + i.product_price * i.quantity

        tax = round((5 * subtotal)/100,2)
        grandtotal = subtotal + tax   

        payment = Payment.objects.get(payment_id = transID)
        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
            'tax':tax,
            'grandtotal':grandtotal,
        }
        return render(request, 'orders/order_complete.html' , context)

    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')     


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def rzp_order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
    payment = Payment(
        user = request.user,
        payment_id = transID,
        payment_method = "Razor Pay",
        amount_paid = order.order_total,
        status = "COMPLETED",
        )
    payment.save()
    order.payment= payment 
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        #for variation - Many to Many field, first save data and then update.
        cart_item = CartItem.objects.get(id = item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id = orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        
        # reduce the quantity of sold products
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear the cart and send order received confirmation to customer
    CartItem.objects.filter(user=request.user).delete()
    
    try:
        order = Order.objects.get(order_number = order_number)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order':order,
            'ordered_products' : ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal':subtotal,
        }
        CartItem.objects.filter(user=request.user).delete()
        return render(request, 'orders/order_complete.html',context)


    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')



@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def cod_order_complete(request,order_number):
    order_number = order_number
    now = datetime.now()
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
    code = order.coupon
    
    try:
        order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
        code = order.coupon
        coupon = CouponCode.objects.get(code__exact = code, valid_from__lte=now, valid_to__gte=now, active = True)
        if coupon:
            discount = coupon.discount
            order_no = order.order_number            
            current_user = request.user
            cart_items = CartItem.objects.filter(user = current_user)
            grand_total = 0
            tax = 0
            total = 0
            quantity = 0
            for cart_item in cart_items:
                total   += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = round((5 * total)/100,2)
            grand_total = round(total + tax,2)
        
            discount_amount = round(grand_total * discount/100,2)
            total_after_coupon = round(float(grand_total - discount_amount),2)
            order.discount_amount = discount_amount
            order.nett_paid = total_after_coupon
            order.coupon_use_status = True
            order.save()
            

        payment = Payment(
            user = request.user,
            payment_id = "COD - Payement pending",  
            payment_method = "COD",
            amount_paid = order.nett_paid,
            status = "COD",
            )
        payment.save()
        order.payment= payment 
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user = request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            #for variation - Many to Many field, first save data and then update.
            cart_item = CartItem.objects.get(id = item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # reduce the quantity of sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # clear the cart and send order received confirmation to customer.
        CartItem.objects.filter(user=request.user).delete()        
    
    except:
        try:
            order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
            payment = Payment(
                user = request.user,
                payment_id = "COD - Payement pending",  
                payment_method = "COD",
                amount_paid = order.order_total,
                status = "COD",
                )
            payment.save()
            order.payment= payment 
            order.is_ordered = True
            order.save()

            cart_items = CartItem.objects.filter(user = request.user)
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()

                #for variation - Many to Many field, first save data and then update.
                cart_item = CartItem.objects.get(id = item.id)
                product_variation = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()

                # reduce the quantity of sold products
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

            # clear the cart and send order received confirmation to customer.
            CartItem.objects.filter(user=request.user).delete()

            try:
                order = Order.objects.get(order_number = order_number)
                ordered_products = OrderProduct.objects.filter(order_id=order.id)
                subtotal = 0
                for i in ordered_products:
                    subtotal += i.product_price * i.quantity


                context = {
                    'order':order,
                    'ordered_products' : ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payment,
                    'subtotal':subtotal,
                    }
                CartItem.objects.filter(user=request.user).delete()
                return render(request, 'orders/order_complete.html',context)

            except (Payment.DoesNotExist, Order.DoesNotExist):
                return redirect('home')
        except:
            return redirect('home')    



def return_order(request, order):
    order = Order.objects.get(user = request.user, order_number = order)
    if request.method == "POST":
        status = request.POST['return_order']
        order.status = status
        order.save()   
 
    return redirect('my_orders')


def cancel_order(request, order):
    order = Order.objects.get(user = request.user, order_number = order)
    if request.method == "POST":
        status = request.POST['cancel_order']
        order.status = status
        order.save()   
 
    return redirect('my_orders')    

