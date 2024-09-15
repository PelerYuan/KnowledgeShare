import hashlib
import os
from urllib.parse import urlencode
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def avatar_path(user):
    if os.path.isfile(settings.MEDIA_ROOT+f'/avatars/{user.username}.png'):
        return f'/storage/avatars/{user.username}.png'
    else:
        return '/storage/avatars/avatar.png'
