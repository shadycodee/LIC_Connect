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
    path('', views.LoginPage, name='login'),

    #Staff PATH
    path('staff_home/', views.staffHome, name='staff_home'),

    # Admin PATH
    path('admin_home/', views.adminHome, name='admin_home'),
    path('manage_staff/', views.manageStaff, name='manage_staff'),
]
