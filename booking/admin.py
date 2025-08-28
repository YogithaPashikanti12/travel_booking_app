from django.contrib import admin

# Register your models here.
#added manually
from .models import TravelOption, Booking

@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ("travel_id", "type", "source", "destination", "date_time", "price", "available_seats")
    list_filter = ("type", "source", "destination")
    search_fields = ("source", "destination")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_id", "user", "travel_option", "number_of_seats", "total_price", "status", "booking_date")
    list_filter = ("status",)
    search_fields = ("user__username",)

