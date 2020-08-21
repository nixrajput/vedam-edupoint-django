import json
import re

from django.conf import settings
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import (
    validate_comma_separated_integer_list, MaxValueValidator
)
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager


class CategoryManager(models.Manager):

    def new_category(self, category):
        new_category = self.create(category=re.sub('\s+', '-', category).lower())

        new_category.save()
        return new_category


class Category(models.Model):
    title = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Category")
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("Course")
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Category")
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.title


class Subject(models.Model):
    title = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Subject")
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")

    def __str__(self):
        return self.title


class TestPaper(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name=_("Title"),
        blank=False,
        help_text=_("Title for test paper.")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name=_("Category"),
        help_text=_("Name of category.")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name=_("Course"),
        help_text=_("Name of course.")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name=_("Subject"),
        help_text=_("Name of subject.")
    )
    max_time = models.IntegerField(
        default=0,
        verbose_name=_("Max Time"),
        help_text=_("Maximum time for test.")
    )
    max_marks = models.IntegerField(
        default=0,
        verbose_name=_("Max Marks"),
        help_text=_("Maximum marks for test.")
    )
    instructions = models.TextField(
        blank=True,
        verbose_name=_("Instructions"),
        help_text=_("Instructions to be followed during test by user.")
    )
    slug = models.SlugField(
        blank=True,
        verbose_name=_("URL"),
        help_text=_("A user friendly url for test.")
    )
    roll_out = models.BooleanField(
        default=False,
        verbose_name=_("Published"),
        help_text=_("Paper is published or not.")
    )
    random_order = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_("Random Order"),
        help_text=_("Display the questions in "
                    "a random order or as they "
                    "are set?")
    )
    answers_at_end = models.BooleanField(
        blank=False,
        default=False,
        verbose_name=_("Show Answers"),
        help_text=_("Correct answer is NOT shown after question."
                    " Answers displayed at the end.")
    )
    single_attempt = models.BooleanField(
        blank=False,
        default=False,
        verbose_name=_("Single Attempt"),
        help_text=_("If yes, only one attempt by"
                    " a user will be permitted."
                    " Non users cannot sit this exam."),
    )
    save_record = models.BooleanField(
        blank=False,
        default=False,
        verbose_name=_("Save Record"),
        help_text=_("If yes, the result of each"
                    " attempt by a user will be"
                    " stored. Necessary for marking."),
    )
    pass_mark = models.SmallIntegerField(
        blank=True,
        default=0,
        verbose_name=_("Pass Mark"),
        help_text=_("Percentage required to pass exam."),
        validators=[MaxValueValidator(100)]
    )
    success_text = models.TextField(
        blank=True,
        verbose_name=_("Success Text"),
        help_text=_("Displayed if user passes.")

    )
    fail_text = models.TextField(
        blank=True,
        verbose_name=_("Fail Text"),
        help_text=_("Displayed if user fails.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.single_attempt is True:
            self.save_record = True

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)

        super(TestPaper, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        ordering = ['timestamp', ]
        verbose_name = _("Test Paper")
        verbose_name_plural = _("Test Papers")

    def __str__(self):
        return self.name

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()


@receiver(pre_save, sender=TestPaper)
def slugify_name(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.name)


class ProgressManager(models.Manager):
    def new_progress(self, user):
        new_progress = self.create(user=user, score="")

        new_progress.save()
        return new_progress


class Progress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )

    score = models.CharField(
        max_length=1024,
        verbose_name=_("Score"),
        validators=[validate_comma_separated_integer_list]
    )

    objects = ProgressManager()

    class Meta:
        verbose_name = _("User Progress")
        verbose_name_plural = _("User Progress Record")

    @property
    def list_all_cat_scores(self):

        score_before = self.score
        output = {}

        for cat in Category.objects.all():
            to_find = re.escape(cat.title) + r",(\d+),(\d+),"

            match = re.search(to_find, self.score, re.IGNORECASE)

            if match:
                score = int(match.group(1))
                possible = int(match.group(2))

                try:
                    percent = int(round((float(score) / float(possible)) * 100))
                except:
                    percent = 0

                output[cat.title] = [score, possible, percent]

        if len(self.score) > len(score_before):
            self.save()

        return output

    def update_score(self, question, score_to_add=0, possible_to_add=0):
        category_test = Category.objects.filter(title=question.category).exists()

        if any([item is False for item in [category_test,
                                           score_to_add,
                                           possible_to_add,
                                           isinstance(score_to_add, int),
                                           isinstance(possible_to_add, int)]]):
            return _("Error"), _("test paper does not exist or invalid score.")

        to_find = re.escape(str(question.category)) + r",(?P<score>\d+),(?P<possible>\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            updated_score = int(match.group('score')) + abs(score_to_add)
            updated_possible = int(match.group('possible')) + abs(possible_to_add)

            new_score = ",".join(
                [
                    str(question.category),
                    str(updated_score),
                    str(updated_possible),
                    ""
                ])

            self.score = self.score.replace(match.group(), new_score)
            self.save()

        else:
            self.score = ",".join(
                [
                    str(question.category),
                    str(score_to_add),
                    str(possible_to_add),
                    ""
                ])

            self.save()

    def show_tests(self):
        return Sitting.objects.filter(user=self.user, complete=True)

    def __str__(self):
        return self.user.username


class SittingManager(models.Manager):
    def new_sitting(self, user, paper):
        if paper.random_order is True:
            question_set = paper.question_set.all().select_subclasses().order_by('?')
        else:
            question_set = paper.question_set.all().select_subclasses()

        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('Question set of the quiz is empty. '
                                       'Please configure questions properly')

        questions = ",".join(map(str, question_set)) + ","

        new_sitting = self.create(
            user=user,
            paper=paper,
            question_order=questions,
            question_list=questions,
            incorrect_questions="",
            current_score=0,
            complete=False,
            user_answers='{}'
        )
        return new_sitting

    def user_sitting(self, user, paper):
        if paper.single_attempt is True and self.filter(user=user,
                                                        paper=paper,
                                                        complete=True).exists():
            return False

        try:
            sitting = self.get(user=user, paper=paper, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, paper)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, paper=paper, complete=False)[0]
        return sitting


class Sitting(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    paper = models.ForeignKey(
        TestPaper,
        on_delete=models.CASCADE,
        verbose_name=_("Paper")
    )
    question_order = models.CharField(
        max_length=1024,
        verbose_name=_("Question Order"),
        validators=[validate_comma_separated_integer_list]
    )

    question_list = models.CharField(
        max_length=1024,
        verbose_name=_("Question List"),
        validators=[validate_comma_separated_integer_list]
    )

    incorrect_questions = models.CharField(
        max_length=1024,
        blank=True,
        verbose_name=_("Incorrect questions"),
        validators=[validate_comma_separated_integer_list])

    current_score = models.IntegerField(
        verbose_name=_("Current Score")
    )

    complete = models.BooleanField(
        default=False,
        blank=False,
        verbose_name=_("Complete")
    )

    user_answers = models.TextField(
        blank=True,
        default='{}',
        verbose_name=_("User Answers")
    )

    start = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Start")
    )

    end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("End")
    )

    objects = SittingManager()

    class Meta:
        verbose_name = _("User Sitting")
        verbose_name_plural = _("User Sitting Record")

    def get_first_question(self):
        if not self.question_list:
            return False

        first, _ = self.question_list.split(',', 1)
        question_id = int(first)
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        if not self.question_list:
            return

        _, others = self.question_list.split(',', 1)
        self.question_list = others
        self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = len(self._question_ids()) * 4
        if divisor < 1:
            return 0

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_testpaper_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    def add_incorrect_question(self, question):
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.paper.pass_mark

    @property
    def result_message(self):
        if self.check_if_passed:
            return self.paper.success_text
        else:
            return self.paper.fail_text

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(
            self.paper.question_set.filter(id__in=question_ids)
                .select_subclasses(),
            key=lambda q: question_ids.index(q.id))

        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                question.user_answer = user_answers[str(question.id)]

        return questions

    @property
    def questions_with_user_answers(self):
        return {
            q: q.user_answer for q in self.get_questions(with_answers=True)
        }

    @property
    def get_max_score(self):
        return len(self._question_ids()) * 4

    def progress(self):
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total

    def __str__(self):
        return self.user.username


class Question(models.Model):
    paper = models.ManyToManyField(
        TestPaper,
        blank=True,
        verbose_name=_("Test Paper"),
        help_text=_("Test paper name.")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name=_("Category"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name=_("Course"),
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name=_("Subject"),
    )
    text = models.TextField(
        max_length=2000,
        null=True,
        verbose_name=_("Question"),
        help_text=_("Enter question text.")
    )
    figure = models.ImageField(
        upload_to='questions',
        blank=True,
        null=True,
        verbose_name=_("Figure"),
        help_text=_("Figure for question if any.")
    )
    explanation = models.TextField(
        max_length=2000,
        blank=True,
        verbose_name=_('Explanation'),
        help_text=_("Explanation to be shown "
                    "after the question has "
                    "been answered.")
    )

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['category']

    def __str__(self):
        return self.text
