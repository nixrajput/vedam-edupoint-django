from django.db import models
from django.utils.translation import ugettext_lazy as _
from edupoint.models import Question


ANSWER_ORDER_OPTIONS = (
    ('content', _('Content')),
    ('random', _('Random')),
    ('none', _('None'))
)


class MultiChoiceQuestion(Question):
    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        default=ANSWER_ORDER_OPTIONS[1] ,
        choices=ANSWER_ORDER_OPTIONS,
        help_text=_("The order in which multiple choice "
                    "answer options are displayed "
                    "to the user"),
        verbose_name=_("Answer Order"))

    def check_if_correct(self, guess):

        if guess != '':
            answer = Answer.objects.get(id=guess)
        else:
            answer = ''

        if answer == '':
            return 'skipped'
        elif answer.correct is True:
            return True
        else:
            return False

    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):

        if guess == '':
            answer = 'Skipped'
        else:
            answer = Answer.objects.get(id=guess).content

        return answer

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")


class Answer(models.Model):
    question = models.ForeignKey(
        MultiChoiceQuestion,
        on_delete=models.CASCADE,
        verbose_name=_("Question"),
    )

    content = models.CharField(
        max_length=1000,
        blank=False,
        verbose_name=_("Content"),
        help_text=_("Enter the answer text that "
                    "you want displayed"),
    )

    correct = models.BooleanField(
        blank=False,
        default=False,
        verbose_name=_("Correct"),
        help_text=_("Is this a correct answer?"),
    )

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
