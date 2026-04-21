import logging
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.db import transaction, models
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.list import BaseListView
from django.views.decorators.clickjacking import xframe_options_sameorigin
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (7, 0):
    from wagtail.admin.paginator import WagtailPaginator as Paginator
else:
    from django.core.paginator import Paginator

if WAGTAIL_VERSION >= (6, 0):
    from wagtail.admin.widgets.button import HeaderButton
else:
    from wagtail.admin.widgets.button import Button as HeaderButton

from wagtail.admin import messages

from ..settings import WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC
from ..models import SharedFile, SharedFileGroup
from ..forms import (
    SharedFileFormSet,
)


logging = logging.getLogger(__name__)

# Create your views here.
@xframe_options_sameorigin
def serve_shared_pdf(request, pk):
    if not WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC:
        if not request.user.is_authenticated:
            return Http404
    
        if not request.user.has_perm("wagtail_admin_files.view_sharedfile"):
            return Http404

    object = get_object_or_404(SharedFile, pk=pk)
    if not object.file.name.lower().endswith(".pdf"):
        raise Http404

    return FileResponse(object.file, content_type="application/pdf")


class SharedFileMixin(WagtailAdminTemplateMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Http404

        if not request.user.has_perm("wagtail_admin_files.view_sharedfile"):
            return Http404

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "WAGTAIL_VERSION": WAGTAIL_VERSION[0],
        }


class SharedFileView(SharedFileMixin, TemplateView):
    header_icon = "doc-empty"
    page_title = _("Shared File Details")
    template_name = "wagtail_admin_files/uploaded_file_detail.html"

    def dispatch(self, request, *args, **kwargs):
        if WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC and request.GET.get("shared", "false").lower() == "true":
            return redirect(reverse("wagtail_public_files:detail", args=[self.kwargs["pk"]]))
        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs_items(self):
        items = super().get_breadcrumbs_items().copy()
        items.append({
            "url": reverse("wagtail_admin_files:list"),
            "label": _("Shared Files"),
        })
        items.append({
            "url": "",
            "label": _("File Details"),
        })
        return items

    def get_shared_file(self):
        return get_object_or_404(SharedFile, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_shared_file()
        context["object"] = obj
        context["sharing"] = self.request.GET.get("shared", "false").lower() == "true"
        context['share_url'] = f'{self.request.build_absolute_uri(reverse("wagtail_admin_files:detail", args=[obj.pk]))}?shared=true'

        if obj.group_id:
            context['group_share_url'] = f'{self.request.build_absolute_uri(reverse("wagtail_admin_files:group_detail", args=[obj.group_id]))}?shared=true'

        return context
    

class SharedFileAddView(SharedFileMixin, TemplateView):
    header_icon = "doc-empty"
    page_title = _("Add Shared File(s)")
    template_name = "wagtail_admin_files/uploaded_file_add.html"

    def get_breadcrumbs_items(self):
        items = super().get_breadcrumbs_items().copy()
        items.append({
            "url": reverse("wagtail_admin_files:list"),
            "label": _("Shared Files"),
        })
        items.append({
            "url": "",
            "label": _("Add Shared File(s)"),
        })
        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'formset' not in context:
            context['formset'] = SharedFileFormSet(queryset=SharedFile.objects.none())

        return context

    def post(self, request, *args, **kwargs):
        formset = SharedFileFormSet(request.POST, request.FILES)
        if formset.is_valid():

            identifier = None
            grouped = False

            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    if len(instances) > 1:
                        group = SharedFileGroup.objects.create()

                        for file in instances:
                            
                            file.group_id = group.id
                            file.save()

                        identifier = group.id
                        grouped = True

                    elif len(instances) == 1:
                        instances[0].group_id = None
                        instances[0].save()

                        identifier = instances[0].id
                        grouped = False

                    else:
                        messages.warning(request, _("No files were uploaded."))

                    formset.save_m2m()  # Save any many-to-many relationships if needed

                    for form in formset.deleted_forms:
                        if form.instance.pk:
                            form.instance.delete()

            except Exception as e:
                logging.error(f"Error saving shared files: {e}")
                formset.add_error(None, _("An error occurred while saving the files."))

            redirect_url = None
            if grouped:
                redirect_url = reverse("wagtail_admin_files:group_detail", args=[identifier])
                messages.success(request, _("Files uploaded successfully."))
            else:
                redirect_url = reverse("wagtail_admin_files:detail", args=[identifier])
                messages.success(request, _("File uploaded successfully."))

            return redirect(redirect_url)

        context = self.get_context_data(**kwargs)
        context['formset'] = formset
        return self.render_to_response(context)


class SharedFileListView(SharedFileMixin, BaseListView, TemplateView):
    model = SharedFile
    paginate_by = 20
    paginator_class = Paginator
    ordering = "-uploaded_at"
    header_icon = "desktop"
    page_title = _("Shared Files")
    template_name = "wagtail_admin_files/uploaded_file_list.html"
    no_results_message = _("No files were found.")
    page_kwarg = "p"

    def get_breadcrumbs_items(self):
        items = super().get_breadcrumbs_items().copy()

        items.append({
            "url": "",
            "label": _("Shared Files"),
        })

        return items
    
    def get_header_buttons(self):
        buttons = super().get_header_buttons()
        buttons.append(HeaderButton(
            label=_("View Groups"),
            url=reverse("wagtail_admin_files:list_groups")
        ))
        buttons.append(HeaderButton(
            label=_("Add file(s)"),
            url=reverse("wagtail_admin_files:add")
        ))
        return buttons

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_results_message"] = self.no_results_message
        context["group_id"] = self.kwargs.get("group")
        return context


class SharedFileGroupDetailView(SharedFileMixin, TemplateView):
    header_icon = "folder"
    page_title = _("File Group Details")
    template_name = "wagtail_admin_files/uploaded_file_group_detail.html"

    def dispatch(self, request, *args, **kwargs):
        if WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC and request.GET.get("shared", "false").lower() == "true":
            return redirect(reverse("wagtail_public_files:group_detail", args=[self.kwargs["group"]]))
        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs_items(self):
        items = super().get_breadcrumbs_items().copy()
        items.append({
            "url": reverse("wagtail_admin_files:list"),
            "label": _("Shared Files"),
        })
        items.append({
            "url": "",
            "label": _("File Group Details"),
        })
        return items
    
    def get_shared_file_group(self):
        return SharedFileGroup.objects\
            .annotate(file_count=models.Count("sharedfile"))\
            .annotate(latest_upload=models.Max("sharedfile__uploaded_at"))\
            .prefetch_related("sharedfile_set")\
            .get(pk=self.kwargs["group"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_shared_file_group()
        context["object"] = obj
        context["sharing"] = self.request.GET.get("shared", "false").lower() == "true"
        context["share_link"] = f"{self.request.build_absolute_uri(reverse('wagtail_admin_files:group_detail', args=[obj.id]))}?shared=true"
        return context


class SharedFileGroupListView(SharedFileMixin, BaseListView, TemplateView):
    model = SharedFileGroup
    paginate_by = 20
    paginator_class = Paginator
    header_icon = "folder"
    page_title = _("Groups of Files")
    template_name = "wagtail_admin_files/uploaded_file_group_list.html"
    no_results_message = _("No groups were found.")
    page_kwarg = "p"

    def get_queryset(self):
        qs = super().get_queryset()\
            .annotate(file_count=models.Count("sharedfile"))\
            .annotate(latest_upload=models.Max("sharedfile__uploaded_at"))\
            .prefetch_related("sharedfile_set")\
            .order_by("-latest_upload")
        return qs

    def get_breadcrumbs_items(self):
        items = super().get_breadcrumbs_items().copy()
        items.append({
            "url": reverse("wagtail_admin_files:list"),
            "label": _("Shared Files"),
        })
        items.append({
            "url": "",
            "label": _("Files in Group"),
        })
        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_results_message"] = self.no_results_message
        return context
