# users/serializers.py
from rest_framework import serializers
from .models import User, Student, Parent
from django.core.exceptions import ValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "image",
            "role",
            "telephone",
            "gender",
            "birthday",
            "address",
            "country",
            "marital_status",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_email(self, value):
        """
        Validate that the email address is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value


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
