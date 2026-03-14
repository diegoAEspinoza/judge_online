from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])
    time_limit = models.FloatField(default=2.0) # segundos
    memory_limit = models.IntegerField(default=128) # MB
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, related_name='testcases', on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    is_visible = models.BooleanField(default=True)

class Submission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('RE', 'Runtime Error'),
        ('TLE', 'Time Limit Exceeded'),
    ]
    result_details = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    execution_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)