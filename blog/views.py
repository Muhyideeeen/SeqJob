from django.shortcuts import render

from . import models,serializer,filter
from rest_framework import mixins,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status,permissions

class BlogViewSets(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    serializer_class = serializer.BlogSerializer
    queryset= models.BlogPost.objects.all()
    permission_classes = [permissions.AllowAny]

    filterset_class = filter.BlogFilter

    @action(['get'],detail=False,)
    def get_categories(self,request,Format=None):

        return Response(data=models.Categories.objects.all().values('names','id'),status=status.HTTP_200_OK)


class EmailSubscriberViewSets(mixins.CreateModelMixin,viewsets.GenericViewSet):
    queryset = models.EmailSubscribers.objects.all()
    serializer_class = serializer.EmailSubscribersSerializer
    permission_classes = [permissions.AllowAny]
