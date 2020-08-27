from django.urls import path

from edupoint.views import (
    home,
    TestListView,
    TestDetailView,
    TestTakeView,
    UserProgressView,
    TestMarkingList,
    TestMarkingDetail,
)

urlpatterns = [
    path('', home, name='home'),
    path('online-test/', TestListView.as_view(), name='online-test-list'),
    path('online-test/<slug>/', TestDetailView.as_view(), name='online-test-detail'),
    path('online-test/<slug>/portal/', TestTakeView.as_view(), name='online-test-portal'),
    path('progress/', UserProgressView.as_view(), name='test-progress'),
    path('marking/', TestMarkingList.as_view(), name='test-marking'),
    path('marking/<pk>/', TestMarkingDetail.as_view(), name='test-marking-detail'),
]
