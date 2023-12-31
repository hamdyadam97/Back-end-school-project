import re
import uuid
import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager as DjangoUserManager
from django.db.models import Count, Q, F
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


from django.conf import settings
from stdimage import StdImageField

"""
        This is function validation on user name.
        
"""
def validate_username_user(username):
    # reg to match egyptien phone number
    pattern = re.compile("^(?=[a-zA-Z0-9\u0600-\u06FF._]{3,20}$)(?!.*[_.]{2})[^_.].*[^_.]$")
    if pattern.match(username):
        return username
    else:
        raise ValidationError("The username field should be between 3 and 20 characters in length and may contain "
                              "characters, numbers, or special characters (_.), but not at the beginning or end.")


# make user generate key in token with username and
class UserManager(DjangoUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': username})


""" 
country model that user have address
"""


class Countries(models.Model):
    name = models.CharField( max_length=50)
    date_created = models.DateField( auto_now=False, auto_now_add=False)
    country_flag = StdImageField(upload_to='countries_flags/', blank=True, null=True, variations={
        'thumbnail': {'width': 1000, 'height': 1000, 'crop': True},
    })

    class Meta:
         verbose_name = "Countries"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    class UserGenderChoices(models.TextChoices):
        MALE = 'male', "Male"
        FEMALE = 'female', "Female"
        PREFERE_NOT_TO_ANSWER = 'prefer_not_to_answer', "Prefere not to answer"

    class UserRoleChoices(models.TextChoices):
        STUDENT = 'student', "Student"
        PARENT = 'parent', "Parent"
        TEACHER = 'teacher', "Teacher"
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=50,
        unique=True,
        help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, validate_username_user],
        error_messages={
            'unique': _("This username already exists."),
        },
    )
    # first_name = models.CharField(max_length=150)
    # last_name = models.CharField(max_length=150)
    email = models.EmailField(_('email address'),unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=20, blank=True, null=True)
    # dob = models.DateField(null=True)
    # gender = models.CharField(max_length=25, choices=UserGenderChoices.choices, blank=True, null=True)
    role = models.CharField(max_length=10, choices=UserRoleChoices.choices, help_text='دور المستخدم')
    # address = models.TextField(default=None, blank=True, null=True)
    # country = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True, blank=True)
    # marital_status = models.CharField(max_length=50, blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_deactivated = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_online = models.DateTimeField(_('last online'), blank=True, null=True)
    is_set_password = models.BooleanField(default=True)
    # This field is for Social users that didn't edit their profile, mainly Apple Users for now.
    last_active = models.DateTimeField(auto_now=True)
    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    is_phone_verified = models.BooleanField(default=False)

    email_username = models.CharField(max_length=200, blank=False, null=True)

    def save(self, *args, **kwargs):
        if self.email:
            self.email_username = self.email
        else:
            self.email_username = self.username
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.display_name

    def get_short_name(self):
        """Return the short name for the user."""
        return self.username

    @cached_property
    def token(self):
        return RefreshToken.for_user(self)




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


class Profile(models.Model):
    class EducationalStageChoice(models.TextChoices):
        PRIMARY_EDUCATION = 'primary_education','Primary education'
        SECONDARY_EDUCATION = 'secondary_education'
        HIGH_SCHOOL = 'High_school','High school'
        TECHNICAL_EDUCATION = 'Technical_education','Technical education'
        UNIVERSITY_EDUCATION = 'University_education','University education'

    class TYPEOFEDUCATIONChoice(models.TextChoices):
        GOVERNMENT_EDUCATION = 'government_education','Government education'
        ARABIC_PRIVATE_EDUCATION = 'arabic_private_education','Arabic private education'
        FOREIGN_PRIVATE_EDUCATION = 'foreign_private_school','foreign privat eschool'
    Educational_qualification = models.CharField(blank=True,null=True,help_text="المؤهل العلمي",max_length=50)
    Graduation_Year = models.DateField(blank=True,null=True,max_length=50,help_text=" سنة التخرج ")
    The_university_issued_the_qualification = models.CharField(max_length=50,blank=True,null=True,help_text="الجامعة الصادر منها المؤهل")
    Nationality = models.CharField(max_length=50,blank=True,null=True,help_text="الجنسية")
    Place_of_residence = models.CharField(max_length=50,blank=True,null=True,help_text="مكان الاقامة")
    Name_of_previous_or_current_workplace = models.CharField(max_length=50,blank=True,null=True,help_text=" اسم مكان العمل السابق او مكان العمل الحالى")
    Specialization = models.CharField(max_length=50,blank=True, null=True, help_text=" التخصص")
    Years_of_Experience = models.CharField(max_length=50,blank=True, null=True, help_text="سنوات الخبرة ")
    Years_of_experience_in_online_education = models.CharField(max_length=50,blank=True, null=True,help_text="سنوات الخبرة ف التعليم الاؤنلاين")
    The_training_courses_you_took = models.CharField(max_length=50,blank=True, null=True, help_text=" الدورات الحاصل عليها")
    Educational_stage = models.CharField(max_length=50,choices=EducationalStageChoice.choices, blank=True, null=True, help_text="مراحل التعليم ")
    Type_of_education = models.CharField(max_length=50,choices=TYPEOFEDUCATIONChoice.choices, blank=True, null=True, help_text="نوع التعليم")
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE, null=False, help_text="البروفايل")
    image = StdImageField(upload_to='profile-image/', blank=True, null=True, variations={
        'thumbnail': {'width': 1000, 'height': 1000, 'crop': True},
    })

    def __str__(self):
        return f' user profile for{self.user.username}'


class UserProfileDateRequired(models.Model):
    Educational_qualification = models.BooleanField(default=False)
    Graduation_Year = models.BooleanField(default=False)
    The_university_issued_the_qualification = models.BooleanField(default=False)
    Nationality = models.BooleanField(default=False)
    Place_of_residence =models.BooleanField(default=False)
    Name_of_previous_or_current_workplace = models.BooleanField(default=False)
    Specialization = models.BooleanField(default=False)
    Years_of_Experience = models.BooleanField(default=False)
    Years_of_experience_in_online_education = models.BooleanField(default=False)
    The_training_courses_you_took = models.BooleanField(default=False)
    Educational_stage = models.BooleanField(default=False)
    Type_of_education = models.BooleanField(default=False)
    image = models.BooleanField(default=False)
    user = models.OneToOneField(User, related_name="user_profile_permission", on_delete=models.CASCADE, null=False, help_text="البروفايل")
    file = models.BooleanField(default=False)

    def __str__(self):
        return f' user profile for{self.user.username}'


class FileDateProfileUser(models.Model):
    profile = models.ForeignKey(Profile,related_name="profile_File",on_delete=models.CASCADE)
    file = models.FileField(upload_to='profile-file/',help_text="ارفع فايل")

    def __str__(self):
        return f' user profile file for{self.profile.user.username}'