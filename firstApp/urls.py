from django.urls import path
from firstApp import views

app_name = 'firstApp'

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    path('top', views.Top.as_view(), name='top'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('input_address', views.InputMailAddress.as_view(), name='mail_address'),
    path('confilm', views.Confilm.as_view(), name='confilm'),
    path('time_display', views.TimeDisplay.as_view(), name='time_display'),
]

