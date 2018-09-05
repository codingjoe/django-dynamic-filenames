from django.db import models

from dynamic_filenames import FilePattern


upload_to_pattern = FilePattern(
    slug_from='title',
    filename_pattern='{slug}{ext}',
)


class DefaultModel(models.Model):
    title = models.CharField(max_length=100)
    file_field = models.FileField(upload_to=upload_to_pattern)
