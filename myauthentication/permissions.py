from rest_framework import  permissions
from utils.exception import CustomValidation
from jobs.models import Job

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'admin'
    
class CompanyAndPanelist(permissions.BasePermission):
    def has_permission(self, request, view):
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        return request.user.user_type=='company' or request.user.user_type=='panelist'

class OnlyCompany(permissions.BasePermission):


    def has_permission(self, request, view):
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        return request.user.user_type=='company'

class OnlyPanelist(permissions.BasePermission):


    def has_permission(self, request, view):
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        return request.user.user_type=='panelist'

class OnlyJobSeeker(permissions.BasePermission):
    def has_permission(self, request, view):
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        return request.user.user_type=='job_seakers'

class MustHaveCV(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.user.user_type != 'job_seakers':
            'must be job_seaker to even have cv'
            raise CustomValidation('You need a job seeker acct',field='cv')
            
        if request.user.jobseekerprofile.has_updated_cv==True:return True
        raise CustomValidation('You Need to upload your cv',field='cv')



class  JobMustHaveTestOrQuetionSetBeforeInterviewPermissions(permissions.BasePermission):


    def has_object_permission(self,request,view,obj:Job):

        if obj.job_variant == 'filter_only' and obj.job_filter == None:
            'this type of job only needs the Cv FIlter Quetion'
            raise CustomValidation(detail='You Need to set CV Filter Before Creating Interview',field='job_id')

        if obj.job_variant =='filter_and_test':
            if obj.job_filter==None or obj.job_test ==None:
                'this type of job needs the Cv FIlter Quetion and Test'
                raise CustomValidation(detail='You Need to set CV Filter and Test Queton Before Creating Interview',field='job_id')
        return True