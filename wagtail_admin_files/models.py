import uuid
from django.db import models, transaction
from django.utils import timezone
from django.urls import reverse

def create_shared_file(title: str, file, group=None, save_copy=False, commit: bool = True):
    if title:
        title = title.strip()

    if not title:
        raise ValueError("Title is required")

    file_model = SharedFile(title=title, group=group)

    if save_copy:
        file_model.file.save(file.name, file)
    else:
        file_model.file.name = file.name

    if commit:
        file_model.save()

    return file_model

class SharedFileManager(models.Manager):
    def create_shared_file(self, title: str, file, group=None, save_copy=False, commit: bool = True):
        return create_shared_file(title=title, file=file, group=group, save_copy=save_copy, commit=commit)
    

class SharedFile(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title       = models.CharField(max_length=255)
    file        = models.FileField(upload_to="wagtail_admin_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    group       = models.ForeignKey("wagtail_admin_files.SharedFileGroup", on_delete=models.CASCADE, null=True, blank=True)

    objects: SharedFileManager = SharedFileManager()

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["-uploaded_at"]

    @property
    def file_extension(self):
        return self.file.name.split('.')[-1]
    
    def get_absolute_url(self, request=None):
        if request:
            return request.build_absolute_uri(reverse("wagtail_admin_files:detail", kwargs={"pk": self.pk}))
        
        return reverse("wagtail_admin_files:detail", kwargs={"pk": self.pk})


class SharedFileGroupContextManager:
    def __init__(self, save_copies: bool = False, commit: bool = True):
        self.group = SharedFileGroup()
        self.save_copies = save_copies
        self.commit = commit
        self._files = []
        self._created_files = []

    def add_file(self, title: str, file):
        self._files.append((title, file))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.cleanup_physical_files()
            return False

        if not self.commit:
            return False

        try:
            self.save()
        except Exception:
            self.cleanup_physical_files()
            raise
        return False
    
    def cleanup_physical_files(self):
        for file in self._created_files:
            file.delete(save=False)

    @transaction.atomic
    def save(self):
        if not self.group._state.adding:
            raise ValueError("This context manager has already been used to save a group. Please create a new instance for each group you want to create.")
        
        if not self._files:
            raise ValueError("At least one file must be added to the group before saving.")
        
        self.group.save()

        unsaved = []
        uploaded_at = timezone.now()
        for title, file in self._files:
            title = title.strip()
            if not title:
                raise ValueError("Title is required")
            
            file_model = SharedFile(
                title=title,
                group=self.group,
                uploaded_at=uploaded_at,
            )
            
            if self.save_copies:
                file_model.file.save(file.name, file, False)
                self._created_files.append(file_model.file)
            else:
                file_model.file.name = file.name

            unsaved.append(file_model)

        if not unsaved:
            raise ValueError("At least one file must be added to the group before saving.")

        return SharedFile.objects.bulk_create(unsaved)


class SharedFileGroup(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    @classmethod
    def context_manager(cls, save_copies: bool = False, commit: bool = True):
        return SharedFileGroupContextManager(save_copies=save_copies, commit=commit)
    
    def get_absolute_url(self, request=None):
        if request:
            return request.build_absolute_uri(reverse("wagtail_admin_files:group_detail", kwargs={"pk": self.pk}))
        
        return reverse("wagtail_admin_files:group_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.id)

