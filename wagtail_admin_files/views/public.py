from django.db import models
from django.urls import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from ..settings import WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC, WAGTAIL_ADMIN_FILES_TEMPLATE_EXTENDS
from ..models import SharedFile, SharedFileGroup


def view_shared_file(request, pk):
    if not WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC:
        return Http404

    obj = get_object_or_404(SharedFile, pk=pk)
    context = {
        "TEMPLATE_EXTENDS": WAGTAIL_ADMIN_FILES_TEMPLATE_EXTENDS,
        "object": obj,
        "sharing": request.GET.get("shared", "false").lower() == "true",
        "share_url": request.build_absolute_uri(reverse("wagtail_public_files:detail", args=[obj.pk])),
    }

    return render(request, "wagtail_public_files/detail.html", context)


def view_shared_file_group(request, pk):
    if not WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC:
        return Http404

    try:
        group = SharedFileGroup.objects\
            .annotate(file_count=models.Count("sharedfile"))\
            .annotate(latest_upload=models.Max("sharedfile__uploaded_at"))\
            .prefetch_related("sharedfile_set")\
            .get(pk=pk)
    except SharedFileGroup.DoesNotExist:
        raise Http404

    context = {
        "TEMPLATE_EXTENDS": WAGTAIL_ADMIN_FILES_TEMPLATE_EXTENDS,
        "object": group,
        "file_count": group.file_count,
        "latest_upload": group.latest_upload,
    }
    
    return render(request, "wagtail_public_files/group_detail.html", context)