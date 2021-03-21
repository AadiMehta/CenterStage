from django.shortcuts import render  
from frontend.forms.post import PostForm 
from engine.models import Post
from django.shortcuts import redirect
from frontend.utils.auth import get_user_from_token, is_authenticated
from engine.serializers import PostCreateSerializer


def get_user(request):
        if is_authenticated(request.COOKIES.get('auth_token')):
            return get_user_from_token(request.COOKIES.get('auth_token'))
        else:
            return False

def NewPost(request):  

	if request.method == "POST":
		print(request.POST)
		form = PostForm(request.POST)
		user = get_user(request)
		print(user)
		if form.is_valid():
			serializer = PostCreateSerializer(data=form.get_cleaned_data())
			serializer.is_valid(raise_exception=True)
			note = serializer.save(user=user)
			return redirect("/dashboard/posts")
	else:
		post = PostForm()
		return render(request,"post/newpost.html",{'form':post})  