from django.urls import path
from . import views
from . import views_checkin
from django.contrib.auth import views as auth_views

app_name = 'flights'

urlpatterns = [
    path('', views.flight_list, name='flight_list'),
    path('search/', views.search_flights, name='search_flights'),
    path('agent/cancel-registration/<int:boarding_pass_id>/', views_checkin.cancel_registration, name='cancel_registration'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('agent/dashboard/', views_checkin.agent_dashboard, name='agent_dashboard'),
    path('agent/checkin/<int:flight_id>/', views_checkin.flight_checkin, name='flight_checkin'),
    path('agent/passenger-lookup/', views_checkin.passenger_lookup, name='passenger_lookup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]