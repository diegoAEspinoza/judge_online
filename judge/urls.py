from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'), # Raíz
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problem/<int:problem_id>/submit/', views.submit_code, name='submit_code'),
    path('problem/<int:problem_id>/leaderboard/', views.leaderboard, name='leaderboard'),
    path('history/', views.submission_history, name='submission_history'),
    path('submission/<int:submission_id>/status/', views.submission_status, name='submission_status'),
]