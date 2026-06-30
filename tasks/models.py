from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):

    PRIORITY = (

        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),

    )

    STATUS = (

        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),

    )

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE

    )

    roadmap = models.ForeignKey(
        "planner.Roadmap",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_tasks"
    )

    title = models.CharField(

        max_length=200

    )

    description = models.TextField()

    priority = models.CharField(

        max_length=20,

        choices=PRIORITY,

        default="Medium"

    )

    status = models.CharField(

        max_length=20,

        choices=STATUS,

        default="Pending"

    )

    deadline = models.DateField(null=True, blank=True)

    estimated_duration = models.IntegerField(
        help_text="Estimated duration in minutes",
        null=True,
        blank=True
    )

    phase = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    order = models.IntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    updated_at = models.DateTimeField(

        auto_now=True

    )

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):

        return self.title