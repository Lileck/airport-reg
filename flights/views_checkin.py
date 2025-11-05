from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse
from .models import Flight, Passenger, BoardingPass, CheckInAgent
import random


def agent_check(user):
    return hasattr(user, 'checkinagent')


@login_required
@user_passes_test(agent_check)
def agent_dashboard(request):
    """Панель агента по регистрации"""
    agent = request.user.checkinagent
    today = timezone.now().date()

    # Активные рейсы на сегодня
    active_flights = Flight.objects.filter(
        departure_time__date=today,
        status__in=['scheduled', 'boarding']
    ).order_by('departure_time')

    # Последние регистрации
    recent_checkins = BoardingPass.objects.filter(
        check_in_agent=agent
    ).order_by('-check_in_time')[:5]

    context = {
        'agent': agent,
        'active_flights': active_flights,
        'recent_checkins': recent_checkins,
        'today': today,
    }
    return render(request, 'flights/agent_dashboard.html', context)


@login_required
@user_passes_test(agent_check)
def flight_checkin(request, flight_id):
    """Страница регистрации на конкретный рейс"""
    flight = get_object_or_404(Flight, id=flight_id)
    agent = request.user.checkinagent

    # Пассажиры без регистрации
    registered_passengers = BoardingPass.objects.filter(flight=flight).values_list('passenger_id', flat=True)
    available_passengers = Passenger.objects.filter(flight=flight).exclude(id__in=registered_passengers)

    # Уже зарегистрированные пассажиры
    boarded_passengers = BoardingPass.objects.filter(flight=flight).select_related('passenger')

    # Доступные места (простая логика)
    all_seats = [f"{row}{seat}" for row in range(1, 31) for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
    taken_seats = [bp.seat_number for bp in boarded_passengers]
    available_seats = [seat for seat in all_seats[:flight.capacity] if seat not in taken_seats]

    if request.method == 'POST':
        # РЕГИСТРАЦИЯ СУЩЕСТВУЮЩЕГО ПАССАЖИРА
        passenger_id = request.POST.get('passenger_id')
        seat_number = request.POST.get('seat_number')

        # СОЗДАНИЕ НОВОГО ПАССАЖИРА
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_passport = request.POST.get('new_passport')
        new_seat_number = request.POST.get('new_seat_number')

        if passenger_id and seat_number:
            # Регистрация существующего пассажира
            passenger = get_object_or_404(Passenger, id=passenger_id)

            # Проверяем, что место свободно
            if BoardingPass.objects.filter(flight=flight, seat_number=seat_number).exists():
                messages.error(request, f'Место {seat_number} уже занято!')
            else:
                # Генерируем номер посадочного талона
                boarding_pass_number = f"BP{flight.number}{random.randint(1000, 9999)}"

                BoardingPass.objects.create(
                    passenger=passenger,
                    flight=flight,
                    boarding_pass_number=boarding_pass_number,
                    seat_number=seat_number,
                    gate=flight.gate,
                    check_in_agent=agent
                )

                messages.success(request, f'✅ Пассажир {passenger} успешно зарегистрирован на место {seat_number}!')
                return redirect('flights:flight_checkin', flight_id=flight_id)

        elif new_first_name and new_last_name and new_passport and new_seat_number:
            # СОЗДАНИЕ И РЕГИСТРАЦИЯ НОВОГО ПАССАЖИРА
            # Проверяем, что место свободно
            if BoardingPass.objects.filter(flight=flight, seat_number=new_seat_number).exists():
                messages.error(request, f'Место {new_seat_number} уже занято!')
            else:
                # Создаем нового пассажира
                passenger = Passenger.objects.create(
                    flight=flight,
                    first_name=new_first_name,
                    last_name=new_last_name,
                    passport_number=new_passport,
                    seat_number=new_seat_number
                )

                # Генерируем номер посадочного талона
                boarding_pass_number = f"BP{flight.number}{random.randint(1000, 9999)}"

                # Сразу регистрируем
                BoardingPass.objects.create(
                    passenger=passenger,
                    flight=flight,
                    boarding_pass_number=boarding_pass_number,
                    seat_number=new_seat_number,
                    gate=flight.gate,
                    check_in_agent=agent
                )

                messages.success(request,
                                 f'✅ Новый пассажир {new_first_name} {new_last_name} создан и зарегистрирован на место {new_seat_number}!')
                return redirect('flights:flight_checkin', flight_id=flight_id)

    context = {
        'flight': flight,
        'agent': agent,
        'available_passengers': available_passengers,
        'boarded_passengers': boarded_passengers,
        'available_seats': available_seats,
        'registered_count': boarded_passengers.count(),
        'total_capacity': flight.capacity,
    }
    return render(request, 'flights/flight_checkin.html', context)


@login_required
@user_passes_test(agent_check)
def passenger_lookup(request):
    """Поиск пассажиров с возможностью регистрации"""
    from django.db.models import Q
    search_query = request.GET.get('search', '')
    passengers = Passenger.objects.all()

    if search_query:
        passengers = passengers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(passport_number__icontains=search_query)
        )

    # Получаем информацию о регистрации для каждого пассажира
    passenger_data = []
    for passenger in passengers:
        # Получаем все посадочные талоны пассажира
        boarding_passes = BoardingPass.objects.filter(passenger=passenger)
        passenger_data.append({
            'passenger': passenger,
            'boarding_passes': boarding_passes,
            'is_registered': boarding_passes.exists()
        })

    # Используем правильные поля для фильтрации рейсов
    # Вместо is_active используем status или другие доступные поля
    context = {
        'passengers_data': passenger_data,
        'search_query': search_query,
        'flights': Flight.objects.all().order_by('departure_time')  # Все рейсы или фильтруем по статусу
    }
    return render(request, 'flights/passenger_lookup.html', context)


def register_from_search(request, passenger_id):
    """Регистрация пассажира из поиска"""
    if request.method == 'POST':
        passenger = get_object_or_404(Passenger, id=passenger_id)
        flight_id = request.POST.get('flight_id')
        seat_number = request.POST.get('seat_number')

        if flight_id and seat_number:
            flight = get_object_or_404(Flight, id=flight_id)

            # Создаем посадочный талон
            boarding_pass, created = BoardingPass.objects.get_or_create(
                passenger=passenger,
                flight=flight,
                defaults={
                    'seat_number': seat_number,
                    'boarding_pass_number': f"{flight.number}-{passenger.passport_number}"
                }
            )

            if created:
                messages.success(request,
                                 f'Пассажир {passenger.first_name} {passenger.last_name} зарегистрирован на рейс {flight.number}')
            else:
                messages.info(request, f'Пассажир уже зарегистрирован на этот рейс')

        return redirect('flights:passenger_lookup')