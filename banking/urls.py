from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('setor/', views.setor_tunai, name='setor_tunai'),
    path('tarik/', views.tarik_tunai, name='tarik_tunai'),
    path('transfer/', views.transfer, name='transfer'),
    path('nasabah/', views.nasabah_list, name='nasabah_list'),
    path('nasabah/tambah/', views.tambah_nasabah, name='tambah_nasabah'),
    path('rekening/<str:no_rekening>/', views.rekening_detail, name='rekening_detail'),
]
