from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='student')
    # semester = models.IntegerField()



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='teacher')


# Generic classroom information about the teacher as well as the students that are part of the classroom
class Classroom(models.Model):
    course_code = models.CharField(max_length=9,unique=True,default=404,null=False)
    host_id = models.ForeignKey(Teacher, on_delete=models.CASCADE,related_name='classes_by_host')
    students = models.ManyToManyField(Student, related_name='classes_by_students',blank=True)
    name = models.CharField(max_length=20)



# It is the attendance session refrencing the classroom for info about the total students that are enrolled within this.
class Attendance_Session(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE ,related_name='classroom_attendance')
    students_present = models.ManyToManyField(Student,related_name='students_attendance',blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['date']

