from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def serialize(self):
        return {
            "id": self.id,
            "name": self.username,
        }

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(User, blank=True, related_name="following")
    followers = models.ManyToManyField(User, blank=True, related_name="followers")

    def serialize(self):
        return {
            "profileID": self.user.id,
            "following": int(self.following.all().count()),
            "followers": int(self.followers.all().count()),
        }


class Post(models.Model):
    title = models.CharField(max_length=64,default=None)
    text = models.TextField(default=None)
    likes = models.ManyToManyField('User', blank=True, related_name='likes')
    creation_date = models.DateTimeField(null=True, default=None)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author", default=None)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "likes": Like.objects.filter(post=self).count(),
            "creation_date": self.creation_date.strftime("%b %d %Y, %I:%M %p"),
            "author": self.author.username,
            "author_id": self.author.id,
        }

    def __str__(self):
        return f"ID:{self.id} Title:{self.title} Text:{self.text} Likes:{self.like_set.count} Created:{self.creation_date} Author:{self.author}"


class Like(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.post)
