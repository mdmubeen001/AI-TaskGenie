from django.urls import path
from . import views

urlpatterns = [

    path(

        "",

        views.ai_planner,

        name="ai_planner"

    ),

]