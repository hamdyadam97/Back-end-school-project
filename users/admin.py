from django.contrib import admin


from users.models import User, Countries, Parent, Student

admin.site.register(User)
admin.site.register(Countries)
admin.site.register(Student)
admin.site.register(Parent)