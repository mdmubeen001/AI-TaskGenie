from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.ai_chat,
        name="ai_chat"
    ),

    path(
        "new/",
        views.new_chat,
        name="new_chat"
    ),

    path(
        "delete/<int:id>/",
        views.delete_chat,
        name="delete_chat"
    ),

]