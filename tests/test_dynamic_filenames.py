import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command

from dynamic_filenames import ExtendedUUID, FilePattern
from tests.testapp.models import DefaultModel


class FixedUUIDFilePattern(FilePattern):
    @staticmethod
    def get_uuid():
        return ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")


class TestFilePattern:
    def test_init(self):
        assert FilePattern().kwargs == {}
        assert FilePattern().override_values == {}

        assert FilePattern(path="sth").kwargs == {"path": "sth"}
        assert FilePattern(path="sth").override_values == {"path": "sth"}

    def test_call__default(self):
        assert (
            FilePattern()(instance=DefaultModel(), filename="test_file.txt")
            == "test_file.txt"
        )

    def test_call__no_extension(self):
        assert (
            FilePattern()(instance=DefaultModel(), filename="test_file") == "test_file"
        )

    def test_call__only_extension(self):
        assert (
            FilePattern()(instance=DefaultModel(), filename=".htaccess") == ".htaccess"
        )

    def test_call__dot_file(self):
        assert (
            FilePattern()(instance=DefaultModel(), filename=".hidden-truth.txt")
            == ".hidden-truth.txt"
        )

    def test_call__full_path(self):
        assert (
            FilePattern()(instance=DefaultModel(), filename="/var/www/index.html")
            == "index.html"
        )

    def test_call__override_pattern(self):
        assert (
            FilePattern(filename_pattern="my_file{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "my_file.txt"
        )

    def test_call__uuid(self):
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid}{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "522d6f35-1920-4b0f-b82a-e8f558af2749.txt"
        )

    def test_call__uuid_str(self):
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid:s}{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "522d6f35-1920-4b0f-b82a-e8f558af2749.txt"
        )

    def test_call__uuid_base10(self):
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid:i}{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "109232604567331952752042348453722793801.txt"
        )

    def test_call__uuid_hex_lower(self):
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid:x}{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "522d6f3519204b0fb82ae8f558af2749.txt"
        )

    def test_call__uuid_hex_upper(self):
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid:X}{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "522D6F3519204B0FB82AE8F558AF2749.txt"
        )

    def test_call__uuid_base32(self):
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid:base32}{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "KIWW6NIZEBFQ7OBK5D2VRLZHJE.txt"
        )

    def test_call__uuid_base64(self):
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid:base64}{ext}")(
                instance=DefaultModel(), filename="other_file.txt"
            )
            == "Ui1vNRkgSw-4Kuj1WK8nSQ.txt"
        )

    def test_call__app_label(self):
        assert (
            FilePattern(filename_pattern="{app_label}/{name}{ext}")(
                instance=DefaultModel(), filename="some_file.txt"
            )
            == "testapp/some_file.txt"
        )

    def test_call__model_name(self):
        assert (
            FilePattern(filename_pattern="{model_name}/{name}{ext}")(
                instance=DefaultModel(), filename="some_file.txt"
            )
            == "defaultmodel/some_file.txt"
        )

    def test_call__name_override(self):
        assert (
            FilePattern(name="special_name")(
                instance=DefaultModel(), filename="some_file.txt"
            )
            == "special_name.txt"
        )

    def test_call__slug(self):
        assert (
            FilePattern(filename_pattern="{instance.title:slug}{ext}")(
                instance=DefaultModel(title="best model with ünicode"),
                filename="some_file.txt",
            )
            == "best-model-with-unicode.txt"
        )

    def test_call__slug_precision(self):
        assert (
            FilePattern(filename_pattern="{instance.title:.4slug}{ext}")(
                instance=DefaultModel(title="best model"), filename="some_file.txt"
            )
            == "best.txt"
        )

    def test_destruct(self):
        assert FilePattern().deconstruct() == ("dynamic_filenames.FilePattern", [], {})
        assert FilePattern(filename_pattern="{name}{ext}").deconstruct() == (
            "dynamic_filenames.FilePattern",
            [],
            {"filename_pattern": "{name}{ext}"},
        )
        assert FilePattern(name="sth").deconstruct() == (
            "dynamic_filenames.FilePattern",
            [],
            {"name": "sth"},
        )

    def test_uuid(self):
        assert isinstance(FilePattern.get_uuid(), uuid.UUID), "type uuid.UUID expected"
        assert FilePattern.get_uuid().hex[12] == "4", "UUID version 4 expected"
        assert (
            FixedUUIDFilePattern(filename_pattern="{uuid:x}{ext}")(
                instance=DefaultModel(title="best model"), filename="some_file.txt"
            )
            == "522d6f3519204b0fb82ae8f558af2749.txt"
        )


class TestExtendedUUID:
    def test_uuid_2_base10(self):
        guid = ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")
        assert isinstance(format(guid, "i"), str)
        assert len(format(guid, "i")) == 39
        assert format(guid, "i") == "109232604567331952752042348453722793801"

    def test_uuid_2_base16_lower(self):
        guid = ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")
        assert isinstance(format(guid, "x"), str)
        assert len(format(guid, "x")) == 32
        assert format(guid, "x") == "522d6f3519204b0fb82ae8f558af2749"

    def test_uuid_2_base16_upper(self):
        guid = ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")
        assert isinstance(format(guid, "X"), str)
        assert len(format(guid, "X")) == 32
        assert format(guid, "X") == "522D6F3519204B0FB82AE8F558AF2749"

    def test_uuid_2_base32(self):
        guid = ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")
        assert isinstance(format(guid, "base32"), str)
        assert len(format(guid, "base32")) == 26
        assert "=" not in format(guid, "base32"), "Trim padding"
        assert format(guid, "base32") == "KIWW6NIZEBFQ7OBK5D2VRLZHJE"

    def test_uuid_2_base64(self):
        guid = ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")
        assert isinstance(format(guid, "base64"), str)
        assert len(format(guid, "base64")) == 22
        assert "=" not in format(guid, "base64"), "Trim padding"
        assert format(guid, "base64") == "Ui1vNRkgSw-4Kuj1WK8nSQ"

    def test_uuid__super(self):
        guid = ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")
        with pytest.raises(TypeError) as e:
            format(guid, "does not exist")
        assert "unsupported format string passed to ExtendedUUID.__format__" in str(e)

    def test_precision(self):
        guid = ExtendedUUID("522d6f3519204b0fb82ae8f558af2749")
        assert len(format(guid, ".11base64")) == 11
        assert format(guid, ".11base64") == "Ui1vNRkgSw-"


def test_migrations(db):
    """Integration tests for deconstruct method."""
    call_command("makemigrations", "testapp", "--no-input")


def test_call(db):
    obj = DefaultModel.objects.create(
        title="hello world",
        file_field=SimpleUploadedFile(name="sample.txt", content=b"hello world"),
    )

    assert obj.file_field.name == "hello-world.txt"
