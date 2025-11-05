from django.shortcuts import render, get_object_or_404
from .models import Flight, Passenger, BoardingPass


def agent_dashboard(request):
    """Панель агента регистрации - сегодняшние рейсы"""
    from datetime import date
    today = date.today()

    # Получаем активные рейсы на сегодня
    active_flights = Flight.objects.filter(
        flight_date=today,
        is_active=True
    ).order_by('departure_time')

    print(f"DEBUG: Найдено рейсов на {today}: {active_flights.count()}")  # Для отладки

    context = {
        'active_flights': active_flights,
        'today': today,
        'workstation': 'Стойка 1'
    }
    return render(request, 'flights/agent_dashboard.html', context)


def start_registration(request, flight_id):
    """Начало регистрации на рейс"""
    flight = get_object_or_404(Flight, id=flight_id)

    # Здесь будет логика регистрации пассажиров
    # Пока просто редирект на детали рейса
    return redirect('flight_detail', flight_id=flight_id)


def flight_checkin(request, flight_id):
    """Страница регистрации пассажиров на рейс"""
    flight = get_object_or_404(Flight, id=flight_id)

    # Получаем пассажиров этого рейса
    passengers = Passenger.objects.filter(flight=flight)

    # Получаем уже зарегистрированных пассажиров
    boarded_passengers = BoardingPass.objects.filter(flight=flight)

    # Генерируем доступные места (простой пример)
    total_seats = flight.available_seats or 180
    all_seats = [f"{row}{seat}" for row in range(1, 31) for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
    taken_seats = [bp.seat_number for bp in boarded_passengers if bp.seat_number]
    available_seats = [seat for seat in all_seats[:total_seats] if seat not in taken_seats]

    context = {
        'flight': flight,
        'passengers': passengers,
        'boarded_passengers': boarded_passengers,
        'available_seats': available_seats,
        'registered_count': boarded_passengers.count(),
        'total_capacity': total_seats,
    }
    return render(request, 'flights/flight_checkin.html', context)

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