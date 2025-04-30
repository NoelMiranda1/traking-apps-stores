from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'scraper'

urlpatterns = [
    path('', views.app_list, name='app_list'),
    path('login/', auth_views.LoginView.as_view(
        template_name='scraper/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='scraper:login',
        template_name='scraper/login.html'
    ), name='logout'),
]