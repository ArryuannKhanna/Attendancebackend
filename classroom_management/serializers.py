from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
import face_recognition


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password','email']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    photo = serializers.ImageField(write_only=True)
    encoding = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Student
        # fields = '__all__'
        fields = ['user','photo','encoding']
    def create(self, validated_data):
        # print('hmm')
        # print(validated_data)
        user_data = validated_data.get('user')  # Assume 'user' is a JSON string
        # print(user_data)
        photo = validated_data.get('photo')

        usr = User.objects.create_user(**user_data)
        instance = Student.objects.create(user = usr)
        # if photo:
            # Process the photo and create the encoding
        image = face_recognition.load_image_file(photo)
        encodings = face_recognition.face_encodings(image)
                # print(photo)
        # print(encodings)
        instance.set_encoding(encoding_array=list(encodings[0]))
        instance.save()

        return instance
    def get_encoding(self,obj):
        return obj.get_encoding()

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
    teacher = serializers.CharField(write_only=True,required=False)
    student = serializers.CharField(write_only=True,required=False)
    teacher_id = serializers.CharField(write_only=True)
    class Meta:
        model = Classroom
        fields = '__all__'

    def create(self, validated_data):
        # print('hello world')
        teacher_username = validated_data.pop('teacher_id', None)
        # print(User.objects.get(username=teacher_username))
        teacher_user = User.objects.get(username=teacher_username)
        host = Teacher.objects.get(user=teacher_user)
        validated_data['host_id'] = host
        classroom = Classroom.objects.create(**validated_data)
        return classroom

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

    user_info = serializers.SerializerMethodField()
    classroom = serializers.CharField()
    students = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    students_present = StudentSerializer(read_only=True,many=True)
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = Attendance_Session
        fields = '__all__'

    def create(self, validated_data):
        classroom = validated_data.pop('classroom')
        classroom = Classroom.objects.get(course_code = classroom)
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

    def get_user_info(self,obj):
        user = self.context['request'].user

        return {
            'id':user.id,
            'username': user.username,
            'email': user.email
        }

    def get_total_students(self, obj):
        return obj.classroom.students.count()

