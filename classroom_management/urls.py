from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('addclassroom/',CreateClassroom), # Admin/Teacher will create classroom
    path('joinclassroom/<str:id>',JoinClassroom), # students using the link will join the classroom
    path('studentclasses/',StudentClasses), # retrieve all the classes of a student
    path('teacherclasses/',TeacherClasses),
    path('classroomsessions/<str:id>',GetSession),
    path('registerteacher/',RegisterTeacher),
    path('registerstudent/',RegisterStudent),
    path('login/',Login),
    path('logout/',Logout),
    path('startsession/',StartSession), # start attendance session
    path('marksession/<int:id>',MarkSession), # send the list of students to be marked
    path('getattendance/',GetAttendance), # Get attendance of student in a particular classroom
]