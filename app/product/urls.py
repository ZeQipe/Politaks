from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('links/', views.get_product_links, name='get_product_links'),
    path('link/', views.get_product_link, name='get_product_link'),
    path('populate/', views.populate_database, name='populate_database'),
    path('populate-csv/', views.populate_from_csv, name='populate_from_csv'),
    path('populate-config/', views.populate_config, name='populate_config'),
]

