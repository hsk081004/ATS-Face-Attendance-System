from django.shortcuts import render, redirect
from .models import Student, Attendance
from .face_recognition import recognize
import threading


def home(request):
    students = Student.objects.all()
    return render(request, "home.html", {"students": students})


def start_attendance(request):
    # run camera in background
    thread = threading.Thread(target=recognize)
    thread.daemon = True
    thread.start()

    return redirect('dashboard')


def dashboard(request):
    attendance = Attendance.objects.all().order_by("-date")
    students = Student.objects.all()

    return render(request, "dashboard.html", {
        "attendance": attendance,
        "total_students": students.count(),
        "total_attendance": attendance.count()
    })


def students(request):
    students = Student.objects.all()
    return render(request, "students.html", {"students": students})


def attendance_view(request):
    records = Attendance.objects.all().order_by("-date")
    return render(request, "attendance.html", {"records": records})
