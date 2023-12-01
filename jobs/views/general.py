from rest_framework import  viewsets,mixins,generics
from jobs.serializers import general as general_job_serializer
from myauthentication.permissions import OnlyCompany
from utils.response_data import response_data
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from jobs import models  as job_models
from rest_framework import status


class QuetionViewset(viewsets.ViewSet):
    permission_classes=[]
    serializer_class = general_job_serializer.FilterQuetionFormatterSerializer


    def get_permissions(self):
        #for now we would change this  because job_seekers and company are ment to access this
        if self.request.user.user_type == 'company':
            self.permission_classes =[OnlyCompany]
        if self.request.user.user_type == 'job_seakers':
            pass
        return super().get_permissions()

    @action(methods=['post'],detail=False,)
    def get_quetion(self,request,*args,**kwargs):
        quetion_id = request.data.get('quetion_id',None)
        quetion = get_object_or_404(job_models.JobFilterQuetion,id=quetion_id)
        serializer = self.serializer_class(quetion,context={'request':request},many=False)
        data = response_data(200,'success',data=serializer.data)
        return Response(data,status.HTTP_200_OK)