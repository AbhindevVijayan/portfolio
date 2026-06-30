from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("contact/", views.submit_contact, name="submit_contact"),

    # Internal API for the MCP server
    path("api/profile/", views.api_profile, name="api_profile"),
    path("api/projects/", views.api_projects, name="api_projects"),
    path("api/projects/<int:pk>/", views.api_project_detail, name="api_project_detail"),
    path("api/skills/", views.api_skills, name="api_skills"),
    path("api/skills/<int:pk>/", views.api_skill_detail, name="api_skill_detail"),
    path("api/messages/", views.api_messages, name="api_messages"),
]
