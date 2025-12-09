"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from .frontend import serve_frontend, serve_next_static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/product/', include('app.product.urls')),
    path('api/', include('app.config.urls')),
    
    # Next.js static files (_next/)
    re_path(r'^_next/(?P<path>.*)$', serve_next_static, name='next_static'),
    
    # Frontend (все пути КРОМЕ api/ и admin/)
    re_path(r'^(?!api/|admin/)(?P<path>.*)$', serve_frontend, name='frontend'),
]
