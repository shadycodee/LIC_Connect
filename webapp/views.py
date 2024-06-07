from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Staff, Student, Session
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from .models import Payment
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
import plotly.express as px
import plotly.graph_objs as go
from django.db.models import Sum
import calendar
from django.core.paginator import Paginator
from django.db import models
from django.contrib.auth.hashers import make_password

# Create your views here.

def check_password_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        encoded_password = request.POST.get('encoded')  # Assuming 'encoded' is the second argument

        if password == encoded_password:
            return JsonResponse({'correct': True})
        else:
            return JsonResponse({'correct': False})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def createStaff(request):
    if request.method == 'POST':
        username = request.POST.get('user')
        name = request.POST.get('name')
        password = request.POST.get('password')
        
        staff = User.objects.create_user(username, name, password)
        staff.save()

    return render(request, 'manage_staff.html')
def delete_sessions(request):
    if request.method == 'POST':
        Payment.objects.all().delete()
        Session.objects.all().delete()
        Student.objects.all().update(time=600)
        messages.success(request, "Records Reset")

    return redirect('analytics')
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        
        # If not authenticated as User, try to authenticate as Staff
        try:
            staff = Staff.objects.get(username=username)
            if check_password(password, staff.password):
                # Store staff information in session
                request.session['staff_id'] = staff.id
                return redirect('dashboard')  # Redirect to a different dashboard for staff
            else:
                error_message = 'Username or password is incorrect'
                return render(request, 'login.html', {'error_message': error_message})
        except Staff.DoesNotExist:
            error_message = 'Username or password is incorrect'
            return render(request, 'login.html', {'error_message': error_message})
        
        
    return render(request, 'login.html')

def adminSettings(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            current_password = request.POST.get('current-password')
            new_password = request.POST.get('new-password')
            confirm_password = request.POST.get('confirm-password')
            
            # Check if New passwords match
            if new_password != confirm_password:
                messages.error(request, "New password and confirm password do not match.")
                return redirect('admin_settings')
            
            # Verify current Password
            if not check_password(current_password, request.user.password):
                messages.error(request, "Current password is incorrect.")
                return redirect('admin_settings')
            
            # Check if new password matches with the current password
            if request.user.check_password(new_password):
                messages.error(request, "New password cannot be the same as the current password.")
                return redirect('admin_settings')
        
            # Method to change password and then save
            request.user.set_password(new_password)
            request.user.save()

            update_session_auth_hash(request, request.user)  # Important to keep the user logged in after password change
            messages.success(request, "Password changed successfully.")
            return redirect('login')
    else:
        messages.error(request, "You are restricted to view this page!")
        return redirect('dashboard')
            
    return render(request, 'admin_settings.html')

def logoutPage(request):
    logout(request)

    return redirect('login')
    
def analytics(request):
     if request.user.is_superuser:
        monthly_data = (
            Session.objects.annotate(month=models.functions.ExtractMonth('date')).values('month').values('month').annotate(total_consumed_time=Sum('consumedTime'))
        )
        # Extracting month numbers and consumed time values
        months = [entry['month'] for entry in monthly_data]
        consumed_times = [entry['total_consumed_time'] for entry in monthly_data]

        # Perform mathematical operations on consumed times (e.g., convert to hours)
        consumed_times = [(time / 60) * 15 for time in consumed_times]
        
        # Map month numbers to month names
        month_names = [calendar.month_name[month] for month in months]
        
        # Plotly graph 1
        fig = go.Figure(data=go.Bar(x=month_names, y=consumed_times, text=consumed_times, textposition='auto'))
        fig.update_layout(
        title={
            'text': "Computer Usage Income",
            'x': 0.5,  # Center title horizontally
            'xanchor': 'center',  # Center title horizontally
            'font': {'size': 22}  # Adjust font size if needed
        },
        xaxis_title="Month",
        yaxis_title="Income"
    )
        
        monthly_data_payment = (
            Payment.objects.annotate(month=models.functions.ExtractMonth('date')).values('month').values('month').annotate(payment=Sum('payment'))
        )
        months = [entry['month'] for entry in monthly_data_payment]
        payments = [entry['payment'] for entry in monthly_data_payment]

       
        # Plotly graph 2
        fig2 = go.Figure(data=go.Bar(x=month_names, y=payments, textposition='auto'))
        fig2.update_layout(
            title={
                'text': "Loading Income",
                'x': 0.5,  # Center title horizontally
                'xanchor': 'center',  # Center title horizontally
                'font': {'size': 22}  # Adjust font size if needed
            },
            xaxis_title="Month",
            yaxis_title="Income"
        )

        chart1 = fig.to_html(full_html=False)
        chart2 = fig2.to_html(full_html=False)
        context = {'chart': chart1, 'chart2': chart2}

          
        return render(request, 'analytics.html', context)
     else:
            messages.error(request, "You are restricted to view this page!")
            return redirect('dashboard')

    
def dashboard(request):
    students = Student.objects.all().values('studentID', 'name', 'course', 'time_left')

    # Convert time_left to hh:mm:00 format
    formatted_students = []
    for student in students:
        time_left_minutes = student['time_left']
        hours = time_left_minutes // 60
        minutes = time_left_minutes % 60
        formatted_time_left = f"{hours:02}:{minutes:02}:00"
        formatted_student = {
            'studentID': student['studentID'],
            'name': student['name'],
            'course': student['course'],
            'time_left': formatted_time_left,
        }
        formatted_students.append(formatted_student)
    
    # Implement pagination
    paginator = Paginator(formatted_students, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        id = request.POST.get('studentid')
        name = request.POST.get('name')
        course = request.POST.get('course')
        password = request.POST.get('password')

        if not Student.objects.filter(studentID=id).exists():
            student = Student.objects.create(
                studentID=id,
                name=name,
                course=course,
                password=password
            )
            student.save()
            messages.success(request, 'Student added successfully!')
            return redirect('dashboard')

        else:
            messages.error(request, 'Student already exists!')
            return redirect('dashboard')

    return render(request, 'dashboard.html', {'page_obj': page_obj})

def studentSessions(request, student_id):
    student = get_object_or_404(Student, studentID=student_id)
    sessions = Session.objects.filter(parent_id=student).values(
        'course', 'date', 'loginTime', 'logoutTime', 'consumedTime'
    )
    
    return JsonResponse(list(sessions), safe=False)

def manageStaff(request):
    if request.user.is_superuser: 
        if request.method == 'POST':
            name = request.POST.get('name')
            username = request.POST.get('username')
            password = request.POST.get('password')

            # message notification to be followed na lang
            if Staff.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
                return redirect('manage_staff')
            else:
                hashed_password = make_password(password)
                staff = Staff(name=name, username=username, password=hashed_password)
                staff.save()
                messages.success(request, 'Staff added successfully!')
                return redirect('manage_staff')

        staffs = Staff.objects.all()
    else:
            messages.error(request, "You are restricted to view this page!")
            return redirect('dashboard')

    return render(request, 'manage_staff.html', {'staffs': staffs})

def deleteStaff(request, staff_id):
    if request.method == 'POST':
        staff = get_object_or_404(Staff, pk=staff_id)
        staff.delete()
        messages.success(request, 'Staff deleted successfully!')
        return redirect('manage_staff')


def deleteStudent(request, studentID):
    if request.method == 'POST':
        student = Student.objects.get(pk=studentID)
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('dashboard')

def process_payment(request):
    if request.method == 'POST':
        student_id = request.POST.get('studentID')
        payment_amount = int(request.POST.get('paymentAmount'))

        student = get_object_or_404(Student, studentID=student_id)
        time_added = (payment_amount / 15) * 60

        # Update time left
        student.time_left += time_added
        student.save()
        
        payment = Payment(parent=student, payment=payment_amount, time=time_added)
        payment.save()
        messages.success(request, f'{time_added} minutes added successfully for student "{student.name}"')
        return redirect('dashboard')
    else:
        return HttpResponse("Invalid request", status=400)

