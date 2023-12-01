from rest_framework import status, generics,viewsets,mixins
from rest_framework.generics import GenericAPIView
from utils.custom_response import Success_response
from utils.response_data import response_data
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,)
from . import serializer as custom_serializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from . import permissions as custom_permission
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from utils.custom_parsers import NestedMultipartParser
from rest_framework.parsers import FormParser
from rest_framework.decorators import action,parser_classes,api_view
from utils.exception import CustomValidation
from myauthentication.permissions import IsAdmin

class AdminManagerUserPassword(viewsets.ViewSet):
    permission_classes=[IsAuthenticated,IsAdmin]

    def create(self,request,*args,**kwargs):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        user = get_object_or_404(get_user_model(),email=email)
        user.set_password(new_password)
        user.save()
        return Success_response('password changed',data=[],)
class Login(TokenObtainPairView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = custom_serializer.LoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if request.user.is_authenticated:
            data = response_data(400, "You are already authenticated", [])
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            data = response_data(401, str(e), [])
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        except TypeError as _:  # noqa: F841
            data = response_data(401, "username or password incorrect", [])
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        data = response_data(
            200, "login successful", {"tokens": serializer.validated_data}
        )
        return Response(data, status=status.HTTP_200_OK)


class AccountCreation(GenericAPIView):
    # permission_classes = []
    # authentication_classes = []

    def post(self, request):

        serializer = self.serializer_class(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = response_data(201, "Account Create Successful", [])
        return Response(data, status=status.HTTP_201_CREATED)


class RegisterCompanyView(AccountCreation):
    serializer_class = custom_serializer.RegisterCompanySerializer


class RegisterHrView(AccountCreation):
    permission_classes=[custom_permission.OnlyCompany]
    serializer_class = custom_serializer.RegisterHr

class RegisterJobSeekerView(AccountCreation):
    permission_classes=[]
    serializer_class = custom_serializer.RegisterJobSeekerSerializer


class GetUserProfileMix:
    def get_user_data(self):
        # use logged in user
        user_id = self.request.query_params.get('user_id',self.request.user.id)

        return  get_object_or_404(get_user_model(),id=user_id)

    def list(self, request, *args, **kwargs):
        
        user = self.get_user_data()
        serializer  =custom_serializer.UserDataCleaner
        clean_data = serializer(instance=user,many=False)

        return Success_response(msg='success',data=clean_data.data)   

    def patch(self, request, *args, **kwargs):
        user = self.get_user_data()
        serializer = self.serializer_class(data=request.data,instance=user)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Success_response('updated Successfully',)    

class CompanyProfileApi(GetUserProfileMix,generics.ListAPIView,generics.UpdateAPIView):
    serializer_class = custom_serializer.CompanyUpdateSerializer
    parser_classes = (NestedMultipartParser,FormParser,)

class JobSeekerProfileApi(GetUserProfileMix,generics.ListAPIView,generics.UpdateAPIView):
    serializer_class = custom_serializer.JobSeekerProfileUpdateSerializer
    parser_classes = (NestedMultipartParser,FormParser,)


@api_view(['post'],)
def parse_cv_file(request,*args,**kwargs):
    serializer =custom_serializer.ParseCvSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_200_OK,data=serializer.data)
class PanelistProfileApi(GetUserProfileMix,generics.ListAPIView,generics.UpdateAPIView):
    serializer_class = custom_serializer.PanelistProfileUpdateSerializer
    parser_classes = (NestedMultipartParser,FormParser,)



class UserSettings(viewsets.ViewSet,):
    # queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]

    @action(methods=['post'],detail=False,)
    def admin_update_any_acc(self,request,*args,**kwargs):
        'only andmin can access this'
        if not (request.user.is_staff== True or request.user.is_admin==True):
            raise CustomValidation(detail='Please Login As A Admin',field='user',status_code=status.HTTP_400_BAD_REQUEST)
        user_email = request.data.get('email','')
        USERMODEL= get_user_model()
        if not USERMODEL.objects.filter(email=user_email).exists():
            raise CustomValidation(detail='user does not exist',field='email')
        
        user = USERMODEL.objects.get(email=user_email)
        user.set_password('backup2020')
        user.save()

        return Success_response(msg='Password Updated Success',status_code=status.HTTP_200_OK)



    @action(methods=['post'],detail=False,)
    def update_password(self,request,*args,**kwargs):
        password = request.data.get('password',None)
        if password is None:
            raise CustomValidation(field='error',detail='Please password is required')
        
        user= get_object_or_404(get_user_model(),id=request.user.id)
        user.set_password(password)
        user.save() 

        return Success_response(msg='Password changed success',data=[])
    
    def destroy(self, request, *args, **kwargs):
        'the user that is logged in is the instance that get delete'
        user= get_object_or_404(get_user_model(),id=request.user.id)
        user.delete()
        return Success_response(msg='Deleted Successfully',status_code=status.HTTP_204_NO_CONTENT)




class ForgotPasswordViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]

    @action(methods=['post'],detail=False,permission_classes=[AllowAny])
    def request_password_change(self,request,*args,**kwargs):
        print({'d':request.data})
        serialzier= custom_serializer.PasswordResetRequestSerializer(data=request.data,context={'request':request})
        serialzier.is_valid(raise_exception=True)
        serialzier.save()
        return Success_response('Forgot password link sent to your mail!')
    
    @action(methods=['post'],detail=False,permission_classes=[AllowAny])
    def rest_password(self,request,*args,**kwargs):
        serialzier =custom_serializer.PasswordResetConfirmationSerializer(data=request.data,context={'request':request})
        serialzier.is_valid(raise_exception=True)
        serialzier.save()
        return Success_response('Password Rest Successfully')