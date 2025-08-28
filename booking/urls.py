#file created manually
#added manually
from django.urls import path
from . import views

urlpatterns = [
    path('', views.travel_list, name='travel_list'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('book/<int:pk>/', views.book, name='book'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
