from django.db import models
from django.utils.text import slugify
from PIL import Image


def optimize_image(path, max_size=(1200, 1200), quality=82):
    try:
        with Image.open(path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(path, format='JPEG', quality=quality, optimize=True)
    except Exception:
        # Keep original file if optimization fails.
        pass

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7) # e.g. #FF0000

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=10) # S, M, L, XL, etc.

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if self.thumbnail and hasattr(self.thumbnail, 'path'):
            optimize_image(self.thumbnail.path, max_size=(1000, 1000), quality=80)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name='variants', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name='variants', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.slug}-{self.color.name}-{self.size.name}".upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.color.name} ({self.size.name})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path'):
            optimize_image(self.image.path, max_size=(1400, 1400), quality=82)

    def __str__(self):
        return f"Image for {self.product.name}"
