from django.contrib import admin
from edupoint.models import *
from multiplechoice.models import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4


class TestAdminForm(forms.ModelForm):
    class Meta:
        model = TestPaper
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Questions"),
            is_stacked=False)
    )

    def __init__(self, *args, **kwargs):
        super(TestAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = \
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        paper = super(TestAdminForm, self).save(commit=False)
        paper.save()
        paper.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return paper


class TestAdmin(admin.ModelAdmin):
    form = TestAdminForm

    list_display = ('name', 'subject',)
    list_filter = ('subject',)
    search_fields = ('subject', 'course')


class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('text',)
    list_filter = ('paper',)
    fields = ('text', 'paper', 'figure', 'explanation', 'answer_order')

    search_fields = ('text', 'explanation')
    filter_horizontal = ('paper',)

    inlines = [AnswerInline]


class ProgressAdmin(admin.ModelAdmin):
    search_fields = ('user', 'score',)


class ProfileImageInline(admin.TabularInline):
    model = UserProfileImage
    extra = 1
    max_num = 1


class CustomUsersAdmin(admin.ModelAdmin):
    inlines = [ProfileImageInline, ]


admin.site.register(CustomUser, CustomUsersAdmin)
admin.site.register(UserProfileImage)

admin.site.register(TestPaper, TestAdmin)
admin.site.register(MultiChoiceQuestion, MultipleChoiceQuestionAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Sitting)
# admin.site.register(TestUser, TestUserAdmin)
# admin.site.register(UsersAnswer)
admin.site.register(ContactUs)
admin.site.register(TeamMember)
