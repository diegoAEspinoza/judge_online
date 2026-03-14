from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problem/<int:problem_id>/submit/', views.submit_code, name='submit_code'),
    path('global_leaderboard/', views.global_leaderboard, name='global_leaderboard'), # Ranking Global
    path('history/', views.submission_history, name='submission_history'),
    path('submission/<int:submission_id>/status/', views.submission_status, name='submission_status'),
]