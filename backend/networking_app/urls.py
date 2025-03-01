from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('people/', views.get_all_people, name='get_all_people'),
] 