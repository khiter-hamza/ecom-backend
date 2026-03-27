from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from products.views import CategoryViewSet, ColorViewSet, SizeViewSet, ProductViewSet, ProductVariantViewSet
from orders.views import OrderViewSet
from inventory.views import StockMovementViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'products', ProductViewSet)
router.register(r'variants', ProductVariantViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'inventory', StockMovementViewSet)

urlpatterns = [
    path('admin/', admin.site.get_ipython_admin_site().urls if hasattr(admin, 'site') and hasattr(admin.site, 'get_ipython_admin_site') else admin.site.urls), # Standard Admin
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
