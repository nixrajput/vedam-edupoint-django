from django.contrib import admin
from .models import *
import nested_admin


class AnswerInline(nested_admin.NestedTabularInline):
    model = Answer
    extra = 4
    max_num = 4


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [AnswerInline, ]
    extra = 1


class TestPaperAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInline, ]


class UsersAnswerInline(nested_admin.NestedTabularInline):
    model = UsersAnswer
    extra = 1


class TestUserAdmin(admin.ModelAdmin):
    inlines = [UsersAnswerInline, ]


class ProfileImageInline(admin.TabularInline):
    model = UserProfileImage
    extra = 1
    max_num = 1


class CustomUsersAdmin(admin.ModelAdmin):
    inlines = [ProfileImageInline, ]


admin.site.register(CustomUser, CustomUsersAdmin)
admin.site.register(UserProfileImage)

admin.site.register(TestPaper, TestPaperAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(TestUser, TestUserAdmin)
admin.site.register(UsersAnswer)
admin.site.register(ContactUs)
admin.site.register(TeamMember)
