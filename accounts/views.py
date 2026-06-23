from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import SignupForm, LoginForm
from tasks.models import Task


# -------------------------
# Signup
# -------------------------

def signup_view(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("login")

    else:

        form = SignupForm()

    return render(
        request,
        "accounts/signup.html",
        {
            "form": form
        }
    )


# -------------------------
# Login
# -------------------------

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        form = LoginForm(request, data=request.POST)

    else:

        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


# -------------------------
# Logout
# -------------------------

def logout_view(request):

    logout(request)

    return redirect("home")


# -------------------------
# Dashboard
# -------------------------

@login_required
def dashboard_view(request):

    total_tasks = Task.objects.filter(
        user=request.user
    ).count()

    pending_tasks = Task.objects.filter(
        user=request.user,
        status="Pending"
    ).count()

    completed_tasks = Task.objects.filter(
        user=request.user,
        status="Completed"
    ).count()

    high_priority_tasks = Task.objects.filter(
        user=request.user,
        priority="High"
    ).count()

    today_tasks = Task.objects.filter(
        user=request.user,
        deadline=timezone.now().date()
    ).count()

    recent_tasks = Task.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    context = {

        "total_tasks": total_tasks,

        "pending_tasks": pending_tasks,

        "completed_tasks": completed_tasks,

        "high_priority_tasks": high_priority_tasks,

        "today_tasks": today_tasks,

        "recent_tasks": recent_tasks,

    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )