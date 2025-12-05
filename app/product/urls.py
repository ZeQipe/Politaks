from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('links/', views.get_product_links, name='get_product_links'),
    path('populate/', views.populate_database, name='populate_database'),
]

