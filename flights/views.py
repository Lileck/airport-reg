from django.shortcuts import render, get_object_or_404
from .models import Flight, Passenger, BoardingPass


def flight_list(request):
    """Список всех рейсов"""
    flights = Flight.objects.all().order_by('departure_time')

    # Поиск по номеру рейса
    search_query = request.GET.get('search', '')
    if search_query:
        flights = flights.filter(number__icontains=search_query)

    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        flights = flights.filter(status=status_filter)

    context = {
        'flights': flights,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'flights/flight_list.html', context)


def flight_detail(request, flight_id):
    """Детальная информация о рейсе и его пассажирах"""
    flight = get_object_or_404(Flight, id=flight_id)
    passengers = Passenger.objects.filter(flight=flight)

    # Получаем информацию о регистрации для каждого пассажира
    passenger_data = []
    for passenger in passengers:
        boarding_pass = BoardingPass.objects.filter(passenger=passenger, flight=flight).first()
        passenger_data.append({
            'passenger': passenger,
            'boarding_pass': boarding_pass,
            'is_registered': boarding_pass is not None
        })

    # Считаем статистику
    registered_count = BoardingPass.objects.filter(flight=flight).count()
    free_seats = flight.capacity - registered_count

    context = {
        'flight': flight,
        'passenger_data': passenger_data,
        'passengers': passengers,
        'registered_count': registered_count,
        'free_seats': free_seats,
        'total_passengers': passengers.count(),
    }
    return render(request, 'flights/flight_detail.html', context)


def search_flights(request):
    """Поиск рейсов по городу вылета или назначения"""
    search_type = request.GET.get('search_type', 'destination')
    city = request.GET.get('city', '')
    flights = Flight.objects.all()

    if city:
        if search_type == 'departure':
            flights = flights.filter(departure_city__icontains=city)
        else:  # destination
            flights = flights.filter(destination_city__icontains=city)

    context = {
        'flights': flights,
        'city': city,
        'search_type': search_type,
    }
    return render(request, 'flights/search.html', context)