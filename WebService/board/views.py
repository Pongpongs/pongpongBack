from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Post
from .forms import PostForm

# Create your views here.
def front_view(request):
	return render(request, 'board/front.html')

def index_view(request):
	return render(request, 'board/index.html')

def post_view(request):
	posts = Post.objects.all().order_by('-created_at')
	return render(request, 'board/post.html', {'posts': posts})

def add_post(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('board:post_view')
	form = PostForm()
	return render(request, 'board/add_post.html', {'form': form})

def delete_post(request, post_id):
	if request.method == "POST":
		post = Post.objects.get(id=post_id)
		post.delete()
		return HttpResponseRedirect('/posts/')
	return HttpResponse("Method not allowed", status=405)

