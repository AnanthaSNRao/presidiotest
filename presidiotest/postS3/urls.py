from django.urls import path
from .views import get, download, get_list

urlpatterns = [
    path('/', get, name='get'),
    path('/download', download, name='download'),
    path('/list', get_list, name='list')
]
