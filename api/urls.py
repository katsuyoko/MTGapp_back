from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('calendar_info/<str:mail_address>/', views.get_calendar_info, name='calInfo'),
    path('item_info/<int:price>/', views.get_item_info, name='itemInfo'),
    # path('save/', views.save_info, name='save'),
]
