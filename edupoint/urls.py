from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('online-test/', views.TestListView.as_view(), name='online-test'),
    path('online-test/<str:slug>/', views.TestDetailView.as_view(), name='online-test-page'),
    path('online-test/<str:slug>/take/', views.TestTakeView.as_view(), name='online-test-take'),
    path('progress/', views.UserProgressView.as_view(), name='test-progress'),
    path('marking/', views.TestMarkingList.as_view(), name='test-marking'),
    path('marking/<pk>', views.TestMarkingDetail.as_view(), name='test-marking-detail'),
]
