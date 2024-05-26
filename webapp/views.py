from django.shortcuts import render

# Create your views here.

def createStaff(request):
    if request.method == 'POST':
        username = request.POST.get('user')
def LoginPage(request):
    if request.method == 'POST':
        request
    return render(request, 'login.html')

def adminHome(request):
    return render(request, 'admin_home.html')