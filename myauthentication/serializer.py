from rest_framework import serializers
from django.contrib.auth import get_user_model,authenticate,user_logged_in
from utils.exception import CustomValidation
from myauthentication import models as user_models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from utils.generate_token import gen_token,update_login
from utils.job_categories import job_categories
import requests,json
from django.utils.encoding import force_str
from mailing.tasks import send_forgot_password_mail
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes



class ParseCvSerializer (serializers.Serializer):
    cv = serializers.FileField()


    def create(self, validated_data):
        cv = validated_data.get('cv')
        apikey='CtISAq6f0GoNKlGu1XLjvXG4DC5sXm8y'
        header ={
            'CtISAq6f0GoNKlGu1XLjvXG4DC5sXm8y':'',
            'apikey':apikey
        }
        
        # resp = requests.post('https://api.apilayer.com/resume_parser/upload',headers=header,data=cv)
        # print(resp.data)
        # resumeparse.read_file('/path/to/resume/file')
        # return resp.data
        
        return dict()
class RegisterCompanySerializer(serializers.Serializer):
    email =serializers.EmailField()
    full_name =serializers.CharField()
    password =serializers.CharField( trim_whitespace=True)
    phone_number =serializers.CharField()
    organisation_name =serializers.CharField()
    organisation_name_shortname =serializers.CharField()
    industry =serializers.CharField()
    addresses =serializers.CharField()
    official_phone =serializers.IntegerField()




    def validate(self, attrs):
        user = get_user_model()
        email = attrs.get('email',None)
        organisation_name_shortname = attrs.get('organisation_name_shortname',None)
        if  user.objects.filter(email=email).exists():
            raise CustomValidation(detail=f'{email} already exist ',field='email')

        if user_models.CompanyProfile.objects.filter(organisation_name_shortname=organisation_name_shortname).exists():
            raise CustomValidation(detail=f'Company short name already exit',field='organisation_name_shortname')
        return super().validate(attrs)

    def create(self, validated_data):
        email = validated_data.get('email',None)
        password = validated_data.get('password',None)
        company_cred = dict()
        company_cred['official_mail'] =validated_data.get('email',None)
        # company_cred['phone_number'] =validated_data.get('phone_number',None)
        company_cred['organisation_name']=validated_data.get('organisation_name',None)
        company_cred['industry'] =validated_data.get('industry',None)
        company_cred['addresses'] =validated_data.get('addresses',None)
        company_cred['organisation_name_shortname'] =validated_data.get('organisation_name_shortname',None)
        company_cred['official_phone']  =validated_data.get('official_phone',None)
        user = get_user_model().objects.create_company(email,password)
        user.full_name = validated_data.get('full_name',None)
        user.phone_number = validated_data.get('phone_number',None)
        user.save()
        compnay_profile = user_models.CompanyProfile.objects.create(
            user=user,**company_cred
        )
        compnay_profile.save()

        return user




class RegisterHr(serializers.Serializer):
    email =serializers.EmailField()
    full_name =serializers.CharField()
    password =serializers.CharField( trim_whitespace=True)
    phone_number = serializers.CharField()


    def validate(self, attrs):
        user = get_user_model()
        email = attrs.get('email',None)
        if  user.objects.filter(email=email).exists():
            raise CustomValidation(detail=f'{email} already exist ',field='email')
  
        return super().validate(attrs)

    def create(self, validated_data):
        USER = get_user_model()
        email = validated_data.get('email',None)
        password = validated_data.get('password',None)
        full_name = validated_data.get('full_name',None)
        organisation_name_shortname = validated_data.get('organisation_name_shortname',None)
        user = USER.objects.create_user(email=email,user_type='hr',password=password)
        user.full_name=full_name
        user.save()
        "we use the logged in company to get his profile"
        company =  user_models.CompanyProfile.objects.get(user=self.context.get('request').user)
        hr_profile = user_models.HrProfile.objects.create(
        user = user,
        company=  company
        )
        hr_profile.save()
        return user


class RegisterJobSeekerSerializer(serializers.Serializer):
    email =serializers.EmailField()
    full_name =serializers.CharField()
    password =serializers.CharField( trim_whitespace=True)
    phone_number = serializers.CharField()
   
    def validate(self, attrs):
        user = get_user_model()
        email = attrs.get('email',None)
        if  user.objects.filter(email=email).exists():
            raise CustomValidation(detail=f'{email} already exist ',field='email')
  
        return super().validate(attrs)

    def create(self, validated_data):
        USER = get_user_model()
        email = validated_data.get('email',None)
        password = validated_data.get('password',None)
        full_name = validated_data.get('full_name',None)
        user = USER.objects.create_user(email=email,user_type='job_seakers',password=password)
        user.full_name=full_name
        user.save()
        "we use the logged in company to get his profile"
        job_seeker = user_models.JobSeekerProfile.objects.create(
        user = user,
        )
        job_seeker.save()
        return user  

class LoginSerializer(TokenObtainPairSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )


    def validate(self, attrs):
        USER_MODEL= get_user_model()
        email = attrs.get("email", None)
        password = attrs.get("password", None)
        request = self.context.get("request", None)


        try:
            user = USER_MODEL.objects.get(email=email)
        except USER_MODEL.DoesNotExist:
            user = None
        auth_user = authenticate(username=email, password=password)
        
        if (not user and not auth_user) or (user.is_active and not auth_user):
            raise AuthenticationFailed(
                "Invalid credentials, username or password incorrect"
            )
        if user.is_active  == False:
            raise AuthenticationFailed(
                "Please check your mail for activation token"
            )
        refresh = self.get_token(user)
        user_login = update_login(refresh)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return user_login

        
    @classmethod
    def get_token(cls, user):
        """
        get the token for a user
        Args:
            user:
        Returns:
        """
        token = gen_token(user)

        return token




class CompanyUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False)
    phone_number=  serializers.CharField(required=False)

    organisation_name = serializers.CharField(required=False)
    industry = serializers.CharField(required=False)
    organisation_size = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False)
    official_mail = serializers.EmailField(required=False)
    addresses = serializers.CharField(required=False)
    official_phone = serializers.CharField(required=False)


    def update(self, instance:user_models.User, validated_data):
        instance.full_name = validated_data.get('full_name',instance.full_name)
        instance.phone_number = validated_data.get('phone_number',instance.phone_number)
        instance.profile_image = validated_data.get('profile_image',instance.profile_image)
        instance.save()
        if(validated_data.get('profile_image',None)) is None:
            panelist = user_models.CompanyProfile.objects.get(user=instance)
            panelist.organisation_name = validated_data.get('organisation_name',panelist.organisation_name)
            panelist.industry = validated_data.get('industry',panelist.industry)
            panelist.organisation_size = validated_data.get('organisation_size',panelist.organisation_size)
            panelist.location = validated_data.get('location',panelist.location)
            panelist.official_mail = validated_data.get('official_mail',panelist.official_mail)
            panelist.addresses = validated_data.get('addresses',panelist.addresses)
            panelist.official_phone = validated_data.get('official_phone',panelist.official_phone)

            panelist.save()
        return instance


class EducationJobSeekerProfileSerializer(serializers.Serializer):
    degree_type = serializers.CharField()
    school_name = serializers.CharField()
    start_year = serializers.CharField()
    end_year = serializers.CharField()
    course_of_study = serializers.CharField()
class ExperienceJobSeekerProfileSerializer(serializers.Serializer):
    company = serializers.CharField()
    start_year = serializers.CharField()
    end_year = serializers.CharField()
    role = serializers.CharField()
    responsibilities = serializers.CharField()

class CertificatonJobSeekerProfileSerializer(serializers.Serializer):
    certification =  serializers.CharField()
    issuer =  serializers.CharField()
    start_year = serializers.CharField()

class RefrencesJobSeekerProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    relationship = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()

class JobSeekerProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False)
    # profile_image = serializers.ImageField()
    cv = serializers.FileField(required=False)
    phone_number=  serializers.CharField(required=False)
    notify_me_on = serializers.CharField(required=False)

    first_name = serializers.CharField()
    middle_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    addresse = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    country_of_residence = serializers.CharField()
    linkdin = serializers.CharField()
    twitter = serializers.CharField()
    personal_statement = serializers.CharField()
    education = EducationJobSeekerProfileSerializer(many=True)
    experience = ExperienceJobSeekerProfileSerializer(many=True)
    certificaton =CertificatonJobSeekerProfileSerializer(many=True)
    refrences = RefrencesJobSeekerProfileSerializer(many=True)

    def update(self, instance:user_models.User, validated_data):
        instance.full_name = validated_data.get('full_name',instance.full_name)
        instance.phone_number = validated_data.get('phone_number',instance.phone_number)
        # instance.profile_image = validated_data.get('profile_image',instance.profile_image)
        instance.save()
        job_seeker = user_models.JobSeekerProfile.objects.get(user=instance)
        job_seeker.cv = validated_data.get('cv',job_seeker.cv)
        job_seeker.notify_me_on = validated_data.get('notify_me_on',job_seeker.notify_me_on)
        job_seeker.first_name = validated_data.get('first_name',job_seeker.first_name)
        job_seeker.middle_name = validated_data.get('middle_name',job_seeker.middle_name)
        job_seeker.last_name = validated_data.get('last_name',job_seeker.last_name)
        job_seeker.email = validated_data.get('email',job_seeker.email)
        job_seeker.addresse = validated_data.get('addresse',job_seeker.addresse)
        job_seeker.city = validated_data.get('city',job_seeker.city)
        job_seeker.state = validated_data.get('state',job_seeker.state)
        job_seeker.country_of_residence = validated_data.get('country_of_residence',job_seeker.country_of_residence)
        job_seeker.linkdin = validated_data.get('linkdin',job_seeker.linkdin)
        job_seeker.personal_statement = validated_data.get('personal_statement',job_seeker.personal_statement)
        job_seeker.twitter = validated_data.get('twitter',job_seeker.twitter)
        if validated_data.get('education',None):
            job_seeker.education = validated_data.get('education')
        if validated_data.get('experience',None):
            job_seeker.experience = validated_data.get('experience')
        if validated_data.get('certificaton',None):
            job_seeker.certificaton = validated_data.get('certificaton')

        if validated_data.get('refrences',None):
            job_seeker.refrences = validated_data.get('refrences')
        job_seeker.has_updated_cv=True
        job_seeker.save()
        return instance

class PanelistProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False)
    phone_number=  serializers.CharField(required=False)

    def update(self, instance:user_models.User, validated_data):
        instance.full_name = validated_data.get('full_name',instance.full_name)
        instance.phone_number = validated_data.get('phone_number',instance.phone_number)
        instance.profile_image = validated_data.get('profile_image',instance.profile_image)
        instance.save()
        return instance

class UserDataCleaner(serializers.ModelSerializer):
    user_extra = serializers.SerializerMethodField()


    def get_user_extra(self,user:user_models.User):
        data = dict()
        if(user.user_type == 'company'):
            company = user.companyprofile
            data['company']= {
                'organisation_name':company.organisation_name,
                'organisation_name_shortname':company.organisation_name_shortname,
                'industry':company.industry,
                'organisation_size':company.organisation_size,
                'location':company.location,
                'official_mail':company.official_mail,
                'official_phone':company.official_phone,
                'addresses':company.addresses
            }
        if user.user_type == 'job_seakers':
            data['job_categories']  = job_categories
            
            job_seakers = user.jobseekerprofile
            cv =''
            try:
                cv= job_seakers.cv.url
            except:
                cv = ''
            data['job_seakers'] = {
                'cv':cv,
                'notify_me_on':user.jobseekerprofile.notify_me_on,
                'cvStucture':{
                'first_name':user.jobseekerprofile.first_name,
                'middle_name':user.jobseekerprofile.middle_name,
                'last_name':user.jobseekerprofile.last_name,
                'phone_number':user.jobseekerprofile.phone_number,
                'email':user.jobseekerprofile.email,
                'addresse':user.jobseekerprofile.addresse,
                'state':user.jobseekerprofile.state,
                'country_of_residence':user.jobseekerprofile.country_of_residence,
                'linkdin':user.jobseekerprofile.linkdin,
                'twitter':user.jobseekerprofile.twitter,
                'personal_statement':user.jobseekerprofile.personal_statement,
                'education':user.jobseekerprofile.education,
                'experience':user.jobseekerprofile.experience,
                'certificaton':user.jobseekerprofile.certificaton,
                'refrences':user.jobseekerprofile.refrences,
                }
            }
        
        return data 

    class Meta:
        model  =user_models.User
        fields = ['full_name','profile_image','phone_number','user_extra']




class PasswordResetRequestSerializer(serializers.Serializer):
    email =  serializers.EmailField()
    def validate_email(self, email):
        User=get_user_model()
        if not User.objects.filter(email=email).exists():
            raise CustomValidation(detail='User with this email address does not exist.')
        return email
    
    def send_password_reset_email(self,user):
        # current_site = get_current_site(self.context['request'])
        uid=urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        domain ='app.sequentialjobs.com'
        reset_url = f"http://{domain}/reset-password/{uid}/{token}/"
        send_forgot_password_mail.delay(user.email,reset_url)
        # print({'reset_url':reset_url})
    def create(self, validated_data):
        user = get_user_model().objects.get(email=validated_data.get('email'))
        self.send_password_reset_email(user)
        return dict()
    
class PasswordResetConfirmationSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, attrs):
        User = get_user_model()
        try:
            uid =force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise CustomValidation(detail='Invalid reset password link.',field='error')

        if not default_token_generator.check_token(user, attrs['token']):
            raise  CustomValidation(detail='Invalid reset password link.',field='error')

        attrs['user'] = user

        return attrs
    
    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data.get('new_password'))
        user.save()