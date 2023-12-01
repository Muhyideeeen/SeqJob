
from rest_framework import viewsets,status
from rest_framework.response import Response
from myauthentication import permissions
from .. import company_serializer
from utils.response_data import response_data
from django.shortcuts import get_object_or_404
from jobs.models import Job 


class CompanySetUpMedicals(viewsets.ViewSet):
    serializer_class = company_serializer.CompanySetUpMedicals
    permission_classes = [permissions.OnlyCompany,]

    def create(self,request,pk=None):
        job_id = self.request.data.get('job_id',-1)
        job = get_object_or_404(Job,id = job_id)
        self.check_object_permissions(self.request,obj=job)
        serializer = self.serializer_class(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = response_data(201,message='Created  Successfully',data=[])
        return Response(data,status=status.HTTP_201_CREATED)
    