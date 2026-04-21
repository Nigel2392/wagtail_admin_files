from django.conf import settings

WAGTAIL_ADMIN_FILES_MENU_HOOK = getattr(settings, "WAGTAIL_ADMIN_FILES_MENU_HOOK", "register_settings_menu_item")
WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC = getattr(settings, "WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC", True)
WAGTAIL_ADMIN_FILES_TEMPLATE_EXTENDS = getattr(settings, "WAGTAIL_ADMIN_FILES_TEMPLATE_EXTENDS", "base.html")