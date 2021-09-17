import base64
import os
import re
import uuid
from string import Formatter


def slugify(value):
    try:  # use unicode-slugify library if installed
        from slugify import slugify as _slugify

        return _slugify(value, only_ascii=True)
    except ImportError:
        from django.utils.text import slugify as _slugify

        return _slugify(value, allow_unicode=False)


class SlugFormatter(Formatter):
    format_spec_pattern = re.compile(r"(\.\d+)?([\d\w]+)?")

    def format_field(self, value, format_spec):
        precision, ftype = self.format_spec_pattern.match(format_spec).groups()
        if precision:
            precision = int(precision.lstrip("."))
        if ftype == "slug":
            return slugify(value)[:precision]
        return super().format_field(value=value, format_spec=format_spec)


class ExtendedUUID(uuid.UUID):
    format_spec_pattern = re.compile(r"(\.\d+)?([\d\w]+)?")

    def __format__(self, format_spec):
        precision, ftype = self.format_spec_pattern.match(format_spec).groups()
        if precision:
            precision = int(precision.lstrip("."))
        if ftype == "":
            return str(self)[:precision]
        if ftype == "s":
            return str(self)[:precision]
        if ftype == "i":
            return str(self.int)[:precision]
        if ftype == "x":
            return self.hex.lower()[:precision]
        if ftype == "X":
            return self.hex.upper()[:precision]
        if ftype == "base32":
            return (
                base64.b32encode(self.bytes).decode("utf-8").rstrip("=\n")[:precision]
            )
        if ftype == "base64":
            return (
                base64.urlsafe_b64encode(self.bytes)
                .decode("utf-8")
                .rstrip("=\n")[:precision]
            )
        return super().__format__(format_spec)


class FilePattern:
    """
    Write advanced filename patterns using the Format String Syntax.

    Basic example:

    .. code-block:: python

        from django.db import models
        from dynamic_names import FilePattern

        upload_to_pattern = FilePattern('{app_label:.25}/{model_name:.30}/{uuid:.30base32}{ext}')

        class FileModel(models.Model):
            my_file = models.FileField(upload_to=upload_to_pattern)

    Args:
        ext: File extension including the dot.
        name: Filename excluding the folders.
        model_name: Name of the Django model.
        app_label: App label of the Django model.
        uuid:
            UUID version 4 that supports multiple type specifiers. The UUID will be
            the same should you use it twice in the same string, but different on each
            invocation of the ``upload_to`` callable.
        instance:
            Instance of the model before it has been saved.
            You may not have a primary key at this point.


    Auto slug example:

    .. code-block:: python

        from django.db import models
        from dynamic_names import FilePattern

        class TitleSlugPattern(FilePattern):
            filename_pattern = '{app_label:.25}/{model_name:.30}/{instance.title:slug}{ext}'

        class FileModel(models.Model):
            title = models.CharField(max_length=100)
            my_file = models.FileField(upload_to=TitleSlugPattern())

    """

    formatter = SlugFormatter()

    filename_pattern = "{name}{ext}"

    def __call__(self, instance, filename):
        """Return filename based for given instance and filename."""
        # UUID needs to be set on call, not per instance to avoid state leakage.
        path, ext = os.path.splitext(filename)
        path, name = os.path.split(path)
        defaults = {
            "ext": ext,
            "name": name,
            "model_name": instance._meta.model_name,
            "app_label": instance._meta.app_label,
            "uuid": self.get_uuid(),
            "instance": instance,
        }
        defaults.update(self.override_values)
        return self.formatter.format(self.filename_pattern, **defaults)

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        override_values = kwargs.copy()
        self.filename_pattern = override_values.pop(
            "filename_pattern", self.filename_pattern
        )
        self.override_values = override_values

    def deconstruct(self):
        """Destruct callable to support Django migrations."""
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        return path, [], self.kwargs

    @staticmethod
    def get_uuid():
        """Return UUID version 4."""
        return ExtendedUUID(bytes=os.urandom(16), version=4)
