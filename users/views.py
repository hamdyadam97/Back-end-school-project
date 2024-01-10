from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
from django.http import HttpResponseForbidden
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.decorators import action, parser_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, \
    ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
# from .models import User,Student,Parent,Teacher,Countries
from .models import User, Countries, Student
from .serializers import SignupSerializer, UserLoginSerializer, CountriesSerializer, StudentSerializer, GroupSerializer, \
    ContentTypeSerializer, PermissionSerializer, UserPermissionUpdateSerializer


# class UserRegistrationView(ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserRegistrationSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return self.create(request, *args, **kwargs)

class UserRegistrationView(CreateAPIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email__iexact=request.data.get('email', ''))

        return self.create(request, *args, **kwargs)


class LoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

@parser_classes([MultiPartParser])
class CountryListCreateView(ListCreateAPIView):
    queryset = Countries.objects.all()
    serializer_class = CountriesSerializer


class CountryDetailDeleteUpdateView(RetrieveUpdateDestroyAPIView):
    queryset = Countries.objects.all()
    serializer_class = CountriesSerializer
    lookup_field = 'id'  # This is the field used for lookup in the URL (e.g., /api/countries/1/)


class StudentListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSerializer
    lookup_field = "id"

    def get_queryset(self):
        queryset = Student.objects.all()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the user has permission to retrieve
        if self.request.user.has_perm('users.view_student'):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            raise PermissionDenied("You don't have permission to retrieve this student.")

    def perform_update(self, serializer):
        instance = self.get_object()

        # Check if the user has permission to edit
        if self.request.user.has_perm('users.change_student'):
            serializer.save()
        else:
            raise PermissionDenied("You don't have permission to edit this student.")

    def perform_destroy(self, instance):
        # Check if the user has permission to delete
        if self.request.user.has_perm('users.delete_student'):
            instance.delete()
        else:
            raise PermissionDenied("You don't have permission to delete this student.")



class UsersGroupCreateView(APIView):
    permission_classes = [IsAdminUser]
    serializer = GroupSerializer()


class PermissionList(ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

class ContentTypeList(ListAPIView):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
    permission_classes = [IsAuthenticated]


class GroupPermissionUpdateView(UpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = UserPermissionUpdateSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the list of permission IDs from the serializer
        permission_ids = serializer.validated_data['user_permissions']

        # Get the permission objects
        permissions = Permission.objects.filter(id__in=permission_ids)

        # Update the group's permissions
        group.permissions.set(permissions)
        print(group)
        # Remove and re-add users to the group to apply the changes
        group= GroupSerializer(group).data

        return Response({'detail': 'Group permissions updated successfully.','data':group}, status=status.HTTP_200_OK)


class GroupListView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Add permission classes

