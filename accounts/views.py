from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .forms import SignupForm, LoginForm, ProfileForm
from .models import Profile

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

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Email login support
            if "@" in username:

                from django.contrib.auth.models import User

                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                return redirect("dashboard")

            else:

                messages.error(
                    request,
                    "Invalid email/username or password."
                )

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

@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    tasks = Task.objects.filter(
        user=request.user
    )

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

    productivity = 0

    if total_tasks > 0:

        productivity = round(

            (completed_tasks / total_tasks) * 100

        )

    context = {

        "profile": profile,

        "total_tasks": total_tasks,

        "completed_tasks": completed_tasks,

        "pending_tasks": pending_tasks,

        "in_progress_tasks": in_progress_tasks,

        "productivity": productivity,

    }

    return render(

        request,

        "accounts/profile.html",

        context

    )

@login_required
def edit_profile(request):

    profile = request.user.profile

    form = ProfileForm(

        request.POST or None,

        request.FILES or None,

        instance=profile

    )

    if form.is_valid():

        form.save()

        messages.success(

            request,

            "Profile updated successfully."

        )

        return redirect("profile")

    return render(

        request,

        "accounts/edit_profile.html",

        {

            "form": form

        }

    )


@login_required
def settings_page(request):

    return render(
        request,
        "accounts/settings.html"
    )


@login_required
def delete_all_tasks(request):

    Task.objects.filter(user=request.user).delete()

    messages.success(
        request,
        "All tasks deleted successfully."
    )

    return redirect("settings")


@login_required
def delete_account(request):

    if request.method == "POST":

        user = request.user

        logout(request)

        user.delete()

        messages.success(
            request,
            "Your account has been deleted successfully."
        )

        return redirect("home")

    return render(
        request,
        "accounts/delete_account.html"
    )