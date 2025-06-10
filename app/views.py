from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Member, CartItem, Order, OrderItem
from .forms import BookForm, MemberForm, OrderStatusForm
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages

def landing(request):
    return render(request, 'landing.html')

def book_list(request):
    books = Book.objects.filter(is_available=True)
    
    # Ensure session exists
    if not request.session.exists(request.session.session_key):
        request.session.create()
    
    session_id = request.session.session_key
    request.session.modified = True  # Mark session as modified
    
    # Get cart items for current session
    cart_items = CartItem.objects.filter(session_id=session_id)
    cart_dict = {item.book_id: item.quantity for item in cart_items}
    
    return render(request, 'book_list.html', {
        'books': books, 
        'cart_dict': cart_dict,
        'cart_items': cart_items
    })

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})

def staff_required(function):
    decorated_function = user_passes_test(lambda u: u.is_staff, login_url='landing')(function)
    return decorated_function

@staff_required
def member_list(request):
    members = Member.objects.all()
    return render(request, 'member_list.html', {'members': members})

@staff_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'member_detail.html', {'member': member})

@staff_required
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('member_list'))
    else:
        form = MemberForm()
    return render(request, 'member_form.html', {'form': form})

@staff_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect(reverse('member_detail', kwargs={'pk': pk}))
    else:
        form = MemberForm(instance=member)
    return render(request, 'member_form.html', {'form': form})

@staff_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        return redirect(reverse('member_list'))
    return render(request, 'member_confirm_delete.html', {'member': member})

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # Ensure session exists
    if not request.session.exists(request.session.session_key):
        request.session.create()
    
    session_id = request.session.session_key
    request.session.modified = True  # Mark session as modified
    # Check stock availability
    current_cart_quantity = CartItem.objects.filter(book=book, session_id=session_id).values_list('quantity', flat=True).first() or 0
    if current_cart_quantity >= book.stock:
        messages.error(request, f'Sorry, maximum stock limit reached. Only {book.stock} copies available.')
        return redirect('book_list')

    cart_item, created = CartItem.objects.get_or_create(
        book=book,
        session_id=session_id,
        defaults={'quantity': 1}
    )

    # Only increment if this is a + action or Add to Cart and we have stock
    if request.method == 'POST':
        action = request.POST.get('action')
        if not created and (action == 'increment' or action is None):
            if cart_item.quantity < book.stock:
                cart_item.quantity += 1
                cart_item.save()
            # If already at stock, do not increment and show error
            elif cart_item.quantity >= book.stock:
                messages.error(request, f'Sorry, maximum stock limit reached. Only {book.stock} copies available.')
                return redirect('book_list')
        elif created and (action == 'increment' or action is None):
            # If just created, but stock is 0, remove from cart and show error
            if cart_item.quantity > book.stock:
                cart_item.delete()
                messages.error(request, f'Sorry, maximum stock limit reached. Only {book.stock} copies available.')
                return redirect('book_list')

    # After all logic, ensure cart quantity never exceeds stock
    if cart_item.quantity > book.stock:
        cart_item.quantity = book.stock
        cart_item.save()
        messages.error(request, f'Sorry, maximum stock limit reached. Only {book.stock} copies available.')

    return redirect('book_list')

def view_cart(request):
    # Ensure session exists
    if not request.session.exists(request.session.session_key):
        request.session.create()
    
    session_id = request.session.session_key
    request.session.modified = True  # Mark session as modified
    
    cart_items = CartItem.objects.filter(session_id=session_id)
    total = sum(item.book.price * item.quantity for item in cart_items if hasattr(item.book, 'price'))
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    session_id = request.session.session_key
    if request.method == 'POST':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    # Always recalculate cart_items and cart_dict for the template
    cart_items = CartItem.objects.filter(session_id=session_id)
    cart_dict = {item.book_id: item.quantity for item in cart_items}
    books = Book.objects.filter(is_available=True)
    return render(request, 'book_list.html', {
        'books': books,
        'cart_dict': cart_dict,
        'cart_items': cart_items,
    })

def checkout(request):
    session_id = request.session.session_key
    if not session_id:
        return redirect('book_list')
    
    cart_items = CartItem.objects.filter(session_id=session_id)
    if not cart_items.exists():
        return redirect('book_list')
    
    total = sum(item.book.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        # Check if member already exists
        member, created = Member.objects.get_or_create(
            email=email,
            defaults={'name': full_name}
        )
        # Create Order
        order = Order.objects.create(
            member=member,
            full_name=full_name,
            email=email,
            address=address,
            phone=phone,
            status='pending'
        )
        # Add items to Order and reduce stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity
            )
            # Reduce stock, never below 0
            item.book.stock = max(item.book.stock - item.quantity, 0)
            item.book.save()
        # Clear the cart
        cart_items.delete()
        # Render success page with appropriate message
        return render(request, 'order_success.html', {
            'member': member,
            'total': total,
            'is_new_member': created,
            'order': order
        })
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@staff_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})

@staff_required
def order_approve(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # If status is provided directly (from Approve/Reject button), update and redirect
        status = request.POST.get('status')
        if status in ['approved', 'rejected']:
            order.status = status
            order.save()
            return redirect('order_list')
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'order_approve.html', {'form': form, 'order': order})

def cart_action(request, book_id=None, cart_item_id=None):
    if request.method == 'POST':
        # If no book_id in URL, try to get it from POST
        if not book_id:
            book_id = request.POST.get('book_id')
        
        action = request.POST.get('action', 'increment')  # default to increment if not specified
        
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        if cart_item_id:  # If we have cart_item_id, this is a remove/decrement action
            cart_item = get_object_or_404(CartItem, id=cart_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        else:  # This is an add/increment action
            book = get_object_or_404(Book, id=book_id)
            cart_item, created = CartItem.objects.get_or_create(
                book=book,
                session_id=session_id,
                defaults={'quantity': 1}
            )
            if not created and action != 'decrement':
                cart_item.quantity += 1
                cart_item.save()

        # Get updated cart state
        cart_items = CartItem.objects.filter(session_id=session_id)
        cart_dict = {item.book_id: item.quantity for item in cart_items}
        return render(request, 'book_list.html', {
            'books': Book.objects.filter(is_available=True),
            'cart_dict': cart_dict,
            'cart_items': cart_items,
        })

    return redirect('book_list')
