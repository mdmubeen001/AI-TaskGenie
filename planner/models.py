from django.db import models
from django.contrib.auth.models import User


class Roadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    phases = models.JSONField(default=list)
    tasks = models.JSONField(default=list)
    available_hours = models.CharField(max_length=10, blank=True, null=True)
    priority = models.CharField(max_length=20, blank=True, null=True)
    energy_level = models.CharField(max_length=20, blank=True, null=True)
    deadline = models.CharField(max_length=20, blank=True, null=True)
    work_style = models.CharField(max_length=20, blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.goal[:50]} - {self.created_at.strftime('%d %b %Y')}"

    @property
    def total_phases(self):
        return len(self.phases)

    @property
    def total_tasks(self):
        return len(self.tasks)

    @property
    def completed_tasks(self):
        from tasks.models import Task
        return Task.objects.filter(roadmap=self, status="Completed").count()

    @property
    def progress_percent(self):
        total = self.total_tasks
        if total == 0:
            return 0
        return int((self.completed_tasks / total) * 100)

    @property
    def completion_status(self):
        if self.completed_tasks == self.total_tasks and self.total_tasks > 0:
            return "Completed"
        elif self.completed_tasks > 0:
            return "In Progress"
        else:
            return "Pending"


class AIPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%d %b %Y')}"