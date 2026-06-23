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

    deadline = models.DateField()

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    updated_at = models.DateTimeField(

        auto_now=True

    )

    def __str__(self):

        return self.title