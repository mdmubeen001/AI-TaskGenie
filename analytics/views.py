from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task


@login_required
def analytics_dashboard(request):

    tasks = Task.objects.filter(user=request.user)

    today = timezone.now().date()

    # =========================
    # Overview Statistics
    # =========================

    total_tasks = tasks.count()

    completed_tasks = tasks.filter(
        status="Completed"
    ).count()

    pending_tasks = tasks.filter(
        status="Pending"
    ).count()

    in_progress_tasks = tasks.filter(
        status="In Progress"
    ).count()

    high_priority_tasks = tasks.filter(
        priority="High"
    ).count()

    # =========================
    # Productivity
    # =========================

    productivity = 0

    if total_tasks > 0:

        productivity = round(

            (completed_tasks / total_tasks) * 100

        )

    # =========================
    # Deadlines
    # =========================

    overdue_tasks = tasks.filter(

        deadline__lt=today,

        status__in=[

            "Pending",

            "In Progress"

        ]

    )

    today_tasks = tasks.filter(

        deadline=today

    )

    upcoming_tasks = tasks.filter(

        deadline__gt=today

    ).order_by(

        "deadline"

    )[:5]

    # =========================
    # Recent Tasks
    # =========================

    recent_tasks = tasks.order_by(

        "-created_at"

    )[:5]

    # =========================
    # High Priority Widget
    # =========================

    high_tasks = tasks.filter(

        priority="High"

    ).order_by(

        "deadline"

    )[:5]

    # =========================
    # Priority Distribution
    # =========================

    low_priority = tasks.filter(

        priority="Low"

    ).count()

    medium_priority = tasks.filter(

        priority="Medium"

    ).count()

    high_priority = tasks.filter(

        priority="High"

    ).count()

    # =========================
    # Weekly Statistics
    # =========================

    weekly = []

    labels = []

    for i in range(6, -1, -1):

        day = today - timedelta(days=i)

        labels.append(

            day.strftime("%a")

        )

        weekly.append(

            tasks.filter(

                created_at__date=day

            ).count()

        )

    # =========================
    # Context
    # =========================

    context = {

        "total_tasks": total_tasks,

        "completed_tasks": completed_tasks,

        "pending_tasks": pending_tasks,

        "in_progress_tasks": in_progress_tasks,

        "high_priority_tasks": high_priority_tasks,

        "productivity": productivity,

        "recent_tasks": recent_tasks,

        "today_tasks": today_tasks,

        "upcoming_tasks": upcoming_tasks,

        "overdue_tasks": overdue_tasks,

        "weekly_labels": labels,

        "weekly_data": weekly,

        "high_tasks": high_tasks,

        "low_priority": low_priority,

        "medium_priority": medium_priority,

        "high_priority": high_priority,

    }

    return render(

        request,

        "analytics/analytics.html",

        context

    )