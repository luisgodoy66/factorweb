from django.urls import path
from django.contrib.auth import views as auth_views

from bases.views import Home, SolicitudesPendientes, HomeSinPrivilegios\
     , dashboard

urlpatterns = [
    path('', Home.as_view(),name='home'),
    # path('', SolicitudesPendientes,name='home'),
    path('login/',auth_views.LoginView.as_view(template_name='bases/page-login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='bases/page-login.html'),name='logout'),
    path('solicitudespendientes',SolicitudesPendientes),
    path('sin_privilegios/',HomeSinPrivilegios.as_view(), name='sin_privilegios'),
    path('dashboard/',dashboard, name='dashboard'),
    ]
