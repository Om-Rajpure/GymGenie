"""
URL configuration for GymGenie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from core import views
from django.conf.urls.static import static
from django.conf import settings
from core.views import track_progress


urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.home, name="home"),
    path('login/',views.login, name='login'),
    path('signup/',views.signup, name='signup'),
    path('join/<str:plan_name>/', views.join_plan, name='join_plan'),
    path('payment/', views.payment, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('weight_gain/', views.weight_gain, name='weight_gain'),
    path('track_progress/', views.track_progress, name='track_progress'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
