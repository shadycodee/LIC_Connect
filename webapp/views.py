from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Staff, Student
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from .models import Payment
from django.shortcuts import get_object_or_404
from django.urls import reverse


# Create your views here.

def createStaff(request):
    if request.method == 'POST':
        username = request.POST.get('user')
        name = request.POST.get('name')
        password = request.POST.get('password')
        
        staff = User.objects.create_user(username, name, password)
        staff.save()

    return render(request, 'manage_staff.html')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        
        # If not authenticated as User, try to authenticate as Staff
        try:
            staff = Staff.objects.get(username=username)
            if check_password(password, staff.password):
                # Store staff information in session
                request.session['staff_id'] = staff.id
                return redirect('home')  # Redirect to a different home for staff
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
         return HttpResponse("Not allowed to access this page.")
            
    return render(request, 'admin_settings.html')

def logoutPage(request):
    logout(request)

    return redirect('login')
    
def analytics(request):
     if request.user.is_superuser:
          return render(request, 'analytics.html')
     else:
          return HttpResponse("Not allowed to access this page.")

    
def home(request):
    students = Student.objects.all().values('studentID', 'name', 'course', 'time_left')
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
            return redirect('/home?message=Student created successfully.')

        else:
            return redirect('/home?message=Student already exists.')

    return render(request, 'home.html', {'students': students})

def manageStaff(request):
    if request.user.is_superuser: 
        if request.method == 'POST':
            name = request.POST.get('name')
            username = request.POST.get('username')
            password = request.POST.get('password')

            # message notification to be followed na lang
            if Staff.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different one.')
            else:
                hashed_password = make_password(password)
                staff = Staff(name=name, username=username, password=hashed_password)
                staff.save()
                return redirect('/manage_staff?message=Staff added successfully!')

        staffs = Staff.objects.all()
    else:
         return HttpResponse("Not allowed to access this page.")

    return render(request, 'manage_staff.html', {'staffs': staffs})

def deleteStaff(request, staff_id):
    if request.method == 'POST':
        staff = get_object_or_404(Staff, pk=staff_id)
        staff.delete()
        return redirect('/manage_staff?message=Staff deleted successfully!')


def deleteStudent(request, studentID):
    if request.method == 'POST':
        student = Student.objects.get(pk=studentID)
        student.delete()
        return redirect('/home?message=Student deleted successfully.')

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
        
        return redirect(f'{reverse("home")}?message={time_added} minutes added successfully for student "{student.name}".')
    else:
        return HttpResponse("Invalid request", status=400)

