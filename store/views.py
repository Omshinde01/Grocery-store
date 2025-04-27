from django.shortcuts import render
from .models import Product

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'store/product_detail.html', {'product': product})





from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm  # Import your custom form
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please fix the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'store/register.html', {'form': form})



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'store/login.html')

from django.contrib.auth import logout
def custom_logout(request):
    logout(request)
    return redirect('home')

from .models import Product
from django.shortcuts import render
from .models import Product

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/cart.html', context)

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})

    # Get quantity from form, default to 1 if missing
    quantity = int(request.POST.get('quantity', 1))

    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity

    request.session['cart'] = cart
    return redirect('home')

from django.shortcuts import get_object_or_404

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_details.html', {'product': product})


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] -= 1  # Decrease quantity by 1
        if cart[product_id_str] <= 0:
            del cart[product_id_str]  # Remove the item if quantity is 0

    request.session['cart'] = cart
    return redirect('view_cart')

from django.shortcuts import render, redirect
from django.contrib import messages

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('home')
    return render(request, 'store/checkout.html')


from .models import Order
from .models import Product
from django.contrib import messages
from django.shortcuts import redirect, render

def place_order(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, "Your cart is empty.")
            return redirect('home')

        # Prepare product summary and total
        products_summary = ""
        total_price = 0

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            products_summary += f"{quantity} x {product.name}, "
            total_price += product.price * quantity

        products_summary = products_summary.rstrip(', ')  # Remove last comma

        # Save order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            address=address,
            contact_number=contact_number,
            products_summary=products_summary,
            total_price=total_price
        )

        # Clear cart
        request.session['cart'] = {}
        messages.success(request, "Order placed successfully! 🚚")
        return redirect('home')

    else:
        return redirect('checkout')


# views.py

from django.contrib.auth.decorators import login_required
from .models import Order

@login_required(login_url='/login/')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        order.save()
    return redirect('my_orders')

from django.contrib.admin.views.decorators import staff_member_required
from .models import Order

@staff_member_required(login_url='/admin/login/')
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/admin_orders.html', {'orders': orders})
