from django.http import HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.shortcuts import render, redirect
from .models import Train, Booking
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
# Create your views here.

@login_required
def home(request):
    source = request.GET.get("source", "").strip()
    destination = request.GET.get("destination", "").strip()
    departure_time = request.GET.get("departure_time", "").strip()
    trains = Train.objects.all().order_by('-departure_time')
   
    if source:
        trains = trains.filter(source__icontains=source)
    
    if destination:
       trains = trains.filter(destination__icontains=destination)
    
    if departure_time:
        trains = trains.filter(departure_time__icontains=departure_time)
        
    for train in trains:
        if train.departure_time < timezone.now():
            train.departed_status = 'Departed'
    return render(request, 'backend/home.html', {'trains':trains})

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, create = Token.objects.get_or_create(user = user)
            return Response({'token':token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self,request):
        user = authenticate(username = request.data['username'], password=request.data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token':token.key})
        return Response({'error':'Invalid Credentials'}, status=400)
    
        
def register_page(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"{username}'s account has been created! Please login")
            return redirect('backend-home')


    else:
        form = UserRegisterForm()
        
    

    return render(request, 'backend/register.html', {'form': form})

@login_required
def train_details(request, pk):
    train = get_object_or_404(Train, id=pk)
    return render(request, 'backend/train_details.html', {'train':train})
    


@login_required
def book_train(request, pk):
    train = get_object_or_404(Train, id=pk)
    if train.seats_available>0 and train.departure_time > timezone.now():
        prev_bookings = Booking.objects.filter(user=request.user)
        for i in prev_bookings:
            if i.train == train:
                messages.error(request, f"Seat is already booked in this train!")
                return redirect('train-details', pk)
            
        else:
        
            seat_number = train.total_seats - train.seats_available + 1
            train.seats_available-=1
            train.save()
            Booking.objects.create(user = request.user, train=train, seat_number = seat_number)
            messages.success(request, f"Booked seat in {train.name} for {request.user}!")
    elif train.departure_time < timezone.now():
        messages.error(request, 'Train has already departed. Cannot book ticket now.')
        return redirect('train-details', pk)
    return redirect('my-bookings')
    


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user = request.user)
    return render(request, 'backend/my_bookings.html', {'bookings':bookings})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    train = booking.train
    train.seats_available+=1
    train.save()
    messages.success(request, f'Booking cancelled for {train}')
    booking.delete()
    return redirect('my-bookings')


def is_super(user):
    return user.is_superuser

class AddTrain(LoginRequiredMixin, UserPassesTestMixin, CreateView): 
    
    model = Train
    success_url = '/trains/'
    fields = ['name', 'source', 'destination', 'departure_time', 'total_seats', 'seats_available']
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return HttpResponse("Only ADMIN is allowed on this page")
        
    def form_valid(self, form):
    
        if Train.objects.filter(
            name = form.cleaned_data.get('name'),
            source = form.cleaned_data.get('source'),
            destination = form.cleaned_data.get('destination'),
            departure_time = form.cleaned_data.get('departure_time'),
            total_seats = form.cleaned_data.get('total_seats'),
            seats_available = form.cleaned_data.get('seats_available')
        ).exists():   
            messages.error(self.request, f'This train already exists. Please add a different train.')
            return redirect('add-train')       
        elif form.cleaned_data.get('seats_available')>form.cleaned_data.get('total_seats'):
            messages.error(self.request, f'Seats available can not be greater than the number of total seats')
            return redirect('add-train')
        return super().form_valid(form)
    
    
class DeleteTrain(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    
    model = Train
    success_url='/trains/'
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return HttpResponse('<h1> Only ADMIN is allowed on this page </h1>')
    
    
class UpdateTrain(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Train
    success_url = '/trains/'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return HttpResponse('<h1> Only Admin is allowed on this page')
    
    fields = ['name', 'source', 'destination', 'departure_time', 'total_seats', 'seats_available']
    
    def form_valid(self, form):
        if form.cleaned_data.get('seats_available') > form.cleaned_data.get('total_seats'):
            form.add_error('seats_available', 'Seats available cannot be greater than the total number of seats.')
            return super().form_invalid(form)
        elif form.cleaned_data.get('departure_time') < timezone.now():
            form.add_error('departure_time', 'Please give a departure time in future.')
            return super().form_invalid(form)
        else:   
            return super().form_valid(form)