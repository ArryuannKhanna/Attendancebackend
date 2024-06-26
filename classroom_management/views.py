from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from rest_framework.decorators import api_view,authentication_classes,permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
import json
# from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def CreateClassroom(request):
    data = request.data.copy()
    data['teacher_id'] = request.user.username
    # print(data)
    serializer = ClassroomSerializer(data=data)
    # print(serializer)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
def JoinClassroom(request, id):
    try:
        classroom = Classroom.objects.get(course_code=id)
    except Classroom.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {'student': request.user.username}  # Assuming you want to add the authenticated user as a student
    serializer = ClassroomSerializer(classroom, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def RegisterTeacher(request):
    data = request.data
    serializer = TeacherSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@parser_classes((MultiPartParser, FormParser, JSONParser))  # Ensure appropriate parsers are used
def RegisterStudent(request):
    data = request.data
    # print(data)
    # if('user' in data and isinstance(data['user'], str)):
    #     user_data = json.loads(data['user'])
    #     print(user_data)

    # Manually handle JSON parsing for nested 'user' data if it's coming as a string
    if 'user' in data and isinstance(data['user'], str):
        try:
            # user_data = data['user']
            user_data = json.loads(data['user'])
            # print(dict(data['user']))
            # Update the 'user' field in data with the parsed dictionary
            data._mutable = True  # Required to modify the QueryDict
            data['user'] = user_data
            # print(user_data)
            data._mutable = False
            photo_data = data['photo']
            data = {**data, 'photo': photo_data}  # Reconstruct the data with the correct 'user' format
            # print(data)
            data['user'] = data['user'][0]
            # print(data)
        except json.JSONDecodeError:
            return Response({'user': ['Invalid JSON format']}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': ['Wrong format babes']}, status=status.HTTP_400_BAD_REQUEST)

    serializer = StudentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def Login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        if Student.objects.filter(user=user).exists():
            return Response({'token': token.key, 'type': 'Student'}, status=status.HTTP_202_ACCEPTED)
        elif Teacher.objects.filter(user=user).exists():
            return Response({'token': token.key, 'type': 'Teacher'}, status=status.HTTP_202_ACCEPTED)

    return Response({'error': 'Invalid username or password'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Logout(request):
    try:
        # This will remove the Token and thus log the user out
        request.user.auth_token.delete()
    except (AttributeError, Token.DoesNotExist):
        # Handle cases where the user had no token or it was already deleted
        return Response({'error': 'Not logged in or already logged out'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def StudentClasses(request):
    usr = request.user
    try:
        student = Student.objects.get(user=usr)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    classes = student.classes_by_students.all()
    serializer = ClassroomSerializer(classes, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def TeacherClasses(request):
    usr = request.user
    try:
        teacher = Teacher.objects.get(user=usr)
    except Teacher.DoesNotExist:
        return Response({'error':'Teacher not found.'},status=status.HTTP_404_NOT_FOUND)

    classes = teacher.classes_by_host.all()
    serializer = ClassroomSerializer(classes,many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetSession(request,id):
    try:
        classes = Classroom.objects.get(course_code = id)
    except Classroom.DoesNotExist:
        return Response({'error':'Classroom does not exists'},status=status.HTTP_404_NOT_FOUND)

    sessions = classes.classroom_attendance.all()

    serializer = Attendance_SessionSerializer(sessions,many=True,context={'request':request})

    data = serializer.data

    # for item in data:
    #     item['user_info'] = request.user
    # print(serializer)

    # print(data)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def StartSession(request):
    data = request.data
    # print(data)
    serializer = Attendance_SessionSerializer(data=data,context={'request':request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def MarkSession(request):
    try:
        instance = Attendance_Session.objects.last()
    except Attendance_Session.DoesNotExist:
        return Response({"error":"Attendance session doesn't exists!"},status=status.HTTP_400_BAD_REQUEST)
    serializer = Attendance_SessionSerializer(instance=instance,data=request.data,partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def GetAttendance(request):
    student_username = request.query_params.get('student')
    classroom_name = request.query_params.get('classroom')

    try:
        usr = User.objects.get(username=student_username)
        student_obj = Student.objects.get(user=usr)
        classroom_obj = Classroom.objects.get(name=classroom_name)
    except (User.DoesNotExist, Student.DoesNotExist, Classroom.DoesNotExist) as e:
        # Make sure to return the Response here
        return Response({"error": "Either class or student doesn't exist!"}, status=status.HTTP_404_NOT_FOUND)

    data = student_obj.students_attendance.filter(classroom=classroom_obj)
    serializer = Attendance_SessionSerializer(data, many=True)

    # Use HTTP_200_OK for successful GET requests
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetClassInfo(request,id):
    data = request.data
    try:
        classinfo = Classroom.objects.get(course_code = id)
    except Classroom.DoesNotExist:
        return Response({'error':'Class does not exist'},status=status.HTTP_404_NOT_FOUND)

    serializer = ClassroomSerializer(classinfo)

    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetSessionHistory(request,id):
    data = request.data
    try:
        classinfo = Classroom.objects.get(course_id = id)
    except Classroom.DoesNotExist:
        return Response({'error':'Classroom does not exists!'},status=status.HTTP_404_NOT_FOUND)

