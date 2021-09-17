from django.db import models

from dynamic_filenames import FilePattern

upload_to_pattern = FilePattern(
    filename_pattern="{instance.title:slug}{ext}",
)


class DefaultModel(models.Model):
    title = models.CharField(max_length=100, default="hello goodby")
    file_field = models.FileField(upload_to=upload_to_pattern)
