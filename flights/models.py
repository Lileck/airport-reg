from django.db import models


class Flight(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('boarding', 'Посадка'),
        ('departed', 'Вылетел'),
        ('landed', 'Приземлился'),
        ('cancelled', 'Отменен'),
    ]

    number = models.CharField(max_length=10, unique=True, verbose_name="Номер рейса")
    departure_city = models.CharField(max_length=100, verbose_name="Город вылета", blank=True, null=True)
    destination_city = models.CharField(max_length=100, verbose_name="Город назначения", blank=True, null=True)
    departure_time = models.DateTimeField(verbose_name="Время вылета")
    arrival_time = models.DateTimeField(verbose_name="Время прибытия")
    gate = models.CharField(max_length=10, verbose_name="Выход", default="A1")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")
    capacity = models.IntegerField(default=180, verbose_name="Вместимость")

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"
        ordering = ['departure_time']  # Сортировка по времени вылета

    def __str__(self):
        return f"{self.number}: {self.departure_city} → {self.destination_city}"


class Passenger(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, verbose_name="Рейс")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    passport_number = models.CharField(max_length=20, verbose_name="Номер паспорта")
    seat_number = models.CharField(max_length=5, verbose_name="Номер места")

    class Meta:
        verbose_name = "Пассажир"
        verbose_name_plural = "Пассажиры"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
class CheckInAgent(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='checkinagent')
    agent_id = models.CharField(max_length=20, unique=True, verbose_name="ID агента")
    workstation = models.CharField(max_length=50, verbose_name="Рабочее место")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    def __str__(self):
        return f"Агент {self.user.username} ({self.workstation})"

class BoardingPass(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, verbose_name="Пассажир")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, verbose_name="Рейс")
    boarding_pass_number = models.CharField(max_length=15, unique=True, verbose_name="Номер посадочного талона")
    seat_number = models.CharField(max_length=5, verbose_name="Номер места")
    gate = models.CharField(max_length=10, blank=True, verbose_name="Выход")
    boarding_time = models.DateTimeField(null=True, blank=True, verbose_name="Время посадки")
    check_in_time = models.DateTimeField(auto_now_add=True, verbose_name="Время регистрации")
    check_in_agent = models.ForeignKey(CheckInAgent, on_delete=models.CASCADE, verbose_name="Агент регистрации")
    status = models.CharField(max_length=20, choices=[
        ('checked_in', 'Зарегистрирован'),
        ('boarded', 'Прошел посадку'),
        ('cancelled', 'Отменен')
    ], default='checked_in', verbose_name="Статус")

    class Meta:
        verbose_name = "Посадочный талон"
        verbose_name_plural = "Посадочные талоны"

    def __str__(self):
        return f"{self.boarding_pass_number} - {self.passenger}"