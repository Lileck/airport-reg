from django.contrib import admin
from .models import Flight, Passenger, CheckInAgent, BoardingPass

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['number', 'departure_city', 'destination_city', 'departure_time', 'status', 'capacity']
    list_filter = ['status', 'departure_city', 'destination_city']
    search_fields = ['number', 'departure_city', 'destination_city']
    ordering = ['departure_time']

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'flight', 'passport_number', 'seat_number']
    list_filter = ['flight']
    search_fields = ['first_name', 'last_name', 'passport_number']
@admin.register(CheckInAgent)
class CheckInAgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'agent_id', 'workstation', 'is_active']

@admin.register(BoardingPass)
class BoardingPassAdmin(admin.ModelAdmin):
    list_display = ['boarding_pass_number', 'passenger', 'flight', 'seat_number', 'status']