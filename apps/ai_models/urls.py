# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/classify-upload/', views.api_auto_fill_product, name='api_classify_upload'),
]