from celery import shared_task
from .models import Submission
from .evaluator import run_python_code

@shared_task
def evaluate_submission(submission_id):
    submission = Submission.objects.get(id=submission_id)
    submission.status = 'RUNNING'
    submission.save()

    testcases = submission.problem.testcases.all()
    all_passed = True
    max_time = 0

    for test in testcases:
        # Pasamos los argumentos reales aquí
        output, error, duration, status = run_python_code(
            submission.code, 
            test.input_data, 
            submission.problem.time_limit
        )
        
        max_time = max(max_time, duration)

        if status == "RE":
            submission.status = 'RE'
            submission.result_details = error
            all_passed = False
            break
        elif status == "TLE":
            submission.status = 'TLE'
            all_passed = False
            break
        elif output != test.expected_output.strip():
            submission.status = 'WA'
            all_passed = False
            break

    if all_passed:
        submission.status = 'AC'
        submission.result_details = "" # Limpiamos errores previos si los hubiera
    
    submission.execution_time = max_time
    submission.save()