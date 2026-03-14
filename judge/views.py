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
from django.db.models import Exists, OuterRef
from .models import Problem, Submission
from django.db.models import Count, Q, Sum
from django.contrib.auth.models import User

def global_leaderboard(request):
    users_ranking = User.objects.annotate(
        solved_count=Count(
            'submission', 
            filter=Q(submission__status='AC'),
            distinct=True
        ),
        total_time=Sum(
            'submission__execution_time',
            filter=Q(submission__status='AC')
        )
    ).filter(solved_count__gt=0).order_by('-solved_count', 'total_time', 'username') 

    return render(request, 'judge/global_leaderboard.html', {
        'rankings': users_ranking
    })

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

def problem_list(request):
    problems = Problem.objects.all().order_by('-created_at')
    
    if request.user.is_authenticated:
        # Creamos una subconsulta: ¿Existe un envío AC de este usuario para este problema?
        solved_subquery = Submission.objects.filter(
            user=request.user,
            problem=OuterRef('pk'),
            status='AC'
        )
        # Anotamos el queryset principal con el resultado de la subconsulta
        problems = problems.annotate(is_solved=Exists(solved_subquery))
    
    return render(request, 'judge/problem_list.html', {'problems': problems})

def submission_status(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return JsonResponse({"status": submission.status})

@login_required
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if not problem.is_active:
        return JsonResponse({
            "error": "El tiempo para este problema ha expirado. No se aceptan más envíos."
        }, status=403)
    
    
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

@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if not problem.is_active:
        return redirect('problem_list')
    
    already_solved = Submission.objects.filter(
        user=request.user, 
        problem=problem, 
        status='AC'
    ).exists()

    if already_solved:
        return redirect('submission_history')

    return render(request, 'judge/problem_details.html', {'problem': problem})