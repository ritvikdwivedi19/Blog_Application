from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    search_vector = SearchVectorField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['search_vector']),
        ]

class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    def __str__(self):
        return self.content