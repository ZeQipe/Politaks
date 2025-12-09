from django.urls import path
from . import views

app_name = 'config'

urlpatterns = [
    path('generation/filters', views.generation_filters, name='generation_filters'),
    path('generation/form-config', views.form_config, name='form_config'),
    path('generation/generate', views.generate, name='generate'),
    path('generation/generate-excel', views.generate_excel, name='generate_excel'),
    path('history/filters', views.history_filters, name='history_filters'),
    path('history', views.history, name='history'),
]

