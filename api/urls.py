from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('', views.Top.as_view(), name='top'),
    path('calendar_info/<str:mail_address>/', views.get_calendar_info, name='calInfo'),
    path('calendar_info/', views.get_calendar_info, name='calInfo'),
    path('item_info/<int:price>/', views.get_item_info, name='itemInfo'),
    path('auth/', views.auth, name='auth'),
    path('callback/', views.callback, name='callback'),
    path('revoke/', views.revoke, name='revoke'),
    # path('save/', views.save_info, name='save'),
]
