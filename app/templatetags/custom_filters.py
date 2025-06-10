from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def star_rating(value):
    try:
        # Convert to int and clamp between 0 and 5
        stars = min(max(int(value), 0), 5)
        return '⭐' * stars
    except (ValueError, TypeError):
        return ''

@register.filter
def dict_get(d, key):
    return d.get(key) if d and key in d else ''

@register.filter
def get_cart_item_id(cart_items, book_id):
    try:
        book_id = int(book_id)
        for item in cart_items:
            if int(item.book.id) == book_id:
                return item.id
    except Exception:
        pass
    return ''

# Ensure this file is loaded by Django by using {% load custom_filters %} at the top of your templates that use these filters.
