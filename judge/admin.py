from django.contrib import admin

from django.contrib import admin
from .models import Problem, TestCase, Submission

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 3

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'deadline', 'is_active_status', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('difficulty',)
    inlines = [TestCaseInline]
    def is_active_status(self, obj):
        return obj.is_active
    is_active_status.boolean = True
    is_active_status.short_description = "Activo"

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'problem', 'status', 'execution_time', 'created_at')
    list_filter = ('status', 'problem')
    readonly_fields = ('created_at',)

    