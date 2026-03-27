import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from products.models import Category, Color, Size, Product, ProductVariant

def seed():
    # Categories
    cat_suits, _ = Category.objects.get_or_create(name='Suits', description='Professional suits for men and women.')
    cat_dresses, _ = Category.objects.get_or_create(name='Dresses', description='Elegant evening and casual dresses.')
    cat_shirts, _ = Category.objects.get_or_create(name='Shirts', description='Premium cotton shirts.')

    # Colors
    colors = [
        Color.objects.get_or_create(name='Midnight Black', hex_code='#000000')[0],
        Color.objects.get_or_create(name='Navy Blue', hex_code='#000080')[0],
        Color.objects.get_or_create(name='Pure White', hex_code='#FFFFFF')[0],
        Color.objects.get_or_create(name='Charcoal Gray', hex_code='#36454F')[0],
    ]

    # Sizes
    sizes = [
        Size.objects.get_or_create(name='S')[0],
        Size.objects.get_or_create(name='M')[0],
        Size.objects.get_or_create(name='L')[0],
        Size.objects.get_or_create(name='XL')[0],
    ]

    # Products
    p1, _ = Product.objects.get_or_create(
        name='Executive Slim-Fit Suit',
        description='A professional slim-fit suit made from premium Italian wool. Perfect for business meetings.',
        category=cat_suits
    )
    
    p2, _ = Product.objects.get_or_create(
        name='Silk Gala Evening Dress',
        description='An elegant silk dress for gala events. Flowing design with a premium finish.',
        category=cat_dresses
    )

    p3, _ = Product.objects.get_or_create(
        name='Oxford Button-Down Shirt',
        description='A classic Oxford shirt for a professional look. Breathable and comfortable.',
        category=cat_shirts
    )

    # Variants (Seed some samples)
    products = [p1, p2, p3]
    for p in products:
        for c in colors[:2]: # First 2 colors
            for s in sizes:
                ProductVariant.objects.get_or_create(
                    product=p,
                    color=c,
                    size=s,
                    price=299.99 if p == p1 else 149.99 if p == p2 else 49.99,
                    stock_quantity=10
                )

    print("Professional Seed Data Created Successfully!")

if __name__ == '__main__':
    seed()
