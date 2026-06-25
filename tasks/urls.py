from django.urls import path
from . import views

urlpatterns = [

    path("add/", views.add_task, name="add_task"),

    path("list/", views.task_list, name="task_list"),

    path("detail/<int:id>/", views.task_detail, name="task_detail"),

    path("update/<int:id>/", views.update_task, name="update_task"),

    path("delete/<int:id>/", views.delete_task, name="delete_task"),

]