from django.urls import path
from . import views

urlpatterns = [
    path("", views.ai_planner, name="ai_planner"),
    path("roadmaps/", views.roadmaps_list, name="roadmaps_list"),
    path("roadmaps/<int:roadmap_id>/", views.roadmap_detail, name="roadmap_detail"),
    path("roadmaps/<int:roadmap_id>/delete/", views.delete_roadmap, name="delete_roadmap"),
]