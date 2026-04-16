from django.apps import AppConfig


class WagtailAdminFilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wagtail_admin_files'

    def ready(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import SharedFile

        content_type = ContentType.objects.get_for_model(SharedFile)
        Permission.objects.get_or_create(
            content_type=content_type,
            codename="view_sharedfile",
            name="Can view shared file",
        )
