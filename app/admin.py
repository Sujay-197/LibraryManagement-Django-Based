from django.contrib import admin
from .models import Book, Member, Order, OrderItem

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_available', 'stock', 'price']
    list_filter = ['is_available']
    search_fields = ['title', 'author']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'joined_date']
    search_fields = ['name', 'email']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']  # Allow editing status directly from the list view
    search_fields = ['full_name', 'email']
    readonly_fields = ['created_at']
    inlines = []  # You can add an inline for OrderItem if desired
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'status':
            kwargs['choices'] = [
                ('pending', 'Pending'),
                ('accepted', 'Accepted'),
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'book', 'quantity']
    search_fields = ['order__full_name', 'book__title']

# http://127.0.0.1:8000/admin --> admin panel

