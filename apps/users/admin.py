from django.contrib import admin
from .models import CustomUser, SavedComment
from django.contrib.auth.models import Group


admin.site.register(CustomUser)
admin.site.register(SavedComment)
admin.site.unregister(Group)