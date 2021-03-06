from django.shortcuts import get_object_or_404, redirect, render
from accounts.forms import RegistrationForm, UserProfileForm,UserForm
from accounts.models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from cart.models import Cart, CartItem
from cart.views import _cart_id
from orders.models import Order
from .private import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_SERVICE_SID



def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        phone_number = request.POST["phone_number"]
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = phone_number
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                username=username,
                password=password,
            )
            user.save()

            profile = UserProfile()
            profile.user_id = user.id
            profile.save()

            # otp account varification

            request.session["mobile"] = phone_number
            user = Account.objects.filter(phone_number=phone_number)

            for m in user:
                if m.phone_number == phone_number:
                    user_mobile = "+91" + phone_number

                    # Your Account Sid and Auth Token from twilio.com / console
                    account_sid = TWILIO_ACCOUNT_SID
                    auth_token = TWILIO_AUTH_TOKEN
                    client = Client(account_sid, auth_token)
                    verification = client.verify.services(TWILIO_SERVICE_SID).verifications.create(to=user_mobile, channel="sms")

                    print(verification.status)
                    return redirect("new_user_otp_varification")
    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # add in otp login also
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                cart_item = CartItem.objects.filter(user=user)
                ex_var_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)

                for pr in product_variation:
                    if pr in ex_var_list:
                        index = ex_var_list.index(pr)
                        item_id = id[index]
                        item = CartItem.objects.get(id=item_id)
                        item.quantity += 1
                        item.user = user
                        item.save()
                    else:
                        cart_item = CartItem.objects.filter(cart=cart)
                        for item in cart_item:
                            item.user = user
                            item.save()

            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now loggen in!")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("home")

        else:
            messages.error(request, "Invalid Credentials!")
            return redirect("login")

    return render(request, "accounts/login.html")


def otp_login(request):
    if request.method == "POST":
        phone_number = request.POST["phone_number"]
        request.session["mobile"] = phone_number
        user = Account.objects.filter(phone_number=phone_number)

        for m in user:
            if m.phone_number == phone_number:
                user_mobile = "+91" + phone_number
                # print(user_mobile)

                # Your Account Sid and Auth Token from twilio.com / console
                account_sid = TWILIO_ACCOUNT_SID
                auth_token = TWILIO_AUTH_TOKEN
                client = Client(account_sid, auth_token)
                verification = client.verify.services(TWILIO_SERVICE_SID).verifications.create(to=user_mobile, channel="sms")

                print(verification.status)
                return redirect("otp_varification")
    else:
        return render(request, "accounts/otp_login.html")


def otp_varification(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        mobile = request.session["mobile"]
        user_mobile = "+91" + mobile

        # twilio code for otp generation
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        verification_check = client.verify.services(TWILIO_SERVICE_SID).verification_checks.create(to=user_mobile, code=otp)

        print(verification_check.status)

        # checking otp is valid or not. If valid redirect home
        if verification_check.status == "approved":
            user_details = Account.objects.get(phone_number=mobile)  # user details
            print(user_details)

            if user_details is not None:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)

                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user_details)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user_details
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user_details
                                item.save()

                except:
                    pass

                auth.login(request, user_details)
                return redirect("home")
        else:
            messages.error(request, "Invalid OTP")
            return render(request, "accounts/otp_page.html")
    else:
        return render(request, "accounts/otp_page.html")


def new_user_otp_varification(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        mobile = request.session["mobile"]
        user_mobile = "+91" + mobile

        # twilio code for otp generation
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        verification_check = client.verify.services(
            TWILIO_SERVICE_SID
        ).verification_checks.create(to=user_mobile, code=otp)

        print(verification_check.status)

        # checking otp is valid or not. If valid redirect home
        if verification_check.status == "approved":
            messages.success(request, "OTP verified successfully.")
            user = Account.objects.get(phone_number=mobile)  # user details
            user.is_active = True
            user.save()
            auth.login(request, user)
            try:
                del request.session["mobile"]
            except:
                pass

            return redirect("home")
        else:
            messages.error(request, "Invalid OTP")
            return render(request, "accounts/new_user_otp_page.html")
    else:
        return render(request, "accounts/new_user_otp_page.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are now logged out!")
    return redirect("login")


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count':orders_count,
    }
    return render(request, "accounts/dashboard.html", context)


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered = True).order_by('-created_at')
    context={
        'orders':orders,
    }
    return render(request, 'accounts/my_orders.html', context)

def manage_address(request):
    user = request.user
    user_address = UserProfile.objects.filter(user=user)
    address_count = user_address.count()
    context = {
        'user_address':user_address,
        'address_count':address_count,
    }
    return render(request, 'accounts/manage_address.html' , context)


def edit_address(request, id):
        instance = get_object_or_404(UserProfile, id=id)
        form = UserProfileForm(request.POST or None, instance=instance)
        if request.method == "POST":
            if form.is_valid():
                form.save()
                return redirect('manage_address')
            else:
                instance = get_object_or_404(UserProfile, id=id)
                form = UserProfileForm(request.POST or None, instance=instance)
                context = {
                    'form'     : form,
                    'address':instance,
                        }
                return render(request, 'accounts/edit_address.html',context)
        else:
            instance = get_object_or_404(UserProfile, id=id)
            form = UserProfileForm(request.POST or None, instance=instance)
            context = {
                'form'     : form,
                'address':instance,
                }
            return render(request, 'accounts/edit_address.html',context)


def add_address(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = Account.objects.get(id = request.user.id)
            address_line_1 = form.cleaned_data['address_line_1']
            address_line_2 = form.cleaned_data['address_line_2']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
    
            new_address = UserProfile.objects.create(user=user, address_line_1=address_line_1, address_line_2=address_line_2, city=city, state=state, country=country)
            new_address.save()       

            return redirect ('manage_address')
        else:
            form = UserProfileForm()    
            context = {
                    'form':form
            }
            return render(request, 'accounts/add_address.html', context)
    else:
            form = UserProfileForm()    
            context = {
                    'form':form
            }
            return render(request, 'accounts/add_address.html', context)        
