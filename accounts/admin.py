from django.contrib import admin
from accounts.models import *


class ProfileImageInline(admin.TabularInline):
    model = UserProfileImage
    extra = 1
    max_num = 1


class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ('img', 'user',)
    list_filter = ('user',)


class CustomUsersAdmin(admin.ModelAdmin):
    list_filter = ('is_superuser', 'is_staff', 'is_valid',)

    inlines = [ProfileImageInline, ]


admin.site.register(CustomUser, CustomUsersAdmin)
admin.site.register(UserProfileImage, ProfilePictureAdmin)
