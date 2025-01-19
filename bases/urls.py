from django.urls import path
from django.contrib.auth import views as auth_views

from bases.views import Home, HomeSinPrivilegios, dashboard, user_editar, user_password

urlpatterns = [
    path('', Home.as_view(),name='home'),
    path('login/',auth_views.LoginView.as_view(template_name='bases/page-login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='bases/page-login.html'),name='logout'),
    path('sin_privilegios/',HomeSinPrivilegios.as_view(), name='sin_permisos'),
    path('dashboard/',dashboard, name='dashboard'),
    path('editarusuario/<int:pk>',user_editar,name='usuario_editar'),
    path('passwordusuario/<int:pk>',user_password,name='usuario_password'),
    ]
