from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from users.views import UserRegistrationView, StudentListCreateView, StudentRetrieveUpdateDestroyView

app_name = 'USERS'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', StudentRetrieveUpdateDestroyView.as_view(), name='student-retrieve-update-destroy'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)