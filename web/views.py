from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()

    context = {
        'form':form,
    }
    return render(request,'registration/register.html',context=context)


@login_required()
def index(request):
    rooms = Room.objects.all()

    context = {
        'rooms':rooms,
    }
    return render(request, 'web/index.html',context)


@login_required()
def room(request, room_name):
    try:
        room = Room.objects.get(room_name=room_name)
        messages = Message.objects.all().filter(room=room)
    except:
        room_name = room_name
        messages = []
    return render(request, 'web/room.html', {
        'room_name': room_name,
    })