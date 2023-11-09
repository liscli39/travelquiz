from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('password', views.PasswordView.as_view(), name='password'),
    path('profile', views.ProfileView.as_view(), name='login'),
    path('questions', views.QuestionView.as_view(), name='questions'),
    path('questions/<str:question_id>', views.QuestionDetailView.as_view(), name='question_detail'),
    path('answers', views.AnswerView.as_view(), name='answers'),
    path('ranks', views.RankView.as_view(), name='rank'),
    path('week', views.WeekView.as_view(), name='week'),

    path('chartdata', views.ChartDataView.as_view(), name='chartdata'),
    # Group
    # path('groups', views.GroupView.as_view(), name='group'),
    # path('groups/<str:group_id>', views.GroupDetailView.as_view(), name='group_detail'),
    # path('groups/<str:group_id>/join', views.GroupJoinView.as_view(), name='group_join'),
    # path('groups/<str:group_id>/ready', views.GroupReadyView.as_view(), name='group_ready'),
    # path('groups/<str:group_id>/questions', views.GroupQuestionView.as_view(), name='group_question'),
    # path('groups/<str:group_id>/questions/<str:question_id>', views.GroupQuestionDetailView.as_view(), name='group_question_detail'),
    # path('groups/<str:group_id>/answers', views.GroupAnswerView.as_view(), name='group_answer'),
    # path('groups/<str:group_id>/ranks', views.GroupRankView.as_view(), name='group_rank'),
]
