from rest_framework import serializers
# импортируем стандартную модель USER
# (в django.contrib.auth находятся модели пользователя, группы и разрешения относящиеся к ним)
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from webapp.models import RegistrationToken, Category, Product, Photo, Order
from rest_framework.authtoken.models import Token



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise ValidationError("Passwords do not match")
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password_confirm', 'email']



class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:user-detail')
    username = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    new_password_confirm = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.EmailField(required=True, allow_blank=False)


    def validate_password(self, value):
        user = self.context['request'].user
        if not authenticate(username=user.username, password=value):
            raise ValidationError('Invalid password for your account')
        return value

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise ValidationError("Passwords do not match")
        return super().validate(attrs)


    def update(self, instance, validated_data):
        validated_data.pop('password')
        new_password = validated_data.pop('new_password')
        validated_data.pop('new_password_confirm')
        instance = super().update(instance, validated_data)


        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'new_password', 'new_password_confirm']


class RegistrationTokenSerializer(serializers.Serializer):
    token = serializers.UUIDField(write_only=True)


    def validate_token(self, token_value):
        try:
            token = RegistrationToken.objects.get(token=token_value)
            if token.is_expired():
                raise ValidationError("Token expired")
            return token
        except RegistrationToken.DoesNotExist:
            raise ValidationError("Token does not exist or already used")



class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate_token(self, token):
        try:
            return Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise ValidationError("Invalid credentials")


class InlineProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ("id", "name")

class InlinePhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ("id", "photo")


class InlineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    categories = InlineCategorySerializer(many=True, read_only=True)
    photos = InlinePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ("url", "id", "name", "description", "date", "price", "categories", "photos")


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("url", "id", "products", "photo")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("url", "id", "name", "description")





class OrderSerializer(serializers.ModelSerializer):
    products = InlineProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("url", "id", "user", "products", "comment", "phone", "address", "date")