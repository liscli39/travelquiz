from django.urls import path

from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('questions', views.QuestionView.as_view(), name='questions'),
    path('questions/<str:question_id>', views.QuestionDetailView.as_view(), name='question_detail'),
    path('answers', views.AnswerView.as_view(), name='answers'),
    path('ranks', views.RankView.as_view(), name='rank'),
]
