from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password','email']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Student
        fields = '__all__'
    def create(self, validated_data):
        user_info = validated_data.pop('user')
        usr = User.objects.create_user(**user_info)
        instance = Student.objects.create(user = usr,**validated_data)
        return instance


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Teacher
        fields = '__all__'
    def create(self, validated_data):
        user_info = validated_data.pop('user')
        usr = User.objects.create_user(**user_info)
        instance = Teacher.objects.create(user = usr,**validated_data)
        return instance


class ClassroomSerializer(serializers.ModelSerializer):
    host_id = TeacherSerializer(read_only=True)
    students = serializers.ListField(child=serializers.CharField(),write_only=True,required=False)
    teacher = serializers.CharField(write_only=True)
    # user = UserSerializer()
    student = serializers.CharField(write_only=True)
    class Meta:
        model = Classroom
        fields = '__all__'

    def create(self, validated_data):
        teacher_id = validated_data.pop('teacher')
        usr = User.objects.get(username = teacher_id)
        host =Teacher.objects.get(user=usr)
        inst = Classroom.objects.create(host_id = host,**validated_data)
        return inst

    def update(self, instance, validated_data):
        student = validated_data.get('student')
        if student:
            try:
                usr = User.objects.get(username = student)
                student_instance = Student.objects.get(user=usr)
                instance.students.add(student_instance)
                instance.save()
            except (User.DoesNotExist, Student.DoesNotExist):
                raise serializers.ValidationError('Student does not exist!')

        return instance




class Attendance_SessionSerializer(serializers.ModelSerializer):
    classroom = serializers.CharField()
    students = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    class Meta:
        model = Attendance_Session
        fields = '__all__'

    def create(self, validated_data):
        classroom = validated_data.pop('classroom')
        classroom = Classroom.objects.get(name = classroom)
        inst = Attendance_Session.objects.create(classroom=classroom)
        return inst

    def update(self, instance, validated_data):
        students = validated_data.pop('students',[])
        for id in students:
            try:
                usr = User.objects.get(username = id)
                student_instance = Student.objects.get(user=usr)
                instance.students_present.add(student_instance)
            except User.DoesNotExist:
                raise serializers.ValidationError('Student doesnt exists!')

        return instance



