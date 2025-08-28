#from django.shortcuts import render

# Create your views here.

#added manually
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import TravelOption, Booking
from .forms import UserRegisterForm, ProfileForm, BookingForm
from datetime import datetime

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('travel_list')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'booking/profile.html', {'form': form})

def travel_list(request):
    items = TravelOption.objects.all().order_by('date_time')
    t = request.GET.get('type')
    src = request.GET.get('source')
    dst = request.GET.get('destination')
    date = request.GET.get('date')
    if t:
        items = items.filter(type=t)
    if src:
        items = items.filter(source__icontains=src)
    if dst:
        items = items.filter(destination__icontains=dst)
    if date:
        try:
            start = datetime.strptime(date, '%Y-%m-%d')
            items = items.filter(date_time__date=start.date())
        except ValueError:
            pass
    context = {'items': items, 'filters': {'type': t or '', 'source': src or '', 'destination': dst or '', 'date': date or ''}}
    return render(request, 'booking/travel_list.html', context)

@login_required
def book(request, pk):
    travel = get_object_or_404(TravelOption, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data['number_of_seats']
            with transaction.atomic():
                locked = TravelOption.objects.select_for_update().get(pk=pk)
                if seats > locked.available_seats:
                    messages.error(request, 'Not enough seats available.')
                    return redirect('book', pk=pk)
                locked.available_seats -= seats
                locked.save()
                total = seats * locked.price
                Booking.objects.create(user=request.user, travel_option=locked, number_of_seats=seats, total_price=total, status='Confirmed')
                messages.success(request, 'Booking confirmed!')
                return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'booking/booking_form.html', {'travel': travel, 'form': form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('travel_option').order_by('-booking_date')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status == 'Cancelled':
        messages.info(request, 'Booking already cancelled.')
        return redirect('my_bookings')
    with transaction.atomic():
        booking.status = 'Cancelled'
        booking.save()
        travel = TravelOption.objects.select_for_update().get(pk=booking.travel_option.pk)
        travel.available_seats += booking.number_of_seats
        travel.save()
        messages.success(request, 'Booking cancelled and seats returned.')
    return redirect('my_bookings')

