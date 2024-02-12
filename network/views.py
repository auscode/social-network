import json
from django import forms
from datetime import datetime
from django.urls import reverse
# from django.core import serializers
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import *

class PostForm(forms.Form):
    title = forms.CharField(label="title")
    postText = forms.Textarea()

def index(request):
    posts_list = Post.objects.all().order_by('-creation_date') 
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/index.html', {'page_obj': page_obj})

@login_required
def user(request):

    following = Profile.objects.get(user = request.user).following.all()
    followers = Profile.objects.get(user = request.user).followers.all()
    
    data = {
        "userName": request.user.username,
        "following": len(following),
        "followers": len(followers)
    }
    
    posts_list = Post.objects.filter(author=request.user).order_by('-creation_date')
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/user.html",{
        "posts_list" : posts_list,
        "data": data,
        "page_obj":page_obj,
        "id":request.user.id
    })

def allPosts(request):
    posts_list = Post.objects.all().order_by('-creation_date') 
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/allposts.html', {
        'page_obj': page_obj,
        'user' : request.user
        })

def following(request):
    # posts_list = Post.objects.all().order_by('-creation_date') 
    user = request.user
    following = Profile.objects.get(user = user).following.all()
    
    posts = []
    for f in following:
        author = User.objects.get(id = f.id)
        
        # Return posts in reverse chronologial order
        posts += Post.objects.filter( author = author).order_by("-creation_date").all()

    posts.sort(key=lambda r: r.creation_date, reverse=True)

    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/following.html', {'page_obj': page_obj})


# JSON
@login_required
def profile_json(request,profile_id):
    user = User.objects.get(id = profile_id)
    following = Profile.objects.get(user = user).following.all()
    followers = Profile.objects.get(user = user).followers.all()

    userName = user.username
    
    data = {
        "userName": userName,
        "following": len(following),
        "followers": len(followers)
    }

    return JsonResponse(data)

def all_posts(request):

    # Return posts in reverse chronologial order
    posts = Post.objects.all().order_by("-creation_date").all()
    return JsonResponse([post.serialize() for post in posts], safe=False)

def get_post(request, post_id):

    post = Post.objects.get(id = post_id)
    return JsonResponse(post.serialize())


def following_posts(request):

    # Return posts of followed users
    user = request.user
    print(user)
    following = Profile.objects.get(user = user).following.all()
    print(following)

    posts = []
    for f in following:
        author = User.objects.get(id = f.id)
        
        # Return posts in reverse chronologial order
        posts += Post.objects.filter( author = author).order_by("-creation_date").all()

    posts.sort(key=lambda r: r.creation_date, reverse=True)

    return JsonResponse([post.serialize() for post in posts], safe=False)


def user_posts(request, profile_id):
    author = User.objects.get(id = profile_id)

    # Return posts in reverse chronologial order
    posts = Post.objects.filter( author = author).order_by("-creation_date").all()
    return JsonResponse([post.serialize() for post in posts], safe=False)

def get_user(request):

    # Return users in reverse chronologial order
    user = User.objects.get(id = request.user.id)
    return JsonResponse(user.serialize(), safe=False)

def get_following(request, profile_id):
    user = User.objects.get(id = profile_id)
    
    # Return followers
    follow_posts = Post.objects.filter( author = user).order_by("-creation_date").all()
    return JsonResponse([post.serialize() for post in follow_posts], safe=False)

def is_follower(request, is_user1, following_user2):
    try:
        is_user1 = User.objects.get(id = is_user1)
        following_user2 = User.objects.get(id = following_user2)

        followers_user2 = Profile.objects.get(user = following_user2).followers.all()

        if followers_user2.filter(username = is_user1).count() > 0:
            result = True
        else:
            result = False

        return JsonResponse({
                "result": result
            }, status=200)
    except:
        return JsonResponse({
                "result": False
            }, status=400)

def like(request, post_id):
    user = request.user
    likedpost = Post.objects.get(pk=post_id)

    if user in likedpost.likes.all():
        likedpost.likes.remove(user)
        like = Like.objects.get(post=likedpost, user=user)
        like.delete()
    else:
        like = Like.objects.get_or_create(post=likedpost, user=user)
        likedpost.likes.add(user)
        likedpost.save()

    return HttpResponse('Success')

# PROFILE
def profile(request):
    posts_list = Post.objects.filter(author=request.user).order_by('-creation_date')


    return render(request, "network/profile.html",{
        "posts_list" : posts_list,
        "user": request.user,
    })

@login_required
def follow(request, followed_profile):

    # Query for requested email 
    try:
        profile = Profile.objects.get(user=followed_profile)
    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(profile.serialize())

    # Update whether email is read or should be archived
    if request.method == "PUT":
        data = json.loads(request.body)

        current_profile_id = request.user.id

        if data.get("profile_id") is not None:
            followed_profile_id = data["profile_id"]

        current_profile = User.objects.get(id = current_profile_id)
        followed_profile = User.objects.get(id = followed_profile_id)

        get_profile = Profile.objects.get(user = current_profile)
        get_profile.following.add(followed_profile)

        get_profile_followed = Profile.objects.get(user = followed_profile)
        get_profile_followed.followers.add(current_profile)

        get_profile.save()
        get_profile_followed.save()

        return HttpResponse(status=204)

    # Email must be via PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

@login_required
def unfollow(request, unfollowed_profile):

   # Query for requested email 
    try:
        profile = Profile.objects.get(user=unfollowed_profile)
    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(profile.serialize())

    # Update whether email is read or should be archived
    if request.method == "PUT":
        data = json.loads(request.body)

        current_profile_id = request.user.id

        if data.get("profile_id") is not None:
            followed_profile_id = data["profile_id"]

        current_profile = User.objects.get(id = current_profile_id)
        followed_profile = User.objects.get(id = followed_profile_id)

        get_profile = Profile.objects.get(user = current_profile)
        get_profile.following.remove(followed_profile)

        get_profile_followed = Profile.objects.get(user = followed_profile)
        get_profile_followed.followers.remove(current_profile)

        get_profile.save()
        get_profile_followed.save()

        return HttpResponse(status=204)

    # Email must be via PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


# POSTS
def addPost(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            postText = form.data["postText"]
            date = datetime.now()

        else:
            message = "Invalid form... Try again."
            return render(request,"network/index.html",{
            })
            
        new_post = Post(title = title, text= postText,creation_date=date, author= request.user)
        new_post.save()

        return redirect('index')
        
    return redirect('index')

def edit_post(request,post_id):
    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        textarea = request.POST["textarea"]
        post.text = textarea
        post.save()
        return redirect('index')
        
    return redirect('index')

# LOGING, AND SIGNING SECTION
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username = username, email = email, password = password)
            user.save()

            profile = Profile.objects.create(user=user)
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")