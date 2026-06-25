from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


from .models import Task
from .forms import TaskForm
from django.contrib import messages


@login_required
def add_task(request):

    if request.method == "POST":

        form = TaskForm(request.POST)

        if form.is_valid():

            task = form.save(commit=False)

            task.user = request.user

            task.save()

            messages.success(

                request,

                "Task created successfully."

            )

            return redirect("task_list")

    else:

        form = TaskForm()

    return render(

        request,

        "tasks/add_task.html",

        {

            "form": form

        }

    )


@login_required
def task_list(request):

    tasks = Task.objects.filter(user=request.user)

    # Search
    search = request.GET.get("search")

    if search:
        tasks = tasks.filter(title__icontains=search)

    # Priority Filter
    priority = request.GET.get("priority")

    if priority:
        tasks = tasks.filter(priority=priority)

    # Status Filter
    status = request.GET.get("status")

    if status:
        tasks = tasks.filter(status=status)

    # Sorting
    sort = request.GET.get("sort")

    if sort == "deadline":
        tasks = tasks.order_by("deadline")

    elif sort == "created":
        tasks = tasks.order_by("-created_at")

    elif sort == "priority":
        tasks = tasks.order_by("priority")

    else:
        tasks = tasks.order_by("-created_at")

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks
        }
    )


@login_required
def task_detail(request, id):

    task = get_object_or_404(

        Task,

        id=id,

        user=request.user

    )

    return render(

        request,

        "tasks/task_detail.html",

        {

            "task": task

        }

    )

@login_required
def update_task(request, id):

    task = get_object_or_404(

        Task,

        id=id,

        user=request.user

    )

    form = TaskForm(

        request.POST or None,

        instance=task

    )

    if form.is_valid():

        form.save()

        messages.success(
            
            request,

            "Task updated successfully."

        )

        return redirect("task_list")

    return render(

        request,

        "tasks/add_task.html",

        {

            "form": form

        }

    )


@login_required
def delete_task(request, id):

    task = get_object_or_404(

        Task,

        id=id,

        user=request.user

    )

    if request.method == "POST":

        task.delete()

        messages.success(
            
            request,

            "Task deleted successfully."

        )

        return redirect("task_list")

    return render(

        request,

        "tasks/delete_task.html",

        {

            "task": task

        }

    )