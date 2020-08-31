from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse


class TestMarkerMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TestMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        test_filter = self.request.GET.get('test_filter')
        if test_filter:
            queryset = queryset.filter(testpaper__name__icontains=test_filter)

        return queryset


class AjaxFormMixin(object):
    def form_invalid(self, form):
        response = super(AjaxFormMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxFormMixin, self).form_valid(form)
        if self.request.is_ajax():
            print(form.cleaned_data)
            data = {
                "message": "Successfully submitted form data."
            }
            return JsonResponse(data)
        else:
            return response
