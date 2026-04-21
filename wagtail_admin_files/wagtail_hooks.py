from django.conf import settings
from django.urls import path, include, reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.admin.menu import MenuItem
from wagtail import hooks

from .settings import WAGTAIL_ADMIN_FILES_MENU_HOOK
from .models import SharedFile
from .views import (
    SharedFileGroupListView,
    SharedFileGroupDetailView,
    SharedFileView,
    SharedFileListView,
    SharedFileAddView,
    serve_shared_pdf,
)

@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("waf/", include(([
            path("", SharedFileListView.as_view(), name="list"),
            path("groups/", SharedFileGroupListView.as_view(), name="list_groups"),
            path("groups/<str:group>/", SharedFileGroupDetailView.as_view(), name="group_detail"),
            path("add/", SharedFileAddView.as_view(), name="add"),
            path("file/<str:pk>/", SharedFileView.as_view(), name="detail"),
            path("file/<str:pk>/pdf/", serve_shared_pdf, name="serve_shared_pdf"),
        ], "wagtail_admin_files"), namespace="wagtail_admin_files"), name="wagtail_admin_files"),
    ]

@hooks.register("register_permissions")
def register_admin_permissions():
    
    content_type = ContentType.objects.get_for_model(SharedFile)
    return Permission.objects.filter(content_type=content_type, codename__in=[
        "view_sharedfile",
    ])

@hooks.register(WAGTAIL_ADMIN_FILES_MENU_HOOK)
def register_admin_files_menu_item():
    return MenuItem(
        label=_("Shared Files"),
        url=reverse("wagtail_admin_files:list"),
        name="wagtail_admin_files",
        icon_name="doc-empty",
    )