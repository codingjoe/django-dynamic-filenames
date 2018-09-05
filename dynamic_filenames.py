import base64
import os
import uuid

try:  # use unicode-slugify library if installed
    from slugify import slugify

    SLUGIFY_KWARGS = dict(only_ascii=True)
except ImportError:
    from django.utils.text import slugify

    SLUGIFY_KWARGS = dict(allow_unicode=False)


class FilePattern:
    """
    Write advanced filename patterns using the Format Specification Mini-Language.

    Basic example:

    .. code-block:: python

        from django.db import models
        from dynamic_names import FilePattern

        upload_to_pattern = FilePattern('{app_name:.25}/{model_name:.30}/{uuid_base32}{ext}')

        class FileModel(models.Model):
            my_file = models.FileField(upload_to=upload_to_pattern)

    Args:

        ext: File extension including the dot.
        name: Filename excluding the folders.
        model_name: Name of the Django model.
        app_label: App label of the Django model.
        uuid_base16: Base16 (hex) representation of a UUID.
        uuid_base32: Base32 representation of a UUID.
        uuid_base64: Base64 representation of a UUID. Not supported by all file systems.
        slug: Auto created slug based on another field on the model instance.
        slug_from: Name of the field the slug should be populated from.


    Auto slug example:

    .. code-block:: python

        from django.db import models
        from dynamic_names import FilePattern

        class SlugPattern(FilePattern):
            filename_pattern = '{app_name:.25}/{model_name:.30}/{slug}{ext}'

        class FileModel(models.Model):
            title = models.CharField(max_length=100)
            my_file = models.FileField(upload_to=SlugPattern(slug_from='title'))

    """

    slug_from = None

    filename_pattern = '{name}{ext}'

    def __call__(self, instance, filename):
        """Return filename based for given instance and filename."""
        # UUID needs to be set on call, not per instance to avoid state leakage.
        guid = self.get_uuid()
        path, ext = os.path.splitext(filename)
        path, name = os.path.split(path)
        defaults = {
            'ext': ext,
            'name': name,
            'model_name': instance._meta.model_name,
            'app_label': instance._meta.app_label,
            'uuid_base10': self.uuid_2_base10(guid),
            'uuid_base16': self.uuid_2_base16(guid),
            'uuid_base32': self.uuid_2_base32(guid),
            'uuid_base64': self.uuid_2_base64(guid),
        }
        defaults.update(self.override_values)
        if self.slug_from is not None:
            field_value = getattr(instance, self.slug_from)
            defaults['slug'] = slugify(field_value, **SLUGIFY_KWARGS)
        return self.filename_pattern.format(**defaults)

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        override_values = kwargs.copy()
        self.slug_from = override_values.pop('slug_from', self.slug_from)
        self.filename_pattern = override_values.pop('filename_pattern', self.filename_pattern)
        self.override_values = override_values

    def deconstruct(self):
        """Destruct callable to support Django migrations."""
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        return path, [], self.kwargs

    @staticmethod
    def get_uuid():
        """Return UUID version 4."""
        return uuid.uuid4()

    @staticmethod
    def uuid_2_base10(uuid):
        """Return 39 digits long integer UUID as Base10."""
        return uuid.int

    @staticmethod
    def uuid_2_base16(uuid):
        """Return 32 char long UUID as Base16 (hex)."""
        return uuid.hex

    @staticmethod
    def uuid_2_base32(uuid):
        """Return 27 char long UUIDv4 as Base32."""
        return base64.b32encode(
            uuid.bytes
        ).decode('utf-8').rstrip('=\n')

    @staticmethod
    def uuid_2_base64(uuid):
        """
        Return 23 char long UUIDv4 as Base64.

        .. warning:: Not all file systems support Base64 file names.
            e.g. The Apple File System (APFS) is case insensitive by default.

        """
        return base64.urlsafe_b64encode(
            uuid.bytes
        ).decode('utf-8').rstrip('=\n')
