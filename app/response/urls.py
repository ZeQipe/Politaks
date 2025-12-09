from django.urls import path
from . import views

app_name = 'response'

urlpatterns = [
    path('save', views.save_excel_response, name='save_excel_response'),
]

