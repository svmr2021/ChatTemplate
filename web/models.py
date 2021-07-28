from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

user = get_user_model()


class Room(models.Model):
    room_name = models.CharField(max_length=30, unique=True)


class Message(models.Model):
    room = models.ForeignKey(Room,on_delete=models.CASCADE,null=True,blank=True)
    author = models.ForeignKey(user,on_delete=models.CASCADE,null=True,blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def last_10(self, room):
        return Message.objects.order_by('-timestamp').all().filter(room=room)[:10]