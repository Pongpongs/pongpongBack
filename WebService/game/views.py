from django.shortcuts import render

# Create your views here.
def index(request):
	return render(request, "game/index.html")

def offoneroom(request, room_name):
	return render(request, "game/offoneroom.html", {"room_name": room_name})

def offmultiroom(request, room_name):
	return render(request, "game/offmultiroom.html", {"room_name": room_name})

def offtourroom(request, room_name):
	return render(request, "game/offtourroom.html", {"room_name": room_name})

def ononeroom(request, room_name):
	return render(request, "game/ononeroom.html", {"room_name": room_name})
