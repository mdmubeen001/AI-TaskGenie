from django.urls import path
from . import views

urlpatterns = [

    path("login/", views.login_view, name="login"),

    path("signup/", views.signup_view, name="signup"),

    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard_view, name="dashboard"),

    path("profile/", views.profile, name="profile"),

    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path("settings/", views.settings_page, name="settings"),
    path("delete-tasks/", views.delete_all_tasks, name="delete_all_tasks"),
    path("delete-account/", views.delete_account, name="delete_account"),  
]