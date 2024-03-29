from django.shortcuts import render

# Create your views here.
def index(request):
	return render(request, "game/index.html")

def off2proom(request, room_name):
	return render(request, "game/off2proom.html", {"room_name": room_name})

def off4proom(request, room_name):
	return render(request, "game/off4proom.html", {"room_name": room_name})

def offtourroom(request, room_name):
	return render(request, "game/offtourroom.html", {"room_name": room_name})

def on2proom(request, room_name):
	return render(request, "game/on2proom.html", {"room_name": room_name})

def on4proom(request, room_name):
	return render(request, "game/on4proom.html", {"room_name": room_name})

# def ontourroom(request, room_name):
# 	return render(request, "game/ontourroom.html", {"room_name": room_name})
