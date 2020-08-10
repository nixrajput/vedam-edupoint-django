from django.contrib import admin

from .models import *


admin.site.register(CustomUser)
admin.site.register(UserProfileImage)
admin.site.register(Course)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Question)
