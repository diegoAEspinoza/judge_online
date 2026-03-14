import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Problem, Submission
from .task import evaluate_submission
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('problem_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('problem_list') 
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    return render(request, 'judge/problem_details.html', {'problem': problem})

def problem_list(request):
    problems = Problem.objects.all()
    return render(request, 'judge/problem_list.html', {'problems': problems})

def submission_status(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return JsonResponse({"status": submission.status})

@login_required
def submit_code(request, problem_id):
    if request.method == "POST":
        data = json.loads(request.body)
        problem = get_object_or_404(Problem, id=problem_id)
        
        # Crear el registro en la DB
        submission = Submission.objects.create(
            user=request.user, 
            problem=problem,
            code=data['code'],
            status='PENDING'
        )
        
        # Enviar a Celery
        evaluate_submission.delay(submission.id)
        
        return JsonResponse({"submission_id": submission.id, "status": "Queued"})

@login_required
def submission_history(request):
    submissions = Submission.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'judge/submission_history.html', {'submissions': submissions})

def leaderboard(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    best_submissions = Submission.objects.filter(
        problem=problem, 
        status='AC'
    ).values('user__username').annotate(
        best_time=Min('execution_time')
    ).order_by('best_time')

    return render(request, 'judge/leaderboard.html', {
        'problem': problem,
        'rankings': best_submissions
    })