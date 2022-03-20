#General imports
from turtle import position
from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
import os
from decouple import config
from django.conf import settings
from django.db.models import F


#Imports from other files
from .models import User, Other, Teacher
from .utils import Util
from .serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_shemes = [config('APP_SCHEME'), 'http', 'https']

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        data = request.data
        user_request_data={}
        user_request_data['email']=data.get('email')
        user_request_data['name']=data.get('name')
        user_request_data['password']=data.get('password')
        user_request_data['user_type']=data.get('user_type')
        user_request_data['employment']=data.get('employment')
        user_request_data['idproof']=data.get('idproof')
        print(user_request_data)
        serializer = self.serializer_class(data=user_request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        if user.user_type=='other':
            print("Other")
            obj=Other.objects.create(name=user.name, email=user.email, education=data.get('education'), employment=user.employment, user=user)
            obj.save()
            print(obj)
        else:
            print("Teacher")
            obj=Teacher.objects.create(name=user.name, email=user.email, college=data.get('college'), position=data.get('position'), employment=user.employment, user=user)
            obj.save()
            print(obj)

        token = RefreshToken.for_user(user)
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'Hi '+user.name + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}

        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    # token_param_config = openapi.Parameter(
    #     'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    # @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        redirect_url = "http://localhost:3000/login"  #Change Base URL before deployment
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            # return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
            return CustomRedirect(redirect_url+'?Success=True&message=Email activated')
        except jwt.ExpiredSignatureError as identifier:
            # return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
            return CustomRedirect(redirect_url+'?Success=False&message=Activation Expired')
        except jwt.exceptions.DecodeError as identifier:
            # return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            return CustomRedirect(redirect_url+'?Success=False&message=Invalid token')


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

        if(User.objects.filter(email=email).exists() and user.is_verified == False):
            token = RefreshToken.for_user(user)
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify')
            absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            email_body = 'Hi '+user.name + \
                ' Use the link below to verify your email \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Verify your email'}

            Util.send_email(data)
            return Response({"detail": "Email is not verified"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        idproof = user.idproof.url
        user_id = user.pk
        if user.user_type == "other":
            oth = Other.objects.get(email=user.email)
            email=oth.email
            name=oth.name
            employment=oth.employment
            education=oth.education
            return Response({'user_data': user_data, 'user_id':user_id, 'other_id':oth.pk, 'email':email, 'name':name, 'idproof':idproof, 'employment':employment, 'education':education})
        else:
            tea = Teacher.objects.get(email=user.email)
            email=tea.email
            name=tea.name
            employment=tea.employment
            college = tea.college
            position = tea.position
            return Response({'user_data': user_data, 'user_id':user_id, 'teacher_id':tea.pk, 'email':email, 'name':name, 'idproof':idproof, 'employment':employment, 'college':college, 'position':position})

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'Logged Out Succesfully'}, status=status.HTTP_200_OK)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'message': 'Password updated successfully',
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = "http://localhost:3000/reset-password"  #Change Base URL before deployment          
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + absurl+"?redirect_url="+redirect_url 
            data = {'email_body': email_body, 'to_email': user.email,                     
                    'email_subject': 'Reset your passsword'}                                                      
            Util.send_email(data)                                                                                          
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)         
        return Response({'failed': 'invalid email'}, status=status.HTTP_400_BAD_REQUEST)         

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 
                                                                                                                           
class PasswordTokenCheckAPI(generics.GenericAPIView):                                                                      
    def get(self, request, uidb64, token):                                                                                 
                                                                                                                            
        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return CustomRedirect(redirect_url+'?token_valid=False')
                #return Response({'error':'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

            #return Response({'success':True, 'message':'Credentials Valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'%3ftoken_valid%3dTrue%26message%3dCredentials_Valid/'+uidb64+'/'+token)
            else:
                return CustomRedirect(redirect_url+'?token_valid=False')
            

        except DjangoUnicodeDecodeError as identifier:
            #return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)
            return CustomRedirect(redirect_url+'?token_valid=False')

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
