from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # path('newadmin/', include('newadmin.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
] 
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
#  + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)