from django.urls import path

from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.certificate_list_view, name='list'),
    path('<uuid:uuid>/', views.certificate_detail_view, name='view'),
]
