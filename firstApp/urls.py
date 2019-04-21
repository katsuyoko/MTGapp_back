from django.urls import path
from firstApp import views
from . import views

app_name = 'firstApp'

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    path('top', views.Top.as_view(), name='top'),
    path('top2', views.Top2.as_view(), name='top2'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('auth/', views.auth, name='auth'),
    path('callback/', views.callback, name='callback'),
    path('revoke/', views.revoke, name='revoke'),
]

