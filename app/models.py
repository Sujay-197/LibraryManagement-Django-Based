from django.db import models
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.PositiveIntegerField(default=1)  # 1 to 5 stars
    stock = models.PositiveIntegerField(default=0)

    def upload_to_cloudinary(self):
        if self.image:
            upload_result = upload(self.image.path)
            self.image = upload_result.get('secure_url')
            self.save()

    def __str__(self):
        return self.title


class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    session_id = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title} (Order #{self.order.id})"
