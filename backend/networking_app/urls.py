from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('people/', views.get_all_people, name='get_all_people'),
    path('people/<str:person_id>/', views.get_person, name='get_person'),
    path('match/', views.get_match_from_text, name='get_match_from_text'),
] 