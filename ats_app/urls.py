from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('students/', views.students, name='students'),

    path('attendance/', views.attendance_view, name='attendance'),

    path('start-attendance/', views.start_attendance, name='start_attendance'),

]