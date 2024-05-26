from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def createStaff(request):
    if request.method == 'POST':
        username = request.POST.get('user')
        name = request.POST.get('name')
        password = request.POST.get('password')
        
        staff = User.objects.create_user(username, name, password)
        staff.save()

    return render(request, 'manage_staff.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')
        print(f"Username: {username}, Password: {password}")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_home')
            else: 
                return redirect('staff_home')
        
        else:
            error_message = 'Invalid credentials'
            return render(request, 'login.html', {'error_message': error_message}) 
    return render(request, 'login.html')

def staffHome(request):
    return render(request, 'staff_home.html')

def adminHome(request):
    return render(request, 'admin_home.html')

def manageStaff(request):
    return render(request, 'manage_staff.html')