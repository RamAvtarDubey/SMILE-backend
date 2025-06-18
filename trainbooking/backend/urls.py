from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='backend-home'),
    path('trains/', views.home, name='backend-home'),
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('register-page/', views.register_page, name='register-page'),
    path('login-page/', auth_views.LoginView.as_view(template_name = 'backend/login.html'), name='login-page'),
    path('logout-page/', auth_views.LogoutView.as_view(template_name= 'backend/logout.html'), name='logout-page'),
    path('trains/<int:pk>/', views.train_details, name='train-details'),
    path('trains/<int:pk>/book', views.book_train, name='book-train'),
    path('bookings/', views.my_bookings, name='my-bookings'),
    path('bookings/cancel/<int:pk>/', views.cancel_booking, name='cancel-booking'),
    path('add-train/', views.AddTrain.as_view(), name='add-train'),
    path('trains/<int:pk>/delete-train/', views.DeleteTrain.as_view(), name='delete-train'),
    path('trains/<int:pk>/update/', views.UpdateTrain.as_view(), name='update-train')
]
