from django.contrib import admin


from users.models import User,Countries

admin.site.register(User)
admin.site.register(Countries)