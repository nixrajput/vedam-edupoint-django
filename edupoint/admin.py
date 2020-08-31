from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from edupoint.models import (
    TestPaper,
    Progress,
    Sitting,
    Category,
    Course,
    Subject,
    Question
)
from multiplechoice.models import MultiChoiceQuestion, Answer


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
            self.fields['questions'].initial = self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        paper = super(TestAdminForm, self).save(commit=False)
        paper.save()
        paper.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return paper


class TestAdmin(admin.ModelAdmin):
    form = TestAdminForm

    list_display = ('name', 'category', 'subject',)
    list_filter = ('category', 'subject',)
    search_fields = ('name', 'category__title', 'course__title', 'subject__title', 'slug',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title',)


class CourseAdmin(admin.ModelAdmin):
    search_fields = ('title', 'category',)
    list_display = ('title', 'category',)
    list_filter = ('category',)


class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('title',)


class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'subject',)
    list_filter = ('category', 'course', 'subject',)
    fields = ('text', 'figure', 'category', 'course', 'subject',
              'paper', 'explanation', 'explanation_figure', 'answer_order')
    search_fields = ('text', 'explanation', 'subject',)
    filter_horizontal = ('paper',)

    inlines = [AnswerInline]


class ProgressAdmin(admin.ModelAdmin):
    search_fields = ('user', 'score',)


admin.site.register(TestPaper, TestAdmin)
admin.site.register(MultiChoiceQuestion, MultipleChoiceQuestionAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Sitting)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Subject, SubjectAdmin)
