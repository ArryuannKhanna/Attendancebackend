from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Classroom)
admin.site.register(Attendance_Session)