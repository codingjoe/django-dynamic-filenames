========================
Django Dynamic Filenames
========================

Write advanced filename patterns using the `Format Specification Mini-Language`__.

__ https://docs.python.org/3/library/string.html#format-string-syntax

Getting Started
---------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

    pip install django-dynamic-filenames

Samples
~~~~~~~

Basic example:

.. code-block:: python

    from django.db import models
    from dynamic_names import FilePattern

    upload_to_pattern = FilePattern('{app_name:.25}/{model_name:.30}/{uuid_base32}{ext}')

    class FileModel(models.Model):
        my_file = models.FileField(upload_to=upload_to_pattern)


Auto slug example:

.. code-block:: python

    from django.db import models
    from dynamic_names import FilePattern

    class SlugPattern(FilePattern):
        filename_pattern = '{app_name:.25}/{model_name:.30}/{slug}{ext}'

    class FileModel(models.Model):
        title = models.CharField(max_length=100)
        my_file = models.FileField(upload_to=SlugPattern(populate_slug_from='title'))

Supported Attributes
--------------------

``ext``
    File extension including the dot.

``name``
    Filename excluding the folders.

``model_name``
    Name of the Django model.

``app_label``
    App label of the Django model.

``uuid_base16``
    Base16 (hex) representation of a UUID.

``uuid_base32``
    Base32 representation of a UUID.

``uuid_base64``
    Base64 representation of a UUID. Not supported by all file systems.

``slug``
    Auto created slug based on another field on the model instance.

``slug_from``
    Name of the field the slug should be populated from.

    .. note:: The field name itself is not part of the pattern.
