import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .models import *
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth import get_user_model


User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):

        self.get_last_messages()
        content = {
            'messages': self.messages_to_json(self.messages),
        }

        for i in content['messages']:
            self.send_message(i)

    def messages_to_json(self,messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self,message):
        return {
            'author':message.author.username,
            'content':message.content,
            'timestamp':str(message.timestamp),
        }

    def new_message(self, data):
        """author = data['from']
        author_user = User.objects.filter(username=author)[0]"""
        room = Room.objects.get(room_name=self.room_name)
        message = Message.objects.create(
             author=self.scope['user'],
             content = data['message'],
             room= room,
        )

        content = {
            'command':'new_message',
            'message':self.message_to_json(message)
        }
        self.send_chat_message(data)

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.save_room(self.room_name)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)


    def send_chat_message(self,message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self,message):
        list = {}
        list['message'] = message['content']
        self.send(text_data=json.dumps(list))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    def save_room(self,room_name):
        try:
            obj = Room.objects.get(room_name=room_name)
            self.room_group_name=obj.room_name
        except:
            obj = Room(room_name=self.room_name)
            obj.save()
            self.room_group_name = 'web_%s' % self.room_name

    def save_message(self,room_name,message):
        user = self.scope['user']
        name = Room.objects.get(room_name=room_name)
        obj = Message(room=name,content=message,author=user)
        obj.save()

    def get_last_messages(self):
        room = Room.objects.get(room_name=self.room_name)
        messages = Message.objects.order_by('timestamp').all().filter(room=room)
        self.messages = messages