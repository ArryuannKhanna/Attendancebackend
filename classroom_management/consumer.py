from channels.generic.websocket import AsyncWebsocketConsumer
# import base64
import numpy as np
import cv2
import face_recognition
import pickle
import json
from channels.db import database_sync_to_async

# from channels.decorator
# from django.db.models import Q
#
# from datetime import datetime
# from django.utils.timezone import make_aware
# from channels.db import database_sync_to_async
# # from .models import LectureRoom
# from asgiref.sync import sync_to_async
# import asyncio


# name_of_students = ['Jatin', 'Tatin', 'Arryuann']
# with open('EncodeFile.p', 'rb') as file:
#     encodeList = pickle.load(file)
# encodelistknown, student_id = encodeList

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_name = self.scope['url_route']['kwargs']['session_name']

        await self.channel_layer.group_add(
            self.session_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.session_name,
            self.channel_name
        )
        # pass
    @database_sync_to_async
    def get_face_encodings(self,class_code):
        from classroom_management.models import Classroom,Student

        class_ = Classroom.objects.get(course_code = class_code)
        students = class_.students.all()
        users = students.values('user')


        encodings = []
        user_ids = []

        for student in students:
            encodings.append(student.get_encoding())

        for student in students:
            user_ids.append(student.user.username)

        # for q in users:
        #     # encodings.append(q['encodings'])
        #     user_ids.append(q['user'])

        encode_list = [encodings,user_ids]

        return encode_list


    @database_sync_to_async
    def markstudents(self,student_username):
        from classroom_management.models import Attendance_Session, Student
        from django.contrib.auth.models import User
        user_ = User.objects.get(username = student_username)
        student_ = Student.objects.get(user=user_)
        session_ = Attendance_Session.objects.last()
        print(user_)
        print(student_)
        print(session_)
        session_.students_present.add(student_)

    #
    async def receive(self, text_data=None, bytes_data=None):
        if text_data == 'PING':
            await self.send('PONG')
        if bytes_data:
            # print(bytes_data)
            encodelistknown,name_of_students = await self.get_face_encodings(class_code = self.session_name)

            # print(name_of_students)
            encodelistknown = np.array(encodelistknown)
            # print("hehe",encodelistknown)
            nparr = np.frombuffer(bytes_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # print(imgS)
            # Detect faces in the image
            face_positions = face_recognition.face_locations(imgS)
            encoding_frame = face_recognition.face_encodings(imgS, face_positions)

            recognized_names = []  # List to hold all recognized names

            for encface, facepos in zip(encoding_frame, face_positions):
                matches = face_recognition.compare_faces(encodelistknown, encface)
                face_dist = face_recognition.face_distance(encodelistknown, encface)
                best_match_index = np.argmin(face_dist)

                if matches[best_match_index]:
                    name = name_of_students[best_match_index]
                    recognized_names.append(name)

                    # print(name)
                    await self.markstudents(student_username = name)
                    # Draw bounding box for the face and put recognized name
                    # Note: Drawing on the image in your consumer might not be the best approach
                    # Consider sending coordinates and names back to the client for rendering
                else:
                    recognized_names.append("Unknown")

            # Prepare the data to send back
            # For simplicity, sending recognized names; adjust as needed for your application
            await self.send(text_data=json.dumps({"recognized_names": recognized_names}))

            # If you need to send back the modified image, encode and send it as before
            # _, img_encoded = cv2.imencode('.jpg', img)
            # await self.send(bytes_data=img_encoded.tobytes())
