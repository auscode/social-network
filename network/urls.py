
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user", views.user, name="user"),
    path("login", views.login_view, name="login"),
    path("addPost", views.addPost, name="addPost"),
    path("profile", views.profile, name="profile"),
    path("logout", views.logout_view, name="logout"),
    path("allPosts", views.allPosts, name="allPosts"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    #path("postsList", views.postsList, name="postsList"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),


    #API routes
    path("get_user", views.get_user, name="get_user"),
    path("like/<int:post_id>", views.like, name="like"),
    path("all_posts", views.all_posts, name="all_posts"),
    path("get_post/<int:post_id>", views.get_post, name="get_post"),
    path("follow/<int:followed_profile>", views.follow, name="follow"),
    path("following_posts", views.following_posts, name="following_posts"),
    path("user_posts/<int:profile_id>", views.user_posts, name="user_posts"),
    path("profile/<int:profile_id>", views.profile_json, name="profile_json"),
    path("unfollow/<int:unfollowed_profile>", views.unfollow, name="unfollow"),
    path("get_following/<int:profile_id>", views.get_following, name="get_following"),
    path("is_follower/<int:is_user1>/<int:following_user2>", views.is_follower, name="is_follower"),


]