import calendar

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from tasks.models import Task


@login_required
def calendar_view(request):

    today = timezone.now().date()

    month = request.GET.get("month")
    year = request.GET.get("year")

    if month and year:

        month = int(month)
        year = int(year)

    else:

        month = today.month
        year = today.year

    cal = calendar.Calendar(firstweekday=6)

    month_days = cal.monthdatescalendar(year, month)

    tasks = Task.objects.filter(

        user=request.user,

        deadline__year=year,

        deadline__month=month

    )

    task_map = {}

    for task in tasks:

        day = task.deadline.day

        if day not in task_map:

            task_map[day] = []

        task_map[day].append(task)

    months = []

    for i in range(1, 13):

        months.append({

            "number": i,

            "name": calendar.month_name[i]

        })

    years = []

    for i in range(today.year - 2, today.year + 3):

        years.append(i)

    previous_month = month - 1
    previous_year = year

    if previous_month == 0:

        previous_month = 12
        previous_year -= 1

    next_month = month + 1
    next_year = year

    if next_month == 13:

        next_month = 1
        next_year += 1

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

    overdue_tasks = Task.objects.filter(

        user=request.user,

        deadline__lt=today,

        status__in=["Pending", "In Progress"]

    ).count()

    context = {

        "today": today,

        "current_month": month,

        "current_year": year,

        "month_name": calendar.month_name[month],

        "month_days": month_days,

        "task_map": task_map,

        "months": months,

        "years": years,

        "previous_month": previous_month,

        "previous_year": previous_year,

        "next_month": next_month,

        "next_year": next_year,

        "total_tasks": total_tasks,

        "completed_tasks": completed_tasks,

        "pending_tasks": pending_tasks,

        "in_progress_tasks": in_progress_tasks,

        "overdue_tasks": overdue_tasks,

    }

    return render(

        request,

        "calendar_app/calendar.html",

        context

    )