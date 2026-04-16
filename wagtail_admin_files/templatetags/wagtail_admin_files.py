from django.conf import settings
from django.template import Library
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from urllib.parse import quote, urljoin

from ..models import SharedFile

register = Library()

@register.simple_tag(name="render_file", takes_context=True)
def render_file(context, file: SharedFile, attrs_str=""):
    if "request" in context:
        request = context["request"]
        base_url = request.build_absolute_uri("/")
    else:
        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL")

    return _render_file(file, attrs_str, base_url=base_url)

def _render_file(file: SharedFile, attrs_str="", base_url=""):
    name_parts = file.file.name.rsplit(".", 1)
    extension = name_parts[1].lower() if len(name_parts) > 1 else ""

    if extension in ["jpg", "jpeg", "png", "gif", "svg", "webp", "avif"]:
        return {
            "html": mark_safe(f'''<img src="{file.file.url}" {attrs_str} alt="{file.title}" />'''),
            "url": file.file.url,
            "type": "image",
            "ext": extension,
        }
    elif extension in ["pdf"]:
        url = reverse("wagtail_admin_files:serve_shared_pdf", args=[file.pk])
        return {
            "html": mark_safe(f'''<iframe src="{url}" {attrs_str} title="{file.title}"></iframe>'''),
            "url": url,
            "type": "pdf",
            "ext": extension,
        }
    elif extension in ["mp4", "webm", "ogg"]:
        return {
            "html": mark_safe(f'''<video src="{file.file.url}" {attrs_str} title="{file.title}"></video>'''),
            "url": file.file.url,
            "type": "video",
            "ext": extension,
        }
    elif extension in ["mp3", "wav", "ogg"]:
        return {
            "html": mark_safe(f'''<audio src="{file.file.url}" {attrs_str} title="{file.title}"></audio>'''),
            "url": file.file.url,
            "type": "audio",
            "ext": extension
        }
    elif extension in ["doc", "docx", "xls", "xlsx", "ppt", "pptx", "zip", "rar", "7z", "tar", "gz"]:
        full_url = urljoin(base_url, file.file.url)
        url = quote(full_url, safe='')
        url = f"https://docs.google.com/gview?url={url}"
        return {
            "html": mark_safe(f'''<iframe src="{url}&embedded=true" {attrs_str} title="{file.title}"></iframe>'''),
            "url": url,
            "type": "document",
            "ext": extension
        }

    not_available = static("wagtail_admin_files/img/not_available_squared.jpg")
    return {
        "html": mark_safe(f'''<img src="{not_available}" alt="{file.title}" data-file-url="{file.file.url}" />'''),
        "url": file.file.url,
        "type": "unknown",
        "ext": extension
    }
