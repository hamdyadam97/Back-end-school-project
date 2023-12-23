import uuid

from django.contrib.auth.models import AbstractUser, Permission,Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from stdimage import StdImageField
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class Countries(models.Model):
    name = models.CharField( max_length=50)
    Date_Created = models.DateField( auto_now=False, auto_now_add=False)
    country_flag = StdImageField(upload_to='countries_flags/', blank=True, null=True, variations={
        'thumbnail': {'width': 100, 'height': 100, 'crop': True},
    })

    class Meta:
         verbose_name = "Countries"

    def __str__(self):
        return self.name


class User(AbstractUser):
    class UserRoleChoices(models.TextChoices):
        STUDENT = 'student', "Student"
        PARENT = 'parent', "Parent"
        TEACHER = 'teacher', "Teacher"

    class UserGenderChoices(models.TextChoices):
        MALE = 'male', "Male"
        FEMALE = 'female', "Female"
        PREFER_NOT_TO_ANSWER = 'prefer_not_to_answer', "Prefer not to answer"

    image = StdImageField(upload_to='profiles/', blank=True, null=True, variations={
        'thumbnail': {'width': 100, 'height': 100, 'crop': True},
    })
    email = models.EmailField(help_text="عنوان الميل")
    role = models.CharField(max_length=10, choices=UserRoleChoices.choices, help_text='دور المستخدم')
    telephone = models.CharField(max_length=15)
    gender = models.CharField(max_length=50, choices=UserGenderChoices.choices)
    birthday = models.DateField(default=None, blank=True, null=True)
    address = models.TextField(default=None, blank=True, null=True)
    country = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True, blank=True)
    marital_status = models.CharField(max_length=50, blank=True, null=True)
    # is_active = models.BooleanField(default=True)  # Set to True by default
    groups = models.ManyToManyField(
        Group,
        related_name='user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='user_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username


    @property
    def teacher(self):
        try:
            return self.teacher_profile
        except Teacher.DoesNotExist:
            return None

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'teacher':
        teacher_profile = Teacher.objects.create(user=instance)
        instance.teacher = teacher_profile
        instance.save()


@receiver(post_save, sender=User)
def save_teacher_profile(sender, instance, **kwargs):
    if instance.role == 'teacher':
        if hasattr(instance, 'teacher'):
            instance.teacher.save()


class CustomPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        user_names = ', '.join(user.username for user in self.user.all())
        permission_names = ', '.join(permission.name for permission in self.permission.all())
        return f'CustomPermission: Users - {user_names}, Permissions - {permission_names}'

    class Meta:
        verbose_name = "Roles and permissions"


class Student(models.Model):
    # Optional field for teachers
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admission_number = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    student_name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=50)
    mobile_phone_number = models.CharField(max_length=15)
    parents = models.ManyToManyField(User, related_name='children', limit_choices_to={'role': 'parent'})

    def __str__(self):
        return self.student_name


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Parent_name = models.CharField(max_length=255, blank=True, null=True)
    Parent_phone = models.CharField(max_length=15, blank=True, null=True)
    Parent_occupation = models.CharField(max_length=255, blank=True, null=True)
    children = models.ManyToManyField(Student, related_name='student', limit_choices_to={'role': 'student'})

    def __str__(self):
        return self.Parent_name or str(self.user)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personnel_id = models.CharField(max_length=20,unique=True)
    role_teacher = models.CharField(max_length=50, blank=True)
    designation_faculty = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    type_of_contract = models.CharField(max_length=50, blank=True, null=True)
    work_shift = models.CharField(max_length=50, blank=True, null=True)
    work_location = models.CharField(max_length=100, blank=True, null=True)
    registration_date = models.DateField(null=True)
    barcode = models.CharField(max_length=20, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username




