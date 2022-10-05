========================
Django Dynamic Filenames
========================

Write advanced filename patterns using the `Format String Syntax`__.

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
    from dynamic_filenames import FilePattern

    upload_to_pattern = FilePattern(
        filename_pattern='{app_label:.25}/{model_name:.30}/{uuid:base32}{ext}'
    )

    class FileModel(models.Model):
        my_file = models.FileField(upload_to=upload_to_pattern)


Auto slug example:


Features
--------

Field names
~~~~~~~~~~~

``ext``
    File extension including the dot.

``name``
    Filename excluding the folders.

``model_name``
    Name of the Django model.

``app_label``
    App label of the Django model.

``instance``
    Instance of the model before it has been saved. You may not have a primary
    key at this point.

``uuid``
    UUID version 4 that supports multiple type specifiers. The UUID will be
    the same should you use it twice in the same string, but different on each
    invocation of the ``upload_to`` callable.

    The type specifiers allow you to format the UUID in different ways, e.g.
    ``{uuid:x}`` will give you a with a hexadecimal UUID.

    The supported type specifiers are:

    ``s``
        String representation of a UUID including dashes.

    ``i``
        Integer representation of a UUID. Like to ``UUID.int``.

    ``x``
        Hexadecimal (Base16) representation of a UUID. Like to ``UUID.hex``.

    ``X``
        Upper case hexadecimal representation of a UUID. Like to
        ``UUID.hex``.

    ``base32``
        Base32 representation of a UUID without padding.

    ``base64``
        Base64 representation of a UUID without padding.

        .. warning:: Not all file systems support Base64 file names.

    All type specifiers also support precisions to cut the string,
    e.g. ``{{uuid:.2base32}}`` would only return the first 2 characters of a
    Base32 encoded UUID.

Type specifiers
~~~~~~~~~~~~~~~

You can also use a special slug type specifier, that slugifies strings.

Example:

.. code-block:: python

    from django.db import models
    from dynamic_filenames import FilePattern

    upload_to_pattern = FilePattern(
        filename_pattern='{app_label:.25}/{model_name:.30}/{instance.title:.40slug}{ext}'
    )

    class FileModel(models.Model):
        title = models.CharField(max_length=100)
        my_file = models.FileField(upload_to=upload_to_pattern)

Slug type specifiers also support precisions to cut the string. In the example
above the slug of the instance title will be cut at 40 characters.
