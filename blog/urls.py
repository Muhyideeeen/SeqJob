

from django.urls import path

from rest_framework.routers import  DefaultRouter
from . import views
route = DefaultRouter()
route.register('blog-view',views.BlogViewSets)
route.register('email-subscription',views.EmailSubscriberViewSets)


urlpatterns = [

]+ route.urls