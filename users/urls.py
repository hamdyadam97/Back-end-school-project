from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from users.views import UserRegistrationView, LoginView, CountryListCreateView, CountryDetailDeleteUpdateView, \
    StudentListCreateView, StudentRetrieveUpdateDestroyView, PermissionList, ContentTypeList, GroupPermissionUpdateView, \
    GroupListView

app_name = 'USERS'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:id>/', StudentRetrieveUpdateDestroyView.as_view(), name='student-retrieve-update-destroy'),
    path('countries/list-create/', CountryListCreateView.as_view(), name='country-list-create'),
    path('countries/<int:id>/', CountryDetailDeleteUpdateView.as_view(), name='country-detail-delete-update'),
    path('permissions/', PermissionList.as_view(), name='permissions-list'),
    path('groups/<int:pk>/permissions/', GroupPermissionUpdateView.as_view(), name='group-permission-update'),
    path('groups/', GroupListView.as_view(), name='group-list'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)