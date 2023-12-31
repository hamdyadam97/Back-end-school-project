# users/serializers.py
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
# from .models import User, Student, Parent
from .models import User, Parent, Student, Countries
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .task import validate_egyptian_phone_number


class SignupSerializer(serializers.ModelSerializer):
    is_update = False
    confirm_password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True, source='token')
    access = serializers.CharField(read_only=True, source='token.access_token')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get('data', {}).get('phone_number'):
            self.fields['email'].required = True




    def validate_password(self, data):
        validate_password(data)
        return data

    def validate_email(self, data):
        users = User.objects.filter(email__iexact=data)

        if self.is_update:
            users.exclude(id=self.instance.id)

        if users.exists():
            raise serializers.ValidationError(_("This email address already exists."))
        return data

    def validate_username(self, data):
        users = User.objects.filter(username__iexact=data)

        if self.is_update:
            users = users.exclude(id=self.instance.id)

        if users.exists():
            raise serializers.ValidationError(_("This username already exists."))
        return data


    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        if 'phone_number' in attrs:
            print(attrs.get('phone_number'))
            print(attrs.get('phone_number').isnumeric() )
            print(validate_egyptian_phone_number(attrs['phone_number']))
            if not attrs.get('phone_number').isnumeric() or validate_egyptian_phone_number(attrs['phone_number']):
                raise serializers.ValidationError(
                    {'error': "This phone number is invalid, please enter valid phone number."})
                users = User.objects.filter(phone_number__iexact=attrs['phone_number'])
                if users.exists():
                    raise serializers.ValidationError({'error': "This phone number already exists."})
        return attrs

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password', None)
        user = super().create(validated_data)

        if confirm_password:
            user.set_password(confirm_password)
            user.save()
        return user

    class Meta:
        model = User
        fields = (
            "password",
            "confirm_password",
            'username',

            'email',
            'phone_number',
            'is_email_verified',
            'email_verification_code',

            'role',


            'is_active',
            'is_deactivated',
            'date_joined',
            'last_online',
            'last_active',
            'is_phone_verified',
            'access',
            'refresh',
        )
        extra_kwargs = {
            'password': {'write_only': True},

        }

class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            super().validate(attrs)
        except AuthenticationFailed as ex:
            raise serializers.ValidationError(_("Incorrect email or password"))
        return SignupSerializer(instance=self.user, context=self.context).data


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

    def validate_phone_number(self,value):
        # Validate that the phone number belongs to Egypt (starts with +20)
        if not value.startswith('+20'):
            raise serializers.ValidationError('Phone number must be from Egypt.')

    def validate_student_name(self, value):
        # Validate that the student name has at least 20 characters and consists of alphanumeric characters and spaces
        if len(value) < 20:
            raise serializers.ValidationError('Student name must have at least 20 characters.')
        if not value.replace(" ", "").isalnum():  # Check if the name consists of alphanumeric characters and spaces
            raise serializers.ValidationError('Student name must not have special characters, and can include spaces.')
        return value


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'


class CountriesSerializer(serializers.ModelSerializer):
    country_flag = serializers.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        model = Countries
        fields = '__all__'

    def validate_name(self, value):
        # Add any custom validation for the 'name' field
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value