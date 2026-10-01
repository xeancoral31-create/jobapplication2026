"""moderation/urls.py"""
from django.urls import path
from . import views

app_name = "moderation"

urlpatterns = [
    path("flags/", views.flag_list, name="flag_list"),
    path("flags/<int:pk>/", views.flag_detail, name="flag_detail"),
    path("report/<str:content_type>/<int:object_id>/", views.report_content, name="report"),
]
