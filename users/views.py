from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.openapi import Parameter, IN_QUERY
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action, parser_classes
from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.views import TokenObtainPairView
# from .models import User,Student,Parent,Teacher,Countries
from .models import User, Countries, Student
from .serializers import SignupSerializer, UserLoginSerializer, CountriesSerializer, StudentSerializer


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
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
