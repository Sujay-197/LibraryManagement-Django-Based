from django import forms
from .models import Book, Member, Order

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'is_available', 'image', 'price', 'rating', 'stock']

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email']

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
