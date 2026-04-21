from django.urls import path
from .views import (
    view_shared_file,
    view_shared_file_group,
)

app_name = "wagtail_public_files"

urlpatterns = [
    path("files/<str:pk>/", view_shared_file, name="detail"),
    path("groups/<str:pk>/", view_shared_file_group, name="group_detail"),
]
