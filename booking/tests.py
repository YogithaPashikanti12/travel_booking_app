from django.test import TestCase

# Create your tests here.

from django.contrib.auth.models import User
from django.urls import reverse
from .models import TravelOption, Booking
from datetime import datetime, timedelta
class BookingFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p')
        self.travel = TravelOption.objects.create(
        type='Bus', source='A', destination='B',
        date_time=datetime.now()+timedelta(days=1), price=100,
        available_seats=10
        )
    def test_booking_reduces_seats(self):
        self.client.login(username='u', password='p')
        resp = self.client.post(reverse('book', args=[self.travel.pk]),
        {'number_of_seats': 3})
        self.assertRedirects(resp, reverse('my_bookings'))
        self.travel.refresh_from_db()
        self.assertEqual(self.travel.available_seats, 7)
        b = Booking.objects.get(user=self.user)
        self.assertEqual(b.total_price, 300)
    def test_cancellation_returns_seats(self):
        self.client.login(username='u', password='p')
        self.client.post(reverse('book', args=[self.travel.pk]),
        {'number_of_seats': 2})
        b = Booking.objects.get(user=self.user)
        self.client.get(reverse('cancel_booking', args=[b.pk]))
        self.travel.refresh_from_db()
        b.refresh_from_db()
        self.assertEqual(self.travel.available_seats, 10)
        self.assertEqual(b.status, 'Cancelled')
