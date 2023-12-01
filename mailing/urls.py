

from .views import request_forgot_password,reset_password ,activate_user
from django.urls import path


urlpatterns= [
    path('request_forgot_password/',request_forgot_password,name='request_forgot_password'),
    path('reset_password/<uidb64>/<token>/',reset_password,name='reset_password'),
        path('activate/<uidb64>/<token>/',activate_user,name='activate'),
]