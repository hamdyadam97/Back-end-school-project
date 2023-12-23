from django.contrib import admin
from .models import User,Student,Countries,Teacher,Parent,CustomPermission

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    # Define the fields to display in the list view
    list_display = ('username', 'first_name', 'last_name', 'image', 'role', 'email', 'telephone', 'gender', 'birthday',
                    'address', 'country', 'marital_status')

    # Define the fields to display in the detail view
    fields = ('username', 'first_name', 'last_name', 'image', 'role', 'email', 'telephone', 'gender', 'birthday',
              'address','country', 'marital_status')

    # Enable searching by name in the Admin interface
    search_fields = ['username']


admin.site.register(User, UserAdmin)


admin.site.register(Student)
admin.site.register(Countries)
admin.site.register(Teacher)
admin.site.register(Parent)
admin.site.register(CustomPermission)

