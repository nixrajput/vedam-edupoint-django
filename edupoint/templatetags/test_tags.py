from django import template

register = template.Library()


@register.inclusion_tag('tests/correct_answer.html', takes_context=True)
def correct_answer_for_all(context, question):

    answers = question.get_answers()
    incorrect_list = context.get('incorrect_questions', [])
    skipped_list = context.get('skipped_questions', [])
    if question.id in incorrect_list:
        user_was_incorrect = True
    else:
        user_was_incorrect = False

    if question.id in skipped_list:
        user_was_skipped = True
    else:
        user_was_skipped = False

    return {'previous': {'answers': answers},
            'user_was_incorrect': user_was_incorrect,
            'user_was_skipped': user_was_skipped}


@register.filter
def answer_choice_to_string(question, answer):
    return question.answer_choice_to_string(answer)
