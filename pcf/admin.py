from django.contrib import admin

from pcf.models import Post, Comment, OneTimeCode


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(OneTimeCode)
