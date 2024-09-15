import mimetypes
import os
import uuid

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
import math

from markdown import markdown

User = get_user_model()


class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 20
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/', filename)


class Post(models.Model):
    message = models.TextField(max_length=4000, null=True, blank=True)
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    topic = models.ForeignKey(Topic, related_name='posts', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def save(self, *args, **kwargs):
        if self.file:
            if 'upload' not in self.file.name:  # 避免重复乱码
                self.file_name = self.file.name
        super().save(*args, **kwargs)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))

    def get_file_path(self):
        return 'storage/' + self.file.name

    def get_file_name(self):
        return self.file_name

    def delete(self, *args, **kwargs):
        # Delete the file from storage
        if self.file and default_storage.exists(self.file.name):
            default_storage.delete(self.file.name)
        super().delete(*args, **kwargs)

    def is_file_image(self):
        mime_type, _ = mimetypes.guess_type(self.get_file_name())
        return mime_type and mime_type.startswith('image')
