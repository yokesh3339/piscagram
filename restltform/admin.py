from django.contrib import admin
from .models import People,follow,comments
from chat.models import Message
# Register your models here.
admin.site.register(People)
admin.site.register(follow)
admin.site.register(comments)
admin.site.register(Message)