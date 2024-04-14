from django.urls import re_path
from .consumer import VideoStreamConsumer
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter

socket_routes = [
            re_path(r'ws/session/(?P<session_name>\w+)/$', VideoStreamConsumer.as_asgi())
            # path("ws/lectures/", LectureRoomConsumer.as_asgi()),
]

