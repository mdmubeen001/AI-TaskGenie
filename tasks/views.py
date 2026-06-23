from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Task
from .forms import TaskForm


@login_required
def add_task(request):

    if request.method == "POST":

        form = TaskForm(request.POST)

        if form.is_valid():

            task = form.save(commit=False)

            task.user = request.user

            task.save()

            return redirect("task_list")

    else:

        form = TaskForm()

    return render(request, "tasks/add_task.html", {

        "form": form

    })


@login_required
def task_list(request):

    tasks = Task.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request,

                  "tasks/task_list.html",

                  {

                      "tasks": tasks

                  })


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

    task.delete()

    return redirect("task_list")