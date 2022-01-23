"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('application.urls')),
    path('api/', include('api.urls')),

    # path('accounts/', include('django.contrib.auth.urls')),
    # path('dashboard/', include('application.urls')),
    # path('dashboard/buttons/',include('application.urls')),
    # path('dashboard/dropdowns/',include('application.urls')),
    # path('dashboard/typography', include('application.urls')),
    # path('dashboard/basic_elements', include('application.urls')),
    # path('dashboard/chartjs', include('application.urls')),
    # path('dashboard/basictable', include('application.urls')),
    # path('dashboard/icons', include('application.urls')),
    # path('dashboard/Login', include('application.urls')),
    # path('dashboard/register', include('application.urls')),
    # path('dashboard/profile', include('application.urls')),
    # path('dashboard/error_404', include('application.urls')),
    # path('dashboard/error_500', include('application.urls')),
    # path('dashboard/documentation', include('application.urls')),




]
