from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.urls import reverse_lazy
from django.core.cache import cache


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=2, choices=[
        ('TA', 'Танки'), ('HE', 'Хилы'), ('DD', 'ДД'), ('ME', 'Торговцы'), ('GM', 'Гилдмастеры'),
        ('QG', 'Квестгиверы'), ('BS', 'Кузнецы'), ('TA', 'Кожевники'), ('PM', 'Зельевары'),
        ('SM', 'Мастера Заклинаний')
        ])
    title = models.CharField(max_length=255)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('post', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        cache.delete('post_list')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        cache.delete('post_list')
        super().delete(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50]


class OneTimeCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.IntegerField()

    def __str__(self):
        return f'{self.user}: {self.code}'

