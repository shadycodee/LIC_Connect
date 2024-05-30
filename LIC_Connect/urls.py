"""
URL configuration for LIC_Connect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webapp import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('home/', views.home, name='home'),


    # Admin PATH
    
    path('manage_staff/', views.manageStaff, name='manage_staff'),
    path('admin_settings/', views.adminSettings, name='admin_settings'),
    path('delete/<int:staff_id>/', views.deleteStaff, name='delete_staff'),
    path('delete_student/<str:studentID>/', views.deleteStudent, name='delete_student'),
    path('analytics/', views.analytics, name='analytics'),
    path('process_payment/', views.process_payment, name='process_payment'),
]
