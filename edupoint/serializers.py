from rest_framework import serializers
from edupoint.models import TestPaper, Sitting, Progress
from multiplechoice.models import MultiChoiceQuestion, Answer


class TestPaperListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField("get_category_from_testpaper")
    course = serializers.SerializerMethodField("get_course_from_testpaper")
    subject = serializers.SerializerMethodField("get_subject_from_testpaper")
    completed = serializers.SerializerMethodField("get_completed_from_sitting")

    class Meta:
        model = TestPaper
        fields = ["id", "name", "category", "course", "subject", "slug", "completed"]

    def get_category_from_testpaper(self, obj):
        category = obj.category.title
        return category

    def get_course_from_testpaper(self, obj):
        course = obj.course.title
        return course

    def get_subject_from_testpaper(self, obj):
        subject = obj.subject.title
        return subject

    def get_completed_from_sitting(self, obj):
        try:
            sitting = Sitting.objects.get(paper=obj, user=self.context["request"].user)
            return sitting.complete
        except Sitting.DoesNotExist:
            return None


class TestPaperDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPaper
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "question", "content"]


class QuestionSerializer(serializers.ModelSerializer):
    answer_set = AnswerSerializer(many=True)

    class Meta:
        model = MultiChoiceQuestion
        fields = "__all__"


class TestTakeSerializer(serializers.ModelSerializer):
    question_set = QuestionSerializer(many=True)

    class Meta:
        model = TestPaper
        fields = "__all__"
