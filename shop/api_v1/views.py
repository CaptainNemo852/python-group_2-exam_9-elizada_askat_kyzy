from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from shop import settings
from webapp.models import RegistrationToken, Product, Photo, Category, Order
from rest_framework import viewsets, status
from api_v1.serializers import UserSerializer, UserRegisterSerializer, RegistrationTokenSerializer, AuthTokenSerializer, \
    CategorySerializer, PhotoSerializer, ProductSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth.models import User

from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token



class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_superuser,
            'is_staff': user.is_staff
        })


class TokenLoginView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        user = token.user
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_superuser,
            'is_staff': user.is_staff
        })


class BaseViewSet(viewsets.ModelViewSet):
    # Метод, который отвечает за проверку разрешений на доступ к данному ViewSet
    def get_permissions(self):
        permissions = super().get_permissions()
        if self.request.method in ["POST", "DELETE", "PUT", "PATCH"]:
            return permissions


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-receipt_date')
    serializer_class = ProductSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-name')
    serializer_class = CategorySerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_date')
    serializer_class = OrderSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()



class UserCreateView(CreateAPIView):
    model = User
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


    def perform_create(self, serializer):
        # после создания пользователя
        user = serializer.save()
        # сохраняем токен
        token = self.create_token(user)
        # отправляем email
        self.send_registration_email(user, token)

    def create_token(self, user):
        return RegistrationToken.objects.create(user=user)


    def send_registration_email(self, user, token):
        url = '%s/register/activate/?token=%s' % (settings.HOST_URL, token)
        email_text = "Your account was successfully created.\nPlease, follow the link to activate:\n\n%s" % url
        user.email_user("Registration at Cinema-App", email_text, settings.EMAIL_DEFAULT_FROM)



class UserActivateView(GenericAPIView):
    serializer_class = RegistrationTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_user_activation(serializer)
        auth_token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': auth_token.key,
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_superuser,
            'is_staff': user.is_staff
        })


    def perform_user_activation(self, serializer):
        token = serializer.validated_data.get('token')
        user = token.user
        user.is_active = True
        user.save()
        token.delete()
        return user



class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        permissions = super().get_permissions()
        if self.request.method in ["POST", "DELETE", "PUT", "PATCH"]:
            permissions.append(IsAuthenticated())
        return permissions

    # Метод, который проверяет права доступа к объекту - запрошенному ресурсу
    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        print(obj, request.user, '===')
        if request.method in ['PUT', 'PATCH', 'DELETE'] and obj != request.user:
            self.permission_denied(request, 'Can not edit other users data!')
