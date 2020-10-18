from django.contrib import admin
from .models import People,follow,comments

# Register your models here.
admin.site.register(People)
admin.site.register(follow)
admin.site.register(comments)